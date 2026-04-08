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
- 当前状态：还未正式开始代码实现
- 当前应执行任务：`Milestone 1 / Task 1`
- 当前代码状态：主要完成了 spec、plan、执行规则、Apple 风格参考文档的整理

## 已完成的关键文档
- 产品规格：[docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md](/Users/zzten/work/zzetzMain/docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md)
- 实施计划：[docs/superpowers/plans/2026-04-08-personal-website-mvp.md](/Users/zzten/work/zzetzMain/docs/superpowers/plans/2026-04-08-personal-website-mvp.md)
- 里程碑计划：[PLANS.md](/Users/zzten/work/zzetzMain/PLANS.md)
- 执行规程：[IMPLEMENT.md](/Users/zzten/work/zzetzMain/IMPLEMENT.md)
- 执行状态记录：[DOCUMENTATION.md](/Users/zzten/work/zzetzMain/DOCUMENTATION.md)

## 核心产品约束
- 只支持简体中文输入与输出
- 第一版必须接入真实 LLM，不能用纯 mock 替代主链路
- 轮询优先，不做 WebSocket
- SQLite 作为内测数据库
- 同时最多 5 个活跃会话占用 LLM 处理资源
- 移动端优先

## 前端设计约束
- 所有前端 UI 以 [apple/DESIGN.md](/Users/zzten/work/zzetzMain/apple/DESIGN.md) 为视觉基准
- 默认深色风格为主，参考 [preview-dark.html](/Users/zzten/work/zzetzMain/apple/preview-dark.html)
- `apple/README.md` 和 `apple/DESIGN.md` 已翻译为简体中文，并加入了适配中文界面的建议
- 中文界面不要机械照搬英文负字距与紧缩参数，优先保证可读性

## 计划里的关键技术决定
- LLM：使用 OpenAI Responses API，通过 `httpx` 同步调用
- 轮询：对话阶段 3 秒，文档生成阶段 5 秒
- 会话：`session token` 标识，无登录
- 阶段：`template -> style -> positioning -> content -> features -> generate`
- 文档生成：摘要提取和 PRD 生成都走真实 LLM
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
从 `Milestone 1 / Task 1` 开始实现，不要再继续打磨 spec/plan，除非发现执行级矛盾。

建议顺序：
1. 读 `PLANS.md` 里的 Milestone 1
2. 读 `docs/superpowers/plans/2026-04-08-personal-website-mvp.md` 的 Task 1
3. 按 `IMPLEMENT.md` 的 TDD 流程开始搭前后端脚手架
4. 完成后更新 `DOCUMENTATION.md`

## 当前仓库里重要但只读的区域
- `docs/superpowers/specs/`
- `docs/superpowers/plans/`

除非明确是在维护文档，否则实现阶段不要改这两个目录。

## 最近重要提交
- `a33a3cb` `docs: translate apple design docs to chinese`
- `74742ee` `feat: add Apple design system guide and optimize agent docs`
- `f29d706` `docs: add final plan guardrails`
- `be92471` `docs: finish mvp plan wiring details`
- `d80cdf3` `docs: refine plan interaction and llm flow`

## 风险提示
- `DOCUMENTATION.md` 目前仍显示“Task 1 not started”，后续一旦开始实现，每完成一个 Task 都必须更新它
- 新会话不要直接开始改代码，先按 `AGENTS.md` 指定顺序读文档
- 前端 UI 实现必须优先遵守 `apple/DESIGN.md`，不要临时发明另一套视觉语言
