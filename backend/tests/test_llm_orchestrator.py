import httpx

from app.services.llm_client import LLMClient
from app.services.llm_orchestrator import (
    build_chat_request,
    build_chat_input,
    extract_summary_update,
    generate_chat_reply,
    generate_stage_reply,
    load_prompt,
    render_final_document_with_llm,
    render_prd_with_llm,
)
from app.services.summary_builder import merge_summary, should_refresh_summary


def test_build_chat_input_includes_previous_document_and_history():
    input_text = build_chat_input(
        session_context={"previous_document": "# 上一版需求文档"},
        recent_messages=[
            {"role": "user", "content": "我想调整首页结构"},
            {"role": "assistant", "content": "可以，我们先梳理页面目标。"},
        ],
    )

    assert "上一版需求文档" in input_text
    assert "user: 我想调整首页结构" in input_text
    assert "assistant: 可以，我们先梳理页面目标。" in input_text


def test_generate_chat_reply_parses_json_envelope():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert "JSON" in instructions
            assert "上一版最终文档" in input_text
            return type(
                "Response",
                (),
                {
                    "text": '{"assistant_message":"信息已经足够，我可以整理最终需求文档。","conversation_intent":"ready_to_generate"}'
                },
            )()

    payload = generate_chat_reply(
        FakeClient(),
        session_context={"previous_document": "# 上一版需求文档"},
        recent_messages=[{"role": "user", "content": "我已经把需求都说完了"}],
    )

    assert payload["assistant_message"] == "信息已经足够，我可以整理最终需求文档。"
    assert payload["conversation_intent"] == "ready_to_generate"


def test_generate_chat_reply_preserves_final_document_intent():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            return type(
                "Response",
                (),
                {
                    "text": '{"assistant_message":"我可以开始整理最终文档。","conversation_intent":"final_document"}'
                },
            )()

    payload = generate_chat_reply(
        FakeClient(),
        session_context={"previous_document": None},
        recent_messages=[{"role": "user", "content": "可以开始出文档了"}],
    )

    assert payload["assistant_message"] == "我可以开始整理最终文档。"
    assert payload["conversation_intent"] == "final_document"


def test_generate_chat_reply_falls_back_when_llm_returns_plain_text():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            return type("Response", (), {"text": "我建议你先补充目标用户和转化动作。"})()

    payload = generate_chat_reply(
        FakeClient(),
        session_context={"previous_document": None},
        recent_messages=[{"role": "user", "content": "帮我看看"}],
    )

    assert payload["assistant_message"] == "我建议你先补充目标用户和转化动作。"
    assert payload["conversation_intent"] == "continue"


def test_generate_chat_reply_includes_previous_document_context():
    captured = {}

    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            captured["input_text"] = input_text
            return type(
                "Response",
                (),
                {"text": '{"assistant_message":"继续聊","conversation_intent":"continue"}'},
            )()

    generate_chat_reply(
        FakeClient(),
        session_context={"previous_document": "# 上一版需求文档"},
        recent_messages=[{"role": "user", "content": "我想调整首页结构"}],
    )

    assert "上一版需求文档" in captured["input_text"]


def test_render_final_document_with_llm_includes_previous_document_context():
    captured = {}

    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            captured["instructions"] = instructions
            captured["input_text"] = input_text
            assert timeout == 45.0
            return type("Response", (), {"text": "# 项目目标\n\n做一个中文作品网站"})()

    summary_text, prd_markdown = render_final_document_with_llm(
        FakeClient(),
        summary_payload={
            "website_type": "个人作品页",
            "visual_direction": "极简高级",
        },
        previous_document="# 上一版需求文档",
        attachments=[{"file_name": "ref-1.png", "caption": "极简排版参考"}],
    )

    assert "上一版需求文档" in captured["input_text"]
    assert "输出中文 PRD" in captured["instructions"]
    assert "个人作品页" in summary_text
    assert "极简高级" in summary_text
    assert prd_markdown.startswith("# 项目目标")


def test_render_final_document_with_llm_includes_recent_messages():
    captured = {}

    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            captured["input_text"] = input_text
            return type("Response", (), {"text": "# 项目目标\n\n做一个中文作品网站"})()

    render_final_document_with_llm(
        FakeClient(),
        summary_payload={"website_type": "个人作品页"},
        previous_document=None,
        recent_messages=[
            {"role": "user", "content": "目标是展示插画作品"},
            {"role": "assistant", "content": "明白，我们继续看风格。"},
        ],
        attachments=[],
    )

    assert "最近对话：" in captured["input_text"]
    assert "user: 目标是展示插画作品" in captured["input_text"]
    assert "assistant: 明白，我们继续看风格。" in captured["input_text"]


def test_welcome_initial_prompt_is_written_for_first_turn():
    prompt = load_prompt("welcome_initial.md")

    assert "网站需求助手" in prompt
    assert "目标" in prompt
    assert "目标用户" in prompt
    assert "想展示的内容" in prompt
    assert "喜欢什么风格" in prompt
    assert "参考案例" in prompt


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


def test_skip_template_moves_to_style():
    from app.services.intake_state_machine import next_stage_for_session

    result = next_stage_for_session(
        current_stage="template",
        selected_template=None,
        selected_style=None,
        summary_payload={},
        user_action="skip",
    )

    assert result == "style"


def test_should_refresh_summary_when_stage_completed():
    assert (
        should_refresh_summary(
            current_stage="positioning",
            stage_completed=True,
            generation_requested=False,
        )
        is True
    )


def test_merge_summary_skips_empty_values():
    merged = merge_summary(
        {"website_type": "个人作品页", "visual_direction": "极简高级"},
        {"visual_direction": "", "positioning_ready": True},
    )

    assert merged == {
        "website_type": "个人作品页",
        "visual_direction": "极简高级",
        "positioning_ready": True,
    }


def test_llm_client_sends_http_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output": [{"content": [{"text": "你好，我来帮你梳理需求。"}]}]}

    def fake_post(url, headers, json, timeout, trust_env):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        captured["trust_env"] = trust_env
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
    assert captured["trust_env"] is False
    assert result.text == "你好，我来帮你梳理需求。"


def test_llm_client_ignores_host_proxy_environment(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output": [{"content": [{"text": "ok"}]}]}

    def fake_post(url, headers, json, timeout, trust_env):
        captured["trust_env"] = trust_env
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    result = client.generate(instructions="请使用中文", input_text="我是插画师")

    assert captured["trust_env"] is False
    assert result.text == "ok"


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
    def fake_post(url, headers, json, timeout, trust_env):
        raise httpx.TimeoutException("boom")

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    try:
        client.generate(instructions="请使用中文", input_text="我是插画师")
    except RuntimeError as exc:
        assert str(exc) == "LLM 调用超时"
    else:
        raise AssertionError("expected RuntimeError")


def test_llm_client_retries_once_after_timeout(monkeypatch):
    attempts = {"count": 0}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output": [{"content": [{"text": "第二次成功"}]}]}

    def fake_post(url, headers, json, timeout, trust_env):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.TimeoutException("boom")
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    result = client.generate(instructions="请使用中文", input_text="我是插画师")

    assert attempts["count"] == 2
    assert result.text == "第二次成功"


def test_llm_client_raises_chinese_runtime_error_on_http_error(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            request = httpx.Request("POST", "https://api.openai.com/v1/responses")
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("server error", request=request, response=response)

        def json(self):
            return {}

    def fake_post(url, headers, json, timeout, trust_env):
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


def test_generate_stage_reply_uses_extended_timeout():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert timeout == 90.0
            return type("Response", (), {"text": "请继续补充目标受众。"})()

    reply = generate_stage_reply(
        FakeClient(),
        stage="positioning",
        summary_payload={"website_type": "个人作品页"},
        recent_messages=[{"role": "user", "content": "我是插画师"}],
    )

    assert reply == "请继续补充目标受众。"


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


def test_extract_summary_update_uses_extended_timeout():
    class FakeClient:
        def generate(self, *, instructions, input_text, timeout=30.0):
            assert timeout == 90.0
            return type("Response", (), {"text": '{"positioning_ready": true}'})()

    result = extract_summary_update(
        FakeClient(),
        current_stage="positioning",
        existing_summary={},
        recent_messages=[{"role": "user", "content": "我想先建立信任"}],
    )

    assert result["positioning_ready"] is True


def test_extract_summary_prompt_requires_ready_flags():
    prompt = load_prompt("extract_summary.md")

    assert "positioning_ready" in prompt
    assert "content_ready" in prompt
    assert "features_ready" in prompt
    assert "只能输出一个 JSON 对象" in prompt


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
