# Version Test Report（条件产物）

> 文件：`{{VERSION_ROOT}}/reports/{{REPORT_ID}}-report.md`
> 仅在跨 TASK 聚合风险、发布审计或用户明确要求时创建。

## Summary

- Version: {{VERSION_ID}}
- Status: {{PASS / RISK_ACCEPTED / FAIL / BLOCKED}}
- Commands run: {{COUNT}}
- Unresolved risks: {{RISKS_OR_NONE}}

## Actual results

| TASK / AC | Type | Command | Actual result | Evidence |
|-----------|------|---------|---------------|----------|
| {{TASK_ID}} / {{AC_ID}} | {{TYPE}} | `{{COMMAND}}` | {{RESULT}} | {{EVIDENCE}} |

## Exceptions

| TASK / AC | Decision | Confirmation | Reason | Residual risk |
|-----------|----------|--------------|--------|---------------|
| {{TASK_ID}} / {{AC_ID}} | {{BLOCKED/WONTFIX}} | {{WHO_WHEN}} | {{REASON}} | {{RISK}} |

不为填表生成评分；只有 `phases/qa_engine.md` 要求且每项都有真实数据时才计算质量分。
