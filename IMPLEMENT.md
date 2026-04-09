# IMPLEMENT.md

## Execution protocol
你必须严格按照以下流程执行任务。

---

## Step 0: Read context
开始任何实现前，先阅读（按 `AGENTS.md` 中 Document map 的顺序）：
- `AGENTS.md` → 约束与地图
- `PLANS.md` → 当前 Task 的目标与验收标准
- `IMPLEMENT.md` → 本文件（执行规程）
- `DOCUMENTATION.md` → 当前状态、阻塞项、上一步的决策

然后深入阅读：
- 当前活跃实施计划（以 `AGENTS.md` 的 `Reference documents` 为准） — 当前 Task 完整描述
- 当前活跃产品规格（以 `AGENTS.md` 的 `Reference documents` 为准） — 产品规格（有行为疑问时读）

最后阅读当前任务直接相关的代码、测试、配置。

不要在未理解上下文前直接修改代码。

---

## Step 0.5: Task isolation（worktree）
如果当前任务满足以下任一条件，**在独立 worktree 中执行**：
- 多个 agent 并行处理不同 Task
- 当前 Task 风险较高（涉及数据库 schema、路由层改动、大量文件变更）
- 希望在不影响主分支的前提下验证后再合并

```bash
# 创建 worktree（在主仓库根目录执行）
git worktree add ../zzetz-task-N -b task/N-short-name

# 在 worktree 中执行任务，完成后合并
git worktree remove ../zzetz-task-N
```

**每个 worktree 规则**：
- 只关注本任务目标，不假设其他 worktree 的改动已存在
- 可在 worktree 根目录放 `TASK.md` 明确当前边界
- 合并前必须再次运行全量验证

---

## Step 1: Restate task internally
在开始实现前，先明确：
- 当前正在做哪个 Milestone / Task（对应 Plan 中的 Task 编号）
- 本次允许修改哪些文件（参考 Plan 中 Task 的 Files 清单）
- 完成标准是什么（参考 PLANS.md 的 Acceptance criteria）
- 要跑哪些验证命令
- 要执行哪些 git commit

如果任务边界模糊，优先选择最小可行范围，不主动扩大任务。

---

## Step 2: Plan minimal implementation
先想清楚：
- Plan 文档中该 Task 的 Step 顺序是什么
- 哪些 Step 是写测试，哪些是写实现
- 是否已有可复用实现
- 哪些测试必须同步调整
- 哪些风险需要提前规避

默认优先：
1. 严格按 Plan 的 Step 顺序执行
2. 复用 Plan 中给出的代码示例
3. 局部调整（如果 Plan 代码有小问题）
4. 自行扩展（仅在 Plan 未覆盖但 Spec 要求时）

---

## Step 3: Implement in small increments
实现时遵循：
- 严格按 Plan 的 TDD 流程：先写测试 → 确认失败 → 写实现 → 确认通过
- 每一轮修改后立即运行相关测试，不积累到最后再验
- 不做无关清理、命名统一、格式化大改
- 每个 Task 结束时执行 Plan 指定的 git commit

**反馈闭环原则**：错误要在发生处捕获，不要等到任务末尾才发现。
- 改了类型 → 立即运行 `tsc`（或 `npm run build`）
- 改了 API → 立即运行对应测试文件
- 改了 prompt → 立即运行 `test_llm_orchestrator.py`
- 不要等到 Step 4 才统一验证

---

## Step 4: Validate before claiming success
完成后必须执行该任务要求的验证命令。

### Rules
- 不得跳过失败的验证
- 不得只因为"代码看起来没问题"就宣称完成
- 若命令失败，必须先处理，或明确记录为阻塞
- 若测试需要环境变量（如 `OPENAI_API_KEY`），使用 monkeypatch 或 mock，不依赖真实外部 API

### Validation scope
| 改动类型 | 必须执行的验证 |
|----------|---------------|
| 后端 API / 业务逻辑 | `pytest -q` + 相关测试文件 |
| 前端 UI / 交互 | `npm test` + `npm run build` |
| 共享 schema / 类型 | 前后端相关测试 + 构建验证 |
| LLM prompt | `test_llm_orchestrator.py` + 确认 prompt 路径正确 |

---

## Step 5: Update DOCUMENTATION.md and SESSION_CONTEXT.md
每完成一个 Task，必须同步更新以下两个文件：

### DOCUMENTATION.md（系统记录，完整）
写入：
- 本次 Task 名称与编号
- 修改摘要
- 关键设计决策（如果偏离了 Plan，说明原因）
- 跑了哪些验证及结果
- 已知问题
- 下一步建议

### SESSION_CONTEXT.md（快速恢复摘要，精简）
更新以下字段：
- `当前阶段` → 改为刚完成的 Task 编号与下一个应执行的 Task
- `当前状态` → 改为当前真实状态（in progress / completed / blocked）
- `下一次会话最应该做什么` → 改为下一个 Task 的具体起点
- `最近重要提交` → 追加本次 commit hash 与 message

**注意**：`SESSION_CONTEXT.md` 里只写相对路径（如 `docs/...`），不写本地绝对路径。

`DOCUMENTATION.md` 是完整记录，`SESSION_CONTEXT.md` 是快速恢复入口。两者都必须在任务结束前更新，否则下一个会话的起点信息是错的。

---

## Step 6: Final self-review
结束前做一次自检：

### Scope check
- 是否超出 Task 的 Files 清单范围？
- 是否改了不该改的文件？

### Quality gates（架构约束的机械执行层）
- 前端 `npm run build` 是否通过？
- 后端 `pytest -q` 是否通过？

这两条 CI 检查不是可选的——它们是架构边界的唯一强制执行机制。它们发现的问题，比事后 code review 发现的更便宜修复。

### Consistency check
- 状态名是否与当前活跃 Spec 一致？
- 路由是否统一在 `/api/sessions/...` 下？
- 中文文案是否与 Spec 一致？

如果答案存在问题，不应直接结束任务。

---

## Output style for task completion
任务完成时，给出简洁总结：

1. 完成了什么（Task 编号与名称）
2. 改了哪些关键文件
3. 跑了哪些验证及结果
4. 当前是否存在风险或阻塞
5. DOCUMENTATION.md 是否已更新
6. 下一个应执行的 Task

---

## Hard rules
### Never do these
- 不阅读上下文就大改
- 不跑验证就说完成
- 发现问题但隐藏不报
- 扩大任务范围
- 删除测试来让测试"通过"
- 编造未实际执行过的命令结果
- 跳过 Plan 中"先确认测试失败"的步骤
- 用纯 mock 替代主链路的真实 LLM 调用（测试中 mock 外部依赖是允许的）
- 输出英文界面文案（必须简体中文）

### Always do these
- 先读 Plan 中当前 Task 的完整描述
- 先做最小方案
- 先验证
- 先记录
- 对不确定项保持明确说明
- 每个 Task 结束时按 Plan 指定的 commit message 提交

---

## Failure handling
若遇到以下情况：
- 缺依赖
- 测试环境损坏
- Plan 中的代码示例有错误
- 配置不完整
- 外部服务不可用

应：
1. 记录真实情况
2. 说明这是 Plan 代码问题还是本次改动引入
3. 说明已经尝试的解决方式
4. 修复后继续（如果是小问题）
5. 记录阻塞并提供下一步建议（如果是大问题）

不要把这类情况伪装成"任务已完全完成"。
