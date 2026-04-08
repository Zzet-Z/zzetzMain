from io import BytesIO
from pathlib import Path

from app import create_app


def test_upload_respects_file_constraints(tmp_path):
    db_path = tmp_path / "upload.db"
    upload_dir = tmp_path / "uploads"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(upload_dir),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

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


def test_upload_rejects_non_image_file(tmp_path):
    db_path = tmp_path / "upload.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"text"), "notes.txt"), "caption": "无效文件"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "只支持 PNG、JPEG、WEBP 图片"}


def test_upload_rejects_file_over_8mb(tmp_path):
    db_path = tmp_path / "upload.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

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
    db_path = tmp_path / "upload.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

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
