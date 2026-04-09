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
FINAL_DOCUMENT_MARKERS = (
    "需求文档",
    "项目目标",
    "网站目标",
    "目标用户",
    "视觉风格",
    "页面结构",
    "功能需求",
)
FINAL_DOCUMENT_CONFIRMATIONS = (
    "生成需求文档",
    "生成文档",
    "开始生成",
    "开始整理",
    "定稿",
    "不用更新",
    "不用改",
    "就这个",
    "确认",
    "没问题",
)


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

    attachments = session_context.get("attachments") or []
    if attachments:
        attachment_lines = []
        for item in attachments:
            file_name = str(item.get("file_name") or "").strip()
            if not file_name:
                continue
            caption = str(item.get("caption") or "").strip()
            attachment_lines.append(f"- {file_name}" + (f"：{caption}" if caption else ""))
        attachment_text = "\n".join(attachment_lines) if attachment_lines else "无"
    else:
        attachment_text = "无"

    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    return (
        "上一版最终文档：\n"
        f"{previous_document_text}\n\n"
        "本轮参考附件：\n"
        f"{attachment_text}\n\n"
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
    if conversation_intent not in {"continue", "ready_to_generate", "final_document"}:
        conversation_intent = "continue"

    return {
        "assistant_message": assistant_message,
        "conversation_intent": conversation_intent,
    }


def _looks_like_final_document(raw: str) -> bool:
    text = _strip_code_fence(raw)
    if len(text.strip()) < 30:
        return False

    marker_hits = sum(1 for marker in FINAL_DOCUMENT_MARKERS if marker in text)
    has_heading = text.lstrip().startswith("#") or "需求文档" in text
    return has_heading and marker_hits >= 2


def _user_confirmed_final_document(recent_messages: list[dict]) -> bool:
    user_messages = [
        str(item.get("content") or "").strip()
        for item in recent_messages
        if item.get("role") == "user"
    ]
    if not user_messages:
        return False

    latest_user_message = user_messages[-1]
    return any(marker in latest_user_message for marker in FINAL_DOCUMENT_CONFIRMATIONS)


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
        if _user_confirmed_final_document(recent_messages) and _looks_like_final_document(raw):
            return {"assistant_message": raw, "conversation_intent": "final_document"}
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


def render_prd_with_llm(
    client,
    *,
    summary_payload: dict,
    attachments: list[dict],
    recent_messages: list[dict] | None = None,
    previous_document: str | None = None,
) -> tuple[str, str]:
    return render_final_document_with_llm(
        client,
        summary_payload=summary_payload,
        previous_document=previous_document,
        recent_messages=recent_messages,
        attachments=attachments,
    )


def render_final_document_with_llm(
    client,
    *,
    summary_payload: dict,
    previous_document: str | None = None,
    recent_messages: list[dict] | None = None,
    attachments: list[dict],
) -> tuple[str, str]:
    instructions = load_prompt("render_final_document.md")
    attachment_text = "\n".join(
        f"- {item['file_name']}：{item.get('caption', '')}" for item in attachments
    )
    previous_document_text = previous_document.strip() if isinstance(previous_document, str) and previous_document.strip() else "无"
    history = "\n".join(
        f"{item['role']}: {item['content']}" for item in (recent_messages or [])
    )
    response = client.generate(
        instructions=instructions,
        input_text=(
            f"结构化摘要：{json.dumps(summary_payload, ensure_ascii=False)}\n"
            f"最近对话：\n{history or '无'}\n"
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
