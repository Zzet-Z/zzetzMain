from app import create_app


def test_create_session_returns_token_and_default_state(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    response = client.post("/api/sessions")
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["status"] == "draft"
    assert payload["locale"] == "zh-CN"
    assert payload["selected_template"] is None
    assert payload["selected_style"] is None
    assert len(payload["token"]) >= 20


def test_get_session_returns_stage_and_summary(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()
    response = client.get(f"/api/sessions/{created['token']}")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["token"] == created["token"]
    assert payload["current_stage"] == "template"
    assert payload["summary"]["payload"] == {}
    assert payload["document"]["status"] == "pending"


def test_patch_session_updates_template_style_and_stage(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()

    template_response = client.patch(
        f"/api/sessions/{created['token']}",
        json={
            "selected_template": "个人作品页",
            "current_stage": "style",
        },
    )
    style_response = client.patch(
        f"/api/sessions/{created['token']}",
        json={
            "selected_style": "极简高级",
            "current_stage": "positioning",
        },
    )
    payload = style_response.get_json()

    assert template_response.status_code == 200
    assert style_response.status_code == 200
    assert payload["selected_template"] == "个人作品页"
    assert payload["selected_style"] == "极简高级"
    assert payload["current_stage"] == "positioning"


def test_patch_session_rejects_invalid_stage_transition(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()
    response = client.patch(
        f"/api/sessions/{created['token']}",
        json={"current_stage": "features"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"message": "当前阶段不能直接跳转到目标阶段。"}


def test_missing_session_returns_chinese_404_message(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    get_response = client.get("/api/sessions/missing-token")
    patch_response = client.patch(
        "/api/sessions/missing-token",
        json={"selected_template": "个人作品页"},
    )

    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert get_response.get_json() == {"message": "这次整理链接可能已失效，请重新开始。"}
    assert patch_response.get_json() == {"message": "这次整理链接可能已失效，请重新开始。"}


def test_api_responses_include_configured_cors_origin(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    response = client.post(
        "/api/sessions",
        headers={"Origin": "http://127.0.0.1:5173"},
    )

    assert response.status_code == 201
    assert response.headers["Access-Control-Allow-Origin"] == "http://127.0.0.1:5173"
