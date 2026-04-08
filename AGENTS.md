# AGENTS.md

## Mission
你是本项目的工程执行代理。你的目标不是"尽量多改代码"，而是：
1. 在明确范围内完成任务
2. 保持项目可运行、可验证、可回滚
3. 优先通过测试、构建、类型检查来证明正确性
4. 始终将项目稳定性放在速度之前

---

## Project overview
本项目是一个面向简体中文非技术用户的个人网站需求梳理工具。用户通过首页了解产品，进入需求梳理页后与真实 LLM 进行引导式对话，最终输出中文摘要与中文 PRD。

### High-level goals
- 按里程碑推进项目，不一次性大改全仓库
- 所有改动都必须可验证
- 所有重要决策都必须记录
- 优先最小改动完成目标，不做无关重构

### Core constraints
- MVP 只支持简体中文输入与输出
- 真实 LLM 必须进入第一版实现，不允许用纯 mock 替代主链路
- 轮询优先，不做 WebSocket
- 前端是一套响应式界面，不拆移动端和桌面端两套应用
- SQLite 作为内测数据库，但数据访问层避免锁死在 SQLite 特性上
- 同时最多 5 个活跃会话占用 LLM 处理资源

---

## Repository map

- `frontend/`：React + TypeScript + Tailwind CSS 前端（Vite 构建）
- `frontend/src/routes/`：页面路由（首页、需求梳理页）
- `frontend/src/components/home/`：首页五段式区块组件
- `frontend/src/components/intake/`：需求梳理页六组件（步骤条、模板选择、风格选择、对话面板、摘要面板、附件面板）
- `frontend/src/components/ui/`：通用 UI 组件
- `frontend/src/lib/`：API 客户端与类型定义
- `frontend/src/test/`：前端测试
- `backend/`：Python Flask 后端
- `backend/app/`：应用工厂、模型、路由、服务
- `backend/app/routes/`：API 路由（health、sessions、messages、uploads、documents）
- `backend/app/services/`：业务逻辑（LLM 客户端、编排器、队列、状态机、摘要构建、文档渲染、存储）
- `backend/app/prompts/`：分阶段中文 prompt 文件
- `backend/tests/`：后端测试
- `docs/superpowers/specs/`：产品规格说明书
- `docs/superpowers/plans/`：实施计划
- `AGENTS.md`：代理工作规则（本文件）
- `PLANS.md`：里程碑计划
- `IMPLEMENT.md`：执行规程
- `DOCUMENTATION.md`：执行日志 / 决策记录 / 当前状态

---

## Reference documents
实施过程中必须参考的核心文档：

- **产品规格**: `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- **实施计划**: `docs/superpowers/plans/2026-04-08-personal-website-mvp.md`

Plan 中的 Task 1–9 是主要执行依据，每个 Task 包含明确的文件清单、代码示例、测试与提交点。

---

## Environment assumptions

### Install
```bash
cd frontend && npm install
cd backend && pip install -e .
```

### Local development
```bash
# 前端开发服务器
cd frontend && npm run dev

# 后端开发服务器
cd backend && python run.py
```

### Environment variables
```bash
# 后端 LLM 调用必需
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"           # 可选，默认 gpt-4.1-mini
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选
```

### Quality checks
```bash
# 前端
cd frontend && npm test                  # Vitest 单元测试
cd frontend && npm run build             # TypeScript 编译 + 生产构建

# 后端
cd backend && pytest -q                  # pytest 全量测试
cd backend && pytest tests/test_health.py -q          # 健康检查
cd backend && pytest tests/test_sessions_api.py -q    # 会话 API
cd backend && pytest tests/test_llm_orchestrator.py -q # LLM 编排
cd backend && pytest tests/test_queue_and_generation.py -q # 队列与文档生成
cd backend && pytest tests/test_uploads_api.py -q     # 上传
```

> 如果某些命令不存在，不要自己编造。应先查找现有脚本并使用真实命令。

---

## Operating rules
你必须遵守以下规则：

1. **先读再改**
   - 开始任务前，先阅读：
     - `AGENTS.md`
     - `PLANS.md`
     - `IMPLEMENT.md`
     - `DOCUMENTATION.md`
   - 再阅读当前 Task 在 Plan 文档中的完整描述
   - 如有必要，再读相关模块代码、测试、配置文件

2. **一次只做一个明确子目标**
   - 不同时处理多个无关问题
   - 不顺手做"看起来也该改"的重构

3. **最小改动原则**
   - 优先局部修复
   - 避免大面积命名重构、目录搬迁、风格统一式改动
   - 不要为了"更优雅"破坏已有稳定逻辑

4. **修改代码时必须同步考虑验证**
   - 只要行为变化，就应补测试或更新测试
   - 如果无法补完整测试，至少增加最小可验证检查，并在 `DOCUMENTATION.md` 记录风险

5. **禁止跳过失败验证**
   - lint/typecheck/test/build 失败时，不得假装完成
   - 必须先定位并修复，或者明确记录阻塞原因

6. **禁止无授权扩 scope**
   - 当前任务未要求的模块，不要主动重做
   - 可记录 follow-up，但不要直接实现

7. **始终更新执行记录**
   - 每完成一个小阶段，都更新 `DOCUMENTATION.md`

8. **保持项目可运行**
   - 不要让仓库处于明显不可构建、不可测试的半废状态后就停止

9. **严格遵循 Plan 中的 TDD 流程**
   - Plan 中每个 Task 都是先写测试、再写实现、再验证
   - 不要跳过"先确认测试失败"这一步

10. **中文输出是硬性要求**
    - 所有面向用户的界面文案、LLM prompt、输出文档都必须是简体中文
    - 代码注释和变量名可以用英文

---

## Code change policy
### Allowed
- 完成当前 Plan Task 需要的功能
- 修复 bug
- 补充必要测试
- 补充必要文档
- 局部重构（仅限完成当前任务所必需）

### Not allowed unless explicitly required
- 大范围重构
- 修改公共 API 却不更新调用方和文档
- 删除测试而不提供替代测试
- 修改构建流程但不验证
- 为"顺手优化"改无关文件
- 替换技术栈组件（如把 SQLite 换成 Postgres）

---

## Testing policy
如果你修改了以下内容，必须执行对应验证：

### Frontend UI / interaction changes
至少执行：
- `cd frontend && npm test`
- `cd frontend && npm run build`

### Backend API / business logic changes
至少执行：
- `cd backend && pytest -q`
- 相关的具体测试文件

### Shared contract / schema / types changes
必须执行：
- 前后端相关测试
- 构建验证

### LLM prompt changes
- 确认 prompt 文件路径正确
- 确认编排器能正确加载
- 运行 `test_llm_orchestrator.py`

---

## Definition of done
一个任务只有在满足以下条件时才算完成：

- 已完成当前 Task 要求的所有 Step
- 改动范围控制在 Task 的 Files 清单内
- 相关测试已执行且通过
- 构建验证已执行且通过
- 已按 Task 要求执行 git commit
- 验证结果已写入 `DOCUMENTATION.md`
- 已知风险与未完成项已记录
- 没有明显的阻塞性错误被忽略

---

## Documentation policy
每次任务结束前，更新 `DOCUMENTATION.md`，至少包括：

- 当前完成到哪里
- 做了哪些关键改动
- 执行了哪些验证及结果
- 有哪些已知问题 / 风险
- 下一步建议

---

## When blocked
如果遇到阻塞：
1. 先定位阻塞范围
2. 尝试最小化解决
3. 若无法解决，不要伪装成功
4. 在 `DOCUMENTATION.md` 写清楚：
   - 阻塞原因
   - 已尝试的方法
   - 建议下一步

---

## Preferred execution style
- 先计划，后实现
- 先局部，后整体
- 先验证，后宣称完成
- 先记录，后结束任务
