from flask import Blueprint, jsonify, request

from ..db import SessionLocal
from ..models import AttachmentRecord, DocumentRecord, MessageRecord, SessionRecord
from ..services.admin_auth import AdminAuthError, require_admin_token
from ..services.session_lifecycle import (
    INVALID_PREVIOUS_DOCUMENT_MESSAGE,
    MISSING_SESSION_MESSAGE,
    apply_session_lifecycle,
    create_token_session,
    utcnow,
)
from .sessions import serialize_document


admin_bp = Blueprint("admin", __name__)


def _authorize():
    try:
        require_admin_token(request)
    except AdminAuthError:
        return jsonify({"message": "管理员凭证无效。"}), 403
    return None


def _document_for_session(db, token: str) -> DocumentRecord | None:
    return (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )


def _previous_summary(db, session: SessionRecord) -> str | None:
    if not session.previous_document_id:
        return None
    previous_document = db.get(DocumentRecord, session.previous_document_id)
    if previous_document is None or not previous_document.summary_text:
        return None
    return previous_document.summary_text


@admin_bp.post("/admin/tokens")
def create_admin_token():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    db = SessionLocal()
    payload = request.get_json(silent=True) or {}
    try:
        session = create_token_session(
            db,
            admin_note=payload.get("admin_note"),
            previous_document_id=payload.get("previous_document_id"),
            now=utcnow(),
        )
    except ValueError as exc:
        if str(exc) == INVALID_PREVIOUS_DOCUMENT_MESSAGE:
            return jsonify({"message": INVALID_PREVIOUS_DOCUMENT_MESSAGE}), 400
        raise
    db.commit()
    return (
        jsonify(
            {
                "token": session.token,
                "status": session.status,
                "admin_note": session.admin_note,
                "previous_document_id": session.previous_document_id,
                "origin_session_token": session.origin_session_token,
                "next_session_token": session.next_session_token,
                "successor_token": None,
            }
        ),
        201,
    )


@admin_bp.get("/admin/tokens")
def list_admin_tokens():
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    db = SessionLocal()
    sessions = db.query(SessionRecord).order_by(SessionRecord.created_at.desc()).all()
    items = []
    for session in sessions:
        apply_session_lifecycle(session, now=utcnow())
        document = _document_for_session(db, session.token)
        items.append(
            {
                "token": session.token,
                "status": session.status,
                "admin_note": session.admin_note,
                "message_count": (
                    db.query(MessageRecord)
                    .filter(MessageRecord.session_token == session.token)
                    .count()
                ),
                "attachment_count": (
                    db.query(AttachmentRecord)
                    .filter(AttachmentRecord.session_token == session.token)
                    .count()
                ),
                "document_status": document.status if document else "pending",
                "last_activity_at": session.last_activity_at,
                "previous_document_id": session.previous_document_id,
                "origin_session_token": session.origin_session_token,
                "next_session_token": session.next_session_token,
                "successor_token": session.next_session_token,
            }
        )
    db.commit()
    return jsonify({"items": items})


@admin_bp.get("/admin/tokens/<token>")
def get_admin_token_detail(token: str):
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        return jsonify({"message": MISSING_SESSION_MESSAGE}), 404

    apply_session_lifecycle(session, now=utcnow())
    document = _document_for_session(db, token)
    payload = {
        "token": session.token,
        "status": session.status,
        "admin_note": session.admin_note,
        "previous_summary": _previous_summary(db, session),
        "previous_document_id": session.previous_document_id,
        "origin_session_token": session.origin_session_token,
        "next_session_token": session.next_session_token,
        "successor_token": session.next_session_token,
        "last_error": session.last_error,
        "document": serialize_document(document),
    }
    db.commit()
    return jsonify(payload)


@admin_bp.post("/admin/tokens/<token>/revoke")
def revoke_admin_token(token: str):
    auth_error = _authorize()
    if auth_error is not None:
        return auth_error

    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        return jsonify({"message": MISSING_SESSION_MESSAGE}), 404

    session.status = "expired"
    session.expires_at = utcnow()
    session.queued_at = None
    session.active_started_at = None
    db.commit()
    return jsonify({"token": session.token, "status": session.status})
