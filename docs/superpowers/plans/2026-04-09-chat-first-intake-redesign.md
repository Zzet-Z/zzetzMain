# Chat-First Intake Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有阶段式需求梳理体验重构为受控 token 驱动的 ChatGPT 风格聊天产品，并补齐后台 token 管理、修订链、最终文档归档与移动端验收。

**Architecture:** 后端继续沿用 Flask + SQLite，但把当前 session 语义改为“管理员签发的一轮受控会话”，并新增轻状态会话生命周期、JSON envelope 对话协议、successor token 修订链和后台管理路由。前端继续沿用 React + Vite + Tailwind，首页保留五段式介绍但改为 token 入口，聊天页收敛为单窗口聊天界面，后台管理页作为独立路由接入同一应用。

**Tech Stack:** React, TypeScript, Vite, Tailwind CSS, Vitest, Flask, SQLAlchemy, SQLite, pytest

---

## 文件结构

### 后端

- Modify: `backend/app/config.py`
  - 增加 `ADMIN_TOKEN`、会话超时、token 失效与消息分页默认值配置
- Modify: `backend/app/models.py`
  - 将 `SessionRecord`、`MessageRecord`、`DocumentRecord` 调整到 chat-first 模型
- Modify: `backend/app/schemas.py`
  - 重新序列化 session、message、document、admin token 列表项
- Modify: `backend/app/__init__.py`
  - 注册新的 admin 路由
- Create: `backend/app/routes/admin.py`
  - 后台 token 签发、列表、详情、撤销接口
- Modify: `backend/app/routes/sessions.py`
  - 去掉匿名创建语义，改为按 token 读取元信息与消息窗口
- Modify: `backend/app/routes/messages.py`
  - 接入 JSON envelope、三次重试、ready-to-generate、successor token 返回
- Modify: `backend/app/routes/documents.py`
  - 返回修订链文档状态与内容
- Modify: `backend/app/routes/uploads.py`
  - 继续复用上传逻辑，但使用新 token 生命周期校验
- Create: `backend/app/services/session_lifecycle.py`
  - 统一处理 5 分钟资源释放、24 小时过期、successor token 创建
- Create: `backend/app/services/admin_auth.py`
  - 统一解析 `Authorization: Bearer <admin_token>`
- Modify: `backend/app/services/queue_manager.py`
  - 明确 `generating_document` 也占用并发槽位
- Modify: `backend/app/services/llm_orchestrator.py`
  - 改为 chat-first prompt、JSON envelope 解析、非 JSON fallback
- Modify: `backend/app/services/document_renderer.py`
  - 支持上一版文档上下文与修订链文档渲染
- Create: `backend/app/prompts/chat_system.md`
- Create: `backend/app/prompts/welcome_initial.md`
- Create: `backend/app/prompts/welcome_revision.md`
- Create: `backend/app/prompts/render_final_document.md`
- Test: `backend/tests/test_sessions_api.py`
- Test: `backend/tests/test_llm_orchestrator.py`
- Test: `backend/tests/test_queue_and_generation.py`
- Create: `backend/tests/test_admin_api.py`

### 前端

- Modify: `frontend/src/app.tsx`
  - 注册首页、聊天页、后台页
- Modify: `frontend/src/lib/types.ts`
  - 替换旧阶段类型，定义 chat-first payload 和 admin payload
- Modify: `frontend/src/lib/api.ts`
  - 增加 token 入口、消息分页、admin API
- Modify: `frontend/src/routes/home-page.tsx`
  - 移除匿名创建会话，改为 token 输入/跳转
- Modify: `frontend/src/routes/session-page.tsx`
  - 单窗口聊天页、typing 态、确认生成、completed 禁用
- Create: `frontend/src/routes/admin-page.tsx`
  - 管理员 token 输入、token 签发、列表、详情、撤销
- Create: `frontend/src/components/home/token-entry.tsx`
  - 首页 token 输入组件
- Modify: `frontend/src/components/intake/chat-panel.tsx`
  - 改成单窗口消息流 + 输入区 + 附件入口
- Modify: `frontend/src/components/intake/attachment-panel.tsx`
  - 收敛为输入区内的附件反馈子组件
- Create: `frontend/src/components/admin/token-list.tsx`
- Create: `frontend/src/components/admin/token-detail.tsx`
- Create: `frontend/src/components/admin/token-create-form.tsx`
- Test: `frontend/src/test/home-page.test.tsx`
- Test: `frontend/src/test/session-page.test.tsx`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `frontend/src/test/mobile-states.test.tsx`
- Create: `frontend/src/test/admin-page.test.tsx`

### 配置与文档

- Modify: `.env.example`
  - 新增 `ADMIN_TOKEN`
- Modify: `DOCUMENTATION.md`
  - 记录本轮重构的验证结果和风险
- Modify: `SESSION_CONTEXT.md`
  - 更新当前阶段与下一步

---

## Task 1: 重构后端数据模型与配置边界

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/models.py`
- Modify: `backend/app/schemas.py`
- Modify: `.env.example`
- Test: `backend/tests/test_sessions_api.py`

- [ ] **Step 1: 先写失败的模型与配置测试**

```python
from pathlib import Path

from app import create_app
from app.db import SessionLocal
from app.models import DocumentRecord, MessageRecord, SessionRecord


def test_session_record_uses_chat_first_fields(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": f"sqlite:///{tmp_path/'chat-first.db'}",
            "ADMIN_TOKEN": "admin-secret",
        }
    )

    with app.app_context():
        db = SessionLocal()
        session = SessionRecord(token="invite-token", status="awaiting_user")
        db.add(session)
        db.add(DocumentRecord(session_token="invite-token", revision_number=1))
        db.add(
            MessageRecord(
                session_token="invite-token",
                role="assistant",
                content="欢迎使用。",
                delivery_status="system",
            )
        )
        db.commit()

        saved = db.get(SessionRecord, "invite-token")

    assert saved.status == "awaiting_user"
    assert not hasattr(saved, "current_stage")
    assert saved.next_session_token is None
```

```python
def test_env_example_mentions_admin_token():
    content = Path(".env.example").read_text(encoding="utf-8")
    assert "ADMIN_TOKEN=" in content
```

- [ ] **Step 2: 运行测试，确认当前失败**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py::test_session_record_uses_chat_first_fields -q
pytest tests/test_sessions_api.py::test_env_example_mentions_admin_token -q
```

Expected:

- `SessionRecord` 仍保留旧 `current_stage` / `selected_template` 字段，无法满足新断言
- `.env.example` 中没有 `ADMIN_TOKEN`

- [ ] **Step 3: 写最小模型、配置与序列化实现**

```python
# backend/app/config.py
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
SESSION_IDLE_TIMEOUT_SECONDS = int(os.getenv("SESSION_IDLE_TIMEOUT_SECONDS", "300"))
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
SESSION_MESSAGES_PAGE_SIZE = int(os.getenv("SESSION_MESSAGES_PAGE_SIZE", "50"))
```

```python
# backend/app/models.py
class SessionRecord(Base):
    __tablename__ = "sessions"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), default="awaiting_user")
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    origin_session_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    previous_document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    next_session_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    queued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_user_message_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    active_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
```

```python
# backend/app/models.py
class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_token: Mapped[str] = mapped_column(ForeignKey("sessions.token"))
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    delivery_status: Mapped[str] = mapped_column(String(32), default="final")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
```

```python
# .env.example
ADMIN_TOKEN=your-admin-token-here
SESSION_IDLE_TIMEOUT_SECONDS=300
SESSION_EXPIRY_HOURS=24
SESSION_MESSAGES_PAGE_SIZE=50
```

- [ ] **Step 4: 运行测试，确认通过**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py::test_session_record_uses_chat_first_fields tests/test_sessions_api.py::test_env_example_mentions_admin_token -q
```

Expected:

- PASS

- [ ] **Step 5: 提交这一轮**

```bash
git add backend/app/config.py backend/app/models.py backend/app/schemas.py .env.example backend/tests/test_sessions_api.py
git commit -m "refactor: reshape chat session models"
```

## Task 2: 落地 chat-first prompt 与 JSON envelope 协议

**Files:**
- Create: `backend/app/prompts/chat_system.md`
- Create: `backend/app/prompts/welcome_initial.md`
- Create: `backend/app/prompts/welcome_revision.md`
- Create: `backend/app/prompts/render_final_document.md`
- Modify: `backend/app/services/llm_orchestrator.py`
- Modify: `backend/app/services/document_renderer.py`
- Test: `backend/tests/test_llm_orchestrator.py`

- [ ] **Step 1: 先写失败的 orchestrator 测试**

```python
class FakeClient:
    def __init__(self, text: str):
        self.text = text

    def generate(self, *, instructions: str, input_text: str, timeout: float):
        return type("Result", (), {"text": self.text})()


def test_generate_chat_reply_parses_ready_to_generate_envelope():
    client = FakeClient(
        '{"assistant_message":"信息已经足够，我可以整理最终需求文档。","conversation_intent":"ready_to_generate"}'
    )

    payload = generate_chat_reply(
        client,
        session_context={"previous_document": None},
        recent_messages=[{"role": "user", "content": "我已经把需求都说完了"}],
    )

    assert payload["assistant_message"] == "信息已经足够，我可以整理最终需求文档。"
    assert payload["conversation_intent"] == "ready_to_generate"
```

```python
def test_generate_chat_reply_falls_back_when_llm_returns_plain_text():
    client = FakeClient("我建议你先补充目标用户和转化动作。")

    payload = generate_chat_reply(
        client,
        session_context={"previous_document": None},
        recent_messages=[{"role": "user", "content": "帮我看看"}],
    )

    assert payload["assistant_message"] == "我建议你先补充目标用户和转化动作。"
    assert payload["conversation_intent"] == "continue"
```

```python
def test_generate_chat_reply_includes_previous_document_context():
    captured = {}

    class CapturingClient(FakeClient):
        def generate(self, *, instructions: str, input_text: str, timeout: float):
            captured["input_text"] = input_text
            return super().generate(instructions=instructions, input_text=input_text, timeout=timeout)

    client = CapturingClient('{"assistant_message":"继续聊","conversation_intent":"continue"}')

    generate_chat_reply(
        client,
        session_context={"previous_document": "# 上一版需求文档"},
        recent_messages=[{"role": "user", "content": "我想调整首页结构"}],
    )

    assert "上一版需求文档" in captured["input_text"]
```

- [ ] **Step 2: 运行测试，确认当前失败**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py::test_generate_chat_reply_parses_ready_to_generate_envelope tests/test_llm_orchestrator.py::test_generate_chat_reply_falls_back_when_llm_returns_plain_text tests/test_llm_orchestrator.py::test_generate_chat_reply_includes_previous_document_context -q
```

Expected:

- 失败，因为当前只存在 `generate_stage_reply()` 和阶段 prompt

- [ ] **Step 3: 写最小实现与 prompt 文件**

```python
# backend/app/services/llm_orchestrator.py
def build_chat_input(*, session_context: dict, recent_messages: list[dict]) -> str:
    previous_document = session_context.get("previous_document") or "无"
    history = "\n".join(f"{item['role']}: {item['content']}" for item in recent_messages)
    return f"上一版最终文档：\n{previous_document}\n\n最近对话：\n{history}"


def generate_chat_reply(client, *, session_context: dict, recent_messages: list[dict]) -> dict:
    response = client.generate(
        instructions=load_prompt("chat_system.md"),
        input_text=build_chat_input(session_context=session_context, recent_messages=recent_messages),
        timeout=CHAT_REPLY_TIMEOUT,
    )
    raw = response.text.strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        current_app.logger.warning("llm envelope parse failed", extra={"raw": raw[:500]})
        return {"assistant_message": raw, "conversation_intent": "continue"}

    return {
        "assistant_message": payload["assistant_message"],
        "conversation_intent": payload.get("conversation_intent", "continue"),
    }
```

```md
<!-- backend/app/prompts/chat_system.md -->
你是一个帮助普通中文用户梳理个人网站需求的 AI 助手。
你必须始终使用简体中文。
你要像懂沟通、懂网站策划、懂审美的产品顾问一样对话。
一次只追问一个最关键的问题。
当信息已经足够形成最终需求文档时，不直接生成，而是先询问用户是否现在开始整理最终需求文档。
你的输出必须是 JSON，字段如下：
{
  "assistant_message": "给用户看的自然语言回复",
  "conversation_intent": "continue 或 ready_to_generate"
}
```

```md
<!-- backend/app/prompts/welcome_initial.md -->
你好！我是你的网站需求助手。
接下来我会帮你梳理个人网站的目标、内容、风格和功能。
你可以先告诉我：你想做一个什么样的网站？面向什么人？
```

```md
<!-- backend/app/prompts/welcome_revision.md -->
欢迎回来。这一轮我会基于上一版需求文档继续帮你修改。
你会先看到上一版需求摘要，然后我们继续补充和调整。
```

- [ ] **Step 4: 运行相关测试**

Run:

```bash
cd backend && pytest tests/test_llm_orchestrator.py -q
```

Expected:

- PASS，包含 JSON envelope 解析和 fallback 测试

- [ ] **Step 5: 提交这一轮**

```bash
git add backend/app/prompts/chat_system.md backend/app/prompts/welcome_initial.md backend/app/prompts/welcome_revision.md backend/app/prompts/render_final_document.md backend/app/services/llm_orchestrator.py backend/app/services/document_renderer.py backend/tests/test_llm_orchestrator.py
git commit -m "feat: add chat envelope orchestration"
```

## Task 3: 重写会话、消息、文档与后台 token API

**Files:**
- Modify: `backend/app/__init__.py`
- Modify: `backend/app/routes/sessions.py`
- Modify: `backend/app/routes/messages.py`
- Modify: `backend/app/routes/documents.py`
- Modify: `backend/app/routes/uploads.py`
- Create: `backend/app/routes/admin.py`
- Create: `backend/app/services/session_lifecycle.py`
- Create: `backend/app/services/admin_auth.py`
- Modify: `backend/app/services/queue_manager.py`
- Test: `backend/tests/test_sessions_api.py`
- Test: `backend/tests/test_queue_and_generation.py`
- Create: `backend/tests/test_admin_api.py`

- [ ] **Step 1: 先写失败的 session / admin / queue 测试**

```python
def test_get_session_returns_recent_messages_and_previous_summary(client, seeded_revision_session):
    response = client.get(f"/api/sessions/{seeded_revision_session.token}")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["messages"][0]["delivery_status"] == "system"
    assert payload["previous_summary"] == "上一版摘要"
    assert payload["has_more"] is False
```

```python
def test_admin_can_revoke_token(client):
    response = client.post(
        "/api/admin/tokens/invite-token/revoke",
        headers={"Authorization": "Bearer admin-secret"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "expired"
```

```python
def test_document_generation_creates_successor_token(client, ready_to_generate_session, monkeypatch):
    monkeypatch.setattr("app.routes.messages.render_document_bundle", lambda **_: ("摘要", "# 文档"))

    response = client.post(
        f"/api/sessions/{ready_to_generate_session.token}/messages",
        json={"content": "请开始生成最终需求文档", "confirm_generate": True},
    )

    payload = response.get_json()

    assert response.status_code == 202
    assert payload["session_status"] == "generating_document"

    follow_up = client.get(f"/api/sessions/{ready_to_generate_session.token}")
    follow_up_payload = follow_up.get_json()

    assert follow_up_payload["status"] == "completed"
    assert follow_up_payload["successor_token"] is not None
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py tests/test_queue_and_generation.py tests/test_admin_api.py -q
```

Expected:

- 失败，因为当前不存在 admin 路由、消息分页、previous_summary、revoke、successor token 逻辑

- [ ] **Step 3: 实现后端生命周期和 API**

```python
# backend/app/services/admin_auth.py
def require_admin_token(request) -> None:
    header = request.headers.get("Authorization", "")
    expected = current_app.config["ADMIN_TOKEN"]
    if header != f"Bearer {expected}":
        raise PermissionError("invalid admin token")
```

```python
# backend/app/services/session_lifecycle.py
def expire_if_needed(session: SessionRecord, *, now: datetime) -> None:
    if session.completed_at is None and session.expires_at and now >= session.expires_at:
        session.status = "expired"
        return

    idle_deadline = now - timedelta(seconds=current_app.config["SESSION_IDLE_TIMEOUT_SECONDS"])
    if session.status == "queued" and session.last_activity_at and session.last_activity_at <= idle_deadline:
        session.status = "awaiting_user"
        session.queued_at = None
```

```python
# backend/app/routes/sessions.py
@sessions_bp.get("/sessions/<token>")
def get_session(token: str):
    session = load_valid_session(token)
    messages = (
        db.query(MessageRecord)
        .filter(MessageRecord.session_token == token)
        .order_by(MessageRecord.id.desc())
        .limit(current_app.config["SESSION_MESSAGES_PAGE_SIZE"])
        .all()
    )
    return jsonify(
        {
            **serialize_session(session),
            "messages": [serialize_message(item) for item in reversed(messages)],
            "has_more": False,
            "previous_summary": load_previous_summary(session),
        }
    )
```

```python
# backend/app/routes/admin.py
@admin_bp.post("/admin/tokens")
def create_admin_token():
    require_admin_token(request)
    token = token_urlsafe(24)
    session = SessionRecord(
        token=token,
        status="awaiting_user",
        admin_note=(request.get_json(silent=True) or {}).get("admin_note"),
    )
    db.add(session)
    db.commit()
    return jsonify(serialize_session(session)), 201
```

- [ ] **Step 4: 运行后端路由测试**

Run:

```bash
cd backend && pytest tests/test_sessions_api.py tests/test_queue_and_generation.py tests/test_admin_api.py -q
```

Expected:

- PASS

- [ ] **Step 5: 提交这一轮**

```bash
git add backend/app/__init__.py backend/app/routes/sessions.py backend/app/routes/messages.py backend/app/routes/documents.py backend/app/routes/uploads.py backend/app/routes/admin.py backend/app/services/session_lifecycle.py backend/app/services/admin_auth.py backend/app/services/queue_manager.py backend/tests/test_sessions_api.py backend/tests/test_queue_and_generation.py backend/tests/test_admin_api.py
git commit -m "feat: add token lifecycle and admin apis"
```

## Task 4: 重构前端路由、类型和首页 token 入口

**Files:**
- Modify: `frontend/src/app.tsx`
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/routes/home-page.tsx`
- Create: `frontend/src/components/home/token-entry.tsx`
- Test: `frontend/src/test/app-shell.test.tsx`
- Test: `frontend/src/test/home-page.test.tsx`

- [ ] **Step 1: 先写失败的前端入口测试**

```tsx
test("首页 CTA 不再匿名创建 session，而是跳转到 token 输入区", async () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  await userEvent.click(screen.getByRole("button", { name: "开始梳理我的网站" }));

  expect(screen.getByLabelText("访问 Token")).toBeInTheDocument();
});
```

```tsx
test("输入 token 后可以跳转到聊天页", async () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  await userEvent.type(screen.getByLabelText("访问 Token"), "invite-token");
  await userEvent.click(screen.getByRole("button", { name: "进入对话" }));

  expect(window.location.pathname).toContain("/session/invite-token");
});
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd frontend && npm test -- app-shell.test.tsx home-page.test.tsx
```

Expected:

- 失败，因为首页仍然调用 `createSession()`

- [ ] **Step 3: 写最小前端入口改造**

```tsx
// frontend/src/components/home/token-entry.tsx
export function TokenEntry({ value, onChange, onSubmit }: Props) {
  return (
    <section className="mx-auto mt-8 max-w-[640px] rounded-[28px] border border-white/10 bg-white/5 p-4">
      <label className="text-sm text-white/70" htmlFor="token-input">
        访问 Token
      </label>
      <div className="mt-3 flex gap-3">
        <input id="token-input" value={value} onChange={(event) => onChange(event.target.value)} />
        <button onClick={onSubmit} type="button">进入对话</button>
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/routes/home-page.tsx
const [token, setToken] = useState("");

function handleEnter() {
  if (!token.trim()) return;
  navigate(`/session/${token.trim()}`);
}
```

```ts
// frontend/src/lib/types.ts
export type ConversationIntent = "continue" | "ready_to_generate";

export type SessionStatus =
  | "queued"
  | "active"
  | "awaiting_user"
  | "generating_document"
  | "completed"
  | "failed"
  | "expired";

export interface SessionPayload {
  token: string;
  status: SessionStatus;
  conversation_intent?: ConversationIntent;
  has_more?: boolean;
  oldest_message_id?: number;
  successor_token?: string | null;
}
```

- [ ] **Step 4: 运行前端入口测试**

Run:

```bash
cd frontend && npm test -- app-shell.test.tsx home-page.test.tsx
```

Expected:

- PASS

- [ ] **Step 5: 提交这一轮**

```bash
git add frontend/src/app.tsx frontend/src/lib/types.ts frontend/src/lib/api.ts frontend/src/routes/home-page.tsx frontend/src/components/home/token-entry.tsx frontend/src/test/app-shell.test.tsx frontend/src/test/home-page.test.tsx
git commit -m "feat: add token-gated homepage entry"
```

## Task 5: 将 session 页收敛为单聊天窗口

**Files:**
- Modify: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/components/intake/chat-panel.tsx`
- Modify: `frontend/src/components/intake/attachment-panel.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/lib/types.ts`
- Test: `frontend/src/test/session-page.test.tsx`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `frontend/src/test/mobile-states.test.tsx`

- [ ] **Step 1: 先写失败的聊天页测试**

```tsx
test("聊天页只展示消息流、输入区和 typing 态", async () => {
  mockSessionFetch({
    status: "awaiting_user",
    messages: [{ id: 1, role: "assistant", content: "欢迎使用。", delivery_status: "system" }],
  });

  renderSessionPage();

  expect(screen.queryByText("模板")).not.toBeInTheDocument();
  expect(screen.queryByText("风格")).not.toBeInTheDocument();
  expect(screen.getByText("欢迎使用。")).toBeInTheDocument();
});
```

```tsx
test("发送消息后先显示 typing，再显示 assistant 回复", async () => {
  mockMessagePost({
    session_status: "awaiting_user",
    assistant_message: "我建议你先明确网站主要目标。",
    typing_started: true,
  });

  renderSessionPage();
  await userEvent.type(screen.getByPlaceholderText("继续描述你的网站需求"), "我想做一个个人网站");
  await userEvent.click(screen.getByRole("button", { name: "发送" }));

  expect(screen.getByText("...")).toBeInTheDocument();
  expect(await screen.findByText("我建议你先明确网站主要目标。")).toBeInTheDocument();
});
```

```tsx
test("当会话进入 ready_to_generate 时展示确认按钮", async () => {
  mockSessionFetch({
    status: "awaiting_user",
    conversation_intent: "ready_to_generate",
    messages: [{ id: 1, role: "assistant", content: "我现在可以整理最终需求文档。", delivery_status: "final" }],
  });

  renderSessionPage();

  expect(await screen.findByRole("button", { name: "开始生成最终需求文档" })).toBeInTheDocument();
});
```

```tsx
test("有更多历史消息时可以点击加载更多", async () => {
  mockSessionFetch({
    status: "awaiting_user",
    has_more: true,
    oldest_message_id: 101,
    messages: [{ id: 102, role: "assistant", content: "最近一条消息", delivery_status: "final" }],
  });
  mockMessagesPageFetch([
    { id: 100, role: "assistant", content: "更早的一条消息", delivery_status: "final" },
  ]);

  renderSessionPage();
  await userEvent.click(await screen.findByRole("button", { name: "加载更多消息" }));

  expect(await screen.findByText("更早的一条消息")).toBeInTheDocument();
});
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx
```

Expected:

- 失败，因为页面仍包含阶段条、摘要栏和自动阶段推进逻辑

- [ ] **Step 3: 写最小聊天页实现**

```tsx
// frontend/src/components/intake/chat-panel.tsx
export function ChatPanel({
  messages,
  draft,
  isSending,
  onDraftChange,
  onSend,
  onConfirmGenerate,
  onLoadMore,
  hasMore,
  conversationIntent,
  attachments,
  onUpload,
}: Props) {
  return (
    <section className="flex min-h-[calc(100vh-96px)] flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto px-4 py-6">
        {hasMore ? (
          <button className="mx-auto block text-sm text-white/70" onClick={onLoadMore} type="button">
            加载更多消息
          </button>
        ) : null}
        {messages.map((message) => (
          <div
            key={message.id}
            className={message.role === "user" ? "ml-auto max-w-[78%]" : "mr-auto max-w-[78%]"}
          >
            <div className="rounded-[24px] bg-white/6 px-4 py-3 text-sm text-white">{message.content}</div>
          </div>
        ))}
        {conversationIntent === "ready_to_generate" ? (
          <button
            className="mr-auto rounded-full bg-[var(--color-accent)] px-4 py-2 text-sm text-white"
            onClick={onConfirmGenerate}
            type="button"
          >
            开始生成最终需求文档
          </button>
        ) : null}
        {isSending ? <div className="mr-auto rounded-[24px] bg-white/6 px-4 py-3 text-sm text-white">...</div> : null}
      </div>
      <div className="sticky bottom-0 border-t border-white/10 bg-black/80 p-4 backdrop-blur">
        <AttachmentPanel attachments={attachments} onUpload={onUpload} />
        <textarea placeholder="继续描述你的网站需求" value={draft} onChange={(event) => onDraftChange(event.target.value)} />
        <button disabled={isSending} onClick={onSend} type="button">发送</button>
      </div>
    </section>
  );
}
```

```tsx
// frontend/src/routes/session-page.tsx
async function handleConfirmGenerate() {
  await sendMessage(token, { content: "请开始生成最终需求文档", confirm_generate: true });
}

if (session.status === "completed" || session.status === "expired" || session.status === "failed") {
  setComposerDisabled(true);
}
```

```ts
// frontend/src/lib/api.ts
export async function getSessionMessages(token: string, beforeId: number, limit = 50): Promise<SessionMessage[]> {
  const response = await fetch(`${API_BASE}/sessions/${token}/messages?before_id=${beforeId}&limit=${limit}`);
  return parseJson<SessionMessage[]>(response, "加载历史消息失败");
}
```

- [ ] **Step 4: 运行前端聊天页测试**

Run:

```bash
cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx
```

Expected:

- PASS

- [ ] **Step 5: 提交这一轮**

```bash
git add frontend/src/routes/session-page.tsx frontend/src/components/intake/chat-panel.tsx frontend/src/components/intake/attachment-panel.tsx frontend/src/lib/api.ts frontend/src/lib/types.ts frontend/src/test/session-page.test.tsx frontend/src/test/session-flow.test.tsx frontend/src/test/mobile-states.test.tsx
git commit -m "feat: rebuild session page as single chat"
```

## Task 6: 实现后台管理页与前端 admin API

**Files:**
- Modify: `frontend/src/app.tsx`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/lib/types.ts`
- Create: `frontend/src/routes/admin-page.tsx`
- Create: `frontend/src/components/admin/token-list.tsx`
- Create: `frontend/src/components/admin/token-detail.tsx`
- Create: `frontend/src/components/admin/token-create-form.tsx`
- Create: `frontend/src/test/admin-page.test.tsx`

- [ ] **Step 1: 先写失败的后台页测试**

```tsx
test("管理员输入 Bearer token 后可以加载 token 列表", async () => {
  mockAdminTokens([
    { token: "invite-token", status: "awaiting_user", admin_note: "李医生主页", message_count: 2 },
  ]);

  render(
    <MemoryRouter initialEntries={["/admin"]}>
      <App />
    </MemoryRouter>,
  );

  await userEvent.type(screen.getByLabelText("管理员 Token"), "admin-secret");
  await userEvent.click(screen.getByRole("button", { name: "进入后台" }));

  expect(await screen.findByText("李医生主页")).toBeInTheDocument();
});
```

```tsx
test("管理员可以撤销 token", async () => {
  mockAdminTokens([{ token: "invite-token", status: "awaiting_user", admin_note: "待撤销" }]);
  mockRevokeToken();

  renderAdminPage();
  await userEvent.click(await screen.findByRole("button", { name: "撤销 Token" }));

  expect(await screen.findByText("expired")).toBeInTheDocument();
});
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
cd frontend && npm test -- admin-page.test.tsx
```

Expected:

- 失败，因为 `/admin` 路由和 admin 客户端都不存在

- [ ] **Step 3: 写最小后台页实现**

```ts
// frontend/src/lib/api.ts
export async function listAdminTokens(adminToken: string): Promise<AdminTokenListItem[]> {
  const response = await fetch(`${API_BASE}/admin/tokens`, {
    headers: { Authorization: `Bearer ${adminToken}` },
  });
  return parseJson(response, "读取 token 列表失败");
}
```

```tsx
// frontend/src/routes/admin-page.tsx
export function AdminPage() {
  const [adminToken, setAdminToken] = useState("");
  const [tokens, setTokens] = useState<AdminTokenListItem[]>([]);

  async function handleLoad() {
    const payload = await listAdminTokens(adminToken);
    setTokens(payload);
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <TokenCreateForm adminToken={adminToken} onTokenChange={setAdminToken} onLoad={handleLoad} />
      <TokenList items={tokens} />
    </main>
  );
}
```

- [ ] **Step 4: 运行后台页测试**

Run:

```bash
cd frontend && npm test -- admin-page.test.tsx
```

Expected:

- PASS

- [ ] **Step 5: 提交这一轮**

```bash
git add frontend/src/app.tsx frontend/src/lib/api.ts frontend/src/lib/types.ts frontend/src/routes/admin-page.tsx frontend/src/components/admin/token-list.tsx frontend/src/components/admin/token-detail.tsx frontend/src/components/admin/token-create-form.tsx frontend/src/test/admin-page.test.tsx
git commit -m "feat: add admin token dashboard"
```

## Task 7: 全量验证、文档更新与浏览器验收

**Files:**
- Modify: `DOCUMENTATION.md`
- Modify: `SESSION_CONTEXT.md`

- [ ] **Step 1: 运行后端全量测试**

Run:

```bash
cd backend && pytest -q
```

Expected:

- PASS，覆盖：
  - token 生命周期
  - JSON envelope 解析 fallback
  - successor token 创建
  - admin 鉴权与 revoke
  - 5 分钟资源释放与 24 小时失效

- [ ] **Step 2: 运行前端全量测试**

Run:

```bash
cd frontend && npm test
```

Expected:

- PASS

- [ ] **Step 3: 运行前端构建**

Run:

```bash
cd frontend && npm run build
```

Expected:

- PASS

- [ ] **Step 4: 启动前后端本地服务**

Run:

```bash
cd backend && python run.py
cd frontend && npm run dev
```

Expected:

- 后端监听 `http://127.0.0.1:5000`
- 前端监听 `http://127.0.0.1:5173`

- [ ] **Step 5: 使用真实浏览器做页面级验收**

Use `agent-browser` skill and validate:

- 首页加载正常，CTA 不再匿名创建会话
- 首页 token 输入可跳转到 `/session/:token`
- 聊天页用户消息在右侧、assistant 消息在左侧
- 发送消息时可见 `...` typing 态
- 附件入口在输入区附近可用
- LLM 发出“可以生成最终需求文档”的确认态后，前端展示确认按钮
- 确认生成后会话进入 `completed`
- 页面能看到 successor token
- `/admin` 可加载 token 列表、详情与 revoke 动作
- 移动端视口下输入区固定底部、消息区滚动正常、没有横向溢出

- [ ] **Step 6: 更新执行文档**

```md
## [2026-04-09] Chat-first redesign
- 记录本轮重构覆盖的路由、状态与已知风险
- 写入后端测试、前端测试、前端构建、真实浏览器验收结果
```

- [ ] **Step 7: 提交最终验证与文档**

```bash
git add DOCUMENTATION.md SESSION_CONTEXT.md
git commit -m "docs: record chat-first redesign validation"
```

---

## 自检

### Spec coverage

- 受控 token、首页入口、单聊天窗口、附件内嵌、后台页、successor token、修订链、5 分钟资源释放、24 小时失效、JSON envelope、fallback、`ADMIN_TOKEN`、revoke、移动端与 `.env.example` 都映射到了任务。

### Placeholder scan

- 无 `TODO`、`TBD`、`implement later`。
- 所有任务都包含具体文件、测试命令和提交点。

### Type consistency

- 后端会话状态统一为 `queued | active | awaiting_user | generating_document | completed | failed | expired`
- JSON envelope 统一为 `assistant_message + conversation_intent`
- admin 鉴权统一为 `Authorization: Bearer <admin_token>`
