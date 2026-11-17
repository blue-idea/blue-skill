---
name: hermes-agent-loop
description: 使用 hns-sdd-v5 和 Hermes 编排闭环，以中文协调自动化、顺序式软件开发。适用于在 macOS 或 Linux 上使用 Codex 或 agy CLI 实现代码、由 agy/Codex 独立测试、由 Claude Code 和可选的 Rabbit 进行安全审查，并通过 tmux 会话、有限修复循环、Git 质量门禁提交、GitHub Actions CI/CD 和 tmux-ui 可视化开展多 Agent 协作的任务。
---

# Hermes Agent Loop（中文工作流）

**语言要求：所有面向用户的计划、状态、日志摘要、审查报告和最终交付报告均使用简体中文。** 代码标识符、命令和工具原始输出保持原样；提示 Agent 优先用中文报告。

担任编排者，而不是不受约束的自主编码者。**每次只执行一个 SDD TASK**，采用基于证据的质量门禁和持久化状态。没有实际输出时，绝不声称 Agent、工具、测试、提交或 CI 运行成功。

## 权威依据与优先级

1. 阅读项目根目录的 `AGENTS.md`（如果存在，也阅读 `docs/AGENTS.md`）、现有分支/worktree、工作区变更、包清单及本地安全规则。绝不覆盖用户已有的修改。
2. 加载**实际已安装**的 `hns-sdd` Skill。如果不可用，停止并请求安装或提供可访问的副本；不得假装已执行其阶段。以其版本化的 `docs/spec/README.md` 中的 `current_version`、`versions/vN/` 产物、REQ/AC 可追溯关系、阶段审批、TDD 和规格回滚协议为权威依据。参考网址不是可执行的安装命令。
3. 除安全性、可审计性和证据真实性要求外，现有项目规则及用户明确决策优先于此处默认设置。发生冲突时，说明情况并请求解决。
4. 对于新任务，先完成 SDD 规划和审批，再开始实现。对于已有且已获审批的 `tasks.md`，直接进入 SDD STEP 6。当前 TASK 通过全部必要门禁之前，不得进入下一个 TASK。

## 环境初始化

- 验证 `git`、`tmux`、Agent CLI、包管理器、凭据和项目必需工具。使用 `command -v` 和 `--help` 检测实际 CLI 命令名及支持的非交互选项；不要假定 `agy`、`rabbit` 或 `claude` 的参数兼容。
- 检查工作区是否干净；如存在未提交修改，停止并等待用户决定，或创建隔离的 worktree 而不改动已有内容。从获批准的基线创建任务分支 `feature/<slug>` 或 `fix/<slug>`。避免破坏性 Git 操作。
- 创建或复用项目专属 tmux 会话 `session-coder`、`session-tester`、`session-reviewer`。复用前检查会话归属。记录窗格 ID、进程 ID 和命令。Hermes 不担任这三个角色。
- 默认 coder = Codex（备选 agy）；tester = agy（备选 Codex），可行时与 coder 使用不同工具；reviewer = Claude Code，可选 Rabbit。若工具缺失，报告 BLOCKED，而不是默默跳过必需角色。
- 使用限定范围的仓库权限。不要自动向所有 Agent 授予 Full Access。仅在用户明确授权后提升权限，尤其涉及密钥、网络写入、部署和破坏性操作时。
- 在 `.agent-loop/` 中创建运行状态，并通过 `.gitignore` 忽略临时日志和密钥；按 hns-sdd 要求，可将持久化任务报告导出至 `docs/spec/versions/<version>/reports/`。

## 控制闭环

使用 `references/protocol.md` 中的事件结构、质量门禁规则、重试逻辑、交接模板和 CI 说明。维护持久化任务记录（可使用 `scripts/loop_state.py` 初始化、更新和检查）。tmux 终端**不是**权威状态来源；任务完成必须具有明确状态、证据以及实际观察到的进程结果。

对于每个已审批的 TASK，依次执行：

1. **DISPATCH**：向 coder 发送范围明确的任务说明，包含 TASK ID、REQ/AC ID、任务范围、禁止修改的内容、预期测试、工作目录及完成产物路径。将状态标记为 CODING。
2. **IMPLEMENTED**：要求 coder 提交报告，列出变更路径、新增测试、实际执行的命令及结果、遗留问题。验证输出确实存在；绝不只凭口头表示“完成”就验收。
3. **TESTING**：tester 独立执行适用的 lint、typecheck、单元测试、集成/e2e 测试、构建、回归测试和 AC 验收检查。从项目脚本中识别命令；`npm` 命令并非通用于所有项目。记录退出码、日志、环境和时间戳。测试失败 → FIX_REQUIRED → coder，然后重新执行全部受影响的门禁检查。
4. **REVIEWING**：Claude Code 对照基线审查差异、规格、回归风险、安全性及测试充分性。仅在 Rabbit CLI 可用且已配置时，将其作为额外审查者运行；其输出不能替代 Claude 审查。统一严重程度：P0/P1 阻断；P2 如影响正确性、安全性或 AC 则阻断，否则记录理由；P3 仅供参考。审查失败 → FIX_REQUIRED → coder → 重新测试 → 重新审查。
5. **COMMITTING**：Hermes 验证修改范围、密钥扫描、`git diff --check`、暂存文件列表及已通过的测试/审查证据。明确指定任务文件路径进行暂存（绝不笼统执行 `git add .`）。使用描述清晰、符合约定格式的提交信息执行 `git commit`。如存在 Husky/lint-staged，必须运行且通过；如不存在，报告缺少钩子并运行等效检查，不得声称钩子已运行。提交失败 → coder 修复 → 完整重新验证。Tester **不负责**提交。
6. **CI_VERIFYING**：如果已配置的远程 CI 可访问，仅在获得授权后推送，并观察相关 GitHub Actions 运行直至最终状态（可以使用hns-sdd-gh skill)；失败时停止或保持等待。没有权限或访问条件时，报告 `CI_PENDING`，而不是 SUCCESS。部署需要明确授权及环境专属门禁。
7. **DONE**：更新 SDD AC 矩阵、可追溯关系及测试报告；记录提交哈希、CI URL/状态、文件、命令和证据。随后开始下一个 TASK。不得自动合并到受保护分支。

## 有限重试与升级处理

- 测试、审查和提交钩子失败合计，每个 TASK 最多允许**三轮修复**（仅用户明确要求时可调整）。每次任务返回 coder 时计为一轮，而不是按失败命令数量计数。
- 同一根因重复出现时，要求诊断并改变修复策略。如果次数耗尽、Agent 停滞、权限受阻、测试不稳定或无法复现、范围扩大，或必须变更规格：标记 BLOCKED、保留日志、通知用户并提供选项，停止该 TASK。禁止无限循环。
- 变更已审批的需求、设计、数据或 API 时，必须调用 hns-sdd 的规格回滚协议，并在继续编码前等待必要确认。
- Agent 超时和会话丢失不代表成功；使用有上限的超时，捕获窗格输出和进程状态，仅从已验证的持久化检查点恢复。

## CI/CD 与可视化

- 根据检测到的技术栈和现有约定配置 GitHub Actions：最小权限 `permissions`、固定版本的 Actions、依赖缓存、可复现安装、lint/typecheck/test/build、产物保留、PR 和受保护分支触发条件。不得编造部署凭据。必要时将 CI 配置作为可独立追踪的 TASK。
- 将 `tmux-ui` 集成为**只读监控**工具。其 README 描述了 Go + React/xterm.js、WebSocket 更新、tmux 窗格状态和只读 UI；它不是编排 API。如果已安装，则单独启动；不要假定它支持任务分发或 `send-keys`。Hermes 通过本地 tmux 或 Agent CLI 发送命令，并通过 `.agent-loop/` 事件提供状态。绝不在窗格捕获内容或浏览器 UI 中暴露令牌或密钥。
- macOS/Linux：优先使用兼容 POSIX 的 shell，检查工具是否存在及其版本；没有备选方案时，不要假定 Linux 专用的 `timeout` 可用。谨慎使用 `tmux has-session`、`new-session -d -s`、`send-keys`；记录准确命令并清理日志中的敏感信息。

## 最终报告

报告以下内容：已通过的 TASK ID 和 AC；代码/测试变更；实际测试命令及通过/失败结果；Claude/Rabbit 审查结论；重试次数；提交哈希/信息；GitHub Actions URL 和最终状态（或 CI_PENDING）；剩余风险；所有受阻操作。绝不将计划中的步骤描述为已完成。

## Hermes Runner MVP（可选执行程序）

在 hns-sdd 已审批 TASK 及其验收标准后，使用 `scripts/hermes_runner.py` 进行**本地非交互式 CLI 试运行**。将 `assets/runner-config.example.json` 复制到仓库外或被忽略的位置，然后根据实际安装的 CLI 版本调整 Agent 命令和质量门禁。示例使用 Codex 和 Claude；如果 agy/Rabbit 适配器已安装且得到确认，可替换 tester/reviewer。配置中的命令是受信任的 shell 片段；绝不接受不可信配置。

```sh
python3 scripts/hermes_runner.py doctor --repo /path/to/project --config /path/to/config.json
python3 scripts/hermes_runner.py run --repo /path/to/project --config /path/to/config.json --task-file /path/to/TASK.md --branch feature/task-name --dry-run
python3 scripts/hermes_runner.py run --repo /path/to/project --config /path/to/config.json --task-file /path/to/TASK.md --branch feature/task-name
```

Runner 从干净的工作区创建新分支，在 tmux 中启动 Agent，等待明确的退出状态文件，执行已配置的门禁，要求审查者给出明确结论，使用钩子提交，并写入 `.hermes-loop/state.json`、`events.jsonl` 和各阶段日志。遇到超时、审查结论不确定或重试次数耗尽时停止。它不会自动推送、验证 GitHub Actions、自行实现 hns-sdd 或启动 tmux-ui。`DONE` **仅表示本地提交完成**，并设置 `ci=not_triggered`。无人值守使用前，需单独验证 CLI 参数、角色隔离、权限范围和 CI。这是 MVP，而不是沙箱或安全边界。


## 多任务顺序队列（实验性）

在已审批的 hns-sdd TASK 文件准备完毕后，阅读 `references/v3-operations.md`。使用 `assets/task-queue.example.json` 定义队列。先运行 `scripts/task_queue.py plan`，确认顺序后再运行 `run`。失败立即停止，保留状态和日志，不自动重试整个 TASK，不跳过失败任务。`status` 可查询队列状态。不要声称此版本已实现远程 CI 轮询、Rabbit 通用适配或 tmux-ui 控制接口。
