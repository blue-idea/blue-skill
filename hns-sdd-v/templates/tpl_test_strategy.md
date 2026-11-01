# Version Test Strategy（按需）

> 文件：`{{VERSION_ROOT}}/test_strategy.md`
> 仅在跨 TASK 风险、多个测试层、性能/安全门禁或独立环境策略存在时创建。

## Cross-task risks

| Risk | TASK / AC | Gate | Evidence |
|------|-----------|------|----------|
| {{RISK}} | {{TASK_AND_AC}} | {{PASS_CONDITION}} | {{EVIDENCE}}

## Test layers and gates

| Layer | Scope | Pass condition |
|-------|-------|----------------|
| {{Unit/Integration/Contract/API/E2E/Performance/Security/Manual}} | {{SCOPE}} | {{GATE}} |

## Environment and data

- Setup / cleanup: {{METHOD}}
- Environment isolation: {{STRATEGY}}
- Sensitive values: reference `{{VERSION_ROOT}}/info.md`; never copy secrets here.

不重复 design 的框架选择，也不复制每个 TASK 的验证命令。
