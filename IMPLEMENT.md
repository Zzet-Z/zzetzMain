# IMPLEMENT.md

## Execution protocol
你必须严格按照以下流程执行任务。

---

## Step 0: Read context
开始任何实现前，先阅读：
- `AGENTS.md`
- `PLANS.md`
- `IMPLEMENT.md`
- `DOCUMENTATION.md`

然后阅读当前 Task 在 Plan 文档中的完整描述：
- `docs/superpowers/plans/2026-04-08-personal-website-mvp.md`

再阅读产品规格（确认行为预期）：
- `docs/superpowers/specs/2026-04-08-personal-site-homepage-and-intake-design.md`

最后阅读当前任务直接相关的代码、测试、配置。

不要在未理解上下文前直接修改代码。

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
- 每一轮修改尽量保持仓库仍可验证
- 不做无关清理
- 不做无关命名统一
- 不做无关格式化大改
- 每个 Task 结束时执行 Plan 指定的 git commit

---

## Step 4: Validate before claiming success
完成后必须执行该任务要求的验证命令。

### Rules
- 不得跳过失败的验证
- 不得只因为"代码看起来没问题"就宣称完成
- 若命令失败，必须先处理，或明确记录为阻塞
- 若测试需要环境变量（如 `OPENAI_API_KEY`），使用 monkeypatch 或 mock，不依赖真实外部 API

---

## Step 5: Update DOCUMENTATION.md
每完成一个 Task，必须更新 `DOCUMENTATION.md`，写入：

- 本次 Task 名称与编号
- 修改摘要
- 关键设计决策（如果偏离了 Plan，说明原因）
- 跑了哪些验证
- 验证结果
- 已知问题
- 下一步建议

---

## Step 6: Final self-review
结束前做一次自检：

### Scope check
- 是否超出 Task 的 Files 清单范围？
- 是否改了不该改的文件？

### Quality check
- 是否按 Plan 补了所有要求的测试？
- 是否更新了 DOCUMENTATION.md？
- 是否有明显回归风险？

### Consistency check
- 代码中的状态名是否与 Spec 一致（draft/queued/active/generating_document/completed/failed）？
- 路由是否统一在 `/api/sessions/...` 下？
- 中文文案是否与 Spec 一致？

### Stability check
- 前端 `npm run build` 是否通过？
- 后端 `pytest -q` 是否通过？

如果答案存在问题，不应直接结束任务。

---

## Output style for task completion
任务完成时，应给出简洁总结，包含：

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

---

## Multi-agent / multi-worktree note
如果当前任务在独立 worktree 或独立线程中执行：
- 只关注本任务目标
- 不假设其他线程的改动已存在
- 不修改其他 worktree 负责的范围
- 合并前再次核对验证
- 每个 worktree 可放一个临时 `TASK.md` 明确当前任务边界
