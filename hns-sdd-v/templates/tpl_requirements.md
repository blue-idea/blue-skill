# Version Requirements

> 文件：`{{VERSION_ROOT}}/requirements.md`
> Version：`{{VERSION_ID}}` · Prefix：`{{VERSION_PREFIX}}`
> 状态：{{DRAFT/CONFIRMED}} · 更新：{{DATE}}

## Version delta

- **Goal**: {{GOAL}}
- **Scope summary**: {{SCOPE}}
- **Steering references**: {{REFERENCES}}
- **Retired IDs**: {{NONE_OR_IDS}}

## {{VERSION_PREFIX}}-REQ-001 · {{NAME}}

**User story**：作为 {{ROLE}}，我希望 {{GOAL}}，以便 {{BENEFIT}}。

### Acceptance criteria

```yaml
- id: {{VERSION_PREFIX}}-REQ-001-AC-001
  ears: >
    When {{TRIGGER}},
    the {{SYSTEM}} shall {{VERIFIABLE_RESPONSE}}.
  test_type: Unit
  expected:
    result: {{EXPECTED_RESULT}}
    side_effects: {{EXPECTED_SIDE_EFFECTS_OR_NONE}}

- id: {{VERSION_PREFIX}}-REQ-001-AC-002
  ears: >
    While {{PRECONDITION}},
    when {{TRIGGER}},
    the {{SYSTEM}} shall {{VERIFIABLE_RESPONSE}}.
  test_type: API
  expected:
    status: {{HTTP_STATUS}}
    body: {{EXPECTED_BODY}}
```

测试类型只使用 `Unit | Integration | Contract | API | E2E | Performance | Security | Manual`。保留实际需要的 AC；不得为覆盖模板而制造场景。
