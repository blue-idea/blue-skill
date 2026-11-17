# 任务状态与事件协议

状态：PLANNED -> DISPATCHED -> CODING -> IMPLEMENTED -> TESTING -> REVIEWING -> COMMITTING -> CI_VERIFYING -> DONE。任何活动阶段均可转为 FIX_REQUIRED -> CODING（增加 correction_cycles），或转为 BLOCKED。绝不直接从 IMPLEMENTED 跳到 DONE。

以原子方式存储 `.agent-loop/state.json`，包含以下键：schema_version、task_id、spec_version、branch、state、correction_cycles、max_correction_cycles、agent_sessions、evidence、last_error、commit、ci。以仅追加方式记录 `.agent-loop/events.jsonl`：`{timestamp, task_id, role, event, state, attempt, artifact, message}`。对令牌、个人数据和密钥进行脱敏；避免无限增长的终端日志。持久化保存进程退出码和超时信息。

Agent 交接约定：
- 任务说明：`task_id`、`spec_version`、`req_ids`、`ac_ids`、`allowed_paths`、`forbidden_paths`、`expected_checks`、`base_commit`、`report_path`。
- Coder 报告：`status`、`changed_files`、`tests_added`、`commands`、`exit_codes`、`known_issues`。
- Tester 报告：`status`、`checks[{name,command,exit_code,log_path}]`、`ac_results`、`regressions`、`environment`。
- Reviewer 报告：`status`、`findings[{severity,file,line,reason,remediation}]`、`reviewed_diff_base`、`unresolved_risks`。
- Hermes 必须独立验证报告中的路径和退出码。仅有退出状态 0 不足以证明 AC 已覆盖。

质量门禁：所有必需检查通过、所有 AC 均有证据、没有阻断性发现、没有意外文件、没有暴露密钥、已安装的钩子通过、提交已记录。如果远程 CI 为必需项，则 `CI_PENDING` 与 `DONE` 不同。绝不强制使用 `--no-verify` 或绕过必需检查。

重试策略：第一次失败 => 诊断并修复；第二次 => 比较根因并改进测试；第三次 => 最后一次修复尝试。如果验证再次失败，标记 BLOCKED。相同失败重复出现或涉及危险操作时通知用户。会话重启后不得悄悄重置计数器。

GitHub Actions：遵循现有工作流约定；可行时将第三方 Actions 固定到不可变 SHA，使用 `permissions: contents: read`，针对已批准的分支使用 pull_request + push 触发、并发分组和依赖锁文件，将 CI 与部署分离。检查 CI 时，仅在 `gh run list/view` 已安装且通过认证的情况下使用；否则保留待验证状态。

任务结果示例：`TASK-004: BLOCKED; cycles=3; lint PASS; unit FAIL; reviewer NOT_RUN; commit none; CI NOT_RUN; see .agent-loop/events.jsonl`。
