# 个人网站 MVP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个面向简体中文用户、移动端优先的 MVP：首页负责建立审美与产品认知，需求梳理页通过真实 LLM 对话引导用户输出中文摘要与中文 PRD。

**Architecture:** 采用单仓库结构，前端使用 React + Tailwind CSS，后端使用 Flask + SQLite。后端负责 `session token`、会话状态、5 会话并发队列、图片上传、结构化摘要、真实 LLM 调用、最终 PRD 渲染；前端负责 mobile-first 的首页与需求梳理体验，并通过短轮询/长轮询驱动状态更新。LLM 采用真实 HTTP API 调用，默认按 OpenAI Responses API 设计，并通过环境变量配置密钥、模型和超时。

**Tech Stack:** React, TypeScript, Vite, Tailwind CSS, Vitest, Flask, SQLAlchemy, SQLite, pytest

---

## 文件结构

### 仓库布局

- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app.tsx`
- Create: `frontend/src/styles.css`
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/routes/home-page.tsx`
- Create: `frontend/src/routes/session-page.tsx`
- Create: `frontend/src/components/home/hero.tsx`
- Create: `frontend/src/components/home/problem.tsx`
- Create: `frontend/src/components/home/process.tsx`
- Create: `frontend/src/components/home/output-preview.tsx`
- Create: `frontend/src/components/home/final-cta.tsx`
- Create: `frontend/src/components/intake/step-header.tsx`
- Create: `frontend/src/components/intake/template-selector.tsx`
- Create: `frontend/src/components/intake/style-selector.tsx`
- Create: `frontend/src/components/intake/chat-panel.tsx`
- Create: `frontend/src/components/intake/summary-panel.tsx`
- Create: `frontend/src/components/intake/attachment-panel.tsx`
- Create: `frontend/src/components/ui/button.tsx`
- Create: `frontend/src/test/app-shell.test.tsx`
- Create: `frontend/src/test/home-page.test.tsx`
- Create: `frontend/src/test/session-page.test.tsx`
- Create: `frontend/src/test/session-flow.test.tsx`
- Create: `frontend/src/test/mobile-states.test.tsx`
- Create: `backend/pyproject.toml`
- Create: `backend/run.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/routes/health.py`
- Create: `backend/app/routes/sessions.py`
- Create: `backend/app/routes/messages.py`
- Create: `backend/app/routes/uploads.py`
- Create: `backend/app/routes/documents.py`
- Create: `backend/app/services/template_catalog.py`
- Create: `backend/app/services/queue_manager.py`
- Create: `backend/app/services/storage.py`
- Create: `backend/app/services/summary_builder.py`
- Create: `backend/app/services/document_renderer.py`
- Create: `backend/app/services/intake_state_machine.py`
- Create: `backend/app/services/llm_client.py`
- Create: `backend/app/services/llm_orchestrator.py`
- Create: `backend/app/prompts/system.md`
- Create: `backend/app/prompts/template.md`
- Create: `backend/app/prompts/style.md`
- Create: `backend/app/prompts/positioning.md`
- Create: `backend/app/prompts/content.md`
- Create: `backend/app/prompts/features.md`
- Create: `backend/app/prompts/extract_summary.md`
- Create: `backend/app/prompts/render_prd.md`
- Create: `backend/tests/test_health.py`
- Create: `backend/tests/test_sessions_api.py`
- Create: `backend/tests/test_llm_orchestrator.py`
- Create: `backend/tests/test_queue_and_generation.py`
- Create: `backend/tests/test_uploads_api.py`
- Create: `README.md`

### 设计边界

- MVP 只支持简体中文输入与输出。
- 真实 LLM 必须进入第一版实现，不允许用纯 mock 替代整条主链路。
- 轮询优先，不做 WebSocket。
- 前端是一套响应式界面，不拆移动端和桌面端两套应用。
- SQLite 可以作为内测数据库，但数据访问层要避免把逻辑锁死在 SQLite 特性上。

## Task 1：搭建前后端脚手架与最小运行面

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/postcss.config.js`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/app.tsx`
- Create: `frontend/src/styles.css`
- Create: `backend/pyproject.toml`
- Create: `backend/run.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/routes/health.py`
- Create: `README.md`
- Test: `frontend/src/test/app-shell.test.tsx`
- Test: `backend/tests/test_health.py`

- [ ] **Step 1: 先写失败的后端健康检查测试**

```python
from app import create_app


def test_healthcheck_returns_ok():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
```

- [ ] **Step 2: 再写失败的前端壳测试**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("首页路由可以渲染", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", { name: /把你想要的网站，说出来。/i }),
  ).toBeInTheDocument();
});
```

- [ ] **Step 3: 运行测试，确认当前确实失败**

Run:

```bash
cd backend && pytest tests/test_health.py -q
cd frontend && npm test -- app-shell.test.tsx
```

Expected:

- 后端失败，因为 `create_app` 和 `/api/health` 还不存在
- 前端失败，因为 React 壳应用还不存在

- [ ] **Step 4: 写出最小后端应用工厂与健康检查**

```python
# backend/app/__init__.py
from flask import Flask


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL="sqlite:///app.db",
        UPLOAD_DIR="uploads",
        MAX_ACTIVE_SESSIONS=5,
        MAX_UPLOAD_SIZE_MB=8,
        MAX_UPLOAD_COUNT=12,
    )
    if config_overrides:
        app.config.update(config_overrides)

    from .routes.health import health_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    return app
```

```python
# backend/app/routes/health.py
from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def healthcheck():
    return jsonify({"status": "ok"})
```

```python
# backend/run.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

- [ ] **Step 5: 写出最小前端壳**

```tsx
// frontend/src/app.tsx
import { Route, Routes } from "react-router-dom";

function HomePage() {
  return <h1>把你想要的网站，说出来。</h1>;
}

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  );
}
```

```tsx
// frontend/src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./app";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);
```

```css
/* frontend/src/styles.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
}
```

- [ ] **Step 6: 写出最小依赖清单**

```json
// frontend/package.json
{
  "name": "zzetz-main-frontend",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.2.0",
    "@types/react": "^19.0.10",
    "@types/react-dom": "^19.0.4",
    "@vitejs/plugin-react": "^5.0.0",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.5.3",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.8.3",
    "vite": "^6.2.0",
    "vitest": "^3.1.1"
  }
}
```

```toml
# backend/pyproject.toml
[project]
name = "zzetz-main-backend"
version = "0.0.1"
dependencies = [
  "Flask>=3.1.0",
  "Flask-Cors>=5.0.0",
  "SQLAlchemy>=2.0.40",
  "httpx>=0.28.1",
  "pytest>=8.3.5",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 7: 重新运行测试，确认脚手架通过**

Run:

```bash
cd backend && pytest tests/test_health.py -q
cd frontend && npm test -- app-shell.test.tsx
```

Expected:

- 两边测试都通过

- [ ] **Step 8: Commit**

```bash
git add README.md backend frontend
git commit -m "chore: scaffold frontend and backend apps"
```

## Task 2：建立会话模型、数据库与基础 API

**Files:**
- Create: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/routes/sessions.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_sessions_api.py`

- [ ] **Step 1: 写失败的 session 创建测试**

```python
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
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_default_state -q
```

Expected:

- 失败，因为 `POST /api/sessions` 还不存在

- [ ] **Step 3: 写数据库初始化与模型**

```python
# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def init_db(database_url: str):
    engine = create_engine(database_url, future=True)
    SessionLocal.configure(bind=engine)
    Base.metadata.create_all(engine)
    return engine
```

```python
# backend/app/models.py
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base


class SessionRecord(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    locale: Mapped[str] = mapped_column(String(16), default="zh-CN")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    current_stage: Mapped[str] = mapped_column(String(32), default="template")
    selected_template: Mapped[str | None] = mapped_column(String(64), nullable=True)
    selected_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class SummarySnapshot(Base):
    __tablename__ = "summary_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    version: Mapped[int] = mapped_column(Integer, default=1)
    summary_text: Mapped[str] = mapped_column(Text, default="")
    prd_markdown: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
```

- [ ] **Step 4: 实现 session 路由**

```python
# backend/app/routes/sessions.py
from secrets import token_urlsafe
from flask import Blueprint, jsonify, request
from ..db import SessionLocal
from ..models import DocumentRecord, SessionRecord, SummarySnapshot

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.post("/sessions")
def create_session():
    db = SessionLocal()
    token = token_urlsafe(24)
    record = SessionRecord(token=token)
    db.add(record)
    db.add(SummarySnapshot(session_token=token, payload={}))
    db.add(DocumentRecord(session_token=token))
    db.commit()
    return (
        jsonify(
            {
                "token": record.token,
                "locale": record.locale,
                "status": record.status,
                "current_stage": record.current_stage,
                "selected_template": record.selected_template,
                "selected_style": record.selected_style,
            }
        ),
        201,
    )
```

```python
@sessions_bp.patch("/sessions/<token>")
def update_session(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        return jsonify({"message": "这次整理链接可能已失效，请重新开始。"}), 404

    payload = request.get_json()
    if "selected_template" in payload:
        session.selected_template = payload["selected_template"]
    if "selected_style" in payload:
        session.selected_style = payload["selected_style"]
    if "current_stage" in payload:
        session.current_stage = payload["current_stage"]
    db.commit()
    return jsonify(
        {
            "token": session.token,
            "current_stage": session.current_stage,
            "selected_template": session.selected_template,
            "selected_style": session.selected_style,
        }
    )
```

```python
# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from .db import init_db
from .db import SessionLocal


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL="sqlite:///app.db",
        FRONTEND_ORIGIN="http://127.0.0.1:5173",
        UPLOAD_DIR="uploads",
        MAX_ACTIVE_SESSIONS=5,
        MAX_UPLOAD_SIZE_MB=8,
        MAX_UPLOAD_COUNT=12,
    )
    if config_overrides:
        app.config.update(config_overrides)

    init_db(app.config["DATABASE_URL"])
    CORS(app, resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}})

    from .routes.health import health_bp
    from .routes.sessions import sessions_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")

    @app.teardown_appcontext
    def cleanup_session(_exception=None):
        SessionLocal.remove()

    return app
```

- [ ] **Step 5: 加一条读取 session 的测试与实现**

```python
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
```

```python
@sessions_bp.get("/sessions/<token>")
def get_session(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        return jsonify({"message": "这次整理链接可能已失效，请重新开始。"}), 404
    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    latest_document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    return jsonify(
        {
            "token": session.token,
            "locale": session.locale,
            "status": session.status,
            "current_stage": session.current_stage,
            "selected_template": session.selected_template,
            "selected_style": session.selected_style,
            "summary": {"payload": latest_summary.payload},
            "document": {"status": latest_document.status},
        }
    )
```

- [ ] **Step 6: 运行 session 测试，确认通过**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py -q
```

Expected:

- session 创建和读取测试通过

- [ ] **Step 7: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add session persistence and api"
```

## Task 3：接入真实 LLM 客户端与基础编排器

**Files:**
- Create: `backend/app/services/llm_client.py`
- Create: `backend/app/services/llm_orchestrator.py`
- Create: `backend/app/prompts/system.md`
- Create: `backend/app/prompts/extract_summary.md`
- Create: `backend/app/prompts/render_prd.md`
- Create: `backend/tests/test_llm_orchestrator.py`

- [ ] **Step 1: 写失败的 LLM 编排测试**

```python
from app.services.llm_orchestrator import build_chat_request


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
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py::test_build_chat_request_uses_chinese_and_stage_prompt -q
```

Expected:

- 失败，因为 LLM 编排器还不存在

- [ ] **Step 3: 写真实 LLM 客户端接口**

```python
# backend/app/services/llm_client.py
from dataclasses import dataclass
import httpx
import os


@dataclass
class LLMResponse:
    text: str


class LLMClient:
    def __init__(self, *, api_key: str, model: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        )

    def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0) -> LLMResponse:
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
                timeout=timeout,
            )
            response.raise_for_status()
            payload = response.json()
            return LLMResponse(text=payload["output"][0]["content"][0]["text"])
        except httpx.TimeoutException as exc:
            raise RuntimeError("LLM 调用超时") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("LLM 调用失败") from exc
```

- [ ] **Step 4: 写阶段化编排器与调用封装**

```python
# backend/app/services/llm_orchestrator.py
import json
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[1] / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8")


def build_chat_request(*, stage: str, summary_payload: dict, recent_messages: list[dict]) -> dict:
    system = load_prompt("system.md")
    stage_prompt = load_prompt(f"{stage}.md")
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    return {
        "stage": stage,
        "locale": "zh-CN",
        "system_prompt": system + "\n\n" + stage_prompt,
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
    instructions = load_prompt("system.md") + "\n\n" + load_prompt("extract_summary.md")
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
    instructions = load_prompt("system.md") + "\n\n" + load_prompt("render_prd.md")
    attachment_text = "\n".join(f"- {item['file_name']}：{item['caption']}" for item in attachments)
    response = client.generate(
        instructions=instructions,
        input_text=f"结构化摘要：{summary_payload}\n附件：{attachment_text}",
        timeout=45.0,
    )
    prd_markdown = response.text
    summary_text = f"网站类型：{summary_payload.get('website_type') or '未确定'}\n视觉方向：{summary_payload.get('visual_direction') or '未确定'}"
    return summary_text, prd_markdown
```

- [ ] **Step 5: 写首版中文 prompt 文件**

```md
<!-- backend/app/prompts/system.md -->
你是一个帮助普通用户梳理个人网站需求的中文 AI 助手。
你必须使用简体中文回复。
你不能假装已经知道用户没有说过的信息。
你的目标是通过阶段化追问，帮助用户产出中文摘要和中文 PRD。
```

```md
<!-- backend/app/prompts/positioning.md -->
当前阶段是“定位”。
你的任务是澄清用户是谁、网站给谁看、希望访客完成什么动作、希望传达什么气质。
每次只问一个问题，避免一次追问多个维度。
```

```md
<!-- backend/app/prompts/template.md -->
当前阶段是“模板”。
你的任务是帮助用户在个人作品页、个人简历页、个人品牌页、服务介绍页、公司介绍页、预约咨询页之间做出选择。
如果用户明确表示跳过，允许进入下一个阶段。
```

```md
<!-- backend/app/prompts/style.md -->
当前阶段是“风格”。
你的任务是帮助用户在极简高级、现代专业、强视觉作品集、温和可信、前卫未来感之间选择，或允许用户跳过。
```

```md
<!-- backend/app/prompts/content.md -->
当前阶段是“内容”。
你的任务是帮助用户梳理网站需要包含的页面和模块，例如作品、经历、服务、联系方式、文章、FAQ。
```

```md
<!-- backend/app/prompts/features.md -->
当前阶段是“功能”。
你的任务是确认联系表单、预约、博客、FAQ、筛选、多页结构，以及用户明确不想要的内容。
```

```md
<!-- backend/app/prompts/extract_summary.md -->
根据当前结构化摘要和本轮新增信息，输出更新后的 JSON 摘要。
只提取明确表达过的信息，不要臆测。
```

```md
<!-- backend/app/prompts/render_prd.md -->
请根据结构化摘要输出中文 PRD。
PRD 至少包含：项目目标、目标受众、网站类型、视觉方向、页面结构、内容模块、功能需求、排除项、附件说明。
```

- [ ] **Step 6: 再补一条真实 HTTP 调用形状测试**

```python
from app.services.llm_client import LLMClient


def test_llm_client_sends_http_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"output": [{"content": [{"text": "你好，我来帮你梳理需求。"}]}]}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse()

    monkeypatch.setattr("app.services.llm_client.httpx.post", fake_post)
    client = LLMClient(api_key="test-key", model="gpt-4.1-mini")

    result = client.generate(instructions="请使用中文", input_text="我是插画师")

    assert captured["url"].endswith("/responses")
    assert captured["json"]["model"] == "gpt-4.1-mini"
    assert result.text == "你好，我来帮你梳理需求。"
```

- [ ] **Step 7: 重新运行 LLM 编排测试**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py -q
```

Expected:

- 测试通过，说明阶段化 prompt 和中文上下文已经接通

- [ ] **Step 8: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add real llm client and prompt orchestration"
```

## Task 4：实现阶段状态机、真实对话引导与摘要提取策略

**Files:**
- Create: `backend/app/services/intake_state_machine.py`
- Create: `backend/app/services/summary_builder.py`
- Create: `backend/app/routes/messages.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_llm_orchestrator.py`
- Test: `backend/tests/test_queue_and_generation.py`

- [ ] **Step 1: 写失败的阶段切换测试**

```python
from app.services.intake_state_machine import next_stage_for_session


def test_skip_template_moves_to_style():
    result = next_stage_for_session(
        current_stage="template",
        selected_template=None,
        selected_style=None,
        summary_payload={},
        user_action="skip",
    )

    assert result == "style"
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py::test_skip_template_moves_to_style -q
```

Expected:

- 失败，因为状态机不存在

- [ ] **Step 3: 写阶段状态机**

```python
# backend/app/services/intake_state_machine.py
ORDER = ["template", "style", "positioning", "content", "features", "generate"]


def next_stage_for_session(*, current_stage: str, selected_template, selected_style, summary_payload: dict, user_action: str):
    if current_stage == "template" and user_action in {"selected", "skip"}:
        return "style"
    if current_stage == "style" and user_action in {"selected", "skip"}:
        return "positioning"
    if current_stage == "positioning" and summary_payload.get("positioning_ready"):
        return "content"
    if current_stage == "content" and summary_payload.get("content_ready"):
        return "features"
    if current_stage == "features" and summary_payload.get("features_ready"):
        return "generate"
    return current_stage
```

- [ ] **Step 4: 写摘要更新策略**

```python
# backend/app/services/summary_builder.py
def should_refresh_summary(*, current_stage: str, stage_completed: bool, generation_requested: bool) -> bool:
    if current_stage in {"template", "style"}:
        return True
    if stage_completed:
        return True
    if generation_requested:
        return True
    return False


def merge_summary(existing: dict, extracted: dict) -> dict:
    merged = dict(existing)
    merged.update({k: v for k, v in extracted.items() if v not in (None, "", [], {})})
    return merged
```

- [ ] **Step 5: 写消息路由，接通真实 LLM 编排**

```python
# backend/app/routes/messages.py
from flask import Blueprint, jsonify, request
from ..db import SessionLocal
from ..models import MessageRecord, SessionRecord, SummarySnapshot
from ..services.intake_state_machine import next_stage_for_session
from ..services.llm_client import LLMClient
from ..services.llm_orchestrator import generate_stage_reply, extract_summary_update
from ..services.summary_builder import should_refresh_summary, merge_summary

messages_bp = Blueprint("messages", __name__)


@messages_bp.post("/sessions/<token>/messages")
def create_message(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    if session is None:
        return jsonify({"message": "这次整理链接可能已失效，请重新开始。"}), 404
    payload = request.get_json()
    content = payload["content"]
    user_action = payload.get("action", "answered")

    db.add(MessageRecord(session_token=token, role="user", content=content, stage=session.current_stage))
    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )

    client = LLMClient.from_env()
    try:
        assistant_reply = generate_stage_reply(
            client,
            stage=session.current_stage,
            summary_payload=latest_summary.payload,
            recent_messages=[{"role": "user", "content": content}],
        )
    except RuntimeError as exc:
        session.last_error = str(exc)
        db.commit()
        return jsonify({"message": "暂时无法继续整理需求，请稍后重试。"}), 502
    db.add(MessageRecord(session_token=token, role="assistant", content=assistant_reply, stage=session.current_stage))

    stage_completed = payload.get("stage_completed", False)
    generation_requested = payload.get("generation_requested", False)

    if should_refresh_summary(
        current_stage=session.current_stage,
        stage_completed=stage_completed,
        generation_requested=generation_requested,
    ):
        extracted = extract_summary_update(
            client,
            current_stage=session.current_stage,
            existing_summary=latest_summary.payload,
            recent_messages=[{"role": "user", "content": content}],
        )
        merged = merge_summary(latest_summary.payload, extracted)
        db.add(SummarySnapshot(session_token=token, payload=merged))
    else:
        merged = latest_summary.payload

    session.current_stage = next_stage_for_session(
        current_stage=session.current_stage,
        selected_template=session.selected_template,
        selected_style=session.selected_style,
        summary_payload=merged,
        user_action=user_action,
    )

    db.commit()
    return jsonify({"assistant_reply": assistant_reply, "current_stage": session.current_stage}), 201
```

- [ ] **Step 6: 补一条测试，确保对话使用当前阶段 prompt**

```python
def test_message_route_uses_current_stage_prompt(tmp_path, monkeypatch):
    db_path = tmp_path / "chat.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    class FakeLLMClient:
        def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
            if "输出更新后的 JSON 摘要" in instructions:
                return type("Resp", (), {"text": "{\"website_type\":\"个人作品页\",\"positioning_ready\": true}"})()
            return type("Resp", (), {"text": "请继续告诉我你的网站主要给谁看。"})()

    monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())

    response = client.post(
        f"/api/sessions/{token}/messages",
        json={"content": "我是插画师", "stage_completed": True, "action": "selected"},
    )
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["assistant_reply"]
    assert payload["current_stage"] == "style"
```

- [ ] **Step 7: 运行测试并确保通过**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q
```

Expected:

- 状态机和消息路由基础测试通过

- [ ] **Step 8: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add stage-aware intake engine"
```

## Task 5：实现并发队列、轮询状态与文档生成

**Files:**
- Create: `backend/app/services/queue_manager.py`
- Create: `backend/app/services/document_renderer.py`
- Create: `backend/app/routes/documents.py`
- Modify: `backend/app/routes/messages.py`
- Modify: `backend/app/services/llm_orchestrator.py`
- Test: `backend/tests/test_queue_and_generation.py`

- [ ] **Step 1: 写失败的排队测试**

```python
from app import create_app


def test_sixth_active_session_is_queued(tmp_path):
    db_path = tmp_path / "queue.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    tokens = [client.post("/api/sessions").get_json()["token"] for _ in range(6)]

    for token in tokens[:5]:
        client.post(f"/api/sessions/{token}/messages", json={"content": "我想做个人网站"})

    response = client.post(f"/api/sessions/{tokens[5]}/messages", json={"content": "我想做公司介绍页"})
    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "queued"
    assert payload["queue_position"] == 1
```

在这条测试和同文件里的文档生成测试中，都需要 monkeypatch `LLMClient.from_env()`，避免测试依赖真实环境变量和外部 API：

```python
class FakeLLMClient:
    def generate(self, *, instructions: str, input_text: str, timeout: float = 30.0):
        if "输出更新后的 JSON 摘要" in instructions:
            return type("Resp", (), {"text": "{\"website_type\":\"个人作品页\",\"visual_direction\":\"极简高级\"}"})()
        if "输出中文 PRD" in instructions:
            return type("Resp", (), {"text": "# 网站需求 PRD\n\n## 项目目标\n展示作品并获取联系。"})()
        return type("Resp", (), {"text": "请继续告诉我你的目标受众。"})()

monkeypatch.setattr("app.routes.messages.LLMClient.from_env", lambda: FakeLLMClient())
monkeypatch.setattr("app.services.document_renderer.LLMClient.from_env", lambda: FakeLLMClient())
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_queue_and_generation.py::test_sixth_active_session_is_queued -q
```

Expected:

- 失败，因为队列控制还未实现

- [ ] **Step 3: 写队列管理器**

```python
# backend/app/services/queue_manager.py
from datetime import UTC, datetime
from ..db import SessionLocal
from ..models import SessionRecord


def reserve_slot(token: str, max_active_sessions: int) -> tuple[str, int | None]:
    db = SessionLocal()
    active_count = (
        db.query(SessionRecord)
        .filter(SessionRecord.status.in_(["active", "generating_document"]))
        .count()
    )
    session = db.get(SessionRecord, token)
    if active_count >= max_active_sessions:
        session.status = "queued"
        session.queued_at = datetime.now(UTC)
        db.commit()
        queued_sessions = (
            db.query(SessionRecord)
            .filter(SessionRecord.status == "queued")
            .order_by(SessionRecord.queued_at.asc(), SessionRecord.token.asc())
            .all()
        )
        queue_position = next(index for index, item in enumerate(queued_sessions, start=1) if item.token == token)
        return "queued", queue_position

    session.status = "active"
    session.queued_at = None
    db.commit()
    return "active", None
```

- [ ] **Step 4: 写中文文档渲染器**

```python
# backend/app/services/document_renderer.py
from ..services.llm_client import LLMClient
from ..services.llm_orchestrator import render_prd_with_llm


def render_document_bundle(*, summary_payload: dict, attachments: list[dict]) -> tuple[str, str]:
    client = LLMClient.from_env()
    return render_prd_with_llm(client, summary_payload=summary_payload, attachments=attachments)
```

- [ ] **Step 5: 更新消息路由，加入排队和生成状态**

```python
status, queue_position = reserve_slot(token, current_app.config["MAX_ACTIVE_SESSIONS"])
if status == "queued":
    return jsonify(
        {
            "session_status": "queued",
            "queue_position": queue_position,
            "message": "当前正在为其他用户整理网站需求，你已进入等待队列。",
            "poll_after_ms": 3000,
        }
    ), 202
```

在文档生成阶段返回：

```python
return jsonify(
    {
        "session_status": "generating_document",
        "message": "正在生成 PRD",
        "poll_after_ms": 5000,
    }
), 202
```

- [ ] **Step 6: 增加文档读取接口测试与实现**

```python
def test_document_endpoint_returns_chinese_summary(tmp_path):
    db_path = tmp_path / "doc.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    client.post(f"/api/sessions/{token}/messages", json={"content": "我是插画师，想展示作品"})
    response = client.get(f"/api/sessions/{token}/document")
    payload = response.get_json()

    assert response.status_code == 200
    assert "网站类型" in payload["summary_text"]
    assert "# 网站需求 PRD" in payload["prd_markdown"]
```

```python
# backend/app/routes/documents.py
from flask import Blueprint, jsonify
from ..db import SessionLocal
from ..models import DocumentRecord

documents_bp = Blueprint("documents", __name__)


@documents_bp.get("/sessions/<token>/document")
def get_document(token: str):
    db = SessionLocal()
    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    return jsonify(
        {
            "status": document.status,
            "summary_text": document.summary_text,
            "prd_markdown": document.prd_markdown,
        }
    )
```

- [ ] **Step 7: 在生成阶段调用 LLM 输出摘要与 PRD**

把下面这段代码插入到 `backend/app/routes/messages.py` 的 `create_message()` 路由里。
位置要求：

- 在 `session.current_stage = next_stage_for_session(...)` 之后
- 在最终 `db.commit()` 之前
- 只在 `generation_requested` 为 `True` 时执行
  这样文档生成会复用同一次请求中已经得到的最新 `merged` 摘要，而不是读取陈旧数据。

```python
from ..models import AttachmentRecord, DocumentRecord
from ..services.document_renderer import render_document_bundle

if generation_requested:
    attachments = [
        {"file_name": item.file_name, "caption": item.caption}
        for item in db.query(AttachmentRecord).filter(AttachmentRecord.session_token == token)
    ]
    summary_text, prd_markdown = render_document_bundle(
        summary_payload=merged,
        attachments=attachments,
    )
    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    document.version += 1
    document.status = "ready"
    document.summary_text = summary_text
    document.prd_markdown = prd_markdown
    session.status = "completed"
```

- [ ] **Step 8: 跑通队列和文档测试**

Run:

```bash
cd backend && pytest tests/test_queue_and_generation.py -q
```

Expected:

- 第六个会话进入排队
- 文档接口返回中文摘要和 PRD

- [ ] **Step 9: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add queue control and document generation states"
```

## Task 6：实现上传、安全限制与错误处理

**Files:**
- Create: `backend/app/services/storage.py`
- Create: `backend/app/routes/uploads.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_uploads_api.py`

- [ ] **Step 1: 写失败的上传测试**

```python
from io import BytesIO
from app import create_app


def test_upload_respects_file_constraints(tmp_path):
    db_path = tmp_path / "upload.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"binary"), "reference.png"), "caption": "首页参考"},
        content_type="multipart/form-data",
    )

    payload = response.get_json()
    assert response.status_code == 201
    assert payload["file_name"] == "reference.png"
```

- [ ] **Step 2: 再写失败的非法类型测试**

```python
def test_upload_rejects_non_image_file(tmp_path):
    db_path = tmp_path / "upload.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()
    token = client.post("/api/sessions").get_json()["token"]

    response = client.post(
        f"/api/sessions/{token}/attachments",
        data={"file": (BytesIO(b"text"), "notes.txt"), "caption": "无效文件"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
```

- [ ] **Step 3: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_uploads_api.py -q
```

Expected:

- 失败，因为上传路由和限制逻辑还不存在

- [ ] **Step 4: 实现文件存储与约束**

```python
# backend/app/services/storage.py
from pathlib import Path
from werkzeug.utils import secure_filename

ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}


def save_upload(upload_dir: str, token: str, file_storage) -> tuple[str, str]:
    if file_storage.mimetype not in ALLOWED_MIME_TYPES:
        raise ValueError("只支持 PNG、JPEG、WEBP 图片")

    token_dir = Path(upload_dir) / token
    token_dir.mkdir(parents=True, exist_ok=True)
    filename = secure_filename(file_storage.filename)
    path = token_dir / filename
    file_storage.save(path)
    return filename, str(path)
```

```python
# backend/app/routes/uploads.py
from flask import Blueprint, current_app, jsonify, request
from ..db import SessionLocal
from ..models import AttachmentRecord
from ..services.storage import save_upload

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.post("/sessions/<token>/attachments")
def create_attachment(token: str):
    file_storage = request.files["file"]
    caption = request.form.get("caption", "")
    try:
        file_name, file_path = save_upload(current_app.config["UPLOAD_DIR"], token, file_storage)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    db = SessionLocal()
    record = AttachmentRecord(
        session_token=token,
        file_name=file_name,
        file_path=file_path,
        mime_type=file_storage.mimetype,
        caption=caption,
    )
    db.add(record)
    db.commit()
    return jsonify({"file_name": file_name, "caption": caption, "file_path": file_path}), 201
```

- [ ] **Step 5: 注册路由并回归测试**

Run:

```bash
cd backend && pytest tests/test_uploads_api.py -q
```

Expected:

- 合法图片上传通过
- 非图片文件被拒绝

- [ ] **Step 6: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add safe image uploads"
```

## Task 7：实现首页移动端优先 UI

**Files:**
- Create: `frontend/src/components/ui/button.tsx`
- Create: `frontend/src/components/home/hero.tsx`
- Create: `frontend/src/components/home/problem.tsx`
- Create: `frontend/src/components/home/process.tsx`
- Create: `frontend/src/components/home/output-preview.tsx`
- Create: `frontend/src/components/home/final-cta.tsx`
- Create: `frontend/src/routes/home-page.tsx`
- Modify: `frontend/src/app.tsx`
- Modify: `frontend/src/styles.css`
- Test: `frontend/src/test/home-page.test.tsx`

- [ ] **Step 1: 写失败的首页测试**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("首页展示主 CTA 与产品副标题", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole("button", { name: /开始梳理我的网站/i })).toBeInTheDocument();
  expect(screen.getByText(/不需要会编程，也不需要先写需求/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd frontend && npm test -- home-page.test.tsx
```

Expected:

- 失败，因为首页结构还未落地

- [ ] **Step 3: 实现首页路由与五段结构**

```tsx
// frontend/src/routes/home-page.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createSession } from "../lib/api";
import { Hero } from "../components/home/hero";
import { ProblemSection } from "../components/home/problem";
import { ProcessSection } from "../components/home/process";
import { OutputPreviewSection } from "../components/home/output-preview";
import { FinalCtaSection } from "../components/home/final-cta";

export function HomePage() {
  const navigate = useNavigate();
  const [isStarting, setIsStarting] = useState(false);

  async function handleStart() {
    setIsStarting(true);
    try {
      const session = await createSession();
      navigate(`/session/${session.token}`);
    } finally {
      setIsStarting(false);
    }
  }

  return (
    <main className="bg-neutral-950 text-white">
      <Hero isStarting={isStarting} onStart={handleStart} />
      <ProblemSection />
      <ProcessSection />
      <OutputPreviewSection />
      <FinalCtaSection isStarting={isStarting} onStart={handleStart} />
    </main>
  );
}
```

```tsx
// frontend/src/components/home/hero.tsx
export function Hero({ isStarting, onStart }: { isStarting: boolean; onStart: () => void }) {
  return (
    <section className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16">
      <h1 className="max-w-4xl text-5xl font-semibold leading-tight sm:text-7xl">
        把你想要的网站，说出来。
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-white/70">
        不需要会编程，也不需要先写需求。通过一次引导式对话，整理出属于你的个人网站方案与标准 PRD。
      </p>
      <button
        className="mt-8 rounded-full bg-white px-6 py-3 text-sm font-medium text-neutral-950"
        disabled={isStarting}
        onClick={onStart}
      >
        {isStarting ? "正在开始..." : "开始梳理我的网站"}
      </button>
    </section>
  );
}
```

```tsx
// frontend/src/components/home/problem.tsx
export function ProblemSection() {
  return (
    <section className="bg-stone-100 px-6 py-20 text-neutral-900">
      <div className="mx-auto max-w-5xl space-y-6">
        <h2 className="text-3xl font-semibold">你知道自己需要网站，但不知道怎么把它说清楚。</h2>
        <ul className="space-y-3 text-base text-neutral-700">
          <li>你知道自己需要一个网站，但不知道应该做成什么样。</li>
          <li>你能看出哪些网站好看，但很难把审美偏好描述清楚。</li>
          <li>你不会写 PRD，也不知道怎么把需求交给 AI 或开发者继续实现。</li>
        </ul>
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/components/home/process.tsx
export function ProcessSection() {
  return (
    <section className="px-6 py-20">
      <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-3">
        <article><h3>1. 选择方向</h3><p>先选网站类型与风格参考，也可以跳过。</p></article>
        <article><h3>2. 梳理需求</h3><p>通过中文对话说明目标、内容、偏好与边界。</p></article>
        <article><h3>3. 获取结果</h3><p>系统输出可直接继续使用的摘要与完整 PRD。</p></article>
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/components/home/output-preview.tsx
export function OutputPreviewSection() {
  return (
    <section className="bg-stone-100 px-6 py-20 text-neutral-900">
      <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-2">
        <article className="rounded-3xl border border-neutral-200 bg-white p-6">
          <h3 className="text-xl font-semibold">网站需求摘要</h3>
          <p className="mt-3 text-sm text-neutral-600">快速确认网站类型、目标受众、视觉方向与核心模块。</p>
        </article>
        <article className="rounded-3xl border border-neutral-200 bg-white p-6">
          <h3 className="text-xl font-semibold">标准 PRD 文档</h3>
          <p className="mt-3 text-sm text-neutral-600">可继续交给 AI 或开发者使用的中文结构化需求文档。</p>
        </article>
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/components/home/final-cta.tsx
export function FinalCtaSection({ isStarting, onStart }: { isStarting: boolean; onStart: () => void }) {
  return (
    <section className="px-6 py-20">
      <button
        className="rounded-full bg-white px-6 py-3 text-sm font-medium text-neutral-950"
        disabled={isStarting}
        onClick={onStart}
      >
        {isStarting ? "正在开始..." : "开始梳理我的网站"}
      </button>
    </section>
  );
}
```

- [ ] **Step 4: 补齐全局样式 token**

```css
:root {
  --bg-dark: #09090b;
  --bg-light: #f5f3ef;
  --text-strong: #f8fafc;
  --text-soft: rgba(248, 250, 252, 0.72);
  --accent: #d8f36b;
}

body {
  background: var(--bg-dark);
  color: var(--text-strong);
}
```

- [ ] **Step 5: 跑测试并人工检查窄屏首屏**

Run:

```bash
cd frontend && npm test -- home-page.test.tsx
cd frontend && npm run dev
```

Expected:

- 首页测试通过
- 在手机宽度下，标题、副标题、CTA 单列布局清晰，无横向溢出

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: build mobile-first homepage"
```

## Task 8：实现需求梳理页移动端优先 UI 与前后端接线

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/lib/types.ts`
- Create: `frontend/src/components/intake/step-header.tsx`
- Create: `frontend/src/components/intake/template-selector.tsx`
- Create: `frontend/src/components/intake/style-selector.tsx`
- Create: `frontend/src/components/intake/chat-panel.tsx`
- Create: `frontend/src/components/intake/summary-panel.tsx`
- Create: `frontend/src/components/intake/attachment-panel.tsx`
- Create: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/app.tsx`
- Test: `frontend/src/test/session-page.test.tsx`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `frontend/src/test/mobile-states.test.tsx`

- [ ] **Step 1: 写失败的需求页布局测试**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("需求页展示步骤条与跳过入口", () => {
  render(
    <MemoryRouter initialEntries={["/session/demo-token"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByText(/模板/i)).toBeInTheDocument();
  expect(screen.getByText(/风格/i)).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /跳过/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: 写失败的首页到需求页流转测试**

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("首页点击开始后进入需求页", async () => {
  const user = userEvent.setup();

  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  await user.click(screen.getByRole("button", { name: /开始梳理我的网站/i }));
  expect(await screen.findByText(/模板/i)).toBeInTheDocument();
});
```

- [ ] **Step 3: 运行前端测试，确认失败**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx
```

Expected:

- 失败，因为需求页和 API 还未接线

- [ ] **Step 4: 实现 API 客户端，并从环境变量读取后端地址**

```ts
// frontend/src/lib/api.ts
const API_BASE = `${import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000"}/api`;

export async function createSession() {
  const response = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  if (!response.ok) throw new Error("创建会话失败");
  return response.json();
}

export async function getSession(token: string) {
  const response = await fetch(`${API_BASE}/sessions/${token}`);
  if (!response.ok) throw new Error("读取会话失败");
  return response.json();
}

export async function updateSession(token: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/sessions/${token}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("更新会话失败");
  return response.json();
}

export async function sendMessage(token: string, content: string) {
  const response = await fetch(`${API_BASE}/sessions/${token}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  return response.json();
}

export async function uploadAttachment(token: string, file: File, caption: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("caption", caption);
  const response = await fetch(`${API_BASE}/sessions/${token}/attachments`, {
    method: "POST",
    body: form,
  });
  return response.json();
}

export async function getDocument(token: string) {
  const response = await fetch(`${API_BASE}/sessions/${token}/document`);
  return response.json();
}
```

- [ ] **Step 5: 为前端测试补 fetch mock**

```tsx
import { vi } from "vitest";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/sessions")) {
        return new Response(JSON.stringify({ token: "demo-token" }), { status: 201 });
      }
      if (url.includes("/sessions/demo-token") && init?.method === "PATCH") {
        const body = JSON.parse(String(init.body ?? "{}"));
        return new Response(
          JSON.stringify({
            token: "demo-token",
            current_stage: body.current_stage ?? "template",
            selected_template: body.selected_template ?? null,
            selected_style: body.selected_style ?? null,
          }),
          { status: 200 },
        );
      }
      if (url.includes("/sessions/demo-token/messages")) {
        return new Response(
          JSON.stringify({
            assistant_reply: "请继续告诉我你的网站主要给谁看。",
            current_stage: "positioning",
          }),
          { status: 201 },
        );
      }
      if (url.includes("/sessions/demo-token/attachments")) {
        return new Response(
          JSON.stringify({ file_name: "reference.png", caption: "参考图片" }),
          { status: 201 },
        );
      }
      if (url.includes("/sessions/demo-token/document")) {
        return new Response(JSON.stringify({ status: "ready", summary_text: "网站类型：个人作品页" }), { status: 200 });
      }
      if (url.includes("/sessions/demo-token")) {
        return new Response(
          JSON.stringify({ status: "draft", current_stage: "template", summary: { payload: {} } }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({}), { status: 200 });
    }),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});
```

- [ ] **Step 6: 实现需求页布局与轮询参数**

```tsx
// frontend/src/routes/session-page.tsx
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getDocument, getSession, sendMessage, updateSession, uploadAttachment } from "../lib/api";
import { StepHeader } from "../components/intake/step-header";
import { TemplateSelector } from "../components/intake/template-selector";
import { StyleSelector } from "../components/intake/style-selector";
import { ChatPanel } from "../components/intake/chat-panel";
import { SummaryPanel } from "../components/intake/summary-panel";
import { AttachmentPanel } from "../components/intake/attachment-panel";

export function SessionPage({ initialState }: { initialState?: { status: string; queuePosition?: number } }) {
  const { token = "" } = useParams();
  const [session, setSession] = useState<any>(initialState ?? null);
  const [documentState, setDocumentState] = useState<any>(null);
  const [messages, setMessages] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
  const [draft, setDraft] = useState("");
  const [attachments, setAttachments] = useState<Array<{ fileName: string; caption: string }>>([]);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const payload = await getSession(token);
      if (!cancelled) setSession(payload);
    }

    load();
    const timer = window.setInterval(load, 3000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [token]);

  useEffect(() => {
    if (!session || session.status !== "generating_document") return;
    let cancelled = false;

    async function pollDocument() {
      const payload = await getDocument(token);
      if (!cancelled) setDocumentState(payload);
    }

    pollDocument();
    const timer = window.setInterval(pollDocument, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [session, token]);

  if (session?.status === "queued") {
    return (
      <main className="px-4 py-6">
        <p>当前正在为其他用户整理网站需求，你已进入等待队列。</p>
        <p>你前面还有 {session.queuePosition} 人。</p>
      </main>
    );
  }

  if (!session) {
    return <main className="px-4 py-6">正在加载...</main>;
  }

  async function handleTemplateSelect(value: string) {
    const nextStage = "style";
    const payload = await updateSession(token, {
      selected_template: value === "跳过" ? null : value,
      current_stage: nextStage,
    });
    setSession((current: any) => ({ ...current, ...payload }));
  }

  async function handleStyleSelect(value: string) {
    const nextStage = "positioning";
    const payload = await updateSession(token, {
      selected_style: value === "跳过" ? null : value,
      current_stage: nextStage,
    });
    setSession((current: any) => ({ ...current, ...payload }));
  }

  async function handleSend() {
    if (!draft.trim()) return;
    const userContent = draft;
    setMessages((current) => [...current, { role: "user", content: userContent }]);
    setDraft("");
    const payload = await sendMessage(token, userContent);
    setMessages((current) => [...current, { role: "assistant", content: payload.assistant_reply }]);
    setSession((current: any) => ({ ...current, current_stage: payload.current_stage }));
  }

  async function handleUpload(file: File) {
    const payload = await uploadAttachment(token, file, "参考图片");
    setAttachments((current) => [...current, { fileName: payload.file_name, caption: payload.caption }]);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-6xl px-4 py-4">
        <StepHeader currentStage={session.current_stage ?? "template"} />
        <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="space-y-4">
            <TemplateSelector onSelect={handleTemplateSelect} onSkip={() => handleTemplateSelect("跳过")} />
            <StyleSelector onSelect={handleStyleSelect} onSkip={() => handleStyleSelect("跳过")} />
            <ChatPanel messages={messages} draft={draft} onDraftChange={setDraft} onSend={handleSend} />
            <AttachmentPanel attachments={attachments} onUpload={handleUpload} />
          </div>
          <SummaryPanel session={session} summaryPayload={session.summary?.payload} documentState={documentState} />
        </div>
      </div>
    </main>
  );
}
```

- [ ] **Step 7: 给需求页组件最小可用实现**

```tsx
// frontend/src/components/intake/step-header.tsx
export function StepHeader({ currentStage }: { currentStage: string }) {
  return (
    <header className="sticky top-0 z-10 rounded-3xl border border-white/10 bg-neutral-950/90 px-4 py-3 backdrop-blur">
      <ol className="flex gap-2 overflow-x-auto text-sm">
        <li>模板</li>
        <li>风格</li>
        <li>定位</li>
        <li>内容</li>
        <li>功能</li>
        <li>生成</li>
      </ol>
      <p className="mt-2 text-xs text-white/60">当前阶段：{currentStage}</p>
    </header>
  );
}
```

```tsx
// frontend/src/components/intake/template-selector.tsx
const TEMPLATE_OPTIONS = [
  "个人作品页",
  "个人简历页",
  "个人品牌页",
  "服务介绍页",
  "公司介绍页",
  "预约/咨询型主页",
];

export function TemplateSelector({ onSelect, onSkip }: { onSelect: (value: string) => void; onSkip: () => void }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h2>模板</h2>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        {TEMPLATE_OPTIONS.map((option) => (
          <button
            key={option}
            className="rounded-2xl border border-white/10 px-4 py-4 text-left"
            onClick={() => onSelect(option)}
          >
            {option}
          </button>
        ))}
      </div>
      <button className="mt-3 rounded-full border border-white/20 px-4 py-2" onClick={onSkip}>跳过</button>
    </section>
  );
}
```

```tsx
// frontend/src/components/intake/style-selector.tsx
const STYLE_OPTIONS = ["极简高级", "现代专业", "强视觉作品集", "温和可信", "前卫未来感"];

export function StyleSelector({ onSelect, onSkip }: { onSelect: (value: string) => void; onSkip: () => void }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h2>风格</h2>
      <div className="mt-3 grid gap-3">
        {STYLE_OPTIONS.map((option) => (
          <button
            key={option}
            className="rounded-2xl border border-white/10 px-4 py-4 text-left"
            onClick={() => onSelect(option)}
          >
            {option}
          </button>
        ))}
      </div>
      <button className="mt-3 rounded-full border border-white/20 px-4 py-2" onClick={onSkip}>跳过</button>
    </section>
  );
}
```

```tsx
// frontend/src/components/intake/chat-panel.tsx
export function ChatPanel({
  messages,
  draft,
  onDraftChange,
  onSend,
}: {
  messages: Array<{ role: "user" | "assistant"; content: string }>;
  draft: string;
  onDraftChange: (value: string) => void;
  onSend: () => void;
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h2>需求对话</h2>
      <div className="mt-4 space-y-3">
        {messages.map((message, index) => (
          <div key={index} className="rounded-2xl bg-black/20 p-3">
            <p className="text-xs text-white/50">{message.role === "user" ? "你" : "助手"}</p>
            <p className="mt-1 text-sm">{message.content}</p>
          </div>
        ))}
      </div>
      <textarea
        className="mt-4 min-h-28 w-full rounded-2xl border border-white/10 bg-black/20 p-3"
        value={draft}
        onChange={(event) => onDraftChange(event.target.value)}
        placeholder="用中文描述你的网站目标、内容和风格偏好"
      />
      <button className="mt-3 rounded-full bg-white px-4 py-2 text-neutral-950" onClick={onSend}>
        发送
      </button>
    </section>
  );
}
```

```tsx
// frontend/src/components/intake/attachment-panel.tsx
export function AttachmentPanel({
  attachments,
  onUpload,
}: {
  attachments: Array<{ fileName: string; caption: string }>;
  onUpload: (file: File) => void;
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h2>图片附件</h2>
      <input
        className="mt-3 block w-full text-sm"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onUpload(file);
        }}
      />
      <div className="mt-3 space-y-2">
        {attachments.map((item) => (
          <div key={item.fileName} className="rounded-2xl bg-black/20 p-3 text-sm">
            {item.fileName} {item.caption ? `- ${item.caption}` : ""}
          </div>
        ))}
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/components/intake/summary-panel.tsx
export function SummaryPanel({
  session,
  summaryPayload,
  documentState,
}: {
  session: any;
  summaryPayload: any;
  documentState: any;
}) {
  return (
    <aside className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h2>摘要</h2>
      <p>当前状态：{session.status}</p>
      <p>当前阶段：{session.current_stage}</p>
      <dl className="mt-3 space-y-2 text-sm">
        <div><dt>网站类型</dt><dd>{summaryPayload?.website_type ?? "未确定"}</dd></div>
        <div><dt>视觉方向</dt><dd>{summaryPayload?.visual_direction ?? "未确定"}</dd></div>
        <div><dt>目标受众</dt><dd>{summaryPayload?.audience ?? "未确定"}</dd></div>
      </dl>
      {documentState?.summary_text ? <pre>{documentState.summary_text}</pre> : null}
    </aside>
  );
}
```

- [ ] **Step 8: 补充移动端状态测试**

```tsx
import { render, screen } from "@testing-library/react";
import { SessionPage } from "../routes/session-page";

test("排队用户能看到等待文案", () => {
  render(<SessionPage initialState={{ status: "queued", queuePosition: 1 }} />);

  expect(screen.getByText(/当前正在为其他用户整理网站需求/i)).toBeInTheDocument();
  expect(screen.getByText(/你前面还有 1 人/i)).toBeInTheDocument();
});
```

- [ ] **Step 9: 运行前端测试并做一次手工联调**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx
cd backend && python run.py
cd frontend && npm run dev
```

Expected:

- 首页点击后可进入真实 token 路由
- 需求页在手机视口下无横向滚动
- 排队和生成状态有明确中文反馈

- [ ] **Step 10: Commit**

```bash
git add frontend
git commit -m "feat: wire mobile-first intake flow"
```

## Task 9：最终文档、回归验证与人工验收清单

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- Test: 仓库级验证

- [ ] **Step 1: 在 README 中写明开发启动方式**

````md
# zzetzMain

## 前端

```bash
cd frontend
npm install
npm run dev
```

## 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
python run.py
```
````

- [ ] **Step 2: 跑完整自动化验证**

Run:

```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
```

Expected:

- 后端测试全通过
- 前端测试全通过
- 前端生产构建成功

- [ ] **Step 3: 执行一条完整人工验收链路**

Run:

```text
1. 打开首页，确认首屏 CTA 在手机视口下可见
2. 点击“开始梳理我的网站”，确认出现 loading 态后跳转到 /session/:token
3. 在模板阶段选择“个人作品页”
4. 在风格阶段选择“极简高级”
5. 输入中文定位信息，例如“我是插画师，想展示作品并让客户联系我”
6. 上传一张 PNG 参考图
7. 继续补充内容与功能信息，直到进入生成阶段
8. 确认页面出现“正在生成 PRD”
9. 确认最终能看到中文摘要
10. 确认文档接口返回中文 PRD，且附件列表被写入
11. 复制 token，再次打开对应链接，确认会话内容仍可读取
```

Expected:

- 整条链路能跑通，且中文输出与移动端体验符合 spec

- [ ] **Step 4: 若实现与 spec 中的状态名或字段名不一致，立即回写 spec**

```md
- 例如如果 `current_stage` 被改名或轮询时间被调整，需要同步更新 spec。
```

- [ ] **Step 5: Commit**

```bash
git add README.md docs/superpowers/specs frontend backend
git commit -m "docs: finalize mvp validation checklist"
```

## 自检

### 规格覆盖

- 首页定位、视觉方向、移动端优先由 Task 7 覆盖。
- 模板、风格、阶段化引导、跳过逻辑由 Task 4 与 Task 8 覆盖。
- 真实 LLM、中文 prompt、摘要提取与 PRD 生成由 Task 3、Task 4、Task 5 覆盖。
- token、回访、图片上传、安全约束由 Task 2 与 Task 6 覆盖。
- 5 会话并发与排队、轮询状态和中文提示由 Task 5 与 Task 8 覆盖。
- CORS、移动端状态与完整验收链路由 Task 2、Task 8、Task 9 覆盖。

### 占位检查

- 没有 `TBD`、`TODO`、`implement later` 这类占位词。
- 每个任务都给出了明确文件、命令、预期结果与提交点。

### 一致性检查

- 当前状态名统一使用 `draft`、`queued`、`active`、`generating_document`、`completed`、`failed`。
- 路由统一放在 `/api/sessions/...` 下。
- 输出统一为简体中文摘要与简体中文 PRD。
