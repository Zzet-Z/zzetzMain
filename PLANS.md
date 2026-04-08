# PLANS.md

> **Spec-first 原则**：本文件与 `docs/superpowers/` 下的规格文档是项目的权威记录。
> 只有写进仓库的内容对 agent 才存在——口头约定、外部文档、个人记忆对执行无效。
> 架构约束通过每个 Milestone 的 Validation 命令机械执行，不依赖人工 code review。

## Project objective
构建一个面向简体中文非技术用户的个人网站需求梳理工具 MVP。首页建立审美与产品认知，需求梳理页通过真实 LLM 对话引导用户输出中文摘要与中文 PRD。

在不破坏现有稳定能力的前提下，按 Plan 文档中的 Task 1–9 逐步推进，并通过分阶段验证保证质量。

---

## Non-goals
以下内容不属于当前计划范围，除非后续明确加入：
- 用户账号体系与登录
- 支付与订阅
- 多人协作
- 网站直接生成（PRD 之后的步骤）
- 复杂图片识别或生成工作流
- 模板市场或 CMS
- 多语言输出
- 全仓库风格统一重构
- WebSocket 实时通信
- 将 SQLite 替换为其他数据库

---

## Milestone 1: 项目基线稳定（对应 Plan Task 1）
### Goal
搭建前后端脚手架，建立可持续推进的项目基线。

### Acceptance criteria
- 前端 React + Tailwind + Vite 项目可安装依赖并启动
- 后端 Flask 项目可安装依赖并启动
- 后端 `/api/health` 返回 `{"status": "ok"}`
- 前端首页路由可渲染中文标题
- 前后端各有一个通过的测试
- `AGENTS.md / PLANS.md / IMPLEMENT.md / DOCUMENTATION.md` 已建立
- README 包含基本启动说明

### Validation
```bash
cd backend && pytest tests/test_health.py -q
cd frontend && npm test -- app-shell.test.tsx
```

### Deliverables
- 前后端脚手架代码
- 依赖清单（package.json、pyproject.toml）
- 配置文件（vite、tailwind、tsconfig、postcss）
- 首轮验证结果
- git commit: `chore: scaffold frontend and backend apps`

---

## Milestone 2: 会话模型与基础 API（对应 Plan Task 2）
### Goal
建立会话持久化存储、数据模型与基础 session CRUD API。

### Acceptance criteria
- `POST /api/sessions` 创建会话并返回 token
- `GET /api/sessions/<token>` 返回会话状态与摘要
- `PATCH /api/sessions/<token>` 更新模板/风格/阶段（含阶段跳转校验）
- 无效 token 返回 404 与中文提示
- 数据库初始化与 teardown 正常工作
- CORS 配置正确

### Validation
```bash
cd backend && pytest tests/test_sessions_api.py -q
```

### Deliverables
- 数据库模型（SessionRecord、MessageRecord、SummarySnapshot、DocumentRecord、AttachmentRecord）
- Session 路由
- git commit: `feat: add session persistence and api`

---

## Milestone 3: LLM 客户端与 Prompt 编排（对应 Plan Task 3）
### Goal
接入真实 LLM HTTP API，建立分阶段 prompt 编排体系。

### Acceptance criteria
- `LLMClient` 通过 httpx 调用 OpenAI Responses API
- 支持环境变量配置 API key、model、base_url、timeout
- 超时和 HTTP 错误有中文 RuntimeError
- `build_chat_request` 按阶段加载对应 prompt 文件
- `generate_stage_reply` 封装完整调用流程
- `extract_summary_update` 从对话中提取结构化 JSON 摘要（含代码块容错）
- `render_prd_with_llm` 通过 LLM 生成中文 PRD
- 全局 system prompt 与六个阶段 prompt 文件就位
- 提取摘要 prompt 和渲染 PRD prompt 就位

### Validation
```bash
cd backend && pytest tests/test_llm_orchestrator.py -q
```

### Deliverables
- `llm_client.py`、`llm_orchestrator.py`
- 8 个 prompt 文件
- git commit: `feat: add real llm client and prompt orchestration`

---

## Milestone 4: 阶段状态机、对话引导与摘要提取（对应 Plan Task 4）
### Goal
实现六阶段状态机、消息路由与摘要更新策略。

### Acceptance criteria
- `next_stage_for_session` 正确处理阶段推进（选择、跳过、摘要就绪）
- `should_refresh_summary` 在阶段完成、生成请求时触发
- `merge_summary` 正确合并已有与新提取摘要
- 消息路由调用真实 LLM 生成回复
- 消息路由调用 LLM 提取摘要（在触发条件满足时）
- 消息路由调用状态机推进阶段
- LLM 调用失败返回 502 与中文提示

### Validation
```bash
cd backend && pytest tests/test_llm_orchestrator.py tests/test_queue_and_generation.py -q
```

### Deliverables
- `intake_state_machine.py`、`summary_builder.py`、`messages.py`
- git commit: `feat: add stage-aware intake engine`

---

## Milestone 5: 并发队列、文档生成与轮询（对应 Plan Task 5）
### Goal
实现 5 会话并发控制、排队机制与 LLM 驱动的文档生成。

### Acceptance criteria
- 第 6 个活跃会话被排队，返回 202 与排队位置
- 排队位置基于 `queued_at` 时间戳计算
- 完成的会话释放活跃槽位
- `generation_requested` 时调用 LLM 生成摘要与 PRD
- `GET /api/sessions/<token>/document` 返回文档内容
- 轮询参数 `poll_after_ms` 在对话中为 3000ms、生成中为 5000ms

### Validation
```bash
cd backend && pytest tests/test_queue_and_generation.py -q
```

### Deliverables
- `queue_manager.py`、`document_renderer.py`、`documents.py`
- git commit: `feat: add queue control and document generation states`

---

## Milestone 6: 上传、安全限制与错误处理（对应 Plan Task 6）
### Goal
实现图片上传与安全约束。

### Acceptance criteria
- 仅允许 PNG、JPEG、WEBP 格式
- 非图片文件返回 400
- 使用 `secure_filename` 防目录遍历
- 文件存储在 token 命名空间目录下
- 附件记录入库并可查询
- 单文件大小限制 8MB
- 单会话上传数量限制 12 个

### Validation
```bash
cd backend && pytest tests/test_uploads_api.py -q
```

### Deliverables
- `storage.py`、`uploads.py`
- git commit: `feat: add safe image uploads`

---

## Milestone 7: 首页移动端优先 UI（对应 Plan Task 7）
### Goal
实现首页五段式结构，mobile-first 响应式设计。

### Acceptance criteria
- Hero：大标题 + 副标题 + 主 CTA（button）+ loading 态
- 痛点与产品理念：三条用户痛点
- 三步流程：选择方向 → 梳理需求 → 获取结果
- 结果展示：摘要卡片 + PRD 卡片双栏（移动端纵向堆叠）
- 页尾 CTA：与 Hero 一致
- 深色背景、大留白、强调色克制
- 手机视口下标题和 CTA 首屏可见，无横向溢出

### Validation
```bash
cd frontend && npm test -- home-page.test.tsx
cd frontend && npm run build
```

### Deliverables
- `hero.tsx`、`problem.tsx`、`process.tsx`、`output-preview.tsx`、`final-cta.tsx`、`home-page.tsx`
- 全局样式 token
- git commit: `feat: build mobile-first homepage`

---

## Milestone 8: 需求梳理页 UI 与前后端接线（对应 Plan Task 8）
### Goal
实现需求梳理页完整 UI 与后端 API 接线。

### Acceptance criteria
- StepHeader 展示六阶段步骤条
- TemplateSelector 展示模板选项列表 + 跳过，选中后调 PATCH API
- StyleSelector 展示风格选项列表 + 跳过，选中后调 PATCH API
- ChatPanel 展示消息列表 + 输入框 + 发送按钮，发送调 POST messages API，有 loading 态和错误处理
- AttachmentPanel 支持图片上传，调 POST attachments API
- SummaryPanel 展示结构化摘要字段与文档状态
- 排队状态展示中文等待文案与排队位置
- API 客户端从环境变量读取后端地址
- 前端测试有 fetch mock
- 轮询：对话中 3s、文档生成中 5s
- 移动端单列布局，桌面端双栏布局

### Validation
```bash
cd frontend && npm test -- session-page.test.tsx session-flow.test.tsx mobile-states.test.tsx
cd frontend && npm run build
```

### Deliverables
- 6 个 intake 组件、session-page、api client、types
- git commit: `feat: wire mobile-first intake flow`

---

## Milestone 9: 最终验证与文档（对应 Plan Task 9）
### Goal
全量回归验证与人工验收。

### Acceptance criteria
- 后端全量测试通过
- 前端全量测试通过
- 前端生产构建成功
- 11 步人工验收链路跑通
- README 包含前后端启动说明
- Spec 与实现术语一致

### Validation
```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
```

### Human acceptance checklist
1. 打开首页，确认首屏 CTA 在手机视口下可见
2. 点击"开始梳理我的网站"，确认 loading 态后跳转到 /session/:token
3. 在模板阶段选择"个人作品页"
4. 在风格阶段选择"极简高级"
5. 输入中文定位信息
6. 上传一张 PNG 参考图
7. 继续补充内容与功能信息，直到进入生成阶段
8. 确认页面出现"正在生成 PRD"
9. 确认最终能看到中文摘要
10. 确认文档接口返回中文 PRD，且附件列表被写入
11. 复制 token，再次打开对应链接，确认会话内容仍可读取

### Deliverables
- README
- 验证结果
- git commit: `docs: finalize mvp validation checklist`

---

## Global execution rules
- 严格按 Milestone 1–9 顺序推进，除非明确记录调整原因
- 每次只推进一个 Milestone 或其子 Task
- 每完成一个 Milestone，必须更新 `DOCUMENTATION.md`
- 若验证失败，不进入下一 Milestone

### Mechanized enforcement
每个 Milestone 的 Validation 命令是架构约束的唯一执行机制：
- 测试失败 = 功能约束违规
- 构建失败 = 类型或接口约束违规
- 这些检查的反馈立即可用，不需要等待 code review
- 错误信息本身就是修复指引，优先从错误信息定位问题

---

## Task template
后续新增任务时，统一按这个格式追加：

### Task: [任务名]
**Scope**
- 本任务允许修改的模块：
- 本任务禁止扩展的范围：

**Acceptance criteria**
- [ ] 条件 1
- [ ] 条件 2
- [ ] 条件 3

**Validation**
- `command 1`
- `command 2`

**Notes**
- 风险：
- 依赖：
- 回退方案：
