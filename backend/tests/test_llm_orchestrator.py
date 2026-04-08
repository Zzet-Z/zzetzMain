import httpx

from app.services.llm_client import LLMClient
from app.services.llm_orchestrator import (
    build_chat_request,
    extract_summary_update,
    generate_stage_reply,
    render_prd_with_llm,
)


def test_build_chat_request_uses_chinese_and_stage_prompt():
    request = build_chat_request(
        stage="positioning",
        summary_payload={"website_type": "个人作品页"},
        recent_messages=[{"role": "user", "content": "我是插画师"}],
    )

    assert request["stage"] == "positioning"
    assert request["locale"] == "zh-CN"
    assert "简体中文" in request["system_prompt"]
    assert "个人作品页" in request["context_text"]


def test_llm_client_sends_http_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output": [{"content": [{"text": "你好，我来帮你梳理需求。"}]}]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    result = client.generate(instructions="请使用中文", input_text="我是插画师")

    assert captured["url"].endswith("/responses")
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["json"]["model"] == "gpt-4.1-mini"
    assert captured["json"]["instructions"] == "请使用中文"
    assert captured["json"]["input"] == "我是插画师"
    assert captured["timeout"] == 30.0
    assert result.text == "你好，我来帮你梳理需求。"


def test_llm_client_reads_settings_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    monkeypatch.setenv("OPENAI_MODEL", "qwen3.5-plus")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    monkeypatch.setenv("OPENAI_TIMEOUT", "45")

    client = LLMClient.from_env()

    assert client.api_key == "env-key"
    assert client.model == "qwen3.5-plus"
    assert client.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"
    assert client.timeout == 45.0


def test_llm_client_raises_chinese_runtime_error_on_timeout(monkeypatch):
    def fake_post(url, headers, json, timeout):
        raise httpx.TimeoutException("boom")

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    try:
        client.generate(instructions="请使用中文", input_text="我是插画师")
    except RuntimeError as exc:
        assert str(exc) == "LLM 调用超时"
    else:
        raise AssertionError("expected RuntimeError")


def test_llm_client_raises_chinese_runtime_error_on_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            request = httpx.Request("POST", "https://api.openai.com/v1/responses")
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("server error", request=request, response=response)

        def json(self):
            return {}

    def fake_post(url, headers, json, timeout):
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    try:
        client.generate(instructions="请使用中文", input_text="我是插画师")
    except RuntimeError as exc:
        assert str(exc) == "LLM 调用失败"
    else:
        raise AssertionError("expected RuntimeError")


def test_generate_stage_reply_passes_prompt_to_client():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert "当前阶段是“定位”" in instructions
            assert "我是插画师" in input_text
            return type("Response", (), {"text": "请先告诉我，你希望网站主要打动谁？"})()

    reply = generate_stage_reply(
        FakeClient(),
        stage="positioning",
        summary_payload={"website_type": "个人作品页"},
        recent_messages=[{"role": "user", "content": "我是插画师"}],
    )

    assert reply == "请先告诉我，你希望网站主要打动谁？"


def test_extract_summary_update_parses_json_code_fence():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert "输出更新后的 JSON 摘要" in instructions
            assert "当前阶段：content" in input_text
            return type(
                "Response",
                (),
                {"text": '```json\n{"website_type":"个人作品页","visual_direction":"极简高级"}\n```'},
            )()

    result = extract_summary_update(
        FakeClient(),
        current_stage="content",
        existing_summary={"website_type": "个人作品页"},
        recent_messages=[{"role": "user", "content": "我想要极简高级"}],
    )

    assert result["visual_direction"] == "极简高级"


def test_extract_summary_update_returns_existing_summary_on_invalid_json():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            return type("Response", (), {"text": "不是 JSON"})()

    existing_summary = {"website_type": "个人作品页"}

    result = extract_summary_update(
        FakeClient(),
        current_stage="content",
        existing_summary=existing_summary,
        recent_messages=[{"role": "user", "content": "我想要极简高级"}],
    )

    assert result == existing_summary


def test_render_prd_with_llm_returns_summary_text_and_markdown():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert "输出中文 PRD" in instructions
            assert "结构化摘要" in input_text
            assert timeout == 45.0
            return type("Response", (), {"text": "# 项目目标\n\n做一个中文作品网站"})()

    summary_text, prd_markdown = render_prd_with_llm(
        FakeClient(),
        summary_payload={
            "website_type": "个人作品页",
            "visual_direction": "极简高级",
        },
        attachments=[{"file_name": "ref-1.png", "caption": "极简排版参考"}],
    )

    assert "个人作品页" in summary_text
    assert "极简高级" in summary_text
    assert prd_markdown.startswith("# 项目目标")
