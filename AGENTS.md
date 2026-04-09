# AGENTS.md

## Mission
你是本项目的工程执行代理。在明确范围内完成任务，保持项目可运行、可验证、可回滚。

详细执行规程见 `IMPLEMENT.md`。

---

## Collaboration principle
默认优先调用子 agent 协作，尤其用于以下三类工作：

- 审查：代码 review、变更检查、回归风险扫描、验收前复核
- 子任务：可独立切分的实现、排查、资料整理、局部重构
- 测试：单测、集成测试、E2E 验证、失败复现与结果复核

主 agent 默认主要承担项目管理职责：

- 读取上下文、确认当前 Task 与范围
- 做任务拆解、优先级判断与分派
- 集成子 agent 结果并处理冲突
- 把控架构一致性、验收标准与提交边界
- 向用户同步进度、风险、验证结果与下一步

只有在以下情况才由主 agent 直接亲自做具体执行：

- 任务太小，分派成本高于直接完成
- 子 agent 不可用或当前环境不支持
- 子任务之间强耦合，必须由同一上下文连续完成
- 涉及最终裁决、范围控制或跨模块集成
---

## Project overview
面向简体中文非技术用户的个人网站需求梳理工具。首页建立产品认知，访客通过管理员签发的 token 进入 chat-first 需求对话页，由真实 LLM 输出中文摘要与最终需求文档，并支持 successor token 修订链。

### Core constraints
- MVP 只支持简体中文输入与输出
- 真实 LLM 必须进入第一版，不允许用纯 mock 替代主链路
- 轮询优先，不做 WebSocket
- SQLite 作为内测数据库，数据访问层避免锁死在 SQLite 特性上
- 同时最多 5 个活跃会话占用 LLM 处理资源
- 用户不能匿名创建 session；会话 token 由管理员手动签发
- 5 分钟无新交互只释放队列 / 并发资源，24 小时未完成才失效 token

---

## Document map
每次开始任务前，**按顺序**阅读以下文件，获取定向信息，再深入代码：

| 文件 | 用途 | 阅读时机 |
|------|------|----------|
| `AGENTS.md`（本文件） | 项目地图、约束、环境 | 每次必读（先） |
| `SESSION_CONTEXT.md` | 上一次会话压缩上下文、当前阶段与关键决策 | 每次必读（紧随 AGENTS） |
| `PLANS.md` | 里程碑目标与验收标准 | 每次必读 |
| `IMPLEMENT.md` | 执行规程（如何做） | 每次必读 |
| `DOCUMENTATION.md` | 当前状态、决策记录、阻塞项 | 每次必读（后） |
| `docs/superpowers/plans/…` | 当前 Task 完整描述与代码示例 | 定位到 Task 后阅读 |
| `docs/superpowers/specs/…` | 产品行为规格 | 有疑问时阅读 |

不要在未完成上面阅读顺序前直接修改代码。
`SESSION_CONTEXT.md` 只用于快速恢复上下文，不能替代 `PLANS.md`、`IMPLEMENT.md` 和当前 Task 计划。

---

## Repository map

| 路径 | 说明 |
|------|------|
| `frontend/src/routes/` | 页面路由（首页、聊天页、后台管理页） |
| `frontend/src/components/home/` | 首页五段式区块组件 |
| `frontend/src/components/intake/` | chat-first 聊天页组件 |
| `frontend/src/components/admin/` | 后台 token 管理组件 |
| `frontend/src/lib/` | API 客户端与类型定义 |
| `backend/app/routes/` | API 路由（health、sessions、messages、uploads、documents、admin） |
| `backend/app/services/` | 业务逻辑（LLM、编排、队列、会话生命周期、后台鉴权、文档） |
| `backend/app/prompts/` | chat-first 中文 prompt、欢迎语与最终文档 prompt |
| `docs/superpowers/specs/` | 产品规格说明书（**只读**） |
| `docs/superpowers/plans/` | 实施计划（**只读**） |

---

## Reference documents
- **当前产品规格**: `docs/superpowers/specs/2026-04-09-chat-first-intake-redesign.md`
- **当前实施计划**: `docs/superpowers/plans/2026-04-09-chat-first-intake-redesign.md`
- **MVP 原始规格**: `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`
- **MVP 原始计划**: `docs/superpowers/plans/2026-04-08-personal-website-mvp.md`

当前执行默认以 `2026-04-09` 的 chat-first spec / plan 为准。`2026-04-08` 的文档保留为 MVP 历史基线与回溯参考。

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

## Frontend testing rule
前端测试不能只依赖单元测试或组件测试。凡是涉及页面流程、关键交互、表单、路由跳转、上传、轮询状态、移动端布局验证，**必须使用 `agent-browser` skill 拉起真实浏览器访问 Web 应用并执行 E2E 测试**。

### 执行要求
1. 前端实现完成后，先运行现有单元测试，再补做真实浏览器 E2E 验证
2. E2E 测试应覆盖真实页面加载、用户点击、输入、上传、跳转与关键状态反馈
3. 不能用“测试通过了组件单测”替代页面级验证
4. 如果页面行为与单元测试结果冲突，以真实浏览器中的行为为准继续排查

### 最低验收标准
- 首页至少验证首屏加载、token 入口可用、移动端布局不破坏
- 聊天页至少验证消息发送、左右消息布局、typing 态、附件上传入口、`ready_to_generate` 确认按钮、completed 后 successor token 展示
- 后台页至少验证管理员 token 鉴权、token 列表、详情与 revoke
- 只有单元测试通过但未做 `agent-browser` E2E 的前端任务，不算完成

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
export OPENAI_MODEL="qwen3.5-plus"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export ADMIN_TOKEN="your-admin-token"
```

### Quality gates（机械化验证，不可跳过）
```bash
# 后端
cd backend && pytest -q

# 前端
cd frontend && npm test
cd frontend && npm run build
```

前端任务完成时，除上述命令外，还必须使用 `agent-browser` skill 对本地运行中的页面进行真实浏览器验证。

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
