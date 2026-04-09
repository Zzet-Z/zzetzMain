from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..db import SessionLocal
from ..models import AttachmentRecord, DocumentRecord, MessageRecord, SessionRecord
from ..services.session_lifecycle import (
    EXPIRED_SESSION_MESSAGE,
    MISSING_SESSION_MESSAGE,
    apply_session_lifecycle,
    utcnow,
)


sessions_bp = Blueprint("sessions", __name__)


def serialize_message(record: MessageRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "role": record.role,
        "content": record.content,
        "delivery_status": record.delivery_status,
        "created_at": record.created_at,
    }


def serialize_attachment(record: AttachmentRecord) -> dict[str, object]:
    return {
        "id": record.id,
        "file_name": record.file_name,
        "caption": record.caption,
        "mime_type": record.mime_type,
        "created_at": record.created_at,
        "preview_url": f"/api/sessions/{record.session_token}/attachments/{record.id}/preview",
    }


def serialize_document(record: DocumentRecord | None) -> dict[str, object]:
    if record is None:
        return {"status": "pending", "summary_text": "", "prd_markdown": ""}

    return {
        "id": record.id,
        "status": record.status,
        "summary_text": record.summary_text,
        "prd_markdown": record.prd_markdown,
        "revision_number": record.revision_number,
        "parent_document_id": record.parent_document_id,
        "root_document_id": record.root_document_id,
        "created_at": record.created_at,
    }


def _previous_summary(db, session: SessionRecord) -> str | None:
    if not session.previous_document_id:
        return None
    previous_document = db.get(DocumentRecord, session.previous_document_id)
    if previous_document is None or not previous_document.summary_text:
        return None
    return previous_document.summary_text


def _message_window(db, token: str, *, limit: int, before_id: int | None = None) -> dict[str, object]:
    query = db.query(MessageRecord).filter(MessageRecord.session_token == token)
    if before_id is not None:
        query = query.filter(MessageRecord.id < before_id)

    records = (
        query.order_by(MessageRecord.id.desc())
        .limit(limit + 1)
        .all()
    )
    has_more = len(records) > limit
    page = list(reversed(records[:limit]))
    oldest_message_id = page[0].id if page else None
    return {
        "messages": [serialize_message(item) for item in page],
        "has_more": has_more,
        "oldest_message_id": oldest_message_id,
    }


def _parse_positive_int_arg(name: str, raw_value: str | None) -> int | None:
    if raw_value is None:
        return None
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise ValueError(name)
    if value <= 0:
        raise ValueError(name)
    return value


def load_session_for_frontend(db, token: str) -> tuple[SessionRecord | None, tuple[dict, int] | None]:
    session = db.get(SessionRecord, token)
    if session is None:
        return None, ({"message": MISSING_SESSION_MESSAGE}, 404)

    apply_session_lifecycle(session, now=utcnow())
    if session.status == "expired":
        db.commit()
        return None, ({"message": EXPIRED_SESSION_MESSAGE}, 410)

    db.commit()
    return session, None


@sessions_bp.get("/sessions/<token>")
def get_session(token: str):
    db = SessionLocal()
    session, error = load_session_for_frontend(db, token)
    if error is not None:
        return jsonify(error[0]), error[1]

    message_window = _message_window(
        db,
        token,
        limit=current_app.config["SESSION_MESSAGES_PAGE_SIZE"],
    )
    attachments = (
        db.query(AttachmentRecord)
        .filter(AttachmentRecord.session_token == token)
        .order_by(AttachmentRecord.id.asc())
        .all()
    )
    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )

    return jsonify(
        {
            "token": session.token,
            "status": session.status,
            "admin_note": session.admin_note,
            "messages": message_window["messages"],
            "attachments": [serialize_attachment(item) for item in attachments],
            "document": serialize_document(document),
            "previous_summary": _previous_summary(db, session),
            "has_more": message_window["has_more"],
            "oldest_message_id": message_window["oldest_message_id"],
            "successor_token": (
                session.next_session_token if session.status == "completed" else None
            ),
            "last_error": session.last_error,
            "last_activity_at": session.last_activity_at,
            "completed_at": session.completed_at,
        }
    )


@sessions_bp.get("/sessions/<token>/messages")
def get_session_messages(token: str):
    db = SessionLocal()
    session, error = load_session_for_frontend(db, token)
    if error is not None:
        return jsonify(error[0]), error[1]

    try:
        before_id = _parse_positive_int_arg("before_id", request.args.get("before_id"))
        raw_limit = request.args.get("limit")
        limit = (
            _parse_positive_int_arg("limit", raw_limit)
            if raw_limit is not None
            else current_app.config["SESSION_MESSAGES_PAGE_SIZE"]
        )
    except ValueError:
        return jsonify({"message": "分页参数不合法。"}), 400

    limit = min(limit, current_app.config["SESSION_MESSAGES_PAGE_SIZE"])
    payload = _message_window(db, session.token, limit=limit, before_id=before_id)
    return jsonify(payload)
