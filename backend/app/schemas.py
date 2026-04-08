from .models import DocumentRecord, SessionRecord, SummarySnapshot


def serialize_session(record: SessionRecord) -> dict[str, object]:
    return {
        "token": record.token,
        "locale": record.locale,
        "status": record.status,
        "current_stage": record.current_stage,
        "selected_template": record.selected_template,
        "selected_style": record.selected_style,
    }


def serialize_summary(record: SummarySnapshot | None) -> dict[str, object]:
    payload = {} if record is None else record.payload
    return {"payload": payload}


def serialize_document(record: DocumentRecord | None) -> dict[str, object]:
    status = "pending" if record is None else record.status
    return {"status": status}
