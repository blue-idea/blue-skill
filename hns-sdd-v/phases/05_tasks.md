# STEP 5 · 任务与验证

使用 tpl_tasks.md；tasks.md 为唯一任务来源。按可交付、可验证增量划分，绑定 REQ、AC、设计锚点、适用 Impact、测试方式、命令/手工步骤、证据与依赖。测试工作默认属于对应交付；独立测试补齐、平台或跨功能验收有实际交付物时可单列 TASK，仍需 AC/风险依据。

每个字段使用 - **Field**: value 格式。编号不重排复用，Status 为权威，checkbox 与之同步；不再手工维护重复 Summary 表。每条 AC 有任务覆盖，每条 Impact 有负责 TASK；依赖存在且无环。

test_strategy.md 用于跨任务环境/风险策略；traceability.md 仅用于大型追溯或审计，是派生视图。info.md 只在确实需要时创建并忽略，优先记录凭据引用。顺序、范围明确时沿用用户授权继续，不额外设置固定确认关卡。
