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
面向简体中文、非技术用户的个人网站需求梳理工具。首页建立产品认知，需求梳理页通过真实 LLM 引导用户输出中文摘要与 PRD。

## 当前阶段
- 当前分支：`main`
- 当前状态：`Milestone 9 / Task 9` 已完成，MVP 可运行、可验证、可回访
- 当前应执行任务：`无强制后续 Task；如继续迭代，属于计划外增强`
- 当前代码状态：后端已具备 SQLite 初始化、session API、真实 LLM client、状态机、消息路由、并发队列、文档生成、附件上传与文档读取接口；前端首页和需求梳理页都已接上线，完整真实浏览器验收链路已打通

## 已完成的关键文档
- 产品规格：`docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- 实施计划：`docs/superpowers/plans/2026-04-08-personal-website-mvp.md`
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
- 轮询：对话阶段 3 秒，文档生成阶段 5 秒
- 会话：`session token` 标识，无登录
- 阶段：`template -> style -> positioning -> content -> features -> generate`
- 文档生成：摘要提取和 PRD 生成都走真实 LLM
- 容错：`LLMClient.generate()` 在超时时会自动重试一次；阶段回复与摘要提取超时已按真实供应商耗时上调到 90 秒
- 前端：React + Tailwind CSS + Vite
- 后端：Flask + SQLite

## 当前计划的实现范围
Milestone 1 到 9 已写完，主要覆盖：
- Task 1：前后端脚手架
- Task 2：会话模型与 session API
- Task 3：真实 LLM 客户端与 prompt 编排
- Task 4：阶段状态机、对话引导、摘要提取
- Task 5：并发队列、文档生成、轮询
- Task 6：上传、安全约束、错误处理
- Task 7：首页五段式移动端优先 UI
- Task 8：需求梳理页六组件与前后端接线
- Task 9：最终验证与文档

## 下一次会话最应该做什么
当前最优先的是把这次生产部署修复提交并推送，然后在服务器上用 `scripts/deploy-zzetz-cn.sh` 重放一次部署，确认脚本本身可用。

如果下一次会话继续推进，优先顺序改为：
1. 固化并复跑生产部署脚本
2. 做 MVP 之后的体验增强
3. 做新一轮产品能力规划

无论做哪一种，仍先按 `AGENTS.md` 的阅读顺序恢复上下文，再决定是否需要新增计划。

## 当前仓库里重要但只读的区域
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

除非明确是在维护文档，否则实现阶段不要改这两个目录。

## 最近重要提交
- `TBD` 本轮尚未提交：生产消息链路修复、`trust_env=False`、部署脚本 `scripts/deploy-zzetz-cn.sh`
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
- 真实 LLM 主链路在百炼兼容层上依然偏慢；生产上一条消息可能包含“阶段回复 + 摘要提取”两次模型调用，因此部署时必须同步放宽 `gunicorn` 与 `nginx` 的超时窗口
- `SessionRecord.status` 现在新增了“处理中结束后的在途状态”语义：`active` 只表示占用并发槽位的处理中请求，完成后会落到 `in_progress`，失败时落到 `failed`
- 远端宿主机存在代理环境变量；`LLMClient` 已通过 `trust_env=False` 显式忽略宿主机代理，后续不要回退这个行为
- 已完成会话重新打开后，附件列表仍不会从后端回放到附件面板；持久化附件以文档 `参考附件` 段落为准
- 新会话不要直接开始改代码，先按 `AGENTS.md` 指定顺序读文档
- 前端 UI 实现必须优先遵守 `apple/DESIGN.md`，不要临时发明另一套视觉语言
- `backend/.env` 已从根目录 `.env.local` 迁入并由 `backend/app/config.py` 读取，后续不要把密钥写回仓库追踪文件
