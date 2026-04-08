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
from ..services.intake_state_machine import next_stage_for_session
from ..services.llm_client import LLMClient
from ..services.llm_orchestrator import extract_summary_update, generate_stage_reply
from ..services.queue_manager import reserve_slot
from ..services.summary_builder import merge_summary, should_refresh_summary


messages_bp = Blueprint("messages", __name__)


@messages_bp.post("/sessions/<token>/messages")
def create_message(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)

    if session is None:
        return jsonify({"message": "这次整理链接可能已失效，请重新开始。"}), 404

    payload = request.get_json(silent=True) or {}
    content = payload["content"]
    user_action = payload.get("action", "answered")
    generation_requested = payload.get("generation_requested", False)

    status, queue_position = reserve_slot(
        token,
        current_app.config["MAX_ACTIVE_SESSIONS"],
    )
    if status == "queued":
        return jsonify(
            {
                "session_status": "queued",
                "queue_position": queue_position,
                "message": "当前正在为其他用户整理网站需求，你已进入等待队列。",
                "poll_after_ms": 3000,
            }
        ), 202

    db.add(
        MessageRecord(
            session_token=token,
            role="user",
            content=content,
            stage=session.current_stage,
        )
    )

    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    summary_payload = {} if latest_summary is None else latest_summary.payload

    if generation_requested:
        document = (
            db.query(DocumentRecord)
            .filter(DocumentRecord.session_token == token)
            .order_by(DocumentRecord.id.desc())
            .first()
        )
        attachments = (
            db.query(AttachmentRecord)
            .filter(AttachmentRecord.session_token == token)
            .order_by(AttachmentRecord.id.asc())
            .all()
        )
        session.status = "generating_document"
        try:
            summary_text, prd_markdown = render_document_bundle(
                summary_payload=summary_payload,
                attachments=[
                    {"file_name": item.file_name, "caption": item.caption}
                    for item in attachments
                ],
            )
        except RuntimeError as exc:
            session.status = "failed"
            session.last_error = str(exc)
            db.commit()
            return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502
        document.version += 1
        document.status = "ready"
        document.summary_text = summary_text
        document.prd_markdown = prd_markdown
        session.status = "completed"
        db.commit()
        return jsonify(
            {
                "session_status": "generating_document",
                "message": "正在生成 PRD",
                "poll_after_ms": 5000,
            }
        ), 202

    client = LLMClient.from_env()
    try:
        assistant_reply = generate_stage_reply(
            client,
            stage=session.current_stage,
            summary_payload=summary_payload,
            recent_messages=[{"role": "user", "content": content}],
        )
    except RuntimeError as exc:
        session.status = "failed"
        session.last_error = str(exc)
        db.commit()
        return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502

    db.add(
        MessageRecord(
            session_token=token,
            role="assistant",
            content=assistant_reply,
            stage=session.current_stage,
        )
    )

    stage_completed = payload.get("stage_completed", False)
    if should_refresh_summary(
        current_stage=session.current_stage,
        stage_completed=stage_completed,
        generation_requested=generation_requested,
    ):
        try:
            extracted = extract_summary_update(
                client,
                current_stage=session.current_stage,
                existing_summary=summary_payload,
                recent_messages=[{"role": "user", "content": content}],
            )
        except RuntimeError as exc:
            session.status = "failed"
            session.last_error = str(exc)
            db.commit()
            return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502
        merged_summary = merge_summary(summary_payload, extracted)
        db.add(SummarySnapshot(session_token=token, payload=merged_summary))
    else:
        merged_summary = summary_payload

    session.current_stage = next_stage_for_session(
        current_stage=session.current_stage,
        selected_template=session.selected_template,
        selected_style=session.selected_style,
        summary_payload=merged_summary,
        user_action=user_action,
    )
    session.status = "in_progress"

    db.commit()
    return jsonify(
        {
            "assistant_reply": assistant_reply,
            "current_stage": session.current_stage,
            "session_status": session.status,
            "poll_after_ms": 3000,
        }
    ), 201
