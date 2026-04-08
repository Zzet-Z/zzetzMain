# Personal Website MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a mobile-first MVP with a premium marketing homepage and a guided intake flow that turns a non-technical user's website idea into a summary and Markdown PRD.

**Architecture:** Use a monorepo with a React + Tailwind frontend and a Flask + SQLite backend. The backend owns session tokens, message persistence, attachments, a 5-slot queue, structured summary snapshots, and PRD generation; the frontend owns the mobile-first homepage and intake experience, using polling first for queue and generation state.

**Tech Stack:** React, TypeScript, Vite, Tailwind CSS, Vitest, Flask, SQLAlchemy, SQLite, pytest

---

## File Structure

### Repository Layout

- Create: `frontend/package.json` for the React app scripts and frontend dependencies
- Create: `frontend/tsconfig.json` for TypeScript settings
- Create: `frontend/vite.config.ts` for Vite configuration
- Create: `frontend/postcss.config.js` for Tailwind PostCSS integration
- Create: `frontend/tailwind.config.ts` for Tailwind theme tokens
- Create: `frontend/index.html` for Vite entry HTML
- Create: `frontend/src/main.tsx` for React bootstrapping
- Create: `frontend/src/app.tsx` for the route shell
- Create: `frontend/src/styles.css` for global styles and design tokens
- Create: `frontend/src/lib/api.ts` for HTTP accessors
- Create: `frontend/src/lib/types.ts` for frontend data contracts
- Create: `frontend/src/routes/home-page.tsx` for the homepage
- Create: `frontend/src/routes/session-page.tsx` for the session route
- Create: `frontend/src/components/home/hero.tsx` for the homepage hero
- Create: `frontend/src/components/home/problem.tsx` for the problem framing section
- Create: `frontend/src/components/home/process.tsx` for the three-step process section
- Create: `frontend/src/components/home/output-preview.tsx` for the summary and PRD output showcase
- Create: `frontend/src/components/home/final-cta.tsx` for the final conversion section
- Create: `frontend/src/components/intake/step-header.tsx` for the sticky step navigation
- Create: `frontend/src/components/intake/template-selector.tsx` for business template cards
- Create: `frontend/src/components/intake/style-selector.tsx` for style preview cards
- Create: `frontend/src/components/intake/chat-panel.tsx` for the guided chat block
- Create: `frontend/src/components/intake/summary-panel.tsx` for the summary drawer or sidebar
- Create: `frontend/src/components/intake/attachment-panel.tsx` for file upload and preview
- Create: `frontend/src/components/ui/button.tsx` for shared CTA styling
- Create: `frontend/src/fixtures/template-options.ts` for local template fixtures
- Create: `frontend/src/fixtures/style-preview-options.ts` for local style fixtures
- Create: `frontend/src/test/app-shell.test.tsx` for app shell coverage
- Create: `frontend/src/test/home-page.test.tsx` for homepage coverage
- Create: `frontend/src/test/session-page.test.tsx` for intake layout coverage
- Create: `frontend/src/test/session-flow.test.tsx` for API-wired navigation coverage
- Create: `frontend/src/test/mobile-states.test.tsx` for mobile and queued states
- Create: `backend/pyproject.toml` for backend dependencies and pytest config
- Create: `backend/app/__init__.py` for Flask app factory
- Create: `backend/app/config.py` for settings
- Create: `backend/app/db.py` for SQLAlchemy setup
- Create: `backend/app/models.py` for sessions, messages, attachments, summaries, and documents
- Create: `backend/app/schemas.py` for API payload schemas
- Create: `backend/app/routes/health.py` for a basic health endpoint
- Create: `backend/app/routes/sessions.py` for session create/read/update endpoints
- Create: `backend/app/routes/messages.py` for chat turn creation and retrieval
- Create: `backend/app/routes/uploads.py` for image upload metadata handling
- Create: `backend/app/routes/documents.py` for summary and PRD retrieval
- Create: `backend/app/services/template_catalog.py` for business templates and style reference definitions
- Create: `backend/app/services/summary_builder.py` for structured summary updates
- Create: `backend/app/services/document_renderer.py` for Markdown PRD rendering
- Create: `backend/app/services/queue_manager.py` for 5-slot queue orchestration
- Create: `backend/app/services/storage.py` for attachment file paths
- Create: `backend/app/services/intake_engine.py` for prompt-stage logic and mock assistant turns
- Create: `backend/app/worker.py` for background job execution
- Create: `backend/run.py` for local development startup
- Create: `backend/tests/test_health.py` for health endpoint coverage
- Create: `backend/tests/test_sessions_api.py` for session lifecycle coverage
- Create: `backend/tests/test_queue_and_generation.py` for queueing and document generation coverage
- Create: `backend/tests/test_uploads_api.py` for attachment upload coverage
- Create: `README.md` for local setup and repository overview

### Target Boundaries

- The frontend should remain a single responsive app rather than separate desktop and mobile implementations.
- The backend should stay monolithic, but queue logic, PRD rendering, and summary updates must be isolated in services.
- Polling is acceptable for MVP status updates. Do not introduce websockets in the first implementation pass.
- Attachment uploads should use the local filesystem through a storage service abstraction so later migration is cheap.

### Task 1: Scaffold Repository And Tooling

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
- Create: `backend/app/db.py`
- Create: `backend/app/routes/health.py`
- Create: `README.md`
- Test: `frontend/src/test/app-shell.test.tsx`
- Test: `backend/tests/test_health.py`

- [ ] **Step 1: Write the failing backend health test**

```python
from app import create_app


def test_healthcheck_returns_ok():
    app = create_app({"TESTING": True, "DATABASE_URL": "sqlite:///:memory:"})
    client = app.test_client()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}
```

- [ ] **Step 2: Write the failing frontend shell test**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("renders the homepage route shell", () => {
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

- [ ] **Step 3: Run the tests to verify both fail**

Run:

```bash
cd backend && pytest tests/test_health.py -q
cd frontend && npm test -- app-shell.test.tsx
```

Expected:

- Backend fails because `create_app` and `/api/health` do not exist
- Frontend fails because the Vite app and `App` component do not exist

- [ ] **Step 4: Create the minimum backend scaffold**

```python
# backend/app/__init__.py
from flask import Flask


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL="sqlite:///app.db",
        UPLOAD_DIR="uploads",
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

- [ ] **Step 5: Create the minimum frontend scaffold**

```tsx
// frontend/src/app.tsx
import { Routes, Route } from "react-router-dom";

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
  font-family: ui-sans-serif, system-ui, sans-serif;
}
```

- [ ] **Step 6: Add the project manifests**

```json
// frontend/package.json
{
  "name": "personal-website-mvp-frontend",
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
name = "personal-website-mvp-backend"
version = "0.0.1"
dependencies = [
  "Flask>=3.1.0",
  "SQLAlchemy>=2.0.40",
  "pytest>=8.3.5",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 7: Run the tests to verify they pass**

Run:

```bash
cd backend && pytest tests/test_health.py -q
cd frontend && npm test -- app-shell.test.tsx
```

Expected:

- Backend test passes with `1 passed`
- Frontend test passes with `1 passed`

- [ ] **Step 8: Commit**

```bash
git add README.md backend frontend
git commit -m "chore: scaffold frontend and backend apps"
```

### Task 2: Implement Backend Data Model And Session APIs

**Files:**
- Modify: `backend/app/__init__.py`
- Modify: `backend/app/db.py`
- Create: `backend/app/models.py`
- Create: `backend/app/schemas.py`
- Create: `backend/app/routes/sessions.py`
- Create: `backend/app/services/template_catalog.py`
- Test: `backend/tests/test_sessions_api.py`

- [ ] **Step 1: Write the failing session API test**

```python
from app import create_app


def test_create_session_returns_token_and_defaults(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{db_path}",
            "UPLOAD_DIR": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()

    response = client.post("/api/sessions")
    payload = response.get_json()

    assert response.status_code == 201
    assert payload["status"] == "draft"
    assert payload["selected_template"] is None
    assert payload["selected_style"] is None
    assert len(payload["token"]) >= 20
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_defaults -q
```

Expected:

- FAIL because `/api/sessions` does not exist

- [ ] **Step 3: Implement database setup and models**

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
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class SessionRecord(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    selected_template: Mapped[str | None] = mapped_column(String(64), nullable=True)
    selected_style: Mapped[str | None] = mapped_column(String(64), nullable=True)
    queue_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class SummarySnapshot(Base):
    __tablename__ = "summary_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    summary_text: Mapped[str] = mapped_column(Text, default="")
    prd_markdown: Mapped[str] = mapped_column(Text, default="")
```

- [ ] **Step 4: Implement the session route**

```python
# backend/app/routes/sessions.py
from secrets import token_urlsafe
from flask import Blueprint, jsonify
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
                "token": token,
                "status": record.status,
                "selected_template": record.selected_template,
                "selected_style": record.selected_style,
            }
        ),
        201,
    )
```

```python
# backend/app/__init__.py
from flask import Flask
from .db import init_db


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE_URL="sqlite:///app.db",
        UPLOAD_DIR="uploads",
    )
    if config_overrides:
        app.config.update(config_overrides)

    init_db(app.config["DATABASE_URL"])

    from .routes.health import health_bp
    from .routes.sessions import sessions_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(sessions_bp, url_prefix="/api")
    return app
```

- [ ] **Step 5: Run the session API test to verify it passes**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_defaults -q
```

Expected:

- PASS with `1 passed`

- [ ] **Step 6: Add a retrieval test and implementation for session details**

```python
def test_get_session_returns_summary_and_document_state(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    created = client.post("/api/sessions").get_json()
    response = client.get(f"/api/sessions/{created['token']}")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["token"] == created["token"]
    assert payload["summary"]["payload"] == {}
    assert payload["document"]["status"] == "pending"
```

```python
@sessions_bp.get("/sessions/<token>")
def get_session(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    return jsonify(
        {
            "token": session.token,
            "status": session.status,
            "selected_template": session.selected_template,
            "selected_style": session.selected_style,
            "summary": {"payload": summary.payload},
            "document": {"status": document.status},
        }
    )
```

- [ ] **Step 7: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add session persistence and api"
```

### Task 3: Implement Queue, Messages, Summary Updates, And PRD Rendering

**Files:**
- Create: `backend/app/routes/messages.py`
- Create: `backend/app/routes/documents.py`
- Create: `backend/app/services/summary_builder.py`
- Create: `backend/app/services/document_renderer.py`
- Create: `backend/app/services/queue_manager.py`
- Create: `backend/app/services/intake_engine.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_queue_and_generation.py`

- [ ] **Step 1: Write the failing queue test**

```python
from app import create_app


def test_sixth_session_is_queued_when_five_are_active(tmp_path):
    db_path = tmp_path / "queue.db"
    app = create_app({"TESTING": True, "DATABASE_URL": f"sqlite:///{db_path}"})
    client = app.test_client()

    tokens = [client.post("/api/sessions").get_json()["token"] for _ in range(6)]

    for token in tokens[:5]:
      client.post(f"/api/sessions/{token}/messages", json={"content": "I need a personal site"})

    response = client.post(
        f"/api/sessions/{tokens[5]}/messages",
        json={"content": "I need a company intro site"},
    )
    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "queued"
    assert payload["queue_position"] == 1
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_queue_and_generation.py::test_sixth_session_is_queued_when_five_are_active -q
```

Expected:

- FAIL because the messages route and queue service do not exist

- [ ] **Step 3: Add message and attachment models**

```python
class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AttachmentRecord(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    file_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(64))
    caption: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

- [ ] **Step 4: Implement queue and summary services**

```python
# backend/app/services/queue_manager.py
from ..db import SessionLocal
from ..models import SessionRecord

ACTIVE_LIMIT = 5


def reserve_slot(token: str) -> tuple[str, int | None]:
    db = SessionLocal()
    active_count = (
        db.query(SessionRecord)
        .filter(SessionRecord.status.in_(["active", "generating_document"]))
        .count()
    )
    session = db.get(SessionRecord, token)
    if active_count >= ACTIVE_LIMIT:
        queued = (
            db.query(SessionRecord)
            .filter(SessionRecord.status == "queued")
            .count()
        )
        session.status = "queued"
        session.queue_position = queued + 1
        db.commit()
        return session.status, session.queue_position

    session.status = "active"
    session.queue_position = None
    db.commit()
    return session.status, None
```

```python
# backend/app/services/summary_builder.py
def update_summary(existing: dict, user_message: str) -> dict:
    payload = dict(existing)
    notes = payload.get("notes", [])
    notes.append(user_message)
    payload["notes"] = notes[-6:]
    payload.setdefault("website_type", None)
    payload.setdefault("visual_direction", None)
    payload.setdefault("content_modules", [])
    payload.setdefault("features", [])
    return payload
```

```python
# backend/app/services/document_renderer.py
def render_summary(payload: dict) -> str:
    website_type = payload.get("website_type") or "未指定"
    visual_direction = payload.get("visual_direction") or "未指定"
    return f"网站类型：{website_type}\n视觉方向：{visual_direction}"


def render_prd(payload: dict, attachments: list[dict]) -> str:
    lines = [
        "# Website PRD",
        "",
        f"- 网站类型：{payload.get('website_type') or '未指定'}",
        f"- 视觉方向：{payload.get('visual_direction') or '未指定'}",
        "",
        "## 内容模块",
    ]
    for item in payload.get("content_modules", []):
        lines.append(f"- {item}")
    lines.extend(["", "## 附件"])
    for item in attachments:
        lines.append(f"- {item['file_name']}: {item['caption']}")
    return "\n".join(lines)
```

- [ ] **Step 5: Implement the messages route with a mock intake engine**

```python
# backend/app/services/intake_engine.py
def generate_assistant_reply(content: str) -> str:
    return f"已收到：{content}"
```

```python
# backend/app/routes/messages.py
from flask import Blueprint, jsonify, request
from ..db import SessionLocal
from ..models import MessageRecord, SessionRecord, SummarySnapshot, DocumentRecord, AttachmentRecord
from ..services.document_renderer import render_prd, render_summary
from ..services.intake_engine import generate_assistant_reply
from ..services.queue_manager import reserve_slot
from ..services.summary_builder import update_summary

messages_bp = Blueprint("messages", __name__)


@messages_bp.post("/sessions/<token>/messages")
def create_message(token: str):
    db = SessionLocal()
    session = db.get(SessionRecord, token)
    status, queue_position = reserve_slot(token)
    if status == "queued":
        return jsonify({"session_status": status, "queue_position": queue_position}), 202

    content = request.get_json()["content"]
    db.add(MessageRecord(session_token=token, role="user", content=content))
    reply = generate_assistant_reply(content)
    db.add(MessageRecord(session_token=token, role="assistant", content=reply))

    latest_summary = (
        db.query(SummarySnapshot)
        .filter(SummarySnapshot.session_token == token)
        .order_by(SummarySnapshot.id.desc())
        .first()
    )
    payload = update_summary(latest_summary.payload, content)
    db.add(SummarySnapshot(session_token=token, payload=payload))

    document = (
        db.query(DocumentRecord)
        .filter(DocumentRecord.session_token == token)
        .order_by(DocumentRecord.id.desc())
        .first()
    )
    attachments = [
        {"file_name": item.file_name, "caption": item.caption}
        for item in db.query(AttachmentRecord).filter(AttachmentRecord.session_token == token)
    ]
    document.summary_text = render_summary(payload)
    document.prd_markdown = render_prd(payload, attachments)
    document.status = "ready"
    session.status = "completed"
    db.commit()
    return jsonify({"session_status": "completed", "assistant_reply": reply}), 201
```

- [ ] **Step 6: Add document retrieval route**

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

- [ ] **Step 7: Run the queue test and add a generation test**

Run:

```bash
cd backend && pytest tests/test_queue_and_generation.py -q
```

Expected:

- PASS for the queueing behavior
- PASS for a second test that verifies a completed session exposes a non-empty `summary_text` and `prd_markdown`

- [ ] **Step 8: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add intake queue and prd generation"
```

### Task 4: Implement Uploads And Attachment Listing

**Files:**
- Create: `backend/app/routes/uploads.py`
- Create: `backend/app/services/storage.py`
- Modify: `backend/app/__init__.py`
- Test: `backend/tests/test_uploads_api.py`

- [ ] **Step 1: Write the failing upload test**

```python
from io import BytesIO
from app import create_app


def test_upload_creates_attachment_record(tmp_path):
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
    assert payload["caption"] == "首页参考"
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd backend && pytest tests/test_uploads_api.py::test_upload_creates_attachment_record -q
```

Expected:

- FAIL because the uploads route does not exist

- [ ] **Step 3: Implement storage and uploads**

```python
# backend/app/services/storage.py
from pathlib import Path
from werkzeug.utils import secure_filename


def save_upload(upload_dir: str, token: str, file_storage) -> tuple[str, str]:
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
    file_name, file_path = save_upload(current_app.config["UPLOAD_DIR"], token, file_storage)

    db = SessionLocal()
    record = AttachmentRecord(
        session_token=token,
        file_name=file_name,
        file_path=file_path,
        mime_type=file_storage.mimetype or "application/octet-stream",
        caption=caption,
    )
    db.add(record)
    db.commit()
    return jsonify({"file_name": file_name, "caption": caption, "file_path": file_path}), 201
```

- [ ] **Step 4: Register the uploads blueprint and run the upload test**

```python
# backend/app/__init__.py
from .routes.uploads import uploads_bp

app.register_blueprint(uploads_bp, url_prefix="/api")
```

Run:

```bash
cd backend && pytest tests/test_uploads_api.py -q
```

Expected:

- PASS with attachment files written under the configured upload directory

- [ ] **Step 5: Commit**

```bash
git add backend/app backend/tests
git commit -m "feat: add session attachment uploads"
```

### Task 5: Build The Homepage UI Mobile-First

**Files:**
- Create: `frontend/src/lib/types.ts`
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

- [ ] **Step 1: Write the failing homepage mobile test**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("homepage exposes the primary mobile CTA", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole("link", { name: /开始梳理我的网站/i })).toBeInTheDocument();
  expect(screen.getByText(/不需要会编程，也不需要先写需求/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd frontend && npm test -- home-page.test.tsx
```

Expected:

- FAIL because the homepage sections and CTA button do not exist

- [ ] **Step 3: Implement the homepage route and sections**

```tsx
// frontend/src/routes/home-page.tsx
import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <main className="bg-neutral-950 text-white">
      <section className="mx-auto flex min-h-screen max-w-6xl flex-col justify-center px-6 py-16">
        <p className="text-sm uppercase tracking-[0.3em] text-white/60">No-code personal website brief</p>
        <h1 className="mt-6 max-w-4xl text-5xl font-semibold leading-tight sm:text-7xl">
          把你想要的网站，说出来。
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-white/72">
          不需要会编程，也不需要先写需求。通过一次引导式对话，整理出属于你的个人网站方案与标准 PRD。
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Link className="rounded-full bg-white px-6 py-3 text-center text-sm font-medium text-neutral-950" to="/session/new">
            开始梳理我的网站
          </Link>
          <a className="rounded-full border border-white/20 px-6 py-3 text-center text-sm font-medium text-white" href="#how-it-works">
            先看看它是怎么工作的
          </a>
        </div>
      </section>
    </main>
  );
}
```

```tsx
// frontend/src/app.tsx
import { Routes, Route } from "react-router-dom";
import { HomePage } from "./routes/home-page";

export function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/session/:token" element={<div>Session Page</div>} />
    </Routes>
  );
}
```

- [ ] **Step 4: Expand the homepage into the final five-section structure**

```tsx
// Sketch of final section composition inside HomePage
<>
  <Hero />
  <ProblemSection />
  <ProcessSection id="how-it-works" />
  <OutputPreviewSection />
  <FinalCtaSection />
</>
```

```css
/* frontend/src/styles.css */
:root {
  --bg-dark: #09090b;
  --bg-light: #f5f3ef;
  --text-strong: #f9fafb;
  --text-soft: rgba(249, 250, 251, 0.72);
  --accent: #d6f36a;
}

body {
  background: var(--bg-dark);
  color: var(--text-strong);
}
```

- [ ] **Step 5: Run the homepage test and visually verify mobile stacking**

Run:

```bash
cd frontend && npm test -- home-page.test.tsx
cd frontend && npm run dev
```

Expected:

- Test passes
- On a narrow viewport, the hero headline, subheadline, and CTA appear in a single clear column without horizontal overflow

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: build mobile-first marketing homepage"
```

### Task 6: Build The Intake UI Mobile-First

**Files:**
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/components/intake/step-header.tsx`
- Create: `frontend/src/components/intake/template-selector.tsx`
- Create: `frontend/src/components/intake/style-selector.tsx`
- Create: `frontend/src/components/intake/chat-panel.tsx`
- Create: `frontend/src/components/intake/summary-panel.tsx`
- Create: `frontend/src/components/intake/attachment-panel.tsx`
- Create: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/app.tsx`
- Test: `frontend/src/test/session-page.test.tsx`

- [ ] **Step 1: Write the failing intake route test**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("session page shows template and style steps", () => {
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

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx
```

Expected:

- FAIL because the real session page does not exist

- [ ] **Step 3: Implement the static intake layout**

```tsx
// frontend/src/routes/session-page.tsx
export function SessionPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white">
      <div className="mx-auto max-w-6xl px-4 py-4">
        <header className="sticky top-0 z-10 rounded-3xl border border-white/10 bg-neutral-950/90 px-4 py-3 backdrop-blur">
          <ol className="flex gap-2 overflow-x-auto text-sm">
            <li>模板</li>
            <li>风格</li>
            <li>定位</li>
            <li>内容</li>
            <li>功能</li>
            <li>生成</li>
          </ol>
        </header>
        <section className="mt-4 grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-4">
            <button className="rounded-full border border-white/20 px-4 py-2">跳过</button>
          </div>
          <aside className="rounded-3xl border border-white/10 bg-white/5 p-4">摘要</aside>
        </section>
      </div>
    </main>
  );
}
```

- [ ] **Step 4: Add the mobile-first interactive sections**

```tsx
// final composition inside SessionPage
<>
  <StepHeader currentStep="template" />
  <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_360px]">
    <div className="space-y-4">
      <TemplateSelector />
      <StyleSelector />
      <ChatPanel />
      <AttachmentPanel />
    </div>
    <SummaryPanel />
  </div>
</>
```

The mobile behavior must be:

- Template cards scroll vertically
- Style cards remain legible in a single column
- Summary panel becomes collapsible below the chat block
- Input area remains visible above the software keyboard

- [ ] **Step 5: Run the intake test and verify mobile behavior**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx
cd frontend && npm run dev
```

Expected:

- Test passes
- On a phone viewport, template cards, style cards, chat input, upload area, and summary panel remain usable without horizontal scrolling

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: add mobile-first intake flow ui"
```

### Task 7: Connect Frontend To Backend Session, Upload, And Document APIs

**Files:**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/routes/home-page.tsx`
- Modify: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/lib/types.ts`
- Test: `frontend/src/test/session-flow.test.tsx`

- [ ] **Step 1: Write the failing integration-style frontend test**

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { App } from "../app";

test("starting from the homepage creates a session and lands on the intake route", async () => {
  const user = userEvent.setup();

  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  await user.click(screen.getByRole("link", { name: /开始梳理我的网站/i }));

  expect(await screen.findByText(/模板/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd frontend && npm test -- session-flow.test.tsx
```

Expected:

- FAIL because the homepage CTA still links to a placeholder route and no API-backed navigation exists

- [ ] **Step 3: Implement the API client and CTA bootstrap**

```ts
// frontend/src/lib/api.ts
const API_BASE = "http://127.0.0.1:5000/api";

export async function createSession() {
  const response = await fetch(`${API_BASE}/sessions`, { method: "POST" });
  if (!response.ok) throw new Error("Failed to create session");
  return response.json();
}

export async function getSession(token: string) {
  const response = await fetch(`${API_BASE}/sessions/${token}`);
  if (!response.ok) throw new Error("Failed to load session");
  return response.json();
}
```

```tsx
// homepage CTA handler sketch
const navigate = useNavigate();

async function handleStart() {
  const session = await createSession();
  navigate(`/session/${session.token}`);
}
```

- [ ] **Step 4: Implement message submission, upload submission, and document retrieval**

```ts
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

- [ ] **Step 5: Run the frontend flow tests and a manual end-to-end smoke test**

Run:

```bash
cd frontend && npm test -- session-flow.test.tsx
cd backend && python run.py
cd frontend && npm run dev
```

Expected:

- Homepage CTA opens a real session
- Session page can load session state from token
- Message send returns a mock assistant reply
- Attachment upload succeeds
- Final document fetch returns non-empty summary and PRD text

- [ ] **Step 6: Commit**

```bash
git add frontend
git commit -m "feat: connect intake ui to backend apis"
```

### Task 8: Polish Mobile UX, Queue Messaging, And Empty States

**Files:**
- Modify: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/components/intake/step-header.tsx`
- Modify: `frontend/src/components/intake/template-selector.tsx`
- Modify: `frontend/src/components/intake/style-selector.tsx`
- Modify: `frontend/src/components/intake/chat-panel.tsx`
- Modify: `frontend/src/components/intake/summary-panel.tsx`
- Modify: `frontend/src/components/intake/attachment-panel.tsx`
- Modify: `backend/app/routes/messages.py`
- Test: `frontend/src/test/mobile-states.test.tsx`
- Test: `backend/tests/test_queue_and_generation.py`

- [ ] **Step 1: Write the failing queued-state frontend test**

```tsx
import { render, screen } from "@testing-library/react";
import { SessionPage } from "../routes/session-page";

test("queued users see a waiting message", () => {
  render(<SessionPage initialState={{ status: "queued", queuePosition: 1 }} />);

  expect(screen.getByText(/当前正在为其他用户整理网站需求/i)).toBeInTheDocument();
  expect(screen.getByText(/你前面还有 1 人/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
cd frontend && npm test -- mobile-states.test.tsx
```

Expected:

- FAIL because the queued message UI does not exist

- [ ] **Step 3: Add queue, loading, failure, and completion states**

```tsx
// state rendering sketch inside SessionPage
type SessionPageProps = {
  initialState?: { status: string; queuePosition?: number };
};

export function SessionPage({ initialState }: SessionPageProps) {
  const session = initialState ?? liveSessionState;

if (session.status === "queued") {
  return (
    <section>
      <p>当前正在为其他用户整理网站需求，你已进入等待队列。</p>
      <p>你前面还有 {session.queuePosition} 人。</p>
    </section>
  );
}

if (document.status === "ready") {
  return (
    <section>
      <h2>你的需求摘要已生成</h2>
      <pre>{document.summary_text}</pre>
    </section>
  );
}
}
```

- [ ] **Step 4: Update backend responses so queue and document states are explicit**

```python
return jsonify(
    {
        "session_status": "queued",
        "queue_position": queue_position,
        "message": "当前正在为其他用户整理网站需求，你已进入等待队列。",
    }
), 202
```

- [ ] **Step 5: Re-run backend and frontend tests**

Run:

```bash
cd backend && pytest tests/test_queue_and_generation.py -q
cd frontend && npm test -- mobile-states.test.tsx
```

Expected:

- Queueing tests still pass
- Mobile queued-state test passes

- [ ] **Step 6: Commit**

```bash
git add backend frontend
git commit -m "feat: polish queue and mobile state handling"
```

### Task 9: Final Repository Documentation And Validation

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- Test: repository-level smoke verification

- [ ] **Step 1: Add project setup instructions to README**

````md
# zzetzMain

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
python run.py
```
````

- [ ] **Step 2: Run full local verification**

Run:

```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
```

Expected:

- Backend test suite passes
- Frontend test suite passes
- Frontend production build succeeds

- [ ] **Step 3: Record any spec deltas directly in the spec if implementation changed terminology**

```md
- Update status names, route names, or schema labels in the spec if they diverged during implementation.
```

- [ ] **Step 4: Commit**

```bash
git add README.md docs/superpowers/specs frontend backend
git commit -m "docs: finalize mvp setup and validation notes"
```

## Self-Review

### Spec Coverage

- Homepage positioning, visual direction, and CTA flow are covered by Tasks 5 and 7.
- Intake template selection, style selection, chat flow, summary panel, and attachment handling are covered by Tasks 3, 4, 6, and 7.
- Session tokens, document output, and revisit behavior are covered by Tasks 2, 3, and 7.
- 5-slot queue handling and queued user messaging are covered by Tasks 3 and 8.
- Mobile-first behavior is covered by Tasks 5, 6, 7, and 8.

### Placeholder Scan

- No `TBD`, `TODO`, or vague "implement later" markers remain in task steps.
- Each task includes exact files, test commands, expected outcomes, and commit checkpoints.

### Type Consistency

- Session status names remain `draft`, `queued`, `active`, `generating_document`, `completed`, and `failed`.
- Frontend API methods align with backend route names under `/api/sessions/...`.
- The PRD output remains Markdown and is represented by `summary_text` and `prd_markdown` in both backend and frontend.
