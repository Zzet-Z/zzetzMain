from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..db import SessionLocal
from ..models import (
    AttachmentRecord,
    DocumentRecord,
    MessageRecord,
    SessionRecord,
    SummarySnapshot,
)
from ..services.document_renderer import render_document_bundle
from ..services.llm_client import LLMClient
from ..services.llm_orchestrator import generate_chat_reply
from ..services.queue_manager import reserve_slot
from ..services.session_lifecycle import (
    EXPIRED_SESSION_MESSAGE,
    FINISHED_SESSION_MESSAGE,
    apply_session_lifecycle,
    create_successor_session,
    touch_session,
    utcnow,
)


messages_bp = Blueprint("messages", __name__)
PLACEHOLDER_SUMMARY_TEXT = "网站类型：未确定\n视觉方向：未确定"


def _recent_messages(db, token: str, *, limit: int = 12) -> list[dict[str, str]]:
    rows = (
        db.query(MessageRecord)
        .filter(MessageRecord.session_token == token)
        .order_by(MessageRecord.id.desc())
        .limit(limit)
        .all()
    )
    return [
        {"role": item.role, "content": item.content}
        for item in reversed(rows)
    ]


def _previous_document_markdown(db, previous_document_id: int | None) -> str | None:
    if not previous_document_id:
        return None
    previous_document = db.get(DocumentRecord, previous_document_id)
    if previous_document is None:
        return None
    return previous_document.prd_markdown


def _latest_document(db, token: str) -> DocumentRecord | None:
    return (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )


def _latest_summary_payload(db, token: str) -> dict:
    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    return {} if latest_summary is None else latest_summary.payload


def _queue_response(queue_position: int | None):
    return (
        jsonify(
            {
                "session_status": "queued",
                "queue_position": queue_position,
                "message": "当前正在为其他用户整理网站需求，你已进入等待队列。",
                "poll_after_ms": 3000,
            }
        ),
        202,
    )


def _run_with_retries(fn):
    last_error = None
    for _ in range(3):
        try:
            return fn()
        except RuntimeError as exc:  # pragma: no cover - exercised through route tests
            last_error = exc
    raise last_error or RuntimeError("暂时无法继续整理需求，请稍后重试。")


def _fallback_summary_text(recent_messages: list[dict[str, str]]) -> str:
    user_messages = [
        item["content"].strip()
        for item in recent_messages
        if item["role"] == "user" and item["content"].strip()
    ]
    if not user_messages:
        return PLACEHOLDER_SUMMARY_TEXT
    return "本轮需求要点：" + "；".join(user_messages[-3:])


@messages_bp.post("/sessions/<token>/messages")
def create_message(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        from ..services.session_lifecycle import MISSING_SESSION_MESSAGE

        return jsonify({"message": MISSING_SESSION_MESSAGE}), 404

    apply_session_lifecycle(session, now=utcnow())
    if session.status == "expired":
        db.commit()
        return jsonify({"message": EXPIRED_SESSION_MESSAGE}), 410
    if session.status in {"completed", "failed"}:
        return jsonify({"message": FINISHED_SESSION_MESSAGE}), 409

    payload = request.get_json(silent=True) or {}
    content = (payload.get("content") or "").strip()
    confirm_generate = bool(payload.get("confirm_generate"))
    if not content and not confirm_generate:
        return jsonify({"message": "请输入你想补充的需求。"}), 400

    slot_status, queue_position = reserve_slot(
        token,
        current_app.config["MAX_ACTIVE_SESSIONS"],
    )
    if slot_status == "queued":
        return _queue_response(queue_position)
    if slot_status == "expired":
        return jsonify({"message": EXPIRED_SESSION_MESSAGE}), 410

    session = db.get(SessionRecord, token)
    now = utcnow()
    touch_session(session, now=now, user_message=True)

    if content:
        db.add(
            MessageRecord(
                session_token=token,
                role="user",
                content=content,
                delivery_status="final",
            )
        )
        db.flush()

    recent_messages = _recent_messages(db, token)

    if confirm_generate:
        attachments = (
            db.query(AttachmentRecord)
            .filter(AttachmentRecord.session_token == token)
            .order_by(AttachmentRecord.id.asc())
            .all()
        )
        document = _latest_document(db, token)
        if document is None:
            document = DocumentRecord(session_token=token, revision_number=1)
            db.add(document)
            db.flush()

        session.status = "generating_document"
        summary_payload = _latest_summary_payload(db, token)
        try:
            summary_text, prd_markdown = _run_with_retries(
                lambda: render_document_bundle(
                    summary_payload=summary_payload,
                    attachments=[
                        {"file_name": item.file_name, "caption": item.caption}
                        for item in attachments
                    ],
                    previous_document=_previous_document_markdown(
                        db,
                        session.previous_document_id,
                    ),
                    recent_messages=recent_messages,
                )
            )
        except RuntimeError as exc:
            session.status = "failed"
            session.last_error = str(exc)
            session.queued_at = None
            session.active_started_at = None
            db.commit()
            return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502

        if not summary_text.strip() or summary_text.strip() == PLACEHOLDER_SUMMARY_TEXT:
            summary_text = _fallback_summary_text(recent_messages)

        document.status = "ready"
        document.summary_text = summary_text
        document.prd_markdown = prd_markdown
        document.root_document_id = document.root_document_id or document.id
        session.status = "completed"
        session.completed_at = utcnow()
        session.queued_at = None
        session.active_started_at = None
        create_successor_session(
            db,
            session=session,
            document=document,
            now=session.completed_at,
        )
        db.commit()
        return (
            jsonify(
                {
                    "session_status": "generating_document",
                    "message": "正在生成最终需求文档",
                    "poll_after_ms": 5000,
                }
            ),
            202,
        )

    client = LLMClient.from_env()
    try:
        envelope = _run_with_retries(
            lambda: generate_chat_reply(
                client,
                session_context={
                    "previous_document": _previous_document_markdown(
                        db,
                        session.previous_document_id,
                    )
                },
                recent_messages=recent_messages,
            )
        )
    except RuntimeError as exc:
        session.status = "failed"
        session.last_error = str(exc)
        session.queued_at = None
        session.active_started_at = None
        db.commit()
        return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502

    db.add(
        MessageRecord(
            session_token=token,
            role="assistant",
            content=envelope["assistant_message"],
            delivery_status="final",
        )
    )

    if envelope["conversation_intent"] == "final_document":
        document = _latest_document(db, token)
        if document is None:
            document = DocumentRecord(session_token=token, revision_number=1)
            db.add(document)
            db.flush()

        summary_text = _fallback_summary_text(recent_messages)
        document.status = "ready"
        document.summary_text = summary_text
        document.prd_markdown = envelope["assistant_message"]
        document.root_document_id = document.root_document_id or document.id
        session.status = "completed"
        session.completed_at = utcnow()
        session.queued_at = None
        session.active_started_at = None
        create_successor_session(
            db,
            session=session,
            document=document,
            now=session.completed_at,
        )
        db.commit()
        return (
            jsonify(
                {
                    "assistant_reply": envelope["assistant_message"],
                    "conversation_intent": envelope["conversation_intent"],
                    "session_status": session.status,
                    "successor_token": session.next_session_token,
                    "poll_after_ms": 3000,
                }
            ),
            201,
        )

    session.status = "awaiting_user"
    session.queued_at = None
    session.active_started_at = None
    touch_session(session, now=utcnow())

    db.commit()
    return (
        jsonify(
            {
                "assistant_reply": envelope["assistant_message"],
                "conversation_intent": envelope["conversation_intent"],
                "session_status": session.status,
                "poll_after_ms": 3000,
            }
        ),
        201,
    )
