from flask import Blueprint, jsonify

from ..db import SessionLocal
from ..models import DocumentRecord
from .sessions import load_session_for_frontend, serialize_document


documents_bp = Blueprint("documents", __name__)


@documents_bp.get("/sessions/<token>/document")
def get_document(token: str):
    db = SessionLocal()
    _session, error = load_session_for_frontend(db, token)
    if error is not None:
        return jsonify(error[0]), error[1]

    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    return jsonify(serialize_document(document))
