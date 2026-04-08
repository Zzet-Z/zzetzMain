from .llm_client import LLMClient
from .llm_orchestrator import render_prd_with_llm


def render_document_bundle(*, summary_payload: dict, attachments: list[dict]) -> tuple[str, str]:
    client = LLMClient.from_env()
    return render_prd_with_llm(
        client,
        summary_payload=summary_payload,
        attachments=attachments,
    )
