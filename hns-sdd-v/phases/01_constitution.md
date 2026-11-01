# STEP 1 · 初始化与恢复

读取已有入口、代码、配置、测试与文档，提取稳定事实。旧 constitution 只迁移已证实内容。

1. 恢复现有 active 或明确选择的 draft。遵守默认唯一 active 与串行规则；空项目可以建立 v1 draft，无须先存在 active。
2. 按 tpl_steering.md 补齐三份工程基线。data/api 仅在存在该领域时创建；用 tpl_current.md 保存已有业务行为，没有行为时不造空文件。
3. 局部更新 docs/AGENTS.md 的导航；若已有根入口，将 SDD 链接接入现有导航，保留无关规则。
4. 建立 versions.md 和 version.md，Version vN 与 Prefix Vn 一致。version.md 为状态与日期来源，注册表仅同步索引。
5. 根据用户已授权范围填写 Goal、Scope、Non-goals、历史依赖；实质未决事项才澄清。范围明确后将两处状态同时设为 active，进入需求。

按 templates/tpl_agents.md、tpl_versions.md、tpl_version.md、tpl_steering.md、tpl_current.md 生成实际内容。无需复制模板目录。
