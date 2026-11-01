# 文档契约与兼容

校验器只读、不执行文档内命令；通过表示机械契约一致，不证明测试声明真实或产品满足全部业务需要。

## 结构

- REQ 声明为二级标题 Vn-REQ-NNN；AC 为 requirements.md 内独占一行的 ID，或 YAML 的 - id: Vn-REQ-NNN-AC-NNN。
- TASK 为带 checkbox 的列表项，ID 可加粗；每项以下字段按 - **Field**: value 填写：REQ、AC、Design、Test type、Verification command、Evidence、Depends on、Status。
- Evidence 路径相对当前 version；Design 同样相对 version，包含标题锚点。
- Status 为 todo / doing / done / confirmed BLOCKED / confirmed WONTFIX。终态勾选 checkbox；例外必须与证据的 Disposition 一致，并填写 Confirmed by / date、Reason、Residual risk。
- AC evidence 的七列顺序固定为 AC ID、Test type、Command / steps、Expected、Actual、Result、Evidence / error；每条本 TASK AC 只能有一行，Result 为 PASS / FAIL / BLOCKED。单元格竖线用 &#124;。
- 证据元数据 Code revision、Spec revision、Environment、Executed 必填；Executed 为 ISO 日期。工作树不干净时身份包含提交号与差异摘要/哈希；Spec revision 包含相关规格与基线身份。校验器验证字段存在，Agent 负责与当前执行输入核对。
- 参考模板中的最小契约即可；自由叙述不被当成结构化字段。

## 链接和历史

采用 Markdown 标题锚点或显式 HTML a id；有重复标题时遵循 -1、-2 后缀。保持规范引用稳定，复杂标题优先显式锚点。校验器支持常用标题规范，不是完整 Markdown 渲染器。

Historical dependencies 中显式列出 vN/文件路径；只允许引用已登记 finished 版本的 REQ/AC/TASK。本期声明不能使用历史前缀。自然语言历史 ID 引用不会被误判为本期声明。

## 基线与收尾

product 域固定对应 current/product.md；现有 data/api 继续保留在 steering，避免双写。Current 只存已接受行为、约束、场景、来源和退役说明，不存任务进度。没有已接受行为的空项目不预建空产品文档。

--check-finish 要求选定 active、Finished 为空、基线候选已经合入、所有影响 synced；它适用于隔离候选。--finish 要求已 finished。普通检查自动核对已完成的本地结构，但不强制历史基线锚点仍符合今天的语义。三个模式均不写文件。

draft 只检查身份、路径及注册关系，不要求需求、设计、任务或 Manifest 完整。active 允许尚未开始设计时没有 Manifest；有设计或 Manifest 后检查影响关系。finished 要求完整非空交付与证据。

## 旧项目升级

保留既有编号和历史文件。先检查旧项目，补真实证据字段与明确任务状态；缺失的运行信息标记 BLOCKED 并重新执行，不编造旧结果。旧 Steering Impact Manifest / No Steering impact / Steering target 继续支持。补 Current 时从代码、已接受需求和测试提取有效行为，逐项记录来源；冲突由用户已有决定或必要澄清解决。

不要为使校验通过而批量将历史 TASK 改成 done。旧历史不满足新契约时报告迁移缺口，由真实补验或明确例外处置关闭。
