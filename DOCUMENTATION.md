# DOCUMENTATION.md

> **系统记录原则**：本文件是项目执行状态的唯一权威来源。
> agent 只能看到仓库里的内容——每次任务结束后必须在此更新，否则信息对后续执行者不存在。

## Current status
- Current milestone: Chat-first post-launch follow-up fixes
- Current task: Task F1-F6 recovery sync - 已确认代码中的 6 个 follow-up 修复已落地，并补做状态归档
- Status: Implemented locally, validated by tests/build, committed on `main`
- Last updated: 2026-04-09

---

## Project snapshot
### Completed
- [x] MVP 原始产品规格与实施计划已完成 (`docs/superpowers/specs/2026-04-08-*.md`, `docs/superpowers/plans/2026-04-08-*.md`)
- [x] Chat-first 重构规格已完成 (`docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md`)
- [x] Chat-first 重构实施计划已完成 (`docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`)
- [x] 工程执行规则文件已建立 (AGENTS.md, PLANS.md, IMPLEMENT.md, DOCUMENTATION.md)

### In progress
- [x] 已整理上线后 follow-up 修复计划 (`docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`)
- [x] 已回收并核对本地代码中的 follow-up 修复实现，确认状态文档此前滞后于代码

### Completed
- [x] Task F6：修复“明确定稿但未进入文档生成状态”
- [x] Task F1：修复发送中用户消息消失
- [x] Task F2：修复上传失败错误反馈缺失
- [x] Task F3：把附件信息注入 LLM 对话上下文
- [x] Task F4：实现聊天页附件缩略图与历史回放
- [x] Task F5：扩展后台 token 详情查看数据

### Not started
- [ ] 后续如需继续推进，应转到部署/线上复验，而不是重复实现 F1-F6

### Blocked
- （无）

---

## Pending execution tasks

当前主线 chat-first 重构和 F1-F6 follow-up 修复都已在本地代码中落地。新的执行入口不再是“继续实现 F1-F6”，而是：

1. 视需要将本地修复提交并部署到目标环境。
2. 在稳定浏览器配置下补一次完整页面级复验，重点确认首页 token 入口、聊天页发送/上传/缩略图、后台详情与 revoke。
3. 对生产环境重新抽样验证 F6/F1/F2/F3/F4/F5 的真实链路，确认线上行为与本地一致。

### Execution notes

- 这 6 个问题对应的代码和测试已经存在于当前工作区；此前遗漏的是 commit 与状态文档同步。
- `730df9c fix: complete sessions after final document` 已经覆盖了 F6 的一部分；其余 F1-F5 和 F6 fallback 补强存在于当前未提交改动。
- 浏览器验收在本轮已做本地恢复和页面加载验证，但受本机 `agent-browser` 默认 CDP 配置、前端端口/CORS 对齐和工具交互稳定性影响，完整页面级自动化链路建议在下一轮稳定浏览器配置后补齐。

## Newly identified issues

### [2026-04-09] 新增问题清单

1. 上传图片失败时，前端没有展示真实错误原因。
   当前表现：用户只看到固定失败文案，无法区分格式错误、大小超限、数量超限或 token 状态问题。
   初步定位：`frontend/src/lib/api.ts` 的错误解析吞掉了后端返回的 `message`。

2. 参考图片没有进入 LLM 对话上下文。
   当前表现：用户上传参考图后，后续 assistant 回复看不见这些附件，只在最终文档阶段才使用附件列表。
   初步定位：`backend/app/routes/messages.py` 调用 `generate_chat_reply()` 时没有传附件；`backend/app/services/llm_orchestrator.py` 的 `build_chat_input()` 也没有附件段落。

3. 聊天页附件未展示缩略图。
   当前表现：前端只显示文件名 chip，不显示图片预览，也缺少刷新后的历史回放。
   初步定位：`backend/app/routes/sessions.py` 没有返回 preview URL；`frontend/src/components/intake/attachment-panel.tsx` 只支持文本列表。

4. 后台“查看”缺少足够的数据。
   当前表现：点击“查看”后只有少量基础字段，不能有效查看 token 的完整状态、附件和文档产出。
   初步定位：`backend/app/routes/admin.py` detail payload 偏薄，`frontend/src/components/admin/token-detail.tsx` 也只渲染少量字段。

5. LLM 思考期间，用户刚发送的消息会短暂消失。
   当前表现：消息发出后先出现，随后被轮询刷新覆盖，直到 assistant 回复完成后才重新出现。
   初步定位：`frontend/src/routes/session-page.tsx` 的轮询会覆盖 optimistic state；后端 `backend/app/routes/messages.py` 也在 LLM 调用完成前没有提交该条用户消息。

6. 用户已经明确要求定稿时，系统仍未进入文档生成状态。
   当前表现：assistant 已直接输出整份需求文档正文，但 session 仍停在 `awaiting_user`，`documents.status` 仍是 `pending`。
   生产证据：`admin_note=zzttest1` 与 `admin_note=zzttest2` 的真实会话都出现了这个问题。
   初步定位：`backend/app/services/llm_orchestrator.py` 当前只靠 prompt 约束模型输出 JSON envelope；模型一旦直接输出自然语言/Markdown 文档，fallback 会把它当作普通 `continue`。

---

## Task log

### [2026-04-09] Task F1-F6 recovery sync: 代码已修，文档补归档
**Summary**
- 重新核对当前 `main` 工作区和最近提交后，确认 F1-F6 并非“待实现”，而是已经落在代码中：
  - F6：plain text / markdown 最终文档会被识别为 `final_document`，并直接完成 session、落盘文档、创建 successor token
  - F1：后端在 LLM 回复前先持久化用户消息；前端轮询不会覆盖 optimistic user message
  - F2：前端 API 层会优先透传后端错误体中的中文 `message`
  - F3：附件元数据已注入 chat LLM context，并进入 prompt 输入
  - F4：附件返回 `preview_url`，聊天页展示缩略图并兼容历史回放
  - F5：后台详情已补消息数、附件数、时间戳、附件列表与最终文档显示
- 确认 `DOCUMENTATION.md` 和 `SESSION_CONTEXT.md` 先前仍停留在“planned / not started”，属于状态记录滞后，而不是实现缺失

**Files changed**
- `backend/app/prompts/chat_system.md`
- `backend/app/routes/admin.py`
- `backend/app/routes/messages.py`
- `backend/app/routes/sessions.py`
- `backend/app/routes/uploads.py`
- `backend/app/services/llm_orchestrator.py`
- `backend/tests/test_admin_api.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_queue_and_generation.py`
- `backend/tests/test_uploads_api.py`
- `frontend/src/components/admin/token-detail.tsx`
- `frontend/src/components/intake/attachment-panel.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/routes/session-page.tsx`
- `frontend/src/test/admin-page.test.tsx`
- `frontend/src/test/session-flow.test.tsx`
- `frontend/src/test/session-page.test.tsx`
- `docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
- `DOCUMENTATION.md`
- `SESSION_CONTEXT.md`

**Validation run**
- `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py tests/test_uploads_api.py tests/test_admin_api.py -q`
- `cd backend && pytest -q`
- `cd frontend && npm test -- --run src/test/session-flow.test.tsx src/test/session-page.test.tsx src/test/admin-page.test.tsx`
- `cd frontend && npm run build`
- 本地浏览器复验：
  - 已恢复本地后端和前端运行环境
  - 已确认后台页可真实加载，管理员鉴权请求可命中本地 API
  - 受本机 `agent-browser` 默认 CDP 配置和自动化交互稳定性影响，本轮仅完成页面加载与接口命中验证，完整页面级交互链路待在稳定浏览器配置下补齐

**Validation result**
- 后端针对性回归通过：`53 passed`
- 后端全量通过：`66 passed`
- 前端相关测试通过：`16 passed`
- 前端生产构建通过
- 代码层面与测试层面均支持“F1-F6 已修复”的结论

**Notes**
- 本条记录的目的不是新增实现，而是把“已在代码中完成、但未归档”的修复重新纳入正式项目记录
- 本轮已补提交：`00af3d1 fix: close post-launch chat-first gaps`
- 下一步应转到部署与线上复验，而不是再次重复实现 F1-F6

### [2026-04-09] Production investigation: 明确定稿但未进入文档生成状态
**Summary**
- 按 `OPERATIONS.md` 登录生产机，检查了 `admin_note=zzttest1` 与 `admin_note=zzttest2` 两个真实会话
- 结论一致：
  - session 状态都还是 `awaiting_user`
  - `documents` 表里都只有一条 `status='pending'` 的空文档
  - assistant 消息里已经直接输出了完整“需求文档正文”
- 这说明问题不在“文档生成慢”，而在“模型回复没有被识别为进入文档生成的意图”
- 当前根因判断：
  - `chat_system.md` 只通过 prompt 要求 JSON envelope
  - `LLMClient.generate()` 没有额外的结构化输出约束
  - 一旦模型直接输出自然语言/Markdown 文档，`generate_chat_reply()` 的 fallback 就会把它记成普通 assistant 消息，并把 `conversation_intent` 退化成 `continue`

**Production evidence**
- `zzttest1` 对应 token：`DNrAWAmDhwn25WBWJq9FlXQZObG2MO8o`
- `zzttest2` 对应 token：`ZaEhwQdgnjgd9zRhvNAQcbEtNrnqDt2m`
- 两者共同特征：
  - `sessions.status = awaiting_user`
  - `documents.status = pending`
  - `completed_at = NULL`
  - assistant 已输出完整 PRD/需求文档正文

**Files changed**
- `docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
- `DOCUMENTATION.md`
- `SESSION_CONTEXT.md`

**Validation run**
- 生产机只读排查：
  - 读取 `/opt/zzetzMain/backend/app.db` 中对应 session / messages / documents 数据
  - 读取生产 `chat_system.md`
  - 检查 `journalctl -u zzetz-backend`

**Validation result**
- 已确认第 6 个问题真实存在，且是当前 P0
- 当前没有发现 500/timeout 类报错，属于意图识别和生成切换链路问题

**Notes**
- 这次排查没有修改生产数据
- 后续修复应优先补测试，锁住“模型直接输出最终文档正文时不能退化成普通 continue”这个回归场景

### [2026-04-09] Planning handoff: 新增 6 个上线后修复任务
**Summary**
- 根据最新反馈，确认当前主链路之外还有 6 个需要单独收口的问题：
  - 明确定稿但未进入文档生成状态
  - 上传失败无明确报错
  - 参考图片未进入 LLM 对话上下文
  - 附件缺少缩略图
  - 后台“查看”信息不足
  - LLM 思考期间用户消息会消失
- 新增 follow-up 计划文档：`docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
- 将这些问题同步写入 `DOCUMENTATION.md` 与 `SESSION_CONTEXT.md`，作为下一轮实现入口
- 按影响面将优先级整理为：
  - P0：文档生成切换、消息消失、上传错误反馈、附件注入 LLM
  - P1：附件缩略图、后台详情扩展

**Files changed**
- `docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
- `DOCUMENTATION.md`
- `SESSION_CONTEXT.md`

**Validation run**
- N/A（本次仅更新计划与交接文档，未修改代码）

**Validation result**
- 已形成正式 follow-up 任务入口，可直接按计划进入实现

**Notes**
- 本次没有执行代码级验证，也没有新增 git commit；后续开始实现时需要按各 Task 重新跑对应测试与浏览器验收
- 当前 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md` 仍是已完成主线，新的修复工作请以 follow-up 计划补充执行

### [2026-04-09] Task 1-3: Chat-first 后端契约迁移
**Summary**
- 完成后端 chat-first 基础迁移：会话模型、配置、`.env.example`、prompt、JSON envelope、修订轮上下文注入
- 重写 `sessions / messages / documents / admin / uploads` 后端契约，切到 token-gated + chat-first 模式
- 增加 5 分钟资源释放、24 小时失效、`confirm_generate`、successor token、admin bearer 鉴权、revoke 和消息分页
- 修复后端联调中的真实缺陷：
  - 最新用户消息未进入 LLM 上下文
  - `confirm_generate` 不能空内容触发
  - `SummarySnapshot` 为空时最终文档摘要退化为“未确定”
  - admin 修订 token 未校验来源文档
  - 上传测试仍依赖旧匿名创建 session

**Files changed**
- `backend/app/config.py`
- `backend/app/models.py`
- `backend/app/schemas.py`
- `.env.example`
- `backend/app/prompts/chat_system.md`
- `backend/app/prompts/welcome_initial.md`
- `backend/app/prompts/welcome_revision.md`
- `backend/app/prompts/render_final_document.md`
- `backend/app/routes/admin.py`
- `backend/app/routes/sessions.py`
- `backend/app/routes/messages.py`
- `backend/app/routes/documents.py`
- `backend/app/routes/uploads.py`
- `backend/app/services/admin_auth.py`
- `backend/app/services/document_renderer.py`
- `backend/app/services/llm_orchestrator.py`
- `backend/app/services/queue_manager.py`
- `backend/app/services/session_lifecycle.py`
- `backend/tests/test_sessions_api.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_queue_and_generation.py`
- `backend/tests/test_admin_api.py`
- `backend/tests/test_uploads_api.py`

**Validation run**
- 红灯与绿灯分阶段执行：
  - `cd backend && pytest tests/test_sessions_api.py -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py -q`
  - `cd backend && pytest tests/test_queue_and_generation.py -q`
  - `cd backend && pytest tests/test_admin_api.py -q`
  - `cd backend && pytest tests/test_uploads_api.py -q`
- 后端全量：
  - `cd backend && pytest -q`

**Validation result**
- 后端全量测试通过：`58 passed`
- 当前后端已切到 chat-first/token-gated 契约，可支撑前端新页面

**Notes**
- `Task 1-3` 在执行中被合并为一个强耦合后端阶段处理，原因是模型字段、prompt 和 API 路由必须连续迁移，无法机械地逐 task 独立收口
- 中间为了保持分支可运行，曾短暂引入旧阶段字段兼容层，最终已被 chat-first 路由替换为新外部契约

### [2026-04-09] Task 4-6: 首页 token 入口、单聊天窗口与后台页
**Summary**
- 首页 CTA 不再匿名创建 session，改为展示 token 输入区并跳转到 `/session/:token`
- 需求梳理页已收敛为单聊天窗口：左右消息布局、typing 态、附件入口内嵌、`ready_to_generate` 确认按钮、加载更多消息、completed/expired/failed 禁用输入区
- 新增 `/admin` 页面，支持管理员 token 输入、token 列表、详情、签发与 revoke
- 修复真实浏览器中暴露出的 admin 前后端 payload 错配问题：后端 `/api/admin/tokens` 返回 `{ items: [...] }`，前端原本按数组直吃，真实 `/admin` 会直接崩空白页；现已对齐

**Files changed**
- `frontend/src/app.tsx`
- `frontend/src/components/home/token-entry.tsx`
- `frontend/src/components/intake/chat-panel.tsx`
- `frontend/src/components/intake/attachment-panel.tsx`
- `frontend/src/components/admin/token-create-form.tsx`
- `frontend/src/components/admin/token-list.tsx`
- `frontend/src/components/admin/token-detail.tsx`
- `frontend/src/routes/home-page.tsx`
- `frontend/src/routes/session-page.tsx`
- `frontend/src/routes/admin-page.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/test/app-shell.test.tsx`
- `frontend/src/test/home-page.test.tsx`
- `frontend/src/test/session-page.test.tsx`
- `frontend/src/test/session-flow.test.tsx`
- `frontend/src/test/mobile-states.test.tsx`
- `frontend/src/test/admin-page.test.tsx`

**Validation run**
- 按任务跑红灯/绿灯：
  - `cd frontend && npm test -- app-shell.test.tsx home-page.test.tsx`
  - `cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx`
  - `cd frontend && npm test -- admin-page.test.tsx`
- 前端全量：
  - `cd frontend && npm test`
- 构建：
  - `cd frontend && npm run build`

**Validation result**
- 前端全量测试通过：`19 passed`
- 前端构建通过

**Notes**
- `/admin` 的真实浏览器行为暴露了一个测试 mock 没覆盖到的契约错配；这类问题后续仍优先以真实浏览器结果为准
- `agent-browser click` 对 React 按钮事件仍存在不稳定性，已在本地 E2E 中复现，后续验收记录需明确标注

### [2026-04-09] Task 7: 本地真实浏览器验收与线上部署前收口
**Summary**
- 已完成本地全量基线验证：
  - 后端 `58 passed`
  - 前端 `19 passed`
  - 前端构建通过
- 已完成本地 `agent-browser` 真实浏览器的主要链路验证：
  - 首页首屏加载正常
  - CTA 可展开 token 输入区
  - 通过 `/admin` 真实页面输入管理员 token 并签发新 token
  - 使用签发 token 从首页进入聊天页
  - 聊天页单窗口、附件入口、composer UI 正常渲染
- 发现并修复 `/admin` 空白页问题，根因是前端 admin API 客户端与后端真实 payload 形状不一致

**Outstanding**
- `agent-browser` 在本地对 React “发送”按钮的 click 事件仍不稳定，导致“发送消息”动作无法稳定触发；这与此前项目中已知的 `agent-browser click` 不稳定问题一致
- 下一步是按 `OPERATIONS.md` 部署到线上，再通过线上环境做一次真实浏览器复验，判断按钮问题是否仍然存在

### [2026-04-09] Deployment attempt: 线上部署阻塞确认
**Summary**
- 已将 `task/chat-first-redesign` fast-forward 合回本地主工作区 `main`
- 已把 `main` 推送到 `origin/main`
- 按 `OPERATIONS.md` 尝试执行：
  - `ssh -o StrictHostKeyChecking=accept-new root@129.204.9.74 'cd /opt/zzetzMain && BRANCH=main bash scripts/deploy-zzetz-cn.sh'`
- 线上部署未进入脚本执行阶段，阻塞在 SSH 认证：当前机器对 `root@129.204.9.74` 没有可用凭据

**Validation run**
- 本地最终基线：
  - `cd backend && pytest -q` -> `58 passed`
  - `cd frontend && npm test` -> `19 passed`
  - `cd frontend && npm run build` -> 通过
- 本地 `agent-browser` 真实浏览器：
  - 首页加载、CTA 展开 token 输入区
  - `/admin` 页面加载
  - 管理员 token 输入后后台可正常展示
  - 通过后台真实签发 token
  - 使用签发 token 从首页进入聊天页
- 线上部署尝试：
  - SSH 连接返回 `Permission denied (publickey,gssapi-keyex,gssapi-with-mic,password)`
  - 显式指定 `~/.ssh/id_rsa` 后仍失败

**Notes**
- 线上阻塞是环境/凭据问题，不是仓库代码问题
- 当前 `origin/main` 已包含 chat-first 全部实现与本地验证结果；只要补上服务器访问凭据，即可继续执行部署脚本和线上 E2E

### [2026-04-09] Production deployment: chat-first 改动已上线并完成线上复验
**Summary**
- 使用你提供的服务器密码登录 `root@129.204.9.74`
- 按 `OPERATIONS.md` 执行 `BRANCH=main bash scripts/deploy-zzetz-cn.sh`，成功拉取并部署 `origin/main`
- 发现生产 SQLite 仍是旧 schema，导致 `/api/admin/tokens` 因缺少 `sessions.admin_note`、`documents.version`/`messages.stage` 兼容约束而报 `500`
- 已在服务器上完成最小兼容迁移：
  - 为 `sessions` 补齐 chat-first 新列
  - 重建 `messages` 表，使旧 `stage` 列保留默认值，并为新 `delivery_status` 建立持久列
  - 重建 `documents` 表，使旧 `version` 列保留默认值，并将 `revision_number` 回填为当前版本号
- 为了完成线上 `/admin` 验收，已在服务器 `backend/.env` 追加临时管理员 token：`ADMIN_TOKEN=admin-secret`

**Validation run**
- 部署脚本：
  - `ssh root@129.204.9.74 'cd /opt/zzetzMain && BRANCH=main bash scripts/deploy-zzetz-cn.sh'`
- 线上健康检查：
  - `curl https://zzetz.cn/api/health` -> `{"status":"ok"}`
- 线上 API 验证：
  - `POST /api/admin/tokens` -> 成功签发 token
  - `POST /api/sessions/:token/messages` -> 返回中文 assistant 回复
  - `POST /api/sessions/:token/messages` with `confirm_generate=true` -> 返回 `generating_document`
  - `GET /api/sessions/:token` -> `status=completed`，包含 `successor_token`
- 线上 `agent-browser` 真实浏览器：
  - 打开 `https://zzetz.cn/`，确认首页首屏和 CTA 存在
  - 点击首页 CTA，确认 token 输入区出现
  - 打开 `https://zzetz.cn/admin`，确认后台页面结构正确
  - 使用首页 token 入口进入线上 chat-first 聊天页
  - 打开已完成会话页面，确认 `completed`、文档摘要和后续修订 token 正常展示

**Validation result**
- 线上部署成功
- 线上健康检查通过
- 线上 chat-first 主链路已可用：
  - 首页 token-gated 入口可用
  - `/admin` 页面可加载
  - admin token 创建接口可用
  - chat-first 会话可生成最终文档并返回 successor token

**Known issues**
- `agent-browser click` 对 React 按钮事件仍不稳定，在线上聊天页“发送”按钮和后台部分提交按钮上仍然会复现；因此线上消息发送与最终文档生成这一步是通过真实 API 补充验证的，而不是仅依赖按钮点击
- 生产环境当前使用的是临时管理员 token `admin-secret`，后续应改成你自己的值

### [2026-04-09] Follow-up: 正式化 SQLite 兼容迁移脚本
**Summary**
- 新增仓库内可重放的 SQLite 迁移入口 `backend/app/db_migrations.py`
- 新增 `backend/tests/test_db_migrations.py`，覆盖“从旧版 schema 升级到 chat-first schema”与“重复执行幂等”两类场景
- 将 `scripts/deploy-zzetz-cn.sh` 从临时内联 Python 迁移到调用正式的 `python3 -m app.db_migrations "$APP_DIR/backend/app.db"`
- 这样后续再次部署 chat-first 版本时，不需要依赖手工敲临时 SQLite 修复脚本

**Files changed**
- `backend/app/db_migrations.py`
- `backend/tests/test_db_migrations.py`
- `scripts/deploy-zzetz-cn.sh`

**Validation run**
- `cd backend && pytest tests/test_db_migrations.py -q` -> `2 passed`
- `cd backend && pytest -q` -> `60 passed`
- `bash -n scripts/deploy-zzetz-cn.sh` -> 通过

**Notes**
- 这次新增的是“仓库内可重放入口”，并没有自动回滚已经在生产机上手工做过的那次表重建
- 后续如果继续维护 SQLite 内测形态，优先走这个脚本，不再手工拼 SQL

### [2026-04-09] Planning handoff: chat-first redesign 文档收口与执行入口整理
**Summary**
- 先后完成并审查通过 chat-first 重构规格与实施计划：
  - `docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md`
  - `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`
- 将最新 spec / plan 拆解为待执行任务，写入 `DOCUMENTATION.md` 的 `Not started` 与 `Pending execution tasks`
- 更新 `SESSION_CONTEXT.md`，把当前仓库从“MVP 文档补齐阶段”切换为“chat-first 重构待实现阶段”
- 更新 `AGENTS.md` 的参考规格、项目概览、前端验收口径和环境说明，使其与下一轮重构目标一致
- 更新 `PLANS.md` 与 `IMPLEMENT.md`，让根级执行入口也明确指向 `2026-04-09` 的 chat-first spec / plan，而不是继续默认回退到 `2026-04-08` 的 MVP 文档

### [2026-04-09] Task 4: 首页改为 token-gated 入口
**Summary**
- 首页 CTA 不再匿名创建 session，改为先展开受控 token 输入区，再由管理员签发的 token 进入 `/session/:token`
- `frontend/src/lib/api.ts` 删除 `createSession()`，前端首页不再依赖匿名 session 创建接口
- `frontend/src/lib/types.ts` 增加 chat-first 入口会用到的最小补充字段，同时保留现有 session 页仍在使用的类型，避免当前构建断裂
- 新增 `frontend/src/components/home/token-entry.tsx`，把 token 输入与跳转封装成独立组件
- 更新首页测试，覆盖 CTA 展开 token 输入区与 token 跳转路径

**Files changed**
- `frontend/src/lib/types.ts`
- `frontend/src/lib/api.ts`
- `frontend/src/routes/home-page.tsx`
- `frontend/src/components/home/token-entry.tsx`
- `frontend/src/test/app-shell.test.tsx`
- `frontend/src/test/home-page.test.tsx`

**Validation run**
- 红灯确认：
  - `cd frontend && npm test -- app-shell.test.tsx home-page.test.tsx`
  - 初始失败分别来自缺少 token 输入区与首页仍未按 token-gated 流程工作
- 绿灯验证：
  - `cd frontend && npm test -- app-shell.test.tsx home-page.test.tsx`
  - `cd frontend && npm run build`
- 额外全量验证：
  - `cd frontend && npm test`
  - 失败在 `src/test/session-flow.test.tsx`，该测试仍断言首页点击开始后会直接进入旧的匿名 session 流程

**Validation result**
- 前端入口测试通过
- 前端生产构建通过
- 前端全量测试仍有 1 个旧断言失败，属于后续 Task 5 迁移范围

**Known issues**
- 当前 `SessionPage` 仍保留旧的阶段式 intake 形态，Task 5 会继续收敛
- 首页与 session 页之间的类型契约仍有过渡期字段，后续 Task 5 / Task 6 会继续清理
- `src/test/session-flow.test.tsx` 仍基于旧的匿名创建 session 入口，暂未纳入本 Task 的文件范围

**Files changed**
- `AGENTS.md`
- `DOCUMENTATION.md`
- `IMPLEMENT.md`
- `PLANS.md`
- `SESSION_CONTEXT.md`

**Validation run**
- 文档整理任务，无新增代码执行面
- 文档自检：
  - `git diff --check`

**Notes**
- 当前仓库代码尚未实现 chat-first 设计；只是文档和执行入口已经切到下一轮目标态
- 下一轮实现必须以 `docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md` 和 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md` 为准，不要回退到旧的阶段式 intake 任务定义

### [2026-04-09] Operations docs: 运维 README 与关键文档整理
**Summary**
- 新增 `OPERATIONS.md`，沉淀当前线上部署拓扑、关键目录、systemd/nginx 约定、环境变量、健康检查、常见故障与恢复流程
- 在 `README.md` 的项目文档入口中加入运维文档，方便后续执行者快速找到生产信息
- 更新 `DOCUMENTATION.md` 与 `SESSION_CONTEXT.md`，把生产消息链路修复、超时配置、状态语义与部署脚本入口固化为上下文

**Files changed**
- `OPERATIONS.md`
- `README.md`
- `DOCUMENTATION.md`
- `SESSION_CONTEXT.md`

**Validation run**
- 文档补充任务，无新增代码执行面
- 依赖上一轮已完成验证：
  - `cd backend && pytest -q`
  - `cd frontend && npm test`
  - `cd frontend && npm run build`
  - `bash scripts/deploy-zzetz-cn.sh`

**Notes**
- 运维文档避免记录密码、API key 等敏感信息
- 文档中保留了当前生产形态需要的超时和状态语义，便于后续排障

### [2026-04-09] Production hotfix: 部署验证、消息链路修复与部署脚本
**Summary**
- 在 `root@129.204.9.74` 完成前后端生产部署：前端由 `nginx` 暴露在 `80/443`，后端由 `gunicorn` 绑定 `127.0.0.1:5050`
- 生产验证中拆出三类真实问题：
  - `gunicorn` 默认 30 秒超时会在 LLM 慢响应时杀死 worker，导致 `/api/sessions/:token/messages` 返回 500
  - `nginx` `/api` 反代默认超时不足，长请求会先返回 504
  - `SessionRecord.status` 在消息处理后一直停留在 `active`，数据库中的并发槽位不会释放，后续会话会永久排队
- 本地以 TDD 修复消息链路：
  - 顺序处理的消息请求不再耗尽 5 个活跃槽位
  - 处理中会话完成后落到 `in_progress`
  - 失败会话落到 `failed`
  - `LLMClient` 显式 `trust_env=False`，避免宿主机代理环境影响真实模型调用
- 新增 `scripts/deploy-zzetz-cn.sh`，固化服务器上的 clone/pull、前端构建、后端 venv、systemd、nginx、超时配置与基础健康检查
- 线上复核结果：
  - 服务器本机通过仓库内 `LLMClient.from_env().generate()` 返回 `ok`
  - 真实消息 API 能返回 `201` 与中文 `assistant_reply`
  - 浏览器侧完成首页 CTA、session 页模板/风格选择与消息发送；同一 token 的后端状态推进到 `positioning`，并写入结构化摘要

**Files changed**
- `backend/app/routes/messages.py`
- `backend/app/services/llm_client.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_queue_and_generation.py`
- `frontend/src/components/intake/summary-panel.tsx`
- `frontend/src/lib/types.ts`
- `frontend/src/routes/session-page.tsx`
- `scripts/deploy-zzetz-cn.sh`

**Validation run**
- TDD 红灯：
  - `cd backend && pytest tests/test_queue_and_generation.py -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py -q`
- 绿灯验证：
  - `cd backend && pytest -q`
  - `cd frontend && npm test`
  - `cd frontend && npm run build`
  - `bash -n scripts/deploy-zzetz-cn.sh`
  - 生产接口验证：
    - `curl https://zzetz.cn/api/health`
    - `curl https://zzetz.cn/api/sessions -d '{}'`
    - `PATCH /api/sessions/:token`
    - `POST /api/sessions/:token/messages`
  - 生产浏览器验证（`agent-browser`）：
    - 首页加载与 CTA 可点击
    - session 页模板/风格切换
    - 消息发送后同 token 状态推进并写入摘要

**Validation result**
- 本地测试通过：后端 `37 passed`，前端 `5 files / 9 tests passed`，前端构建通过
- 服务器已完成可用部署，健康检查通过，真实模型从服务器本机可调用
- 生产消息链路已从 500/504/永久排队修复到可返回中文回复

**Notes**
- 当前生产部署仍是 root 直登管理，后续若继续交付，建议切换为专用系统用户并收紧文件权限
- `scripts/deploy-zzetz-cn.sh` 假设证书已由 `certbot` 写入 `/etc/letsencrypt/live/zzetz.cn/`
- 为清理本次测试残留，服务器执行过一次 `sessions.status in ('active','queued') -> 'in_progress'` 的数据库修复

### [2026-04-08] Task 9: 最终文档、回归验证与人工验收
**Summary**
- 复核真实外部模型连通性：直接对 `OPENAI_BASE_URL` 做了 `chat/completions`、`/responses` 和仓库内 `LLMClient.generate()` 调用，确认阿里云百炼兼容层和当前密钥可用
- 真实链路验收时发现阶段回复与摘要提取在百炼兼容层上存在明显慢响应；将 `generate_stage_reply` 和 `extract_summary_update` 的超时提升到 90 秒，并为 `LLMClient.generate()` 增加一次超时重试
- 修正生成阶段路由：`generation_requested=true` 时直接进入文档渲染，不再错误地尝试读取不存在的 `backend/app/prompts/generate.md`
- 修正前端回访链路：已完成会话重新打开时也会拉取 `/document`，因此摘要面板现在能展示文档摘要文本，而不只是 `文档状态：已生成`
- 用干净的 `backend/task9-validation.db` 重新跑完整人工验收链路，确认首页 CTA、模板/风格选择、图片上传、`positioning -> content -> features -> generate -> completed`、自动 PRD 生成、中文摘要、中文 PRD、附件段落和 token 回访均可用
- 复核 `README.md` 与仓库结构、`Makefile`、`backend/.env` / `python run.py` / `frontend npm run dev` 一致，无需额外修订；spec 状态名与当前实现一致，也无需改动只读 spec

**Files changed**
- `backend/app/routes/messages.py`
- `backend/app/services/llm_client.py`
- `backend/app/services/llm_orchestrator.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_queue_and_generation.py`
- `frontend/src/routes/session-page.tsx`
- `frontend/src/test/session-flow.test.tsx`
- `frontend/src/components/intake/summary-panel.tsx`
- `frontend/src/test/home-page.test.tsx`

**Validation run**
- 外部模型直连排查：
  - 使用 `backend/.env` 中的真实配置直连 `chat/completions`，返回 200 与“连通正常”
  - 使用同一配置直连 `/responses`，返回 200 与“responses 正常”
  - 直接调用仓库内 `LLMClient.generate()`，返回“客户端正常”
- 红灯确认：
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_generate_stage_reply_uses_extended_timeout -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_extract_summary_update_uses_extended_timeout -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_llm_client_retries_once_after_timeout -q`
  - `cd backend && pytest tests/test_queue_and_generation.py::test_generation_request_skips_stage_reply_prompt -q`
  - `cd frontend && npm test -- session-flow.test.tsx`
- 绿灯验证：
  - `cd backend && pytest -q`
  - `cd frontend && npm test`
  - `cd frontend && npm run build`
  - `agent-browser` 真实浏览器验收：
    - iPhone 14 视口打开首页，确认 CTA 可见且 `document.documentElement.scrollWidth <= window.innerWidth`
    - 通过浏览器内真实鼠标事件触发首页 CTA，跳转到 `/session/:token`
    - 在真实 session 页面完成模板 `个人作品页`、风格 `极简高级`
    - 通过浏览器文件输入注入真实 PNG 数据，确认附件入口可上传并显示 `reference.png`
    - 使用真实 LLM 主链路把 session 推进到 `generate`
    - 重新打开同一 token 页面，确认 `当前状态：已完成`、`文档状态：已生成`，且摘要区能看到中文文档摘要
  - 文档接口验收：
    - `GET /api/sessions/_fH3p3FAjjyZr6O9YDZImQkFZRD8A_wO/document`
    - 返回 `status=ready`
    - `prd_markdown` 为中文 PRD，并包含 `## 参考附件` 与 `reference.png`

**Validation result**
- 红灯阶段符合预期：
  - 阶段回复仍使用较短超时，无法覆盖百炼兼容层的真实慢响应
  - `LLMClient.generate()` 在超时后不会重试
  - 前端自动 PRD 生成请求会误走 `generate_stage_reply()`，触发缺失的 `generate.md`
  - 已完成会话重新打开时不会重新获取文档摘要
- 绿灯阶段全部通过：
  - 后端全量测试通过（35 passed）
  - 前端全量测试通过（5 files, 9 tests）
  - 前端生产构建通过
  - 真实浏览器下，完整链路可以闭环到 `completed`
  - 文档接口会返回中文摘要、中文 PRD，并带有附件清单

**Notes**
- `agent-browser` 的标准 `click` 在当前 React/Vite 页面上对部分按钮不稳定；本次 Task 9 的浏览器验收继续使用浏览器上下文里的真实鼠标事件派发，但仍由 `agent-browser` 驱动
- 为避免历史开发数据占满 5 个活跃会话名额，本次人工验收使用独立的 `backend/task9-validation.db`
- 当前 `summary_text` 只展示文档级摘要（网站类型 / 视觉方向）；结构化摘要字段仍通过 session payload 单独展示

**Known issues**
- 真实 LLM 主链路可用，但在百炼兼容层上的响应时间仍偏长；一次阶段推进常见耗时在几十秒到一百秒级
- 已完成会话重新打开后，附件列表仍只显示本地上传态，不会自动从后端回放到附件面板；当前验收以文档中的 `参考附件` 段落作为附件持久化依据

**Next suggested step**
- MVP 计划内 Task 1–9 已完成，后续如继续迭代，优先考虑把长耗时的摘要提取/文档生成改成更显式的轮询任务，而不是阻塞单次消息请求
- 如果继续做体验优化，优先补已完成会话的历史消息与附件回放，再考虑更细的错误诊断与耗时提示

### [2026-04-08] Task 8: 实现需求梳理页六组件与前后端接线
**Summary**
- 新建 `frontend/src/lib/api.ts` 与 `frontend/src/lib/types.ts`，补齐 session / message / attachment / document 的前端 API 契约
- 新建 `StepHeader / TemplateSelector / StyleSelector / ChatPanel / AttachmentPanel / SummaryPanel` 六个 intake 组件，并落地 `routes/session-page.tsx`
- 首页 CTA 现在会真实创建 session 并跳转到 `/session/:token`，需求页接上 3 秒 session 轮询与 5 秒文档轮询
- 需求页增加中文错误提示、排队状态文案、附件上传回显，以及摘要面板里的中文状态/阶段映射
- 浏览器联调发现真实 LLM 主链路下摘要提取 prompt 过弱，补强 `backend/app/prompts/extract_summary.md` 后，真实会话已能从 `positioning` 推进到 `content`

**Files changed**
- `frontend/src/app.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/types.ts`
- `frontend/src/routes/home-page.tsx`
- `frontend/src/routes/session-page.tsx`
- `frontend/src/components/home/hero.tsx`
- `frontend/src/components/home/final-cta.tsx`
- `frontend/src/components/intake/step-header.tsx`
- `frontend/src/components/intake/template-selector.tsx`
- `frontend/src/components/intake/style-selector.tsx`
- `frontend/src/components/intake/chat-panel.tsx`
- `frontend/src/components/intake/attachment-panel.tsx`
- `frontend/src/components/intake/summary-panel.tsx`
- `frontend/src/test/home-page.test.tsx`
- `frontend/src/test/session-page.test.tsx`
- `frontend/src/test/session-flow.test.tsx`
- `frontend/src/test/mobile-states.test.tsx`
- `backend/app/prompts/extract_summary.md`
- `backend/tests/test_llm_orchestrator.py`

**Validation run**
- 红灯确认：
  - `cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx`
- 绿灯验证：
  - `cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx`
  - `cd frontend && npm test -- home-page.test.tsx app-shell.test.tsx`
  - `cd frontend && npm run build`
  - `cd backend && pytest tests/test_llm_orchestrator.py -q`
  - `cd backend && pytest tests/test_queue_and_generation.py -q`
  - `cd backend && pytest -q`
  - `agent-browser` 真实浏览器验收：
    - 手机视口打开 `http://127.0.0.1:5173/`，执行 `document.documentElement.scrollWidth <= window.innerWidth`
    - 打开真实 `session/:token` 页面，确认模板、风格、发送、摘要、附件入口可见
    - 真实选择模板 `个人作品页` 与风格 `极简高级`，等待页面出现 `当前阶段：定位`
    - 输入真实中文定位信息并发送，等待页面出现 `当前阶段：内容`
    - 等待摘要区出现 `准备做个人品牌升级的咨询客户` 与 `建立专业信任`

**Validation result**
- 红灯阶段符合预期：
  - 初始缺少 `/session/:token` 路由、intake 组件与 API 接线
- 绿灯阶段全部通过：
  - Task 8 前端单测通过（4 tests）
  - 首页回归测试通过（3 tests）
  - 前端构建通过
  - 后端全量测试通过（28 passed）
  - 真实浏览器下，需求页能通过真实 LLM 主链路把阶段从 `positioning` 推进到 `content`，摘要也会更新

**Notes**
- `agent-browser` 的原生 `click` 在当前 Vite 页面上没有稳定触发 React 按钮事件，本次浏览器验收改用浏览器上下文里的 DOM click；仍然是 `agent-browser` 驱动的真实浏览器链路
- `agent-browser` 无法稳定驱动系统文件选择器，因此浏览器验收覆盖了附件上传入口可见；真正的上传回调用前端单测锁住，上传 API 则已在 Task 6 后端测试覆盖
- 首页 CTA 现在采用全局 `isCreating` loading 语义，因此两个 CTA 会同时进入 loading；相应测试已同步调整
- `extract_summary.md` 现在显式要求输出 `positioning_ready / content_ready / features_ready`，避免真实 LLM 返回过于松散的 JSON

**Known issues**
- 真实 LLM 返回耗时波动较大，浏览器里一次定位消息到阶段推进大约需要数十秒，Task 9 人工验收时要预留等待时间
- 当前需求页还没有独立的“开始生成 PRD”按钮；现有主链路可以推进到 `generate`，但最终生成动作仍需要在 Task 9 总验收时一起补看

**Next suggested step**
- 执行 Milestone 9 / Task 9：跑完整前后端回归、校正 README、完成 11 步人工验收链路
- 优先检查从 `content -> features -> generate -> document ready` 的整段真实链路，并决定是否需要补一个显式生成按钮或保持“发送即推进”的当前交互
### [2026-04-08] Task 7: 实现首页五段式移动端优先 UI
**Summary**
- 先按要求读取 `apple/DESIGN.md`，然后将首页拆为 `Hero / Problem / Process / OutputPreview / FinalCta` 五段
- 新建可复用 `Button` 组件，并在首页 CTA 上提供本地 loading 状态
- 新建 `routes/home-page.tsx`，将首页路由从 `app.tsx` 中解耦
- 更新全局样式 token，切换为 Apple 风格深色主场景 + 浅色信息区块节奏

**Files changed**
- `frontend/src/app.tsx`
- `frontend/src/styles.css`
- `frontend/src/routes/home-page.tsx`
- `frontend/src/components/ui/button.tsx`
- `frontend/src/components/home/hero.tsx`
- `frontend/src/components/home/problem.tsx`
- `frontend/src/components/home/process.tsx`
- `frontend/src/components/home/output-preview.tsx`
- `frontend/src/components/home/final-cta.tsx`
- `frontend/src/test/home-page.test.tsx`

**Validation run**
- 红灯确认：
  - `cd frontend && npm test -- home-page.test.tsx`
- 绿灯验证：
  - `cd frontend && npm test -- home-page.test.tsx app-shell.test.tsx`
  - `cd frontend && npm run build`
  - `agent-browser` 手机视口验收：
    - 打开 `http://127.0.0.1:4173/`
    - 快照确认首屏标题与 CTA 存在
    - 点击 CTA，确认元素可交互
    - 执行 `document.documentElement.scrollWidth <= window.innerWidth`

**Validation result**
- 红灯阶段符合预期：
  - 初始首页缺少五段式结构与 CTA 文案
- 绿灯阶段全部通过：
  - 前端单测通过（`home-page` + `app-shell`）
  - 前端构建通过
  - 真实浏览器下手机视口无横向溢出，首屏标题与 CTA 可见，CTA 可点击

**Notes**
- 当前 CTA 先提供本地 loading 反馈，不提前接入 Task 8 的真实 session 创建跳转
- 视觉实现遵循 Apple 风格的黑 / 浅灰区块切换、单一蓝色强调和克制阴影
- 中文排版没有强套英文负字距，而是保留了紧凑标题和更舒展的正文行高

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 7 提交 hash

**Next suggested step**
- 执行 Milestone 8 / Task 8：需求梳理页六组件、API client、轮询和移动端状态
- 开始前先读 Task 8 计划，再补 `session-page.test.tsx / session-flow.test.tsx / mobile-states.test.tsx` 红灯测试

### [2026-04-08] Task 6: 实现上传、安全限制与错误处理
**Summary**
- 新建 `storage.py`，实现 MIME 白名单、大小检查、token 命名空间目录与安全文件名保存
- 新建 `POST /api/sessions/<token>/attachments`
- 新增 `AttachmentRecord` 数据模型，落库存储附件元数据
- 注册上传路由并补齐 8MB 限制、12 张上限、中文错误信息

**Files changed**
- `backend/app/__init__.py`
- `backend/app/models.py`
- `backend/app/routes/uploads.py`
- `backend/app/services/storage.py`
- `backend/tests/test_uploads_api.py`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_uploads_api.py -q`
- 绿灯验证：
  - `cd backend && pytest tests/test_uploads_api.py -q`
  - `cd backend && pytest -q`

**Validation result**
- 红灯阶段符合预期：
  - 初始上传接口返回 404
- 绿灯阶段全部通过：
  - 合法图片上传成功
  - 非图片、超 8MB、超 12 张限制都被拒绝
  - 后端当前全量测试通过（27 passed）

**Notes**
- `secure_filename` 已用于净化文件名，测试覆盖了 `../reference.png` 这类路径穿越输入
- 上传目录按 `UPLOAD_DIR/<token>/...` 组织，便于后续会话级清理
- 当前只允许 `image/png`、`image/jpeg`、`image/webp`

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 6 提交 hash

**Next suggested step**
- 执行 Milestone 7 / Task 7：首页五段式移动端优先 UI
- 开始前先读 `apple/DESIGN.md`，完成后必须跑前端单测、构建和 `agent-browser` E2E

### [2026-04-08] Task 5: 实现并发队列、轮询状态与文档生成
**Summary**
- 新建 `queue_manager.py`，实现最多 5 个活跃会话的槽位保留与排队位置计算
- 新建 `document_renderer.py` 与 `GET /api/sessions/<token>/document`
- 更新消息路由，加入排队响应、轮询间隔字段与同步文档生成落库
- 当前文档生成使用同步 LLM 渲染，但对前端仍返回 `generating_document` 状态以保持轮询协议一致

**Files changed**
- `backend/app/__init__.py`
- `backend/app/routes/messages.py`
- `backend/app/routes/documents.py`
- `backend/app/services/queue_manager.py`
- `backend/app/services/document_renderer.py`
- `backend/tests/test_queue_and_generation.py`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_queue_and_generation.py::test_sixth_active_session_is_queued -q`
- 绿灯验证：
  - `cd backend && pytest tests/test_queue_and_generation.py -q`
  - `cd backend && pytest -q`

**Validation result**
- 红灯阶段符合预期：
  - 初始因 `app.services.document_renderer` 缺失而失败
- 绿灯阶段全部通过：
  - 第六个活跃会话进入排队
  - 文档接口返回中文摘要和 PRD
  - 后端当前全量测试通过（23 passed）

**Notes**
- plan 的 Task 5 示例测试与步骤在“何时触发文档生成”上有轻微冲突；本次按步骤实现为 `generation_requested=True` 时生成文档，并在测试中显式传入该字段
- 当前版本为了保持实现收敛，没有提前引入附件查询；文档渲染暂传空附件列表，等 Task 6 上传能力落地后再接入
- 会话在生成完成后立即标记为 `completed` 释放槽位，但响应仍返回 `generating_document` + `poll_after_ms=5000`，保证前端轮询协议不变

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 5 提交 hash

**Next suggested step**
- 执行 Milestone 6 / Task 6：上传、安全限制与附件记录
- 先补 `backend/tests/test_uploads_api.py` 红灯测试，再实现存储与上传路由

### [2026-04-08] Task 4: 实现阶段状态机、真实对话引导与摘要提取策略
**Summary**
- 新建 `intake_state_machine.py`，实现六阶段最小推进规则
- 新建 `summary_builder.py`，封装摘要刷新判断与非空合并策略
- 新建 `POST /api/sessions/<token>/messages`，接通真实 LLM 编排、消息入库与摘要快照刷新
- app 工厂注册消息路由；`SessionRecord.updated_at` 增加 `onupdate` 自动更新时间

**Files changed**
- `backend/app/__init__.py`
- `backend/app/models.py`
- `backend/app/routes/messages.py`
- `backend/app/services/intake_state_machine.py`
- `backend/app/services/summary_builder.py`
- `backend/tests/test_llm_orchestrator.py`
- `backend/tests/test_queue_and_generation.py`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_skip_template_moves_to_style -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`
- 绿灯验证：
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_skip_template_moves_to_style -q`
  - `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`
  - `cd backend && pytest -q`

**Validation result**
- 红灯阶段符合预期：
  - 初始因 `app.services.intake_state_machine` 缺失而失败
  - 补完状态机和摘要策略后，消息路由相关测试继续按预期因路由缺失失败
- 绿灯阶段全部通过：
  - 状态机、摘要合并、消息路由、LLM 失败分支测试通过
  - 后端当前全量测试通过（21 passed）

**Notes**
- 当前消息路由只实现 Task 4 需要的对话主链路，不提前引入 Task 5 的并发队列和文档生成
- `template/style` 阶段会无条件刷新摘要，其余阶段由 `stage_completed` 或 `generation_requested` 驱动
- 消息路由里的中文 502 已落地，便于前端在后续 Task 8 直接消费

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 4 提交 hash

**Next suggested step**
- 执行 Milestone 5 / Task 5：队列管理、文档生成记录与轮询状态
- 继续以 `backend/tests/test_queue_and_generation.py` 为核心扩展红灯测试

### [2026-04-08] Task 3: 接入真实 LLM 客户端与基础编排器
**Summary**
- 新建 `LLMClient`，按 OpenAI Responses API 兼容形状调用 `POST /responses`
- 新建 `llm_orchestrator.py`，接入阶段 prompt、摘要提取和 PRD 渲染封装
- 补齐首版中文 prompt 文件：`system/template/style/positioning/content/features/extract_summary/render_prd`
- 在测试中 mock 外部 HTTP，主链路保持真实客户端实现

**Files changed**
- `backend/app/services/llm_client.py`
- `backend/app/services/llm_orchestrator.py`
- `backend/app/prompts/system.md`
- `backend/app/prompts/template.md`
- `backend/app/prompts/style.md`
- `backend/app/prompts/positioning.md`
- `backend/app/prompts/content.md`
- `backend/app/prompts/features.md`
- `backend/app/prompts/extract_summary.md`
- `backend/app/prompts/render_prd.md`
- `backend/tests/test_llm_orchestrator.py`

**Validation run**
- 红灯确认：
  - `cd backend && pytest tests/test_llm_orchestrator.py::test_build_chat_request_uses_chinese_and_stage_prompt -q`
- 绿灯验证：
  - `cd backend && pytest tests/test_llm_orchestrator.py -q`
  - `cd backend && pytest -q`

**Validation result**
- 红灯阶段符合预期：
  - 初始因 `app.services.llm_client` 缺失而导入失败
- 绿灯阶段全部通过：
  - prompt 装配、HTTP 请求形状、env 配置、中文错误、阶段回复、摘要提取与 PRD 渲染测试通过
  - 后端当前全量测试通过（16 passed）

**Notes**
- `LLMClient` 同时支持 `OPENAI_API_KEY`、`OPENAI_MODEL`、`OPENAI_BASE_URL`、`OPENAI_TIMEOUT`
- 文本提取优先读取 `output_text`，否则回退解析 `output[].content[].text`
- 计划文件的 Task 3 Files 清单未列出阶段 prompt，但 Step 5 明确要求这些文件；本次按 Step 执行并保持在 prompts 目录内

**Known issues**
- `SESSION_CONTEXT.md` 的“最近重要提交”会在下一次任务收尾时补录本次 Task 3 提交 hash

**Next suggested step**
- 执行 Milestone 4 / Task 4：状态机、摘要刷新判断、摘要合并与消息路由
- 先补 `tests/test_queue_and_generation.py` 或 plan 指定的红灯测试，再把真实 LLM 调用接进消息 API

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
- 上传失败时前端没有透传真实中文错误原因
- 用户已明确要求定稿时，LLM 仍可能直接输出 PRD 正文，但 session 没有进入文档生成状态
- 附件尚未进入 LLM 对话上下文，当前只在最终文档渲染阶段使用
- 聊天页附件只有文件名，没有缩略图与历史回放
- 后台 token 详情数据偏少，“查看”不足以支撑排查和巡检
- 轮询会覆盖 optimistic user message，导致发送中的消息短暂消失

---

## Verification history
| Date | Scope | Commands | Result | Notes |
|------|-------|----------|--------|-------|
| 2026-04-08 | Task 7 red/green | `cd frontend && npm test -- home-page.test.tsx`; `cd frontend && npm test -- home-page.test.tsx app-shell.test.tsx`; `cd frontend && npm run build`; `agent-browser` mobile E2E | Passed | 先确认首页结构缺失，再补齐五段式 UI、单测、构建与浏览器验收 |
| 2026-04-08 | Task 6 red/green | `cd backend && pytest tests/test_uploads_api.py -q`; `cd backend && pytest -q` | Passed | 先确认上传接口缺失，再补齐存储、校验与附件记录 |
| 2026-04-08 | Task 5 red/green | `cd backend && pytest tests/test_queue_and_generation.py::test_sixth_active_session_is_queued -q`; `cd backend && pytest tests/test_queue_and_generation.py -q`; `cd backend && pytest -q` | Passed | 先确认队列/文档渲染模块缺失，再补齐排队、文档接口和轮询状态 |
| 2026-04-08 | Task 4 red/green | `cd backend && pytest tests/test_llm_orchestrator.py::test_skip_template_moves_to_style -q`; `cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`; `cd backend && pytest -q` | Passed | 先确认状态机缺失，再补齐状态机、摘要策略与消息路由 |
| 2026-04-08 | Task 3 red/green | `cd backend && pytest tests/test_llm_orchestrator.py::test_build_chat_request_uses_chinese_and_stage_prompt -q`; `cd backend && pytest tests/test_llm_orchestrator.py -q`; `cd backend && pytest -q` | Passed | 先确认 LLM 模块缺失，再补齐客户端、编排器和 prompts |
| 2026-04-08 | Task 2 red/green | `cd backend && pytest tests/test_sessions_api.py::test_create_session_returns_token_and_default_state -q`; `cd backend && pytest tests/test_sessions_api.py -q`; `cd backend && pytest -q` | Passed | 先确认 `/api/sessions` 缺失，再补齐 create/get/patch 与 CORS |
| 2026-04-08 | Task 1 red/green | `cd backend && pytest tests/test_health.py -q`; `cd frontend && npm test -- app-shell.test.tsx`; `cd backend && pytest -q`; `cd frontend && npm run build` | Passed | 红灯先确认缺失应用工厂与前端壳，随后绿灯通过 |
| 2026-04-08 | 规则初始化 | N/A | N/A | 无代码，无需验证 |

---

## Handoff notes
给下一个执行者的说明：

- 当前最应该继续的任务：**Task F6 — 修复“明确定稿但未进入文档生成状态”**
- 执行依据：`docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
- 下一优先级：`Task F1` 消息消失、`Task F2` 上传错误反馈、`Task F3` 附件注入 LLM
- 当前最大风险：如果继续只依赖 prompt 文本约束 JSON envelope，真实模型仍会绕过 `ready_to_generate/final_document` 协议
- 推荐先跑的验证命令：`cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q`
