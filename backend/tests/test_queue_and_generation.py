from app import create_app


def test_message_route_uses_current_stage_prompt(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    class FakeLLMClient:
        def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
            if "输出更新后的 JSON 摘要" in instructions:
                return type(
                    "Resp",
                    (),
                    {"text": '{"website_type":"个人作品页","positioning_ready": true}'},
                )()
            assert "当前阶段是“模板”" in instructions
            assert "我是插画师" in input_text
            return type("Resp", (), {"text": "请继续告诉我你的网站主要给谁看。"})()

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "我是插画师", "stage_completed": True, "action": "selected"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["assistant_reply"] == "请继续告诉我你的网站主要给谁看。"
    assert payload["current_stage"] == "style"


def test_message_route_returns_502_when_llm_fails(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    class FailingLLMClient:
        def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
            raise RuntimeError("LLM 调用失败")

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FailingLLMClient())

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "我是插画师"},
    )

    assert response.status_code == 502
    assert response.get_json() == {"message": "暂时无法继续整理需求，请稍后重试。"}
