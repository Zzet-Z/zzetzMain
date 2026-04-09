from __future__ import annotations

import json
import logging
from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"
STAGE_REPLY_TIMEOUT = 90.0
SUMMARY_EXTRACTION_TIMEOUT = 90.0
DOCUMENT_RENDER_TIMEOUT = 45.0
CHAT_REPLY_TIMEOUT = 90.0

logger = logging.getLogger(__name__)


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def build_chat_input(*, session_context: dict, recent_messages: list[dict]) -> str:
    previous_document = session_context.get("previous_document")
    if isinstance(previous_document, str) and previous_document.strip():
        previous_document_text = previous_document.strip()
    elif previous_document:
        previous_document_text = str(previous_document)
    else:
        previous_document_text = "无"

    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    return (
        "上一版最终文档：\n"
        f"{previous_document_text}\n\n"
        "最近对话：\n"
        f"{history}\n\n"
        "请严格按照系统提示输出 JSON envelope。"
    )


def build_chat_request(*, stage: str, summary_payload: dict, recent_messages: list[dict]) -> dict:
    system_prompt = load_prompt("system.md")
    stage_prompt = load_prompt(f"{stage}.md")
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    return {
        "stage": stage,
        "locale": "zh-CN",
        "system_prompt": f"{system_prompt}\n\n{stage_prompt}",
        "context_text": f"摘要：{summary_payload}\n最近对话：{history}",
    }


def generate_stage_reply(client, *, stage: str, summary_payload: dict, recent_messages: list[dict]) -> str:
    request = build_chat_request(
        stage=stage,
        summary_payload=summary_payload,
        recent_messages=recent_messages,
    )
    response = client.generate(
        instructions=request["system_prompt"],
        input_text=request["context_text"],
        timeout=STAGE_REPLY_TIMEOUT,
    )
    return response.text


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return text


def _parse_chat_envelope(raw: str) -> dict | None:
    text = _strip_code_fence(raw)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    assistant_message = payload.get("assistant_message")
    if not isinstance(assistant_message, str) or not assistant_message.strip():
        return None

    conversation_intent = payload.get("conversation_intent", "continue")
    if conversation_intent not in {"continue", "ready_to_generate"}:
        conversation_intent = "continue"

    return {
        "assistant_message": assistant_message,
        "conversation_intent": conversation_intent,
    }


def generate_chat_reply(client, *, session_context: dict, recent_messages: list[dict]) -> dict:
    response = client.generate(
        instructions=load_prompt("chat_system.md"),
        input_text=build_chat_input(session_context=session_context, recent_messages=recent_messages),
        timeout=CHAT_REPLY_TIMEOUT,
    )
    raw = response.text.strip()
    payload = _parse_chat_envelope(raw)
    if payload is None:
        logger.warning("llm envelope parse failed")
        return {"assistant_message": raw, "conversation_intent": "continue"}
    return payload


def extract_summary_update(client, *, current_stage: str, existing_summary: dict, recent_messages: list[dict]) -> dict:
    instructions = f"{load_prompt('system.md')}\n\n{load_prompt('extract_summary.md')}"
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    response = client.generate(
        instructions=instructions,
        input_text=f"当前阶段：{current_stage}\n已有摘要：{existing_summary}\n新增对话：{history}",
        timeout=SUMMARY_EXTRACTION_TIMEOUT,
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return existing_summary


def render_prd_with_llm(client, *, summary_payload: dict, attachments: list[dict]) -> tuple[str, str]:
    return render_final_document_with_llm(
        client,
        summary_payload=summary_payload,
        previous_document=None,
        attachments=attachments,
    )


def render_final_document_with_llm(
    client,
    *,
    summary_payload: dict,
    previous_document: str | None = None,
    attachments: list[dict],
) -> tuple[str, str]:
    instructions = load_prompt("render_final_document.md")
    attachment_text = "\n".join(
        f"- {item['file_name']}：{item.get('caption', '')}" for item in attachments
    )
    previous_document_text = previous_document.strip() if isinstance(previous_document, str) and previous_document.strip() else "无"
    response = client.generate(
        instructions=instructions,
        input_text=(
            f"结构化摘要：{json.dumps(summary_payload, ensure_ascii=False)}\n"
            f"上一版最终文档：\n{previous_document_text}\n"
            f"附件：\n{attachment_text or '无'}"
        ),
        timeout=DOCUMENT_RENDER_TIMEOUT,
    )
    summary_text = (
        f"网站类型：{summary_payload.get('website_type') or '未确定'}\n"
        f"视觉方向：{summary_payload.get('visual_direction') or '未确定'}"
    )
    prd_markdown = response.text
    if attachments:
        attachment_section = "\n".join(
            f"- {item['file_name']}：{item.get('caption', '')}" for item in attachments
        )
        prd_markdown = f"{prd_markdown.rstrip()}\n\n## 参考附件\n{attachment_section}\n"
    return summary_text, prd_markdown
