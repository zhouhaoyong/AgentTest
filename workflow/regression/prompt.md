# 回归测试 Prompt

你正在执行 Bug 修复后的当前 Version 全量回归测试。

## 进入条件

- 用户确认相关 Bug 已修复，并明确说“开始正式测试”或等价表达，要求回归当前 Version 。
- 测试地址、环境和当前范围的完整测试用例文件可用。

## 必读资料

1. 根目录 `AGENTS.md`、当前 Version 的配置、`test-scripts/`、`report/requirement.md` 和相关 System 的配置。
2. 相关 Bug 历史、最近一次 `report/report.md`。
3. 当前范围最终的完整 `test-cases/test-cases.md`、相关脚本、Memory、Element Map 和环境配置。
4. [`testing/rules.md`](../testing/rules.md)。

> 加载策略（省 token）：系统级资产（Element Map / Memory）跨版本复用、按 `element-map/index.yaml` 只加载相关模块，不整包灌入；读历史报告优先看顶部"结论摘要"，需要细节再下钻明细表。

## 决策与执行

正式执行前先执行正式测试启动闸门，再做本地环境 pre-flight 检查（操作系统、系统 Chrome、Playwright 可用性），并核对测试用例批准指纹（`.agentest/state.yaml` 的 `test_cases_fingerprint`）与当前 `test-cases.md` 一致；任一不一致时暂停并要求用户重新确认后再回归。

1. 重新执行当前 Version 的完整测试用例集合，而非只执行原失败场景或推测的直接相关场景。
2. 原 Bug 关联的 Test Case 必须存在于当前集合；若不存在，暂停并要求用户先更新测试用例。
3. 脚本批量复用 / 调整、按模块 / 业务流程分组、同组复用同一隔离浏览器会话、运行时发现数据、数据缺口自愈与熔断上报、前后端归因、结果记录（`PASS`、`FAIL`、`BLOCKED`、`NOT RUN`）、重试与熔断阈值等执行细则统一遵循 [`testing/rules.md`](../testing/rules.md)；环境数据缺口记 `BLOCKED`、环境异常不能直接判定为 Bug。
4. 单系统时仅在当前 Version 范围内回归；多端联动时只执行各参与端 `version.yaml` 的 `linked_ends` 所登记的 System 和 Version。不自动扩大到其他 Version 或 System。
5. 交付回归报告前执行交付闸门；发现用例、进度、脚本、证据或报告不同说法时，先修正记录，不交付矛盾结论。

## 允许写入的位置

- 当前 Version 的可重复测试脚本和唯一 `report/report.md`。
- 仅当长期有效且经过验证时，更新对应 System 的 Memory 或 Element Map。
- 不删除历史 Bug、历史失败信息或旧报告证据。

## 交付物与移交方向

- 报告单独统计本次当前范围全量回归，保留历史结果作比较，并记录 Bug、脚本与执行时间。
- 向用户汇报完整集合的结果分布、仍失败的 Bug、阻塞项和风险。

## 强制停止条件

- 遇到登录立即暂停，由用户手动完成并明确确认。
- 测试结束或异常退出时先保存证据和状态，再自动关闭所有页面、Browser Context、Browser 和 Playwright；不询问用户是否关闭。
- 测试完成后不得进行当前范围外的回归，除非用户另行明确要求。
