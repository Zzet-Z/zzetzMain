from flask import Blueprint, jsonify, request

from ..db import SessionLocal
from ..models import MessageRecord, SessionRecord, SummarySnapshot
from ..services.intake_state_machine import next_stage_for_session
from ..services.llm_client import LLMClient
from ..services.llm_orchestrator import extract_summary_update, generate_stage_reply
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

    client = LLMClient.from_env()
    try:
        assistant_reply = generate_stage_reply(
            client,
            stage=session.current_stage,
            summary_payload=summary_payload,
            recent_messages=[{"role": "user", "content": content}],
        )
    except RuntimeError as exc:
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
    generation_requested = payload.get("generation_requested", False)

    if should_refresh_summary(
        current_stage=session.current_stage,
        stage_completed=stage_completed,
        generation_requested=generation_requested,
    ):
        extracted = extract_summary_update(
            client,
            current_stage=session.current_stage,
            existing_summary=summary_payload,
            recent_messages=[{"role": "user", "content": content}],
        )
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

    db.commit()
    return jsonify(
        {
            "assistant_reply": assistant_reply,
            "current_stage": session.current_stage,
        }
    ), 201
