# STEP 6 · 实现、验收、收尾

读取 active version、当前 TASK 的 REQ/AC、设计和相关基线。任务通常顺序执行；若项目明确允许并行，先确认依赖和文件写入隔离。Git 操作遵循现有项目约定。

## TASK

1. 标记 doing，按 phases/tdd.md 选择合适验证方式；缺陷修复优先建立复现测试。使用 QA 对应章节即可。
2. 实现并执行任务验证及适用项目门禁。命令失败时定位原因，在已授权范围内修复并重验；必要环境缺失记录 BLOCKED。
3. 按 tpl_ac_matrix.md 记录真实结果及代码/规格/基线身份。规格或实现变化后使受影响证据失效并重验。
4. AC 全部 PASS 才使用 done。confirmed BLOCKED / confirmed WONTFIX 必须有真实用户决定、日期、原因、残余风险，原始 Result 不改成 PASS。
5. 更新任务 Status 和 checkbox；有长期影响的验收通过后将对应 Manifest 改为 verified。未交付影响不能因用户接受风险而自动成为 synced。

遇到产品语义、范围、对外契约变化时，说明冲突与受影响项，复用已有决定或进行必要澄清，然后局部重审需求/设计/任务。内部修复无需重复确认。

## Version 完成

1. 核对覆盖、任务终态、真实证据与最终实现。简单 version 在 Completion evidence 汇总即可；跨任务聚合风险、发布审计或用户要求时才写完整测试报告。
2. 从当前工作树（包含授权范围内未提交变更）建立隔离收尾候选，记录输入代码、规格和基线身份。不要复制凭据。
3. 在候选内把已验证 product 变化合入 docs/sdd/current/product.md；工程变化写入对应 docs/sdd/steering/project-rules.md、tech-stack.md、style-guide.md、data.md、api.md。没有影响的文件不改写。
4. 候选中重验通过后 Manifest 设 synced，sync 汇总一致；源项目仍 active。候选同样保留 active 和空 Finished 日期。
5. 执行 python <skill>/scripts/validate_sdd.py <candidate> --check-finish vN，并运行真实回归及适用门禁。失败保留 active、说明阻塞；用户例外仍不能伪造 PASS。
6. 确认源输入自候选建立后没有变化；将基线、证据、任务及版本元数据作为同一组收尾变更应用，同时在 version.md 与 versions.md 写 finished 和相同真实日期。
7. 执行 --finish vN 复核。脚本只读，不负责自动应用；中断时检查差异并恢复一致状态，禁止仅靠写 finished 绕过门禁。
8. finished 冻结。默认不得创建或编写下一个 version，直到前期收尾全部完成。发现新行为需求时进入下一 version。

历史 finished 的普通校验核对当时结构与证据；当前基线锚点在显式收尾检查时核对，避免后来合法更新令所有历史失效。
