from pathlib import Path

from flask import Blueprint, current_app, jsonify, request, send_file

from ..db import SessionLocal
from ..models import AttachmentRecord
from ..services.session_lifecycle import (
    COMPLETED_SESSION_MESSAGE,
    EXPIRED_SESSION_MESSAGE,
)
from ..services.storage import save_upload
from .sessions import load_session_for_frontend


uploads_bp = Blueprint("uploads", __name__)


def resolve_attachment_file_path(raw_path: str) -> Path:
    file_path = Path(raw_path)
    if file_path.is_absolute():
        return file_path

    cwd_candidate = (Path.cwd() / file_path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    app_candidate = (Path(current_app.root_path).parent / file_path).resolve()
    return app_candidate


@uploads_bp.post("/sessions/<token>/attachments")
def create_attachment(token: str):
    db = SessionLocal()
    session, error = load_session_for_frontend(db, token)
    if error is not None:
        return jsonify(error[0]), error[1]

    if session.status in {"completed", "failed"}:
        return jsonify({"message": COMPLETED_SESSION_MESSAGE}), 409

    attachment_count = (
        db.query(AttachmentRecord)
        .filter(AttachmentRecord.session_token == token)
        .count()
    )
    if attachment_count >= current_app.config["MAX_UPLOAD_COUNT"]:
        return jsonify({"message": "当前会话最多上传 12 张图片"}), 400

    file_storage = request.files.get("file")
    if file_storage is None:
        return jsonify({"message": "请上传图片文件。"}), 400
    caption = request.form.get("caption", "")

    try:
        file_name, file_path = save_upload(
            current_app.config["UPLOAD_DIR"],
            token,
            file_storage,
            max_upload_size_mb=current_app.config["MAX_UPLOAD_SIZE_MB"],
        )
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    if session.status == "expired":
        return jsonify({"message": EXPIRED_SESSION_MESSAGE}), 410

    record = AttachmentRecord(
        session_token=token,
        file_name=file_name,
        file_path=file_path,
        mime_type=file_storage.mimetype,
        caption=caption,
    )
    db.add(record)
    db.commit()
    return jsonify(
        {
            "id": record.id,
            "file_name": file_name,
            "caption": caption,
            "file_path": file_path,
            "mime_type": record.mime_type,
            "preview_url": f"/api/sessions/{token}/attachments/{record.id}/preview",
        }
    ), 201


@uploads_bp.get("/sessions/<token>/attachments/<int:attachment_id>/preview")
def get_attachment_preview(token: str, attachment_id: int):
    db = SessionLocal()
    session, error = load_session_for_frontend(db, token)
    if error is not None:
        return jsonify(error[0]), error[1]

    record = (
        db.query(AttachmentRecord)
        .filter(
            AttachmentRecord.session_token == session.token,
            AttachmentRecord.id == attachment_id,
        )
        .first()
    )
    if record is None:
        return jsonify({"message": "附件不存在。"}), 404

    file_path = resolve_attachment_file_path(record.file_path)
    if not file_path.exists():
        return jsonify({"message": "附件不存在。"}), 404

    return send_file(file_path, mimetype=record.mime_type)
