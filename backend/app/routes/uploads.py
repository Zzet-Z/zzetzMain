from flask import Blueprint, current_app, jsonify, request

from ..db import SessionLocal
from ..models import AttachmentRecord
from ..services.session_lifecycle import (
    COMPLETED_SESSION_MESSAGE,
    EXPIRED_SESSION_MESSAGE,
)
from ..services.storage import save_upload
from .sessions import load_session_for_frontend


uploads_bp = Blueprint("uploads", __name__)


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

    file_storage = request.files["file"]
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
            "file_name": file_name,
            "caption": caption,
            "file_path": file_path,
        }
    ), 201
