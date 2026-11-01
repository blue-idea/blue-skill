# STEP 3 · 最小设计与基线影响

读取 requirements、相关工程约束和当前业务基线。存在真实决定才用 tpl_design.md 创建 design.md；沿用现状时，在 version.md 的 Design decision 章节写 no new design 及所依循基线。

设计说明覆盖的 REQ/AC、实现边界、错误处理、数据/API、兼容迁移与验证接口；只写适用内容。data/API 增量优先内联，明显影响可读性时再拆文件。

在 version.md 唯一 Manifest 登记长期影响，planned 状态，精确到基线目标和本期 delta 锚点。业务行为使用 product 域，目标 current/product.md，来源可为 requirements.md。没有长期变化时写 No Steering impact: true 及依据。

active 执行时不提前发布提案为稳定基线；基线合并在收尾候选中准备。内部实现调整在授权范围内继续；对外行为变化先处理范围决定。
