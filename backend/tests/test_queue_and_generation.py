from datetime import UTC, datetime, timedelta
from io import BytesIO

from app import create_app
from app.db import SessionLocal
from app.models import AttachmentRecord, DocumentRecord, MessageRecord, SessionRecord


def build_app(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{tmp_path / 'queue.db'}",
        "ADMIN_TOKEN": "admin-secret",
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "SESSION_MESSAGES_PAGE_SIZE": 50,
    }
    config.update(overrides)
    return create_app(config)


def seed_session(
    app,
    *,
    token: str,
    status: str = "awaiting_user",
    last_activity_at: datetime | None = None,
    expires_at: datetime | None = None,
):
    now = datetime.now(UTC)

    with app.app_context():
        db = SessionLocal()
        try:
            session = SessionRecord(
                token=token,
                status=status,
                last_activity_at=last_activity_at or now,
                last_user_message_at=last_activity_at or now,
                expires_at=expires_at or (now + timedelta(hours=24)),
            )
            db.add(session)
            db.add(DocumentRecord(session_token=token, revision_number=1))
            db.add(
                MessageRecord(
                    session_token=token,
                    role="assistant",
                    content="欢迎使用。",
                    delivery_status="system",
                )
            )
            db.commit()
        finally:
            db.close()


def test_message_route_returns_ready_to_generate_intent(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="invite-token")

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        lambda *args, **kwargs: {
            "assistant_message": "信息已经足够，我可以整理最终需求文档。",
            "conversation_intent": "ready_to_generate",
        },
        raising=False,
    )
    monkeypatch.setattr(
        "app.routes.messages.LLMClient.from_env",
        lambda: object(),
    )

    response = client.post(
        "/api/sessions/invite-token/messages",
        json={"content": "我想做一个极简的个人作品网站"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["assistant_reply"] == "信息已经足够，我可以整理最终需求文档。"
    assert payload["conversation_intent"] == "ready_to_generate"
    assert payload["session_status"] == "awaiting_user"
    assert payload["poll_after_ms"] == 3000


def test_message_route_final_document_intent_completes_session(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="final-doc-token")

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        lambda *args, **kwargs: {
            "assistant_message": "# 最终需求文档\n\n这是整理后的最终文档。",
            "conversation_intent": "final_document",
        },
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    response = client.post(
        "/api/sessions/final-doc-token/messages",
        json={"content": "够了，直接帮我生成最终需求文档。"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["session_status"] == "completed"
    assert payload["successor_token"] is not None
    assert payload["assistant_reply"].startswith("# 最终需求文档")

    session_payload = client.get("/api/sessions/final-doc-token").get_json()
    assert session_payload["status"] == "completed"
    assert session_payload["successor_token"] is not None

    document_payload = client.get("/api/sessions/final-doc-token/document").get_json()
    assert document_payload["status"] == "ready"
    assert document_payload["prd_markdown"].startswith("# 最终需求文档")


def test_message_route_includes_new_user_message_in_llm_context(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="context-token")
    captured = {}

    def fake_generate_chat_reply(_client, *, session_context, recent_messages):
        captured["recent_messages"] = recent_messages
        return {
            "assistant_message": "继续告诉我你的目标用户。",
            "conversation_intent": "continue",
        }

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        fake_generate_chat_reply,
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    response = client.post(
        "/api/sessions/context-token/messages",
        json={"content": "我想做一个摄影作品集网站"},
    )

    assert response.status_code == 201
    assert captured["recent_messages"][-1] == {
        "role": "user",
        "content": "我想做一个摄影作品集网站",
    }


def test_user_message_is_committed_before_llm_reply_returns(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="committed-user-message-token")
    captured = {}

    def fake_generate_chat_reply(_client, *, session_context, recent_messages):
        db = SessionLocal()
        try:
            rows = (
                db.query(MessageRecord)
                .filter(MessageRecord.session_token == "committed-user-message-token")
                .order_by(MessageRecord.id.asc())
                .all()
            )
            captured["persisted_messages"] = [
                {"role": row.role, "content": row.content} for row in rows
            ]
        finally:
            db.close()

        return {
            "assistant_message": "继续告诉我你最想突出哪些作品。",
            "conversation_intent": "continue",
        }

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        fake_generate_chat_reply,
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    response = client.post(
        "/api/sessions/committed-user-message-token/messages",
        json={"content": "我想先突出建筑摄影作品"},
    )

    assert response.status_code == 201
    assert captured["persisted_messages"][-1] == {
        "role": "user",
        "content": "我想先突出建筑摄影作品",
    }


def test_message_route_includes_attachments_in_llm_context(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="attachment-context-token")
    captured = {}

    with app.app_context():
        db = SessionLocal()
        try:
            db.add(
                AttachmentRecord(
                    session_token="attachment-context-token",
                    file_name="reference.png",
                    file_path=str(tmp_path / "uploads" / "attachment-context-token" / "reference.png"),
                    mime_type="image/png",
                    caption="苹果官网风格参考",
                )
            )
            db.commit()
        finally:
            db.close()

    def fake_generate_chat_reply(_client, *, session_context, recent_messages):
        captured["session_context"] = session_context
        return {
            "assistant_message": "我已经看到你上传的参考图了。",
            "conversation_intent": "continue",
        }

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        fake_generate_chat_reply,
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    response = client.post(
        "/api/sessions/attachment-context-token/messages",
        json={"content": "参考我上传的图片继续整理"},
    )

    assert response.status_code == 201
    assert captured["session_context"]["attachments"] == [
        {
            "file_name": "reference.png",
            "caption": "苹果官网风格参考",
            "mime_type": "image/png",
        }
    ]


def test_plain_text_final_document_reply_still_completes_session(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="plain-final-doc-token")

    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            return type(
                "Response",
                (),
                {
                    "text": "# 个人摄影作品集网站需求文档\n\n## 1. 网站目标\n- 展示摄影作品\n\n## 2. 视觉风格\n- 黑白极简"
                },
            )()

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeClient())

    response = client.post(
        "/api/sessions/plain-final-doc-token/messages",
        json={"content": "不用更新了 就这个"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["session_status"] == "completed"
    assert payload["successor_token"] is not None

    document_payload = client.get("/api/sessions/plain-final-doc-token/document").get_json()
    assert document_payload["status"] == "ready"
    assert document_payload["prd_markdown"].startswith("# 个人摄影作品集网站需求文档")


def test_document_generation_creates_successor_token(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="ready-token")

    monkeypatch.setattr(
        "app.routes.messages.render_document_bundle",
        lambda **_: ("摘要", "# 文档"),
    )

    response = client.post(
        "/api/sessions/ready-token/messages",
        json={"content": "请开始生成最终需求文档", "confirm_generate": True},
    )
    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "generating_document"
    assert payload["poll_after_ms"] == 5000

    follow_up = client.get("/api/sessions/ready-token")
    follow_up_payload = follow_up.get_json()

    assert follow_up.status_code == 200
    assert follow_up_payload["status"] == "completed"
    assert follow_up_payload["successor_token"] is not None

    document_response = client.get("/api/sessions/ready-token/document")
    assert document_response.get_json()["prd_markdown"] == "# 文档"


def test_confirm_generate_allows_empty_content(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="empty-confirm-token")

    monkeypatch.setattr(
        "app.routes.messages.render_document_bundle",
        lambda **_: ("摘要", "# 文档"),
    )

    response = client.post(
        "/api/sessions/empty-confirm-token/messages",
        json={"confirm_generate": True},
    )

    assert response.status_code == 202
    assert response.get_json()["session_status"] == "generating_document"


def test_confirm_generate_replaces_placeholder_summary_with_conversation_summary(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="summary-token")

    monkeypatch.setattr(
        "app.routes.messages.render_document_bundle",
        lambda **_: ("网站类型：未确定\n视觉方向：未确定", "# 文档"),
    )

    response = client.post(
        "/api/sessions/summary-token/messages",
        json={"content": "我想做一个极简的建筑事务所官网", "confirm_generate": True},
    )

    assert response.status_code == 202

    document_response = client.get("/api/sessions/summary-token/document")
    payload = document_response.get_json()

    assert payload["summary_text"] != "网站类型：未确定\n视觉方向：未确定"
    assert "建筑事务所官网" in payload["summary_text"]


def test_sequential_messages_release_active_slots(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()

    for index in range(6):
        seed_session(app, token=f"token-{index}")

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        lambda *args, **kwargs: {
            "assistant_message": "继续告诉我你想展示什么内容。",
            "conversation_intent": "continue",
        },
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    for index in range(6):
        response = client.post(
            f"/api/sessions/token-{index}/messages",
            json={"content": "我想做个人网站"},
        )
        assert response.status_code == 201

    with app.app_context():
        db = SessionLocal()
        try:
            statuses = [db.get(SessionRecord, f"token-{index}").status for index in range(6)]
        finally:
            db.close()

    assert statuses == ["awaiting_user"] * 6


def test_sixth_processing_session_is_queued(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    for index in range(6):
        seed_session(app, token=f"token-{index}")

    with app.app_context():
        db = SessionLocal()
        try:
            for index in range(5):
                session = db.get(SessionRecord, f"token-{index}")
                session.status = "active"
                session.last_activity_at = datetime.now(UTC)
            db.commit()
        finally:
            db.close()

    response = client.post(
        "/api/sessions/token-5/messages",
        json={"content": "我想做公司介绍页"},
    )
    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "queued"
    assert payload["queue_position"] == 1
    assert payload["poll_after_ms"] == 3000


def test_idle_sessions_release_slots_after_five_minutes(tmp_path, monkeypatch):
    app = build_app(tmp_path)
    client = app.test_client()
    stale_time = datetime.now(UTC) - timedelta(minutes=6)

    for index in range(6):
        seed_session(app, token=f"idle-{index}", status="active" if index < 5 else "awaiting_user", last_activity_at=stale_time)

    monkeypatch.setattr(
        "app.routes.messages.generate_chat_reply",
        lambda *args, **kwargs: {
            "assistant_message": "继续告诉我你的目标用户。",
            "conversation_intent": "continue",
        },
        raising=False,
    )
    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: object())

    response = client.post(
        "/api/sessions/idle-5/messages",
        json={"content": "我想做一个品牌主页"},
    )

    assert response.status_code == 201

    with app.app_context():
        db = SessionLocal()
        try:
            stale_statuses = [db.get(SessionRecord, f"idle-{index}").status for index in range(5)]
        finally:
            db.close()

    assert stale_statuses == ["awaiting_user"] * 5


def test_message_route_rejects_expired_token_after_twenty_four_hours(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(
        app,
        token="expired-token",
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )

    response = client.post(
        "/api/sessions/expired-token/messages",
        json={"content": "还能继续吗"},
    )

    assert response.status_code == 410
    assert response.get_json() == {"message": "这个整理链接已经失效，请联系管理员获取新的入口。"}


def test_upload_route_rejects_completed_or_expired_token(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="completed-token", status="completed")
    seed_session(
        app,
        token="expired-token",
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )

    completed_response = client.post(
        "/api/sessions/completed-token/attachments",
        data={"file": (BytesIO(b"binary"), "reference.png")},
        content_type="multipart/form-data",
    )
    expired_response = client.post(
        "/api/sessions/expired-token/attachments",
        data={"file": (BytesIO(b"binary"), "reference.png")},
        content_type="multipart/form-data",
    )

    assert completed_response.status_code == 409
    assert completed_response.get_json() == {"message": "当前整理链接已结束，不能继续上传附件。"}
    assert expired_response.status_code == 410
    assert expired_response.get_json() == {"message": "这个整理链接已经失效，请联系管理员获取新的入口。"}


def test_upload_route_returns_json_error_when_file_is_missing(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="missing-file-token")

    response = client.post(
        "/api/sessions/missing-file-token/attachments",
        data={"caption": "没有文件"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "请上传图片文件。"}
