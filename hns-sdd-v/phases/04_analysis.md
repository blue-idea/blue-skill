# STEP 4 · 对齐

读取当前 requirements、存在时的 design/data/api、相关 Current/Steering 和显式历史依赖。检查：

- REQ → AC → 设计或 no new design 依据 → Manifest → TASK（已存在时）的覆盖。
- 新业务行为能在收尾后进入 Current；增删改与替代对象明确，锚点可定位。
- Scope、术语、数据、API、异常、权限及验证方式没有冲突。
- 删除孤立设计和重复历史内容，保留用户要求的交付物。

在 version.md 的 Alignment review 记录真实日期、检查范围、Result 与关键依据。P0/P1 未解决时 BLOCKED，不能开始受影响实现；P2 不自动扩大范围。有复杂问题或审计要求时才维护单一 analysis-report.md。规格变化后更新受影响结论，不能复用过期 PASS。
