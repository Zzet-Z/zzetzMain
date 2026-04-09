# Chat-First Post-Launch Follow-up Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 chat-first 上线后暴露的 6 个实际问题，恢复文档生成切换、上传反馈、附件参与对话、后台详情可见性，以及消息发送过程中的稳定回显。

**Architecture:** 继续沿用现有 Flask + SQLite + React + 轮询架构，不新增后台人工流程，也不改动 token 生命周期主模型。本轮以“最小闭环修复”为原则，优先补齐错误透传、附件上下文注入、附件预览 URL、后台详情 payload，以及前端 optimistic message 与轮询数据的同步策略。

**Tech Stack:** React, TypeScript, Vite, Tailwind CSS, Vitest, Flask, SQLAlchemy, SQLite, pytest, agent-browser

---

## Scope

本轮只处理以下 6 个问题：

1. 上传图片失败时前端没有给出明确报错
2. 参考图片没有进入 LLM 对话上下文
3. 聊天页附件只显示文件名，不显示缩略图
4. 后台“查看”缺少足够的 token 明细数据
5. 用户发送消息后，在 LLM 思考期间该条消息会短暂消失
6. 用户已经明确要求定稿时，LLM 仍未进入文档生成状态

不在本轮范围内：

- 改造为真正的多模态图片理解链路
- 引入 WebSocket
- 重写后台为多页应用
- 大规模 UI 重构

## Priority

### P0

- Task F6: 修复“明确定稿但未进入文档生成状态”
- Task F1: 修复发送中用户消息消失
- Task F2: 打通上传失败错误反馈
- Task F3: 把附件信息注入 LLM 对话上下文

### P1

- Task F4: 聊天页附件缩略图展示
- Task F5: 后台 token 详情扩展

## Task F6: 修复“明确定稿但未进入文档生成状态”

**Problem**
- 生产环境里，用户已经明确表达“生成需求文档吧”“不用更新了 就这个”，但会话仍停留在 `awaiting_user`
- assistant 直接把完整需求文档正文作为普通聊天消息发出，数据库里的 `documents.status` 仍是 `pending`
- 当前链路对 `final_document` / `ready_to_generate` 的进入过度依赖模型严格遵守 JSON envelope；一旦模型直接输出自然语言或 Markdown 文档，fallback 就会把它当作普通 `continue`

**Production evidence**
- `admin_note=zzttest1` 对应会话：assistant 已输出“个人设计作品集网站需求文档”全文，但 session 仍为 `awaiting_user`
- `admin_note=zzttest2` 对应会话：assistant 已输出“个人摄影作品集网站需求文档”全文，但 session 仍为 `awaiting_user`

**Likely files**
- Modify: `backend/app/services/llm_client.py`
- Modify: `backend/app/services/llm_orchestrator.py`
- Modify: `backend/app/routes/messages.py`
- Modify: `backend/app/prompts/chat_system.md`
- Test: `backend/tests/test_llm_orchestrator.py`
- Test: `backend/tests/test_queue_and_generation.py`

**Plan**
- 先强化模型结构化输出约束，优先评估在 Responses API 侧增加明确的 JSON 输出模式，而不是只靠 prompt 文本约束
- 增加“plain text / markdown final doc 被错误回退为 continue”的回归测试
- 在 fallback 路径补一层保底识别：如果模型明显已经输出完整需求文档或用户刚刚明确确认定稿，后端不能继续把它当普通闲聊消息
- 明确最终只允许两条产品路径：
  - assistant 先返回 `ready_to_generate`，用户点击确认后进入 `confirm_generate`
  - 或 assistant 返回合法 `final_document`，服务端直接落盘并 `completed`

**Acceptance**
- 用户明确要求生成或确认定稿后，会话必须进入 `ready_to_generate`、`generating_document` 或 `completed` 之一，不能继续停在 `awaiting_user`
- 不允许 assistant 把整份 PRD 当普通聊天消息吐给用户，同时数据库文档仍为空
- 生产环境里像 `zzttest1/zzttest2` 这样的对话应能稳定生成最终文档

**Validation**
- `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`
- 真实会话复现“请生成需求文档 / 就这个不用改了”路径
- `agent-browser` 或真实 API 复验 completed / successor token 链路

## Task F1: 修复发送中用户消息消失

**Problem**
- 当前聊天页发送消息后会先插入 optimistic user message
- 同时 `GET /api/sessions/:token` 的轮询会用旧消息窗口覆盖本地状态
- 因为后端在 LLM 调用完成前尚未提交本次用户消息，轮询拿到的还是“未包含当前用户消息”的旧快照

**Likely files**
- Modify: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/components/intake/chat-panel.tsx`
- Modify: `frontend/src/lib/types.ts`
- Modify: `backend/app/routes/messages.py`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `backend/tests/test_sessions_api.py` or `backend/tests/test_queue_and_generation.py`

**Plan**
- 明确发送中的本地消息合并策略，避免轮询直接覆盖 optimistic message
- 后端评估是否在进入 LLM 调用前先持久化用户消息并提交，再进入生成链路
- 前端在 `isSending` 期间禁止用旧快照回退本地已发送消息，直到服务端确认回包

**Acceptance**
- 用户点击发送后，右侧用户消息应持续可见
- 左侧可同时展示 typing / “思考中”占位
- 即使轮询返回旧列表，也不能把刚发送的消息抹掉

**Validation**
- `cd frontend && npm test -- session-flow.test.tsx session-page.test.tsx`
- `cd backend && pytest tests/test_queue_and_generation.py -q`
- `agent-browser` 真实浏览器验证发送消息到返回回复的整段过程

## Task F2: 打通上传失败错误反馈

**Problem**
- 前端 `parseJson()` 只要 `response.ok=false` 就抛通用错误，忽略了后端返回的中文 `message`
- 聊天页只能显示固定文案“图片上传失败”，用户看不到真实原因，例如格式不支持、超大小、数量超限、token 已结束

**Likely files**
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/routes/session-page.tsx`
- Modify: `frontend/src/components/intake/attachment-panel.tsx`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `backend/tests/test_uploads_api.py`

**Plan**
- API 层统一优先解析后端错误体中的 `message`
- 上传入口在失败时展示具体中文原因，而不是固定兜底文案
- 保留网络异常兜底，区分“服务端明确拒绝”与“请求异常”

**Acceptance**
- 上传非图片、超大小、超上限、已完成 token 上传时，前端能显示对应中文原因
- 错误展示位置靠近附件入口或聊天页全局错误区，用户能感知

**Validation**
- `cd backend && pytest tests/test_uploads_api.py -q`
- `cd frontend && npm test -- session-flow.test.tsx session-page.test.tsx`
- `agent-browser` 真实浏览器验证非法上传后的错误提示

## Task F3: 把附件信息注入 LLM 对话上下文

**Problem**
- 当前附件信息只在最终文档渲染 `render_final_document.md` 中使用
- `generate_chat_reply()` 的 `session_context` 没有附件数据，`build_chat_input()` 也没有“本轮参考附件”段落
- 结果是 LLM 在对话阶段不知道用户已经上传了哪些参考图

**Likely files**
- Modify: `backend/app/routes/messages.py`
- Modify: `backend/app/services/llm_orchestrator.py`
- Modify: `backend/app/prompts/chat_system.md`
- Test: `backend/tests/test_llm_orchestrator.py`
- Test: `backend/tests/test_queue_and_generation.py`

**Plan**
- 在消息路由里查询当前 token 的附件列表，并把文件名、caption、必要时 mime/type 传入 chat session context
- `build_chat_input()` 增加“本轮参考附件”段落
- 调整 `chat_system.md`，要求模型在合适时机引用“用户上传的参考图”继续追问或确认理解

**Acceptance**
- 已上传附件后，LLM 后续回复能显式感知“你上传了参考图/案例图”
- 不要求本轮直接升级为视觉识别，但至少要让附件元数据进入对话上下文
- 最终文档链路继续保留附件说明

**Validation**
- `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`
- 真实会话里上传图片后发送补充消息，确认回复不再忽略附件存在

## Task F4: 聊天页附件缩略图展示

**Problem**
- 当前附件面板只把附件渲染成文件名 chip
- 后端 session payload 没有可直接用于前端展示的 preview URL
- 前端无法展示已上传图片缩略图，也无法区分历史附件与刚上传附件

**Likely files**
- Modify: `backend/app/routes/sessions.py`
- Modify: `backend/app/routes/uploads.py`
- Create or Modify: 附件预览读取路由（建议放在 `backend/app/routes/uploads.py`）
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/components/intake/attachment-panel.tsx`
- Modify: `frontend/src/routes/session-page.tsx`
- Test: `backend/tests/test_uploads_api.py`
- Test: `frontend/src/test/session-flow.test.tsx`
- Test: `frontend/src/test/session-page.test.tsx`

**Plan**
- 后端为附件返回稳定的 preview URL，而不是本地磁盘 `file_path`
- 增加受 token 保护的附件预览读取接口，避免直接暴露磁盘路径
- 前端把附件列表改为“缩略图 + 文件名/备注”的卡片形式，并兼容历史回放

**Acceptance**
- 聊天页附件区可显示已上传图片缩略图
- 刷新页面后仍能回放历史附件缩略图
- 移动端下缩略图布局不挤爆输入区

**Validation**
- `cd backend && pytest tests/test_uploads_api.py -q`
- `cd frontend && npm test -- session-flow.test.tsx session-page.test.tsx mobile-states.test.tsx`
- `agent-browser` 真实浏览器验证上传、刷新、回放

## Task F5: 后台 token 详情扩展

**Problem**
- 当前后台“查看”能打开详情，但数据过少
- 后端 detail payload 只返回基本字段、摘要和 last_error，缺少更完整的会话数据
- 前端详情区也没有展示消息数、附件清单、时间戳、文档内容入口等更有用的信息

**Likely files**
- Modify: `backend/app/routes/admin.py`
- Modify: `frontend/src/lib/types.ts`
- Modify: `frontend/src/lib/api.ts`
- Modify: `frontend/src/components/admin/token-detail.tsx`
- Modify: `frontend/src/components/admin/token-list.tsx`
- Modify: `frontend/src/routes/admin-page.tsx`
- Test: `backend/tests/test_admin_api.py`
- Test: `frontend/src/test/admin-page.test.tsx`

**Plan**
- 后端 detail payload 补齐：
  - `created_at` / `last_activity_at` / `completed_at` / `expires_at`
  - `message_count` / `attachment_count`
  - 附件列表
  - 文档摘要与 PRD 片段或全文入口
  - 修订链关系字段
- 前端详情区按“基本信息 / 产出信息 / 附件 / 错误与状态”重排

**Acceptance**
- 点击“查看”后，管理员能看到该 token 的关键数据，而不是只有少量摘要字段
- 至少能判断该 token 是否完成、生成了什么、有哪些附件、是否有 successor token、失败原因是什么

**Validation**
- `cd backend && pytest tests/test_admin_api.py -q`
- `cd frontend && npm test -- admin-page.test.tsx`
- `agent-browser` 真实浏览器验证后台查看链路

## Execution order

建议按以下顺序执行：

1. `Task F6` 修复明确定稿却不生成文档
2. `Task F1` 修复消息消失
3. `Task F2` 修复上传错误反馈
4. `Task F3` 注入附件到 LLM 对话上下文
5. `Task F4` 增加附件缩略图与历史回放
6. `Task F5` 扩展后台详情

## Final validation

全部修复完成后统一执行：

```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
```

并补做 `agent-browser` 页面级验收：

- 首页 token 入口
- 聊天页消息发送、typing 态、上传失败提示、缩略图展示、completed 后 successor token
- 后台页管理员鉴权、token 列表、查看详情、撤销
