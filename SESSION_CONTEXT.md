# SESSION_CONTEXT.md

## 用途
这是一份给“下一次会话”快速恢复上下文用的压缩摘要。

阅读顺序建议：
1. `AGENTS.md`
2. `SESSION_CONTEXT.md`
3. `PLANS.md`
4. `IMPLEMENT.md`
5. `DOCUMENTATION.md`
6. 当前 Milestone 对应的 `docs/superpowers/plans/...`
7. 有行为疑问时再读 `docs/superpowers/specs/...`

不要只靠本文件执行实现；它是快速恢复上下文，不是完整规范。

---

## 项目一句话
面向简体中文、非技术用户的个人网站需求梳理工具。首页建立产品认知，访客通过管理员签发的 token 进入 chat-first 需求对话页，由真实 LLM 输出中文摘要与最终需求文档，并通过 successor token 支持后续修订。

## 当前阶段
- 当前分支：`task/chat-first-redesign`
- 当前状态：Chat-first 重构已完成本地验证并已部署到线上；线上健康检查通过，线上主链路可用
- 当前应执行任务：无阻塞性实现任务；若继续推进，优先处理生产环境的临时管理员 token 和数据库迁移长期方案
- 当前代码状态：首页已切到 token-gated 入口，session 页已切到单聊天窗口，`/admin` 页面可管理 token；后端已切为 chat-first/token-gated 契约并上线到 `https://zzetz.cn`

## 已完成的关键文档
- MVP 产品规格：`docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- MVP 实施计划：`docs/superpowers/plans/2026-04-08-personal-website-mvp.md`
- Chat-first 重构规格：`docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md`
- Chat-first 重构实施计划：`docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`
- 里程碑计划：`PLANS.md`
- 执行规程：`IMPLEMENT.md`
- 执行状态记录：`DOCUMENTATION.md`

## 核心产品约束
- 只支持简体中文输入与输出
- 第一版必须接入真实 LLM，不能用纯 mock 替代主链路
- 轮询优先，不做 WebSocket
- SQLite 作为内测数据库
- 同时最多 5 个活跃会话占用 LLM 处理资源
- 移动端优先

## 前端设计约束
- 所有前端 UI 以 `apple/DESIGN.md` 为视觉基准
- 默认深色风格为主，参考 `apple/preview-dark.html`
- `apple/README.md` 和 `apple/DESIGN.md` 已翻译为简体中文，并加入了适配中文界面的建议
- 中文界面不要机械照搬英文负字距与紧缩参数，优先保证可读性

## 计划里的关键技术决定
- LLM：使用阿里云百炼 Qwen（`qwen3.5-plus`），兼容 OpenAI Responses API，通过 `httpx` 同步调用；base_url 为 `https://dashscope.aliyuncs.com/compatible-mode/v1`
- 轮询：继续保留轮询，不做 WebSocket；对话消息和文档生成都由 chat-first 接口返回轮询信号
- 会话：`token = 一次受控访问的一轮会话`，由管理员签发，不再允许匿名创建 session
- 会话状态：`queued -> active -> awaiting_user -> generating_document -> completed / failed / expired`
- 资源释放：5 分钟无新交互只释放队列/并发资源，不直接废 token；24 小时未完成则标记为 `expired`
- 对话协议：LLM 使用 JSON envelope，至少返回 `assistant_message` 与 `conversation_intent`
- 容错：若 envelope 解析失败，则回退为 `assistant_message=原文`、`conversation_intent=continue`；不计入三次失败重试
- 生成确认：用户确认生成最终文档时，显式传 `confirm_generate=true`
- 修订链：最终文档落盘成功后同步创建 successor token；修订轮会把上一版最终文档注入 LLM 上下文
- 欢迎语：`welcome_initial.md` 与 `welcome_revision.md` 由后端固定返回，不走 LLM
- 后台鉴权：环境变量 `ADMIN_TOKEN`，请求头使用 `Authorization: Bearer <admin_token>`
- 前端：React + Tailwind CSS + Vite
- 后端：Flask + SQLite

## 当前计划的实现范围
当前活跃计划是 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`，主要覆盖：
- Task 1：已完成
- Task 2：已完成
- Task 3：已完成
- Task 4：已完成
- Task 5：已完成
- Task 6：已完成
- Task 7：已完成（本地验收、线上部署、线上复验已做）

## 下一次会话最应该做什么
下一次会话如果继续推进，优先级建议改为：

1. 按 `AGENTS.md` 阅读顺序恢复上下文
2. 决定是否把 `task/chat-first-redesign` worktree 清理掉，因为变更已经合回 `main`
3. 把生产环境中的临时 `ADMIN_TOKEN=admin-secret` 改成你自己的值
4. 评估是否需要把当前 SQLite 兼容迁移整理成仓库内可重放的正式迁移脚本
5. 如需继续做体验优化，优先排查 `agent-browser click` / React 按钮事件不稳定的问题，以及已完成会话附件列表不回放的问题

## 当前仓库里重要但只读的区域
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

除非明确是在维护文档，否则实现阶段不要改这两个目录。

## 最近重要提交
- `3d9623e` `docs: record chat-first implementation progress`
- `5bd20b3` `fix: align admin frontend with api payloads`
- `ae9c012` `feat: add admin token dashboard`
- `b48f0a7` `feat: rebuild session page as single chat`
- `9bec5ce` `fix: harden backend message and pagination flows`
- `e6efc13` `feat: add token-gated homepage entry`
- `db54c83` `fix: tighten admin revision token validation`
- `84514d8` `test: migrate upload token setup`
- `36e4b13` `feat: add token lifecycle and admin apis`
- `8261f00` `fix: complete chat-first prompt requirements`
- `ae5f38e` `fix: preserve final document intent and context`
- `d783788` `feat: add chat-first prompt orchestration`
- `afb5696` `refactor: restore session compatibility shims`
- `ec3a513` `docs: align chat-first spec and plan`
- `8671dfd` `docs: add chat-first redesign plan`
- `e7d7e6b` `docs: finalize chat-first redesign spec`
- `6852601` `docs: refine chat-first redesign spec`
- `2720879` `docs: add chat-first intake redesign spec`
- `2f6ac7f` `fix: harden production message pipeline`
- `df52b38` `docs: add architecture guide and delegation rule`
- `7f2e238` `feat: wire mobile-first intake flow`
- `5ae8615` `feat: build mobile-first homepage`
- `05f3376` `feat: add safe image uploads`
- `ddc5c03` `feat: add queue control and document generation states`
- `fd565f1` `feat: add stage-aware intake engine`
- `fbd24fa` `feat: add real llm client and prompt orchestration`
- `c282917` `feat: add session persistence and api`
- `d1aa76c` `chore: ignore tsbuildinfo artifact`
- `bd01f6d` `chore: scaffold frontend and backend apps`
- `a33a3cb` `docs: translate apple design docs to chinese`
- `74742ee` `feat: add Apple design system guide and optimize agent docs`
- `f29d706` `docs: add final plan guardrails`
- `be92471` `docs: finish mvp plan wiring details`
- `d80cdf3` `docs: refine plan interaction and llm flow`

## 风险提示
- 当前 chat-first 实现已经合回本地 `main` 并推送到 `origin/main`，生产环境也已拉取
- 本地和线上的 `agent-browser` 对 React 按钮 click 事件仍存在不稳定性，尤其体现在聊天页“发送”按钮和后台部分提交按钮；页面结构和 API 主链路已验证通过，但纯按钮驱动 E2E 仍需后续工具/交互层排查
- 生产环境当前临时使用 `ADMIN_TOKEN=admin-secret`，需要后续替换
- 生产库为了兼容 chat-first 上线，已在服务器上做了最小 SQLite 表重建；后续应评估是否将其固化为仓库内可重放的迁移步骤
- 真实 LLM 主链路在百炼兼容层上依然偏慢；生产上一条消息可能包含“阶段回复 + 摘要提取”两次模型调用，因此部署时必须同步放宽 `gunicorn` 与 `nginx` 的超时窗口
- `SessionRecord.status` 现在新增了“处理中结束后的在途状态”语义：`active` 只表示占用并发槽位的处理中请求，完成后会落到 `in_progress`，失败时落到 `failed`
- 远端宿主机存在代理环境变量；`LLMClient` 已通过 `trust_env=False` 显式忽略宿主机代理，后续不要回退这个行为
- 首页 CTA 现在不会匿名创建 session；入口改成 token 输入后再跳转到 `/session/:token`
- 新会话不要直接开始改代码，先按 `AGENTS.md` 指定顺序读文档
- 前端 UI 实现必须优先遵守 `apple/DESIGN.md`，不要临时发明另一套视觉语言
- `backend/.env` 已从根目录 `.env.local` 迁入并由 `backend/app/config.py` 读取，后续不要把密钥写回仓库追踪文件
