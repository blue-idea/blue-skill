# STEP 2 · 增量需求

读取选定 active version.md、相关 Current 和 Steering。用 templates/tpl_requirements.md 描述本期行为变化、边界与可测试 AC；未变化行为链接 Current。

REQ 使用 Vn-REQ-NNN，AC 使用 Vn-REQ-NNN-AC-NNN；确认后不重排复用。每条 REQ 至少一个 AC，写明触发条件、预期结果、异常路径与适用测试类型。类型为 Unit / Integration / Contract / API / E2E / Performance / Security / Manual。

已授权且明确的需求直接完善，不重复逐条请求批准。产品语义、范围或风险存在实质冲突时澄清。历史引用必须在 version.md 的 Historical dependencies 登记；本期声明使用当前前缀。需求改变后重审受影响设计、任务和证据，不机械重做无关步骤。
