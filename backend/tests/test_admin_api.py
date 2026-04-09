from datetime import UTC, datetime, timedelta

from app import create_app
from app.db import SessionLocal
from app.models import AttachmentRecord, DocumentRecord, MessageRecord, SessionRecord


def build_app(tmp_path, **overrides):
    config = {
        "TESTING": True,
        "DATABASE_URL": f"sqlite:///{tmp_path / 'admin.db'}",
        "ADMIN_TOKEN": "admin-secret",
        "UPLOAD_DIR": str(tmp_path / "uploads"),
    }
    config.update(overrides)
    return create_app(config)


def seed_session(
    app,
    *,
    token: str = "invite-token",
    status: str = "awaiting_user",
    next_session_token: str | None = None,
    previous_summary: str | None = None,
    origin_session_token: str | None = None,
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
                admin_note="李医生主页",
                previous_document_id=previous_document_id,
                origin_session_token=origin_session_token,
                next_session_token=next_session_token,
                last_activity_at=now,
                last_user_message_at=now,
                expires_at=now + timedelta(hours=24),
            )
            db.add(session)
            document = DocumentRecord(
                session_token=token,
                status="ready" if status == "completed" else "pending",
                revision_number=1,
                summary_text="这是摘要" if status == "completed" else "",
                prd_markdown="# 文档" if status == "completed" else "",
            )
            db.add(document)
            db.flush()
            db.add(
                MessageRecord(
                    session_token=token,
                    role="assistant",
                    content="欢迎使用。",
                    delivery_status="system",
                )
            )
            db.add(
                MessageRecord(
                    session_token=token,
                    role="user",
                    content="我想做一个医生个人主页。",
                )
            )
            db.add(
                AttachmentRecord(
                    session_token=token,
                    file_name="reference.png",
                    file_path="/tmp/reference.png",
                    mime_type="image/png",
                    caption="参考图",
                )
            )
            db.commit()
        finally:
            db.close()


def test_admin_routes_require_bearer_token(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    missing = client.get("/api/admin/tokens")
    invalid = client.get(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert missing.status_code == 403
    assert invalid.status_code == 403
    assert missing.get_json() == {"message": "管理员凭证无效。"}
    assert invalid.get_json() == {"message": "管理员凭证无效。"}


def test_admin_can_create_token(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    response = client.post(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer admin-secret"},
        json={"admin_note": "李医生主页"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["status"] == "awaiting_user"
    assert payload["admin_note"] == "李医生主页"
    assert payload["successor_token"] is None
    assert "current_stage" not in payload
    assert len(payload["token"]) >= 20

    session_response = client.get(f"/api/sessions/{payload['token']}")
    session_payload = session_response.get_json()

    assert session_response.status_code == 200
    assert session_payload["messages"][0]["delivery_status"] == "system"


def test_admin_create_revision_token_requires_ready_previous_document(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()

    with app.app_context():
        db = SessionLocal()
        try:
            db.add(SessionRecord(token="origin-token", status="completed"))
            ready_document = DocumentRecord(
                session_token="origin-token",
                status="ready",
                revision_number=1,
                summary_text="上一版摘要",
                prd_markdown="# 文档",
            )
            pending_document = DocumentRecord(
                session_token="origin-token",
                status="pending",
                revision_number=2,
            )
            db.add(ready_document)
            db.add(pending_document)
            db.commit()
            ready_id = ready_document.id
            pending_id = pending_document.id
        finally:
            db.close()

    missing_response = client.post(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer admin-secret"},
        json={"admin_note": "修订轮", "previous_document_id": 999999},
    )
    pending_response = client.post(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer admin-secret"},
        json={"admin_note": "修订轮", "previous_document_id": pending_id},
    )
    ready_response = client.post(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer admin-secret"},
        json={"admin_note": "修订轮", "previous_document_id": ready_id},
    )

    assert missing_response.status_code == 400
    assert missing_response.get_json() == {"message": "上一版文档不存在，或还未生成完成。"}
    assert pending_response.status_code == 400
    assert pending_response.get_json() == {"message": "上一版文档不存在，或还未生成完成。"}
    assert ready_response.status_code == 201
    assert ready_response.get_json()["previous_document_id"] == ready_id


def test_admin_can_list_and_read_token_detail(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(
        app,
        token="invite-token",
        status="completed",
        next_session_token="successor-token",
        previous_summary="上一版摘要",
        origin_session_token="origin-token",
    )

    list_response = client.get(
        "/api/admin/tokens",
        headers={"Authorization": "Bearer admin-secret"},
    )
    detail_response = client.get(
        "/api/admin/tokens/invite-token",
        headers={"Authorization": "Bearer admin-secret"},
    )

    list_payload = list_response.get_json()
    detail_payload = detail_response.get_json()

    assert list_response.status_code == 200
    assert list_payload["items"][0]["token"] == "invite-token"
    assert list_payload["items"][0]["status"] == "completed"
    assert list_payload["items"][0]["message_count"] == 2
    assert list_payload["items"][0]["attachment_count"] == 1
    assert list_payload["items"][0]["document_status"] == "ready"
    assert list_payload["items"][0]["previous_document_id"] is not None
    assert list_payload["items"][0]["origin_session_token"] == "origin-token"
    assert list_payload["items"][0]["next_session_token"] == "successor-token"

    assert detail_response.status_code == 200
    assert detail_payload["token"] == "invite-token"
    assert detail_payload["message_count"] == 2
    assert detail_payload["attachment_count"] == 1
    assert detail_payload["last_activity_at"] is not None
    assert detail_payload["created_at"] is not None
    assert detail_payload["completed_at"] is None
    assert detail_payload["document"]["summary_text"] == "这是摘要"
    assert detail_payload["document"]["prd_markdown"] == "# 文档"
    assert detail_payload["previous_summary"] == "上一版摘要"
    assert detail_payload["successor_token"] == "successor-token"
    assert detail_payload["previous_document_id"] is not None
    assert detail_payload["origin_session_token"] == "origin-token"
    assert detail_payload["next_session_token"] == "successor-token"
    assert detail_payload["attachments"][0]["file_name"] == "reference.png"
    assert detail_payload["attachments"][0]["caption"] == "参考图"
    assert detail_payload["attachments"][0]["preview_url"] == "/api/sessions/invite-token/attachments/1/preview"


def test_admin_can_revoke_token(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    seed_session(app, token="invite-token")

    response = client.post(
        "/api/admin/tokens/invite-token/revoke",
        headers={"Authorization": "Bearer admin-secret"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "expired"

    with app.app_context():
        db = SessionLocal()
        try:
            session = db.get(SessionRecord, "invite-token")
        finally:
            db.close()

    assert session.status == "expired"
