from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


@dataclass
class LLMResponse:
    text: str


class LLMClient:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @classmethod
    def from_env(cls) -> "LLMClient":
        return cls(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout=float(os.getenv("OPENAI_TIMEOUT", "30")),
        )

    def generate(
        self,
        *,
        instructions: str,
        input_text: str,
        timeout: float | None = None,
    ) -> LLMResponse:
        request_timeout = self.timeout if timeout is None else timeout

        for attempt in range(2):
            try:
                response = httpx.post(
                    f"{self.base_url}/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "instructions": instructions,
                        "input": input_text,
                    },
                    timeout=request_timeout,
                )
                response.raise_for_status()
                payload = response.json()
                return LLMResponse(text=_extract_text(payload))
            except httpx.TimeoutException as exc:
                if attempt == 1:
                    raise RuntimeError("LLM 调用超时") from exc
            except httpx.HTTPError as exc:
                raise RuntimeError("LLM 调用失败") from exc

        raise RuntimeError("LLM 调用超时")


def _extract_text(payload: dict) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]

    output_items = payload.get("output", [])
    for item in output_items:
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                return text
    return ""
