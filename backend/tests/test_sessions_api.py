from pathlib import Path

from app import create_app
from app.db import SessionLocal
from app.models import DocumentRecord, MessageRecord, SessionRecord
from app.schemas import serialize_document, serialize_session


def test_session_record_uses_chat_first_fields(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{tmp_path / 'chat-first.db'}",
            "ADMIN_TOKEN": "admin-secret",
        }
    )

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
            saved_document = db.query(DocumentRecord).filter_by(session_token="invite-token").one()
            saved_message = db.query(MessageRecord).filter_by(session_token="invite-token").one()
        finally:
            db.close()

    assert saved_session.status == "awaiting_user"
    assert not hasattr(saved_session, "current_stage")
    assert saved_session.next_session_token is None
    assert saved_session.admin_note == "首版需求"
    assert saved_session.origin_session_token == "origin-token"
    assert saved_document.revision_number == 1
    assert saved_message.delivery_status == "system"


def test_serializers_use_chat_first_payloads():
    session = SessionRecord(
        token="invite-token",
        status="awaiting_user",
        admin_note="首版需求",
        origin_session_token="origin-token",
        next_session_token="successor-token",
    )

    session_payload = serialize_session(session)
    document_payload = serialize_document(
        DocumentRecord(session_token="invite-token", revision_number=3)
    )

    assert session_payload["status"] == "awaiting_user"
    assert session_payload["admin_note"] == "首版需求"
    assert session_payload["origin_session_token"] == "origin-token"
    assert session_payload["next_session_token"] == "successor-token"
    assert "current_stage" not in session_payload
    assert document_payload["revision_number"] == 3


def test_default_config_includes_chat_first_runtime_settings(tmp_path, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("SESSION_IDLE_TIMEOUT_SECONDS", "301")
    monkeypatch.setenv("SESSION_EXPIRY_HOURS", "25")
    monkeypatch.setenv("SESSION_MESSAGES_PAGE_SIZE", "51")

    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{tmp_path / 'chat-first.db'}"})

    assert app.config["ADMIN_TOKEN"] == "admin-secret"
    assert app.config["SESSION_IDLE_TIMEOUT_SECONDS"] == 301
    assert app.config["SESSION_EXPIRY_HOURS"] == 25
    assert app.config["SESSION_MESSAGES_PAGE_SIZE"] == 51


def test_env_example_mentions_admin_token():
    content = Path(__file__).resolve().parents[2] / ".env.example"
    content = content.read_text(encoding="utf-8")
    assert "ADMIN_TOKEN=" in content
