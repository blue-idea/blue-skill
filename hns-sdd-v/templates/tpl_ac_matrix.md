# TASK AC Evidence

> 文件：{{VERSION_ROOT}}/ac/{{TASK_ID}}-AC.md

- **Code revision**: {{COMMIT_AND_DIRTY_DIFF_IDENTITY}}
- **Spec revision**: {{SPEC_AND_BASELINE_IDENTITY}}
- **Environment**: {{REAL_ENVIRONMENT_WITHOUT_SECRETS}}
- **Executed**: {{YYYY-MM-DD}}

| AC ID | Test type | Command / steps | Expected | Actual | Result | Evidence / error |
|-------|-----------|-----------------|----------|--------|--------|------------------|
| {{VERSION_PREFIX}}-REQ-001-AC-001 | {{TYPE}} | {{REAL_COMMAND_OR_STEPS}} | {{EXPECTED}} | {{ACTUAL}} | {{PASS/FAIL/BLOCKED}} | {{RUN_ARTIFACT_OR_OBSERVATION}} |

## Exception decision

- **Disposition**: {{none/confirmed BLOCKED/confirmed WONTFIX}}
- **Confirmed by / date**: {{REAL_CONFIRMATION_OR_none}}
- **Reason**: {{REASON_OR_none}}
- **Residual risk**: {{RISK_OR_none}}

WONTFIX 是处置，原始 Result 保留 FAIL 或 BLOCKED。只保留当前任务 AC，每条一行；单元格内竖线写 &#124;。人工测试记录具体步骤和观察，不伪造命令或退出码。
