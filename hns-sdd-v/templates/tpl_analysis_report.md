# Alignment Analysis Report

> 文件：`{{VERSION_ROOT}}/analysis-report.md`
> Version：`{{VERSION_ID}}` · 更新：{{DATE}}
> 仅在存在 P0/P1、复杂澄清或审计要求时创建；恢复审查时更新同一文件。

## Scope

| Type | File / section | Why included |
|------|----------------|--------------|
| Steering | `docs/sdd/steering/{{FILE}}` | {{REASON}} |
| Current | docs/sdd/current/product.md | {{RELEVANT_BEHAVIOR}} |
| Active version | `{{VERSION_ROOT}}/{{FILE}}` | {{REASON}} |
| Finished dependency | `docs/sdd/specs/{{VERSION}}/{{FILE}}` | `version.md` explicit reference |

## Coverage

| REQ | AC | Design section | Manifest Impact | data/API | Result |
|-----|----|----------------|-----------------|----------|--------|
| {{VERSION_PREFIX}}-REQ-001 | {{VERSION_PREFIX}}-REQ-001-AC-001 | {{SECTION}} | {{VERSION_PREFIX}}-IMP-001 / none | {{REFERENCE_OR_NONE}} | {{PASS/ISSUE}} |

## Findings

| Priority | REQ / AC or anchor | Issue | Decision | Status |
|----------|--------------------|-------|----------|--------|
| P1 | {{ID_OR_FILE_SECTION}} | {{ISSUE}} | {{ACTION}} | {{OPEN/RESOLVED/BLOCKED}} |

## Conclusion

- Unresolved P0: {{COUNT}}
- Unresolved P1: {{COUNT}}
- Result: {{PASS / BLOCKED}}
- Updated files: {{FILES}}
