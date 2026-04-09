from .models import DocumentRecord, SessionRecord, SummarySnapshot


def serialize_session(record: SessionRecord) -> dict[str, object]:
    return {
        "token": record.token,
        "locale": record.locale,
        "status": record.status,
        "admin_note": record.admin_note,
        "origin_session_token": record.origin_session_token,
        "previous_document_id": record.previous_document_id,
        "next_session_token": record.next_session_token,
        "queued_at": record.queued_at,
        "last_activity_at": record.last_activity_at,
        "last_user_message_at": record.last_user_message_at,
        "active_started_at": record.active_started_at,
        "completed_at": record.completed_at,
        "expires_at": record.expires_at,
        "last_error": record.last_error,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


def serialize_summary(record: SummarySnapshot | None) -> dict[str, object]:
    payload = {} if record is None else record.payload
    return {"payload": payload}


def serialize_document(record: DocumentRecord | None) -> dict[str, object]:
    if record is None:
        return {
            "status": "pending",
            "revision_number": None,
            "parent_document_id": None,
            "root_document_id": None,
            "summary_text": "",
            "prd_markdown": "",
        }

    return {
        "id": record.id,
        "session_token": record.session_token,
        "status": record.status,
        "parent_document_id": record.parent_document_id,
        "root_document_id": record.root_document_id,
        "revision_number": record.revision_number,
        "summary_text": record.summary_text,
        "prd_markdown": record.prd_markdown,
        "created_at": record.created_at,
    }
