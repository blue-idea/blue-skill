# V3 操作手册（中文）

## 已实现
- `task_queue.py`：按 JSON 顺序调用已有 `hermes_runner.py`；任务失败立即停止，不跳过失败任务。
- `plan`：仅验证任务文件并打印计划；`status`：读取持久化状态。
- 队列状态写入 `.hermes-loop/queue-state.json`，每项任务输出 `queue-N.log`。

## 执行前置条件
- 项目已按 hns-sdd-v5 审批每个 TASK；`AGENTS.md` 存在；工作区干净。
- `tmux` 和所选 Agent CLI 已安装并配置为可退出的非交互命令。
- `assets/runner-config.example.json` 的测试命令、可修改路径、角色命令必须改成项目真实配置。
- 此版本每个 TASK 创建独立分支；后续任务从当前 HEAD 建分支，形成线性提交链。请事先确认这符合项目分支策略。

## 命令
```sh
python3 scripts/task_queue.py plan --repo /path/to/repo --config /path/to/config.json --queue /path/to/queue.json
python3 scripts/task_queue.py run --repo /path/to/repo --config /path/to/config.json --queue /path/to/queue.json
python3 scripts/task_queue.py status --repo /path/to/repo
```

## 当前限制
- 不自动恢复中断队列：提交结果不确定时必须人工检查 `git log`、状态和日志，防止重复提交。
- 未实现 GitHub Actions 轮询、Rabbit CLI 通用适配器、tmux-ui 的专用状态 API；这些不能标记为已完成。
- 运行日志可能包含 Agent 输出；使用私有权限保存并检查敏感信息。
- 现有 Runner 以本地提交为成功标准，不代表 CI 已通过；推送和部署均需另行授权。
