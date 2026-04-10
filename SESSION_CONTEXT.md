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
- 当前状态：生产复验已经完成；部署脚本已修复为每次发布后显式重启 `zzetz-backend`，附件预览 `500` 已消失，Playwright 公网 E2E 已验证上传缩略图、上传错误透传、文档生成 completed、successor token 修订链与撤销后失效提示
- 当前应执行任务：如继续推进，优先处理运维尾项而不是继续追历史缺陷：替换生产临时 `ADMIN_TOKEN=admin-secret`，决定是否正式纳入 repo 内 `skills/playwright/`，并在后续公网回归中优先使用 Playwright CLI
- 当前代码状态：首页 token 入口、单聊天窗口、后台 token 管理已经落地；F6 文档生成切换、F1 发送态消息回显、F2 上传错误透传、F3 附件注入对话上下文、F4 附件缩略图与历史回放、F5 后台详情扩展均已在当前代码中实现；本轮又补了两处稳定性修复：上传失败中文错误不会被轮询立即清掉；session 首屏会优先展示后端返回的无效 / 失效 token 中文原因

## 已完成的关键文档
- MVP 产品规格：`docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- MVP 实施计划：`docs/superpowers/plans/2026-04-08-personal-website-mvp.md`
- Chat-first 重构规格：`docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md`
- Chat-first 重构实施计划：`docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`
- Chat-first 上线后修复计划：`docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`
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
已完成的主线计划是 `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`，主要覆盖：
- Task 1：已完成
- Task 2：已完成
- Task 3：已完成
- Task 4：已完成
- Task 5：已完成
- Task 6：已完成
- Task 7：已完成（本地验收、线上部署、线上复验已做）

当前新增的活跃 follow-up 计划是 `docs/superpowers/plans/2026-04-09-chat-first-post-launch-fixes.md`，主要覆盖：
- Task F6：已修复“明确定稿但未进入文档生成状态”
- Task F1：已修复发送中用户消息消失
- Task F2：已修复上传失败错误反馈缺失
- Task F3：已实现附件信息注入 LLM 对话上下文
- Task F4：已实现聊天页附件缩略图与历史回放
- Task F5：已扩展后台 token 详情查看数据

## 下一次会话最应该做什么
下一次会话如果继续推进，优先级建议改为：

1. 按 `AGENTS.md` 阅读顺序恢复上下文
2. 优先阅读 `DOCUMENTATION.md` 中 2026-04-10 的 “Production rerun: 修复部署脚本重启缺口并完成 Playwright 公网复验”
3. 如继续做公网回归，直接使用 `skills/playwright/scripts/playwright_cli.sh`，不要再把 `agent-browser` 的点击不稳定当作业务结论
4. 先处理运维尾项：替换生产 `ADMIN_TOKEN=admin-secret`，再决定是否把本地 `skills/` / `.playwright-cli/` / `output/` 作为正式仓库策略处理
5. 若后续又出现“代码文件已更新但线上行为未更新”，先检查部署脚本是否真的重启了服务，再看业务代码

---

## 生产环境浏览器验收结论（2026-04-10）

本轮改用 repo 内 `skills/playwright/` 的 Playwright CLI 对 `https://zzetz.cn` 做了完整公网复验，核心结论如下：

### 已验证正常
- 首页 CTA 可稳定弹出 token 输入区，不再出现“正在准备梳理页...”
- 新签发 token 与既有 token 都能进入 session 页面，不再停留在永久“正在加载...”
- 消息发送后，右侧用户消息持续可见，页面出现 `思考中...`
- 图片上传后缩略图可见，刷新后历史回放仍在
- 附件预览接口已恢复，`/attachments/<id>/preview` 返回真实图片而非 `500`
- 上传非法 `pdf` 文件时，页面稳定显示 `只支持 PNG、JPEG、WEBP 图片`
- 在携带参考图的真实对话中，assistant 生成的最终文档明确引用了上传附件 `zzetz-e2e.png`
- 同一会话成功进入 `completed`，弹出“您的网站将于3-24小时内上线”，并展示 successor token `lp5D5VE2i6HMmOrWt9HXRhiakkbYsqVx`
- 点击弹框“确认”后已回到首页
- successor token 可进入修订轮，展示上一版摘要与“欢迎回来”
- 撤销 successor token 后，页面显示 `这个整理链接已经失效，请联系管理员获取新的入口。`

### 已定位并修复的线上根因
- 生产附件预览 `500` 的根因不是上传路由，而是 `scripts/deploy-zzetz-cn.sh` 没有重启已运行的 `zzetz-backend`
- 部署脚本现已改为每次发布后显式 `systemctl restart zzetz-backend`

### 剩余注意事项
- 公网 E2E 不要再把 `agent-browser` 的点击结果当作业务最终结论；当前项目上 Playwright CLI 稳定性明显更高
- 生产仍临时使用 `ADMIN_TOKEN=admin-secret`，需要后续替换

## 当前仓库里重要但只读的区域
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

除非明确是在维护文档，否则实现阶段不要改这两个目录。

## 最近重要提交
- `a0a9ddf` `fix: surface invalid session errors on load`
- `b39538f` `fix: preserve upload errors and restart backend on deploy`
- `f68d89f` `fix: harden homepage entry and session load states`
- `00af3d1` `fix: close post-launch chat-first gaps`
- `730df9c` `fix: complete sessions after final document`
- `572d2a1` `fix: clarify assistant thinking state`
- `602c6b8` `feat: add repeatable sqlite migration script`
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
- 当前 chat-first 实现已经合回本地 `main` 并推送到 `origin/main`，本轮又补了本地提交 `00af3d1`；是否继续推送和部署需要下一步明确执行
- 本地 `agent-browser` 默认使用 `~/.agent-browser/config.json` 中固定的 `cdp: 9222` 配置，导致浏览器验收前需要先手动拉起 Chrome；本轮已恢复可用环境，但完整交互自动化仍受工具稳定性影响
- 已确认 `agent-browser snapshot -i` 会枚举视口外按钮，但 `click @ref` 对视口外目标不会稳定自动滚动；后续公网 E2E 必须先把目标按钮滚进视口再点击
- 生产环境当前临时使用 `ADMIN_TOKEN=admin-secret`，需要后续替换
- 完整页面级浏览器验收还需要在稳定浏览器配置下再补一轮，当前主要证据仍以代码、测试和构建验证为主
- 仓库内已加入正式可重放的 SQLite 迁移脚本 `backend/app/db_migrations.py`，但生产机上已经做过一次手工表重建；后续若重建环境，应优先走脚本而不是重跑手工 SQL
- 真实 LLM 主链路在百炼兼容层上依然偏慢；生产上一条消息可能包含“阶段回复 + 摘要提取”两次模型调用，因此部署时必须同步放宽 `gunicorn` 与 `nginx` 的超时窗口
- `SessionRecord.status` 现在新增了“处理中结束后的在途状态”语义：`active` 只表示占用并发槽位的处理中请求，完成后会落到 `in_progress`，失败时落到 `failed`
- 远端宿主机存在代理环境变量；`LLMClient` 已通过 `trust_env=False` 显式忽略宿主机代理，后续不要回退这个行为
- 首页 CTA 现在不会匿名创建 session；入口改成 token 输入后再跳转到 `/session/:token`
- 新会话不要直接开始改代码，先按 `AGENTS.md` 指定顺序读文档
- 前端 UI 实现必须优先遵守 `apple/DESIGN.md`，不要临时发明另一套视觉语言
- `backend/.env` 已从根目录 `.env.local` 迁入并由 `backend/app/config.py` 读取，后续不要把密钥写回仓库追踪文件
