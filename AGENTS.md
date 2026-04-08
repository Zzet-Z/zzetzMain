# AGENTS.md

## Mission
你是本项目的工程执行代理。在明确范围内完成任务，保持项目可运行、可验证、可回滚。

详细执行规程见 `IMPLEMENT.md`。

---

## Project overview
面向简体中文非技术用户的个人网站需求梳理工具。首页建立产品认知，需求梳理页通过真实 LLM 引导用户输出中文摘要与 PRD。

### Core constraints
- MVP 只支持简体中文输入与输出
- 真实 LLM 必须进入第一版，不允许用纯 mock 替代主链路
- 轮询优先，不做 WebSocket
- SQLite 作为内测数据库，数据访问层避免锁死在 SQLite 特性上
- 同时最多 5 个活跃会话占用 LLM 处理资源

---

## Document map
每次开始任务前，**按顺序**阅读以下文件，获取定向信息，再深入代码：

| 文件 | 用途 | 阅读时机 |
|------|------|----------|
| `AGENTS.md`（本文件） | 项目地图、约束、环境 | 每次必读（先） |
| `PLANS.md` | 里程碑目标与验收标准 | 每次必读 |
| `IMPLEMENT.md` | 执行规程（如何做） | 每次必读 |
| `DOCUMENTATION.md` | 当前状态、决策记录、阻塞项 | 每次必读（后） |
| `docs/superpowers/plans/…` | 当前 Task 完整描述与代码示例 | 定位到 Task 后阅读 |
| `docs/superpowers/specs/…` | 产品行为规格 | 有疑问时阅读 |

不要在未完成上面阅读顺序前直接修改代码。

---

## Repository map

| 路径 | 说明 |
|------|------|
| `frontend/src/routes/` | 页面路由（首页、需求梳理页） |
| `frontend/src/components/home/` | 首页五段式区块组件 |
| `frontend/src/components/intake/` | 需求梳理页六组件 |
| `frontend/src/lib/` | API 客户端与类型定义 |
| `backend/app/routes/` | API 路由（health、sessions、messages、uploads、documents） |
| `backend/app/services/` | 业务逻辑（LLM、编排、队列、状态机、摘要、文档） |
| `backend/app/prompts/` | 分阶段中文 prompt 文件 |
| `docs/superpowers/specs/` | 产品规格说明书（**只读**） |
| `docs/superpowers/plans/` | 实施计划（**只读**） |

---

## Reference documents
- **产品规格**: `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- **实施计划**: `docs/superpowers/plans/2026-04-08-personal-website-mvp.md`

Plan 中的 Task 1–9 是主要执行依据。每个 Task 包含明确的文件清单、代码示例、测试与提交点。

---

## Frontend UI style guide
**所有前端 UI 开发必须以 `apple/DESIGN.md` 作为视觉风格基准。**

```
apple/
├── DESIGN.md          ← 主参考文件（颜色、字体、间距、组件规范）
├── README.md          ← 使用说明
├── preview.html       ← 设计 token 交互预览（亮色）
└── preview-dark.html  ← 设计 token 交互预览（暗色）
```

### 使用规则
1. **开始任何前端 UI 任务前，先阅读 `apple/DESIGN.md`**，了解颜色 token、字体系统、间距规范、组件样式
2. 本项目使用**深色背景**（dark mode 为主），参考 `preview-dark.html` 的配色方案
3. 样式决策优先级：`apple/DESIGN.md` > 产品规格 Spec > 自行发挥
4. 实现中文用户界面时，字体大小与行高参考 DESIGN.md 中的 Typography 章节，确保中文可读性
5. 不要引入与 Apple 风格相悖的视觉元素（如强饱和色、阴影过重、边框装饰过多）

### 覆盖范围
- 所有 `frontend/src/components/` 下的组件
- Tailwind 配置中的颜色与字体 token
- 全局 CSS 变量

---

## Environment

```bash
# 安装
cd frontend && npm install
cd backend && pip install -e .

# 本地开发
cd frontend && npm run dev
cd backend && python run.py

# 环境变量（后端 LLM 调用必需）
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Quality gates（机械化验证，不可跳过）
```bash
# 后端
cd backend && pytest -q

# 前端
cd frontend && npm test
cd frontend && npm run build
```

> 这些命令是架构约束的执行层。测试失败 = 架构违规，不能假装通过。
> 如果某些命令不存在，先查找现有脚本，不要编造。

---

## Definition of done
只有满足以下**所有**条件，任务才算完成：

- [ ] 完成当前 Task 要求的所有 Step
- [ ] 改动范围控制在 Task 的 Files 清单内
- [ ] 相关测试执行并通过
- [ ] 构建验证执行并通过
- [ ] 按 Task 要求执行 git commit
- [ ] 验证结果写入 `DOCUMENTATION.md`
- [ ] 已知风险与未完成项已记录
