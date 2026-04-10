from io import BytesIO
from pathlib import Path

from app import create_app
from app.db import SessionLocal
from app.models import DocumentRecord, SessionRecord


def build_app(tmp_path, upload_dir: str | None = None):
    return create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{tmp_path / 'upload.db'}",
            "UPLOAD_DIR": upload_dir or str(tmp_path / "uploads"),
            "ADMIN_TOKEN": "admin-secret",
        }
    )


def seed_session(app, token: str = "invite-token"):
    with app.app_context():
        db = SessionLocal()
        try:
            session = SessionRecord(token=token, status="awaiting_user")
            db.add(session)
            db.add(DocumentRecord(session_token=token, revision_number=1))
            db.commit()
        finally:
            db.close()
    return token


def test_upload_respects_file_constraints(tmp_path):
    upload_dir = tmp_path / "uploads"
    app = build_app(tmp_path)
    client = app.test_client()
    token = seed_session(app)

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"binary"), "../reference.png"), "caption": "首页参考"},
        content_type="multipart/form-data",
    )

    payload = response.get_json()
    assert response.status_code == 201
    assert payload["file_name"] == "reference.png"
    assert payload["caption"] == "首页参考"
    assert Path(payload["file_path"]).exists()
    assert payload["preview_url"] == f"/api/sessions/{token}/attachments/{payload['id']}/preview"

    preview_response = client.get(payload["preview_url"])
    assert preview_response.status_code == 200
    assert preview_response.mimetype == "image/png"


def test_upload_rejects_non_image_file(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    token = seed_session(app)

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"text"), "notes.txt"), "caption": "无效文件"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "只支持 PNG、JPEG、WEBP 图片"}


def test_upload_rejects_file_over_8mb(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    token = seed_session(app)

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={
            "file": (BytesIO(b"x" * (8 * 1024 * 1024 + 1)), "oversize.png"),
            "caption": "太大了",
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "单张图片不能超过 8MB"}


def test_upload_rejects_when_attachment_count_exceeds_limit(tmp_path):
    app = build_app(tmp_path)
    client = app.test_client()
    token = seed_session(app)

    for index in range(12):
        response = client.post(
            f"/api/sessions/{token}/attachments",
            data={
                "file": (BytesIO(f"img-{index}".encode()), f"ref-{index}.png"),
                "caption": f"参考 {index}",
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == 201

    overflow_response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"overflow"), "overflow.png"), "caption": "超额"},
        content_type="multipart/form-data",
    )

    assert overflow_response.status_code == 400
    assert overflow_response.get_json() == {"message": "当前会话最多上传 12 张图片"}


def test_preview_works_when_attachment_path_is_relative(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    app = build_app(tmp_path, upload_dir="uploads")
    client = app.test_client()
    token = seed_session(app)

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"binary"), "reference.png"), "caption": "首页参考"},
        content_type="multipart/form-data",
    )

    payload = response.get_json()
    assert response.status_code == 201
    assert payload["file_path"] == f"uploads/{token}/reference.png"

    preview_response = client.get(payload["preview_url"])
    assert preview_response.status_code == 200
    assert preview_response.mimetype == "image/png"
