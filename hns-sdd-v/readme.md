# HNS-SDD

使用 Steering 保存工程约束、Current 保存已接受业务行为、specs/vN 保存本期增量。vN 是工作规格单元，finished 不自动表示发布。

入口为 SKILL.md。默认交付文档是 version.md、requirements.md、tasks.md；有真实设计决定时才创建 design.md，其余报告和矩阵按需。

校验命令：

    python <skill>/scripts/validate_sdd.py <project>
    python <skill>/scripts/validate_sdd.py <candidate> --check-finish v1
    python <skill>/scripts/validate_sdd.py <project> --finish v1

预检在隔离收尾候选中执行：保留 active 和空完成日期，将真实已验收增量合入候选基线并标记 synced。预检与真实回归通过后，核对输入未变化，再应用整组收尾变更并同步 finished 日期。脚本只读，不执行测试或自动应用。

字段契约和旧项目升级方式见 references/document-contract.md。
