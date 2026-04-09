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
- 当前分支：`main`
- 当前状态：Task 4 已完成，首页入口已切换为 token-gated 流程
- 当前应执行任务：`docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md` 的 `Task 5`
- 当前代码状态：首页不再匿名创建 session，改为展示 token 输入并跳转到 `/session/:token`；session 页仍保持旧的阶段式 intake 形态，等待下一步收敛

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
- Task 1：重构后端数据模型、配置和 `.env.example`
- Task 2：落地 chat-first prompt、JSON envelope 和修订轮上下文注入
- Task 3：重写 session / message / document / admin API 与生命周期
- Task 4：改首页入口为 token-gated 流程
- Task 5：将 session 页收敛为单聊天窗口，并接入确认生成与消息分页
- Task 6：实现后台管理页与前端 admin API
- Task 7：全量验证、真实浏览器验收与文档回写

## 下一次会话最应该做什么
下一次会话应直接进入 chat-first 重构实现，不再停留在文档讨论阶段。

推荐顺序：
1. 先按 `AGENTS.md` 阅读顺序恢复上下文
2. 阅读 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`
3. 直接开始 `Task 5`
4. 先把 session 页收敛为单聊天窗口，再接入确认生成与消息分页

当前不建议跳过 `Task 1` 直接改前端页面，因为 chat-first 前端依赖新的 session / message / admin API 契约。

## 当前仓库里重要但只读的区域
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

除非明确是在维护文档，否则实现阶段不要改这两个目录。

## 最近重要提交
- 本次 Task 4 待提交/已提交：`feat: add token-gated homepage entry`
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
- 当前 `main` 分支上的代码与最新 chat-first spec / plan 有意存在差异：文档已切到目标态，但功能代码仍是旧的阶段式 intake。下一轮实现前不要把“文档已完成”误判成“功能已落地”
- 新一轮实现会同时改数据库模型、核心 API、首页入口、聊天主页面和后台页，属于高风险改动；建议默认考虑 worktree
- `PLANS.md` 仍是 MVP 初始里程碑记录；实际执行时应以 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md` 为当前主计划
- 真实 LLM 主链路在百炼兼容层上依然偏慢；生产上一条消息可能包含“阶段回复 + 摘要提取”两次模型调用，因此部署时必须同步放宽 `gunicorn` 与 `nginx` 的超时窗口
- `SessionRecord.status` 现在新增了“处理中结束后的在途状态”语义：`active` 只表示占用并发槽位的处理中请求，完成后会落到 `in_progress`，失败时落到 `failed`
- 远端宿主机存在代理环境变量；`LLMClient` 已通过 `trust_env=False` 显式忽略宿主机代理，后续不要回退这个行为
- 已完成会话重新打开后，附件列表仍不会从后端回放到附件面板；持久化附件以文档 `参考附件` 段落为准
- 首页 CTA 现在不会匿名创建 session；入口改成 token 输入后再跳转到 `/session/:token`
- `src/test/session-flow.test.tsx` 还停留在旧的匿名创建 session 断言，下一轮 Task 5 需要一起迁移
- 新会话不要直接开始改代码，先按 `AGENTS.md` 指定顺序读文档
- 前端 UI 实现必须优先遵守 `apple/DESIGN.md`，不要临时发明另一套视觉语言
- `backend/.env` 已从根目录 `.env.local` 迁入并由 `backend/app/config.py` 读取，后续不要把密钥写回仓库追踪文件
