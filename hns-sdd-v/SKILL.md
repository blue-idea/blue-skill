---
name: hns-sdd
description: Maintain versioned software specifications and execute scoped development with traceable acceptance evidence. Use for docs/sdd setup, incremental requirements/design/tasks, baseline convergence, or version acceptance; ordinary coding does not require adopting the full workflow.
---

# HNS-SDD

## 模型与边界

Steering 保存已接受的工程约束；Current 保存当前业务行为与场景；version 保存本期增量、决定、任务和证据。

    已接受规格 = Steering + Current
    本期目标 = 已接受规格 + active version 增量

active 表示正在实现的目标，不能据此声称实现已满足规格。v1、v2 是工作增量编号，与产品发布版本分开；finished 表示验收闭环，不自动表示发布。

## 项目布局

    docs/AGENTS.md
    docs/sdd/versions.md
    docs/sdd/steering/{project-rules,tech-stack,style-guide}.md
    docs/sdd/steering/{data,api}.md          # 已有契约按需保留，保持唯一来源
    docs/sdd/current/product.md            # 有已接受业务行为时创建
    docs/sdd/specs/<version>/version.md
    docs/sdd/specs/<version>/requirements.md
    docs/sdd/specs/<version>/tasks.md

design.md 仅在有真实设计决定时创建。analysis-report.md、test_strategy.md、traceability.md、data.md、api.md、reports/ 按实际复杂度或审计需要创建。ac/ 保存逐 TASK 验收证据。模板只在生成对应产物时读取，不复制模板目录。

## 进入与恢复

1. 读取已有项目入口及 versions.md；恢复唯一 active，或按用户指定处理 draft/finished。没有 active 时允许初始化、规划和只读审查，不猜测执行目标。
2. 读取相关 Steering、Current 章节以及选定 version.md。只有 Historical dependencies 显式引用的 finished 历史才加载。
3. 按操作读取下方对应阶段；执行只加载当前 TASK 及直接依赖，不预载整个 QA 手册。
4. version.md 的 Status/日期为权威，versions.md 为一致索引；任务 Status 为权威，checkbox 必须一致。禁止另建手工任务账本。

状态为 draft → active → finished；至多一个 active。默认严格串行：前一版本完成前不得创建或编写下一个 version（包括 draft），这是本工作流的范围约束；用户明确要求未来规划时先约定隔离规则。finished 的行为变化进入新 version。纯笔误修订应保留说明。

## 不变量

- 本期声明使用不可变前缀：V1-REQ-001、V1-REQ-001-AC-001、V1-TASK-001、V1-IMP-001；确认后不重排或复用。
- 每个 REQ 有 AC；每个 TASK 绑定本期 REQ/AC、设计锚点、测试方式、命令/手工步骤和证据位置。历史引用与本期声明分开处理。
- requirements 是 AC 来源，tasks 是唯一任务来源；traceability 为按需派生视图。
- 测试默认绑定交付 TASK；独立测试平台、测试补齐或跨功能验收确有独立交付物时可建测试 TASK，并绑定 AC/风险。禁止重复登记同一测试工作。
- 复用用户已授权范围。范围、业务语义、对外契约或风险接受发生实质变化时才澄清；正常实现缺陷修复、内部设计调整和验证持续推进。
- 不用通用覆盖率、性能预算或评分替代项目门槛。未执行不得声称 PASS；环境受阻记录 BLOCKED。
- 测试凭据来自用户或真实环境；优先存引用。敏感 info.md 按需创建并忽略，不在证据中复制密钥。

## Baseline Impact Manifest

version.md 内保留唯一影响表；兼容原名 Steering Impact Manifest 与 No Steering impact 字段。无长期影响需有依据，不用空表默认推定。

每行包含 Impact ID、Domain、Action、Steering target（兼容列名）、Version delta、Verification、State：
- Domain 为 product / project-rules / tech-stack / style-guide / data / api。
- product 目标为 docs/sdd/current/product.md#anchor；其余目标为对应 steering 文件。
- delta 为本期 requirements/design/data/api/version.md#anchor。目标用稳定锚点，change/remove/deprecate 明确旧行为及替代关系；删除后锚点保留退役说明，避免历史引用失效。
- planned → verified → synced：设计登记 planned；对应交付通过后 verified；收尾候选中合入已验证基线并重验后 synced。
- Verification 在 verified/synced 时指向本期证据文件，可带锚点；表格单元格内的竖线使用 HTML 实体。
- 同步汇总从 Manifest 派生；product 使用 current/product.md 行，其余沿用文件名。没有影响的文件不能标记已同步。

用户接受 BLOCKED/WONTFIX 不会令未交付影响成为 synced；需要继续阻塞，或经已授权的范围决定撤回该影响及对应目标，并重新对齐。原始失败证据保留。

## 操作路由

- 初始化/迁移：phases/01_constitution.md；参考 templates/tpl_agents.md、tpl_versions.md、tpl_version.md、tpl_steering.md。Current 模板为 tpl_current.md。
- 需求：phases/02_requirements.md。
- 设计和影响：phases/03_design.md。
- 对齐：phases/04_analysis.md。
- 任务：phases/05_tasks.md。
- 执行/收尾：phases/06_execution.md；行为变更参考 phases/tdd.md；QA 按测试类型读取 phases/qa_engine.md 的相关章节；使用 Mock 时读取 testing-anti-patterns.md 的相关条目。
- 仅迁移旧结构时查 references/sdd-v4-entry.md；它不是当前执行规范。
- 机械文档契约与迁移说明：references/document-contract.md。

## 完成与证据

所有 TASK 必须为 done 或带真实确认记录的 confirmed BLOCKED / confirmed WONTFIX；done 要求全部 AC PASS。证据按 tpl_ac_matrix.md 记录代码身份、规格身份、环境、日期、命令、预期、实际与结果。代码/规格/基线变化后，只重验受影响项，不复用过期 PASS。

先在隔离副本准备基线、Manifest synced、sync 汇总和真实证据，保留 active 与空 Finished 日期。运行：

    python <skill>/scripts/validate_sdd.py <candidate> --check-finish v1

这是只读预检，仍需执行真实回归和适用质量门禁。失败保持源项目 active。通过后核对源输入未变化，将候选基线与版本文档作为同一组收尾变更应用，同时写入两个位置的 finished 和相同真实日期；最后运行 --finish v1。脚本不负责自动应用或文件系统事务，意外中断时检查现存差异、恢复一致 active 或完整 finished，再重验。

普通校验自动检查已完成版本的结构和证据；显式 --finish 另外检查当前基线目标。历史证据是当时快照，不对今天的代码重新声称通过。

## 回复

说明结果、选定 version、实际改动、真实验证与剩余阻塞。无需每次罗列所有已读文件或重复请求已给出的授权。
