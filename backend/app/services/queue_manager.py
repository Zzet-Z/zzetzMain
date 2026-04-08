from datetime import UTC, datetime

from ..db import SessionLocal
from ..models import SessionRecord


ACTIVE_SESSION_STATUSES = ["active", "generating_document"]


def reserve_slot(token: str, max_active_sessions: int) -> tuple[str, int | None]:
    db = SessionLocal()
    session = db.get(SessionRecord, token)

    if session is None:
        return "missing", None

    if session.status in ACTIVE_SESSION_STATUSES:
        return session.status, None

    active_count = (
        db.query(SessionRecord)
        .filter(SessionRecord.status.in_(ACTIVE_SESSION_STATUSES))
        .count()
    )

    if active_count >= max_active_sessions:
        session.status = "queued"
        session.queued_at = datetime.now(UTC)
        db.commit()
        queued_sessions = (
            db.query(SessionRecord)
            .filter(SessionRecord.status == "queued")
            .order_by(SessionRecord.queued_at.asc(), SessionRecord.token.asc())
            .all()
        )
        queue_position = next(
            index
            for index, item in enumerate(queued_sessions, start=1)
            if item.token == token
        )
        return "queued", queue_position

    session.status = "active"
    session.queued_at = None
    db.commit()
    return "active", None
