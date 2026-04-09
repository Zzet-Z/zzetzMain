from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from flask import current_app

from ..models import DocumentRecord, MessageRecord, SessionRecord
from .llm_orchestrator import load_prompt


MISSING_SESSION_MESSAGE = "这次整理链接可能已失效，请联系管理员获取新的入口。"
EXPIRED_SESSION_MESSAGE = "这个整理链接已经失效，请联系管理员获取新的入口。"
COMPLETED_SESSION_MESSAGE = "当前整理链接已结束，不能继续上传附件。"
FINISHED_SESSION_MESSAGE = "当前整理链接已结束，不能继续发送消息。"


def utcnow() -> datetime:
    return datetime.now(UTC)


def _coerce_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def apply_session_lifecycle(session: SessionRecord, *, now: datetime | None = None) -> SessionRecord:
    now = _coerce_utc(now or utcnow())
    expires_at = _coerce_utc(session.expires_at)
    last_activity_at = _coerce_utc(session.last_activity_at)

    if (
        session.status != "completed"
        and expires_at is not None
        and now >= expires_at
    ):
        session.status = "expired"
        session.queued_at = None
        session.active_started_at = None
        return session

    idle_deadline = now - timedelta(
        seconds=current_app.config["SESSION_IDLE_TIMEOUT_SECONDS"]
    )
    if (
        session.status in {"queued", "active", "generating_document"}
        and last_activity_at is not None
        and last_activity_at <= idle_deadline
    ):
        session.status = "awaiting_user"
        session.queued_at = None
        session.active_started_at = None

    return session


def touch_session(
    session: SessionRecord,
    *,
    now: datetime | None = None,
    user_message: bool = False,
) -> SessionRecord:
    now = now or utcnow()
    session.last_activity_at = now
    if user_message:
        session.last_user_message_at = now
    if session.expires_at is None:
        session.expires_at = now + timedelta(
            hours=current_app.config["SESSION_EXPIRY_HOURS"]
        )
    return session


def create_token_session(
    db,
    *,
    admin_note: str | None = None,
    previous_document_id: int | None = None,
    origin_session_token: str | None = None,
    token: str | None = None,
    now: datetime | None = None,
) -> SessionRecord:
    now = now or utcnow()
    previous_document = (
        db.get(DocumentRecord, previous_document_id) if previous_document_id else None
    )
    token = token or token_urlsafe(24)

    session = SessionRecord(
        token=token,
        status="awaiting_user",
        admin_note=admin_note,
        origin_session_token=origin_session_token,
        previous_document_id=previous_document_id,
        last_activity_at=now,
        expires_at=now + timedelta(hours=current_app.config["SESSION_EXPIRY_HOURS"]),
    )
    db.add(session)
    db.flush()

    db.add(
        DocumentRecord(
            session_token=token,
            status="pending",
            revision_number=(
                (previous_document.revision_number + 1) if previous_document else 1
            ),
            parent_document_id=previous_document.id if previous_document else None,
            root_document_id=(
                previous_document.root_document_id or previous_document.id
                if previous_document
                else None
            ),
        )
    )
    db.add(
        MessageRecord(
            session_token=token,
            role="assistant",
            content=load_prompt(
                "welcome_revision.md" if previous_document_id else "welcome_initial.md"
            ).strip(),
            delivery_status="system",
        )
    )
    return session


def create_successor_session(
    db,
    *,
    session: SessionRecord,
    document: DocumentRecord,
    now: datetime | None = None,
) -> SessionRecord:
    if session.next_session_token:
        successor = db.get(SessionRecord, session.next_session_token)
        if successor is not None:
            return successor

    successor = create_token_session(
        db,
        admin_note=session.admin_note,
        previous_document_id=document.id,
        origin_session_token=session.origin_session_token or session.token,
        now=now,
    )
    session.next_session_token = successor.token
    return successor
