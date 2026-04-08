# 个人网站需求梳理工具

面向简体中文非技术用户的个人网站需求梳理 MVP。首页建立产品认知，需求梳理页通过真实 LLM 引导用户输出中文摘要与 PRD。

---

## 快速启动

### 1. 环境变量

```bash
cp .env.example backend/.env
# 编辑 backend/.env，填入 OPENAI_API_KEY
```

### 2. 安装依赖

```bash
# 后端
cd backend && pip install -e .

# 前端
cd frontend && npm install
```

### 3. 启动服务

```bash
# 后端（默认 http://localhost:5000）
cd backend && python run.py

# 前端（默认 http://localhost:5173）
cd frontend && npm run dev
```

### 4. 验证

```bash
# 后端健康检查
curl http://localhost:5000/api/health
# 返回 {"status": "ok"}
```

---

## 验证与测试

```bash
make test      # 前后端全量测试
make build     # 前端生产构建
make check     # test + build 全部执行
```

或手动执行：

```bash
cd backend && pytest -q
cd frontend && npm test
cd frontend && npm run build
```

---

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | React + TypeScript + Tailwind CSS（Vite） |
| 后端 | Python Flask + SQLAlchemy + SQLite |
| LLM | OpenAI Responses API（httpx 同步调用） |
| 测试 | Vitest（前端）、pytest（后端） |

---

## 项目文档

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | Agent 工作规则与项目地图 |
| `SESSION_CONTEXT.md` | 会话间上下文恢复摘要 |
| `PLANS.md` | 里程碑计划与验收标准 |
| `IMPLEMENT.md` | 执行规程（TDD 流程、worktree、反馈闭环） |
| `DOCUMENTATION.md` | 执行日志、决策记录、当前状态 |
| `apple/DESIGN.md` | 前端 UI 视觉风格指南 |
| `docs/superpowers/specs/` | 产品规格说明书 |
| `docs/superpowers/plans/` | 详细实施计划（Task 1–9） |

---

## 常见问题

**Q: 启动后端时报 `OPENAI_API_KEY not set`**
确认 `backend/.env` 文件存在且包含正确的 key。

**Q: 端口冲突**
后端默认 5000，前端默认 5173。如有冲突可在 `.env` 中修改 `FLASK_PORT`，前端在 `vite.config.ts` 中修改。

**Q: SQLite 数据库在哪**
默认在 `backend/instance/app.db`，已在 `.gitignore` 中排除。

**Q: 测试需要真实 API key 吗**
不需要。所有测试通过 monkeypatch/mock 隔离外部依赖，不调用真实 LLM。
