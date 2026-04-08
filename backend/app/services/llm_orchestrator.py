from __future__ import annotations

import json
from pathlib import Path


PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


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
    )
    return response.text


def extract_summary_update(client, *, current_stage: str, existing_summary: dict, recent_messages: list[dict]) -> dict:
    instructions = f"{load_prompt('system.md')}\n\n{load_prompt('extract_summary.md')}"
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    response = client.generate(
        instructions=instructions,
        input_text=f"当前阶段：{current_stage}\n已有摘要：{existing_summary}\n新增对话：{history}",
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return existing_summary


def render_prd_with_llm(client, *, summary_payload: dict, attachments: list[dict]) -> tuple[str, str]:
    instructions = f"{load_prompt('system.md')}\n\n{load_prompt('render_prd.md')}"
    attachment_text = "\n".join(
        f"- {item['file_name']}：{item.get('caption', '')}" for item in attachments
    )
    response = client.generate(
        instructions=instructions,
        input_text=f"结构化摘要：{summary_payload}\n附件：{attachment_text}",
        timeout=45.0,
    )
    summary_text = (
        f"网站类型：{summary_payload.get('website_type') or '未确定'}\n"
        f"视觉方向：{summary_payload.get('visual_direction') or '未确定'}"
    )
    return summary_text, response.text
