from datetime import UTC, datetime
from secrets import token_urlsafe

from flask import Blueprint, jsonify, request

from ..db import SessionLocal
from ..models import DocumentRecord, SessionRecord, SummarySnapshot
from ..schemas import serialize_document, serialize_session, serialize_summary


sessions_bp = Blueprint("sessions", __name__)

MISSING_SESSION_MESSAGE = {"message": "这次整理链接可能已失效，请重新开始。"}
ALLOWED_STAGE_TRANSITIONS = {
    "template": {"style"},
    "style": {"positioning"},
    "positioning": {"content"},
    "content": {"features"},
    "features": {"generate"},
    "generate": set(),
}


@sessions_bp.post("/sessions")
def create_session():
    db = SessionLocal()
    token = token_urlsafe(24)
    record = SessionRecord(token=token)
    db.add(record)
    db.add(SummarySnapshot(session_token=token, payload={}))
    db.add(DocumentRecord(session_token=token))
    db.commit()

    return jsonify(serialize_session(record)), 201


@sessions_bp.get("/sessions/<token>")
def get_session(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)

    if session is None:
        return jsonify(MISSING_SESSION_MESSAGE), 404

    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    latest_document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )

    payload = serialize_session(session)
    payload["summary"] = serialize_summary(latest_summary)
    payload["document"] = serialize_document(latest_document)
    return jsonify(payload)


@sessions_bp.patch("/sessions/<token>")
def update_session(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)

    if session is None:
        return jsonify(MISSING_SESSION_MESSAGE), 404

    payload = request.get_json(silent=True) or {}

    if "selected_template" in payload:
        session.selected_template = payload["selected_template"]

    if "selected_style" in payload:
        session.selected_style = payload["selected_style"]

    if "current_stage" in payload:
        requested_stage = payload["current_stage"]
        allowed_stages = ALLOWED_STAGE_TRANSITIONS.get(session.current_stage, set())
        if (
            requested_stage != session.current_stage
            and requested_stage not in allowed_stages
        ):
            return jsonify({"message": "当前阶段不能直接跳转到目标阶段。"}), 400
        session.current_stage = requested_stage

    session.updated_at = datetime.now(UTC)
    db.commit()
    return jsonify(serialize_session(session))
