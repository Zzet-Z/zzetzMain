# DOCUMENTATION.md

> **系统记录原则**：本文件是项目执行状态的唯一权威来源。
> agent 只能看到仓库里的内容——每次任务结束后必须在此更新，否则信息对后续执行者不存在。

## Current status
- Current milestone: Milestone 3 — LLM 客户端与 Prompt 编排
- Current task: Task 3 — 接入真实 LLM 客户端与 Prompt 编排
- Status: Task 2 completed, Task 3 ready to start
- Last updated: 2026-04-08

---

## Project snapshot
### Completed
- [x] 产品规格文档已完成 (`docs/superpowers/specs/`)
- [x] 实施计划已完成 (`docs/superpowers/plans/`)
- [x] 工程执行规则文件已建立 (AGENTS.md, PLANS.md, IMPLEMENT.md, DOCUMENTATION.md)

### In progress
- （无）

### Not started
- Milestone 3: LLM 客户端与 Prompt 编排（Task 3）
- Milestone 4: 阶段状态机与对话引导（Task 4）
- Milestone 5: 并发队列与文档生成（Task 5）
- Milestone 6: 上传与安全限制（Task 6）
- Milestone 7: 首页移动端优先 UI（Task 7）
- Milestone 8: 需求梳理页 UI 与前后端接线（Task 8）
- Milestone 9: 最终验证与文档（Task 9）

### Blocked
- （无）

---

## Task log

### [2026-04-08] Task 2: 建立会话模型、数据库与基础 API
**Summary**
- 新建 SQLAlchemy 数据层：`db.py`、`models.py`、`schemas.py`
- 新增 `POST /api/sessions`、`GET /api/sessions/<token>`、`PATCH /api/sessions/<token>`
- app 工厂接入 SQLite 初始化、CORS 与 `SessionLocal.remove()` teardown
- 建立会话默认状态：`draft`、`template`、`zh-CN`，并在创建时自动生成空摘要与待生成文档记录

**Files changed**
- `backend/app/__init__.py`
- `backend/app/db.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `backend/app/routes/sessions.py`
- `backend/tests/test_sessions_api.py`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_default_state -q`
  - `cd backend && pytest tests/test_sessions_api.py -q`
- 绿灯验证：
  - `cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_default_state -q`
  - `cd backend && pytest tests/test_sessions_api.py -q`
  - `cd backend && pytest -q`

**Validation result**
- 红灯阶段符合预期：
  - 初始 `POST /api/sessions` 返回 404
  - 补完 create 之后，`GET/PATCH` 与中文 404 仍按预期失败
- 绿灯阶段全部通过：
  - session 创建、读取、更新、无效跳转、失效 token、CORS 头测试通过
  - 后端当前全量测试通过（7 passed）

**Notes**
- 为避免建表漏表，`create_app` 在 `init_db` 前显式导入模型模块
- `schemas.py` 目前只承担最小序列化职责，后续 Task 3/4 继续复用即可
- 阶段跳转白名单已按 plan 落地，但暂不支持回退阶段

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 2 提交 hash，原因同 Task 1

**Next suggested step**
- 执行 Milestone 3 / Task 3：真实 LLM 客户端、prompt 文件与 orchestrator
- 先补 `backend/tests/test_llm_orchestrator.py` 的红灯测试，再创建 prompt 文件与 httpx 客户端

### [2026-04-08] Task 1: 搭建前后端脚手架与最小运行面
**Summary**
- 新建 `backend/` 最小 Flask 脚手架，提供 `create_app` 工厂、`backend/.env` 读取入口与 `/api/health`
- 新建 `frontend/` 最小 React + Vite + Tailwind 脚手架，首页路由可渲染中文标题
- 按 TDD 先补后端健康检查测试与前端 app shell 测试，并先验证红灯再实现
- 将根目录 `.env.local` 中的 LLM 配置迁移到 `backend/.env`，且保持不进入 git

**Files changed**
- `backend/pyproject.toml`
- `backend/run.py`
- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/routes/health.py`
- `backend/tests/test_health.py`
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/vite.config.ts`
- `frontend/postcss.config.js`
- `frontend/tailwind.config.ts`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/app.tsx`
- `frontend/src/styles.css`
- `frontend/src/test/app-shell.test.tsx`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_health.py -q`
  - `cd frontend && npm test -- app-shell.test.tsx`
- 绿灯验证：
  - `cd backend && pytest tests/test_health.py -q`
  - `cd frontend && npm test -- app-shell.test.tsx`
  - `cd backend && pytest -q`
  - `cd frontend && npm run build`

**Validation result**
- 红灯阶段符合预期：
  - 后端初始失败，原因是 `app` 模块不存在
  - 前端初始失败，原因是 `frontend/package.json` 不存在
- 绿灯阶段全部通过：
  - 后端健康检查测试通过
  - 后端当前全量测试通过（1 passed）
  - 前端 app shell 测试通过（1 passed）
  - 前端生产构建通过

**Notes**
- `backend/app/config.py` 先实现了极简 `.env` 加载，避免后续真实 LLM 接线前还要返工配置入口
- 当前前端只保留首页最小壳，不提前引入 Task 7 的完整 UI 结构，保持 Task 边界收敛

**Known issues**
- `README.md` 当前无需改动；启动和验证命令已与新脚手架一致
- `SESSION_CONTEXT.md` 的“最近重要提交”将在下一次任务收尾时补录本次提交 hash，避免为写入 hash 违反“不 amend commit”规则

**Next suggested step**
- 执行 Milestone 2 / Task 2：建立 SQLite 会话模型、数据库初始化与 Session API
- 重点先看 `docs/superpowers/plans/2026-04-08-personal-website-mvp.md` 中的 Task 2 Files 与 Step 顺序

### [2026-04-08] Task: 初始化工程规则
**Summary**
- 新建了 `AGENTS.md` — 代理工作规则
- 新建了 `PLANS.md` — 里程碑计划（9 个 Milestone 对应 Plan 的 9 个 Task）
- 新建了 `IMPLEMENT.md` — 执行规程
- 新建了 `DOCUMENTATION.md` — 执行日志（本文件）

**Files changed**
- `AGENTS.md`
- `PLANS.md`
- `IMPLEMENT.md`
- `DOCUMENTATION.md`

**Validation run**
- N/A（尚无代码，无需运行质量检查）

**Validation result**
- 未执行（当前仅完成规则初始化）

**Notes**
- 工程执行规则基于项目实际技术栈（React + Tailwind + Vite / Flask + SQLite）定制
- Milestone 划分与 Plan 文档中的 Task 1–9 一一对应
- 验证命令来自 Plan 中各 Task 的 Run 指令

**Known issues**
- （无）

**Next suggested step**
- 执行 Milestone 1 / Task 1：搭建前后端脚手架与最小运行面
- 参考 `docs/superpowers/plans/2026-04-08-personal-website-mvp.md` 的 Task 1 部分

---

## Architecture / decision notes
### Decision 1: LLM 调用方式
- Date: 2026-04-08
- Context: MVP 需要真实 LLM 能力，不能用 mock 替代主链路
- Decision: 使用 OpenAI Responses API，通过 httpx 同步调用
- Why: Spec 明确要求真实 LLM 是 MVP 的核心能力；OpenAI API 生态成熟，支持多模型切换
- Trade-off: 同步调用在高并发下可能阻塞 Flask worker，但 MVP 内测规模（5 并发）可接受

### Decision 2: 前端轮询而非 WebSocket
- Date: 2026-04-08
- Context: 需要实时更新对话状态和文档生成进度
- Decision: 使用短轮询（对话 3s、生成 5s），不引入 WebSocket
- Why: MVP 阶段复杂度优先，5 并发下轮询开销可忽略
- Trade-off: 用户感知延迟略高，但避免了 WebSocket 连接管理和断线重连的复杂度

### Decision 3: 阶段跳转校验
- Date: 2026-04-08
- Context: PATCH 接口允许前端设置 current_stage
- Decision: 后端用白名单校验阶段只能按顺序推进
- Why: 防止客户端跳过阶段，保证对话引导完整性
- Trade-off: 如果后续需要支持"回到前序阶段修改"，需要扩展白名单（Spec 11.2 已定义此需求）

---

## Known issues
（当前无已知问题）

---

## Verification history
| Date | Scope | Commands | Result | Notes |
|------|-------|----------|--------|-------|
| 2026-04-08 | Task 2 red/green | `cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_default_state -q`; `cd backend && pytest tests/test_sessions_api.py -q`; `cd backend && pytest -q` | Passed | 先确认 `/api/sessions` 缺失，再补齐 create/get/patch 与 CORS |
| 2026-04-08 | Task 1 red/green | `cd backend && pytest tests/test_health.py -q`; `cd frontend && npm test -- app-shell.test.tsx`; `cd backend && pytest -q`; `cd frontend && npm run build` | Passed | 红灯先确认缺失应用工厂与前端壳，随后绿灯通过 |
| 2026-04-08 | 规则初始化 | N/A | N/A | 无代码，无需验证 |

---

## Handoff notes
给下一个执行者的说明：

- 当前最应该继续的任务：**Milestone 3 / Task 3 — 接入真实 LLM 客户端与 Prompt 编排**
- 执行依据：`docs/superpowers/plans/2026-04-08-personal-website-mvp.md` 的 Task 3 部分
- 不要动的区域：`docs/superpowers/` 下的 spec 和 plan 文件
- 当前最大风险：Task 3 会首次接入真实 LLM HTTP 协议与 prompt 文件，必须继续保持测试里 mock 外部依赖、主链路里使用真实客户端
- 推荐先跑的验证命令：Task 3 的红灯从 `cd backend && pytest tests/test_llm_orchestrator.py -q` 开始
