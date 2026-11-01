# Version {{VERSION}}

- **Version**: `{{VERSION}}`
- **Version Prefix**: `{{VERSION_PREFIX}}`
- **Status**: `{{draft/active/finished}}`
- **Started**: {{YYYY-MM-DD_OR_EMPTY}}
- **Finished**: {{YYYY-MM-DD_OR_DASH}}

## Goal

{{GOAL}}

## Scope

- {{IN_SCOPE}}

## Non-goals

- {{OUT_OF_SCOPE}}

## Historical dependencies

- {{FINISHED_VERSION_ARTIFACT_OR_NONE}}

## Design decision

- **Design decision**: {{DESIGN_FILE_REFERENCE_OR_no new design_AND_BASELINE_REFERENCE}}

## Steering Impact Manifest

- **No Steering impact**: {{true/false}}

| Impact ID | Domain | Action | Steering target | Version delta | Verification | State |
|-----------|--------|--------|-----------------|---------------|--------------|-------|
| {{VERSION_PREFIX}}-IMP-001 | {{product/project-rules/tech-stack/style-guide/data/api}} | {{add/change/deprecate/remove}} | `docs/sdd/{{steering_OR_current}}/{{FILE}}.md#{{ANCHOR}}` | `{{requirements.md/design.md/data.md/api.md/version.md}}#{{ANCHOR}}` | {{LOCAL_EVIDENCE_FILE_OR_PLANNED_CHECK}} | planned |

状态只允许 `planned / verified / synced`。无长期影响时设置 `No Steering impact: true` 并删除示例数据行；有行时必须为 false。Manifest 是唯一影响清单，不在 design 或其他文件复制表格。

## Alignment review

- **Date**: {{DATE_OR_EMPTY}}
- **Scope checked**: {{STEERING_AND_VERSION_FILES}}
- **Result**: {{PASS / BLOCKED / NOT_RUN}}
- **Notes**: {{KEY_FINDINGS_OR_NONE}}
- **Detailed report**: {{analysis-report.md / not_needed}}

## Steering sync

product 影响存在时增加 current/product.md 行；其他行从 Manifest 派生。

| Document | State | Evidence |
|----------|-------|----------|
| `project-rules.md` | {{待确认/未变化/已同步/不适用}} | {{DETAIL}} |
| `tech-stack.md` | {{待确认/未变化/已同步/不适用}} | {{DETAIL}} |
| `style-guide.md` | {{待确认/未变化/已同步/不适用}} | {{DETAIL}} |
| `data.md` | {{待确认/未变化/已同步/不适用}} | {{DETAIL}} |
| `api.md` | {{待确认/未变化/已同步/不适用}} | {{DETAIL}} |

存在 `待确认` 时不得 finished。
Manifest 指向某文档时，该文档 finished 前必须为 `已同步`；没有 Manifest 的文档不得标记 `已同步`。

## Completion evidence

- **Commands and actual results**: {{COMMANDS_AND_RESULTS}}
- **TASK / AC evidence**: {{EVIDENCE_REFERENCES}}
- **Confirmed exceptions**: {{BLOCKED_WONTFIX_OR_NONE}}
- **Residual risks**: {{RISKS_OR_NONE}}
