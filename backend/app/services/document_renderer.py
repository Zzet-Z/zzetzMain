from .llm_client import LLMClient
from .llm_orchestrator import render_final_document_with_llm


def render_document_bundle(
    *,
    summary_payload: dict,
    attachments: list[dict],
    previous_document: str | None = None,
    recent_messages: list[dict] | None = None,
) -> tuple[str, str]:
    client = LLMClient.from_env()
    return render_final_document_with_llm(
        client,
        summary_payload=summary_payload,
        previous_document=previous_document,
        recent_messages=recent_messages,
        attachments=attachments,
    )
