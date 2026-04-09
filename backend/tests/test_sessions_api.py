from datetime import UTC, datetime, timedelta
from pathlib import Path

from app import create_app
from app.db import SessionLocal
from app.models import AttachmentRecord, DocumentRecord, MessageRecord, SessionRecord


def build_app(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{tmp_path / 'test.db'}",
        "ADMIN_TOKEN": "admin-secret",
        "UPLOAD_DIR": str(tmp_path / "uploads"),
    }
    config.update(overrides)
    return create_app(config)


def seed_session(
    app,
    *,
    token: str,
    status: str = "awaiting_user",
    previous_summary: str | None = None,
    messages: list[dict] | None = None,
    attachments: list[dict] | None = None,
    expires_at: datetime | None = None,
    next_session_token: str | None = None,
):
    now = datetime.now(UTC)

    with app.app_context():
        db = SessionLocal()
        try:
            previous_document_id = None
            if previous_summary is not None:
                db.add(SessionRecord(token="origin-token", status="completed"))
                previous_document = DocumentRecord(
                    session_token="origin-token",
                    status="ready",
                    revision_number=1,
                    summary_text=previous_summary,
                    prd_markdown="# 上一版文档",
                )
                db.add(previous_document)
                db.flush()
                previous_document_id = previous_document.id

            session = SessionRecord(
                token=token,
                status=status,
                admin_note="测试会话",
                previous_document_id=previous_document_id,
                next_session_token=next_session_token,
                last_activity_at=now,
                last_user_message_at=now,
                expires_at=expires_at or (now + timedelta(hours=24)),
            )
            db.add(session)
            db.add(DocumentRecord(session_token=token, revision_number=1))
            db.flush()

            for item in messages or []:
                db.add(
                    MessageRecord(
                        session_token=token,
                        role=item["role"],
                        content=item["content"],
                        delivery_status=item.get("delivery_status", "final"),
                    )
                )

            for item in attachments or []:
                db.add(
                    AttachmentRecord(
                        session_token=token,
                        file_name=item["file_name"],
                        file_path=item.get("file_path", f"/tmp/{item['file_name']}"),
                        mime_type=item.get("mime_type", "image/png"),
                        caption=item.get("caption", ""),
                    )
                )

            db.commit()
        finally:
            db.close()


def test_create_session_endpoint_is_not_available(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    response = client.post("/api/sessions")

    assert response.status_code == 404


def test_get_session_returns_recent_messages_and_previous_summary(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(
        app,
        token="invite-token",
        previous_summary="上一版摘要",
        messages=[
            {"role": "assistant", "content": "欢迎使用。", "delivery_status": "system"},
            {"role": "user", "content": "我想做个人作品网站。"},
            {"role": "assistant", "content": "先告诉我你的目标用户。"},
        ],
        attachments=[{"file_name": "reference.png", "caption": "首页参考"}],
    )

    response = client.get("/api/sessions/invite-token")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["token"] == "invite-token"
    assert payload["status"] == "awaiting_user"
    assert payload["messages"][0]["delivery_status"] == "system"
    assert payload["previous_summary"] == "上一版摘要"
    assert payload["attachments"][0]["file_name"] == "reference.png"
    assert payload["document"]["status"] == "pending"
    assert payload["successor_token"] is None
    assert payload["has_more"] is False
    assert payload["oldest_message_id"] == payload["messages"][0]["id"]
    assert "current_stage" not in payload
    assert "selected_template" not in payload
    assert "selected_style" not in payload


def test_get_session_reports_recent_window_and_has_more(tmp_path):
    app = build_app(tmp_path, SESSION_MESSAGES_PAGE_SIZE=2)
    client = app.test_client()
    seed_session(
        app,
        token="window-token",
        messages=[
            {"role": "assistant", "content": "欢迎。", "delivery_status": "system"},
            {"role": "user", "content": "第一条"},
            {"role": "assistant", "content": "第二条"},
        ],
    )

    response = client.get("/api/sessions/window-token")
    payload = response.get_json()

    assert response.status_code == 200
    assert [item["content"] for item in payload["messages"]] == ["第一条", "第二条"]
    assert payload["has_more"] is True
    assert payload["oldest_message_id"] == payload["messages"][0]["id"]


def test_get_session_messages_supports_before_id_pagination(tmp_path):
    app = build_app(tmp_path, SESSION_MESSAGES_PAGE_SIZE=2)
    client = app.test_client()
    seed_session(
        app,
        token="history-token",
        messages=[
            {"role": "assistant", "content": "欢迎。", "delivery_status": "system"},
            {"role": "user", "content": "第一条"},
            {"role": "assistant", "content": "第二条"},
            {"role": "user", "content": "第三条"},
        ],
    )

    session_payload = client.get("/api/sessions/history-token").get_json()
    before_id = session_payload["oldest_message_id"]

    response = client.get(f"/api/sessions/history-token/messages?before_id={before_id}&limit=2")
    payload = response.get_json()

    assert response.status_code == 200
    assert [item["content"] for item in payload["messages"]] == ["欢迎。", "第一条"]
    assert payload["has_more"] is False
    assert payload["oldest_message_id"] == payload["messages"][0]["id"]


def test_missing_session_returns_chinese_404_message(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    response = client.get("/api/sessions/missing-token")

    assert response.status_code == 404
    assert response.get_json() == {"message": "这次整理链接可能已失效，请联系管理员获取新的入口。"}


def test_expired_session_returns_clear_message_and_marks_record(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(
        app,
        token="expired-token",
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )

    response = client.get("/api/sessions/expired-token")

    assert response.status_code == 410
    assert response.get_json() == {"message": "这个整理链接已经失效，请联系管理员获取新的入口。"}

    with app.app_context():
        db = SessionLocal()
        try:
            saved = db.get(SessionRecord, "expired-token")
        finally:
            db.close()

    assert saved.status == "expired"


def test_session_record_uses_chat_first_fields(tmp_path):
    app = build_app(tmp_path, DATABASE_URL=f"sqlite:///{tmp_path / 'chat-first.db'}")

    with app.app_context():
        db = SessionLocal()
        try:
            session = SessionRecord(
                token="invite-token",
                status="awaiting_user",
                admin_note="首版需求",
                origin_session_token="origin-token",
            )
            db.add(session)
            db.add(DocumentRecord(session_token="invite-token", revision_number=1))
            db.add(
                MessageRecord(
                    session_token="invite-token",
                    role="assistant",
                    content="欢迎使用。",
                    delivery_status="system",
                )
            )
            db.commit()

            saved_session = db.get(SessionRecord, "invite-token")
            saved_document = (
                db.query(DocumentRecord).filter_by(session_token="invite-token").one()
            )
            saved_message = (
                db.query(MessageRecord).filter_by(session_token="invite-token").one()
            )
        finally:
            db.close()

    assert saved_session.status == "awaiting_user"
    assert saved_session.next_session_token is None
    assert saved_session.admin_note == "首版需求"
    assert saved_session.origin_session_token == "origin-token"
    assert saved_document.revision_number == 1
    assert saved_message.delivery_status == "system"


def test_default_config_includes_chat_first_runtime_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("SESSION_IDLE_TIMEOUT_SECONDS", "301")
    monkeypatch.setenv("SESSION_EXPIRY_HOURS", "25")
    monkeypatch.setenv("SESSION_MESSAGES_PAGE_SIZE", "51")

    app = build_app(tmp_path, DATABASE_URL=f"sqlite:///{tmp_path / 'chat-first.db'}")

    assert app.config["ADMIN_TOKEN"] == "admin-secret"
    assert app.config["SESSION_IDLE_TIMEOUT_SECONDS"] == 301
    assert app.config["SESSION_EXPIRY_HOURS"] == 25
    assert app.config["SESSION_MESSAGES_PAGE_SIZE"] == 51


def test_env_example_mentions_admin_token():
    content = Path(__file__).resolve().parents[2] / ".env.example"
    content = content.read_text(encoding="utf-8")
    assert "ADMIN_TOKEN=" in content
