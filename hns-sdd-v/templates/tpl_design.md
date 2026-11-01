# Version Design（按需）

> 文件：`{{VERSION_ROOT}}/design.md`
> 仅在当前 version 有新的架构、流程、数据、API、兼容或安全决策时创建。

## Increment overview

- Scope: {{SCOPE}}
- Steering references: {{REFERENCES}}
- Covers: {{VERSION_PREFIX}}-REQ-001 / {{VERSION_PREFIX}}-REQ-001-AC-001

## Implementation decision

{{MINIMAL_IMPLEMENTATION_AND_BOUNDARY}}

## Data / API delta

{{INLINE_DELTA_OR_REFERENCE_TO_VERSION_DATA_OR_API}}

## Failure, security and compatibility

{{ERROR_SECURITY_COMPATIBILITY}}

## Verification surface

{{OBSERVABLE_RESULTS_AND_TEST_HOOKS}}

## Steering impact

{{IMPACT_DETAILS_AND_VERSION_PREFIX_IMP_IDS_OR_NONE}}

这里只解释设计影响并引用 Impact ID；唯一 Manifest 表维护在 `version.md`。
