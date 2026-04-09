from pathlib import Path

from app import create_app
from app.db import SessionLocal
from app.models import DocumentRecord, MessageRecord, SessionRecord
from app.schemas import serialize_document, serialize_session


def test_create_session_returns_token_and_default_state(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    response = client.post("/api/sessions")
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["status"] == "awaiting_user"
    assert payload["locale"] == "zh-CN"
    assert payload["current_stage"] == "template"
    assert payload["selected_template"] is None
    assert payload["selected_style"] is None
    assert len(payload["token"]) >= 20


def test_get_session_returns_stage_summary_and_document(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()
    response = client.get(f"/api/sessions/{created['token']}")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["token"] == created["token"]
    assert payload["current_stage"] == "template"
    assert payload["summary"]["payload"] == {}
    assert payload["document"]["status"] == "pending"


def test_patch_session_updates_template_style_and_stage(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()

    template_response = client.patch(
        f"/api/sessions/{created['token']}",
        json={
            "selected_template": "个人作品页",
            "current_stage": "style",
        },
    )
    style_response = client.patch(
        f"/api/sessions/{created['token']}",
        json={
            "selected_style": "极简高级",
            "current_stage": "positioning",
        },
    )
    payload = style_response.get_json()

    assert template_response.status_code == 200
    assert style_response.status_code == 200
    assert payload["selected_template"] == "个人作品页"
    assert payload["selected_style"] == "极简高级"
    assert payload["current_stage"] == "positioning"


def test_patch_session_rejects_invalid_stage_transition(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()
    response = client.patch(
        f"/api/sessions/{created['token']}",
        json={"current_stage": "features"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "当前阶段不能直接跳转到目标阶段。"}


def test_missing_session_returns_chinese_404_message(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    get_response = client.get("/api/sessions/missing-token")
    patch_response = client.patch(
        "/api/sessions/missing-token",
        json={"selected_template": "个人作品页"},
    )

    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert get_response.get_json() == {"message": "这次整理链接可能已失效，请重新开始。"}
    assert patch_response.get_json() == {"message": "这次整理链接可能已失效，请重新开始。"}


def test_api_responses_include_configured_cors_origin(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    response = client.post(
        "/api/sessions",
        headers={"Origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 201
    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:5173"


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
    assert saved_session.current_stage == "template"
    assert saved_session.selected_template is None
    assert saved_session.selected_style is None
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
    assert session_payload["current_stage"] == "template"
    assert session_payload["admin_note"] == "首版需求"
    assert session_payload["origin_session_token"] == "origin-token"
    assert session_payload["next_session_token"] == "successor-token"
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
