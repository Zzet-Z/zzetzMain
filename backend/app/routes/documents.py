from flask import Blueprint, jsonify

from ..db import SessionLocal
from ..models import DocumentRecord


documents_bp = Blueprint("documents", __name__)


@documents_bp.get("/sessions/<token>/document")
def get_document(token: str):
    db = SessionLocal()
    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )

    return jsonify(
        {
            "status": document.status,
            "summary_text": document.summary_text,
            "prd_markdown": document.prd_markdown,
        }
    )
