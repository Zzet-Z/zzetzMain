from io import BytesIO

from app import create_app


class FakeLLMClient:
    def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
        if "输出更新后的 JSON 摘要" in instructions:
            return type(
                "Resp",
                (),
                {"text": '{"website_type":"个人作品页","visual_direction":"极简高级"}'},
            )()
        if "输出中文 PRD" in instructions:
            return type(
                "Resp",
                (),
                {"text": "# 网站需求 PRD\n\n## 项目目标\n展示作品并获取联系。"},
            )()
        return type("Resp", (), {"text": "请继续告诉我你的目标受众。"})()


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


def test_message_route_returns_502_when_summary_extraction_fails(tmp_path, monkeypatch):
    db_path = tmp_path / "summary-fail.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    class ReplyingLLMClient:
        def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
            return type("Resp", (), {"text": "请继续告诉我你的网站主要给谁看。"})()

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: ReplyingLLMClient())
    monkeypatch.setattr(
        "app.routes.messages.extract_summary_update",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("LLM 调用超时")),
    )

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "我是插画师", "stage_completed": True},
    )

    assert response.status_code == 502
    assert response.get_json() == {"message": "暂时无法继续整理需求，请稍后重试。"}


def test_sixth_active_session_is_queued(tmp_path, monkeypatch):
    db_path = tmp_path / "queue.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    tokens = [client.post("/api/sessions").get_json()["token"] for _ in range(6)]

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
    monkeypatch.setattr(
        "app.services.document_renderer.LLMClient.from_env",
        lambda: FakeLLMClient(),
    )

    for token in tokens[:5]:
        response = client.post(
            f"/api/sessions/{token}/messages",
            json={"content": "我想做个人网站"},
        )
        assert response.status_code == 201

    response = client.post(
        f"/api/sessions/{tokens[5]}/messages",
        json={"content": "我想做公司介绍页"},
    )
    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "queued"
    assert payload["queue_position"] == 1
    assert payload["poll_after_ms"] == 3000


def test_document_endpoint_returns_chinese_summary(tmp_path, monkeypatch):
    db_path = tmp_path / "doc.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
    monkeypatch.setattr(
        "app.services.document_renderer.LLMClient.from_env",
        lambda: FakeLLMClient(),
    )

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "我是插画师，想展示作品", "generation_requested": True},
    )

    assert response.status_code == 202

    document_response = client.get(f"/api/sessions/{token}/document")
    payload = document_response.get_json()

    assert document_response.status_code == 200
    assert "网站类型" in payload["summary_text"]
    assert "# 网站需求 PRD" in payload["prd_markdown"]


def test_generation_request_skips_stage_reply_prompt(tmp_path, monkeypatch):
    db_path = tmp_path / "doc-generate.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    client.patch(f"/api/sessions/{token}", json={"current_stage": "generate"})

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
    monkeypatch.setattr(
        "app.services.document_renderer.LLMClient.from_env",
        lambda: FakeLLMClient(),
    )
    monkeypatch.setattr(
        "app.routes.messages.generate_stage_reply",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not generate stage reply")),
    )

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "请开始生成 PRD", "generation_requested": True},
    )

    assert response.status_code == 202
    assert response.get_json()["message"] == "正在生成 PRD"

    document_response = client.get(f"/api/sessions/{token}/document")
    payload = document_response.get_json()

    assert document_response.status_code == 200
    assert payload["status"] == "ready"
    assert "# 网站需求 PRD" in payload["prd_markdown"]


def test_message_route_returns_502_when_document_render_fails(tmp_path, monkeypatch):
    db_path = tmp_path / "doc-fail.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
    monkeypatch.setattr(
        "app.routes.messages.render_document_bundle",
        lambda **kwargs: (_ for _ in ()).throw(RuntimeError("LLM 调用超时")),
    )

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "请直接生成 PRD", "generation_requested": True},
    )

    assert response.status_code == 502
    assert response.get_json() == {"message": "暂时无法继续整理需求，请稍后重试。"}


def test_document_generation_includes_attachment_list(tmp_path, monkeypatch):
    db_path = tmp_path / "doc-attachments.db"
    upload_dir = tmp_path / "uploads"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(upload_dir),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
    monkeypatch.setattr(
        "app.services.document_renderer.LLMClient.from_env",
        lambda: FakeLLMClient(),
    )

    upload_response = client.post(
        f"/api/sessions/{token}/attachments",
        data={
            "file": (BytesIO(b"binary"), "reference.png"),
            "caption": "极简排版参考",
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "请直接生成 PRD", "generation_requested": True},
    )

    assert response.status_code == 202

    document_response = client.get(f"/api/sessions/{token}/document")
    payload = document_response.get_json()

    assert "## 参考附件" in payload["prd_markdown"]
    assert "reference.png" in payload["prd_markdown"]
    assert "极简排版参考" in payload["prd_markdown"]
