# 回归测试 Prompt

你正在执行 AgentTest 的 Bug 修复后回归测试阶段。

## 前置阅读

先阅读：

1. 根目录 `AGENTS.md`。
2. 当前 Version 的 `version.yaml`、`test-scripts/`、`report/requirement.md` 和当前 System 的 `system.yaml`。
3. 相关 Bug 的历史记录和最近一次 `report/report.md`。
4. 关联的 Test Point 和已有测试脚本。
5. 必要的 System Memory、Element Map 和测试环境配置。

## 执行要求

1. 先确认 Bug 已修复、测试地址和环境未变更，且回归范围得到用户确认。
2. 优先复用当前 Version 中与 Bug 关联的已有测试脚本；脚本至少应支持当前 Version 内的重复测试。
3. 至少回归原失败场景，并覆盖修复可能影响的直接相关场景。
4. 不自动扩大到无关功能；需要扩大范围时先询问用户。
5. 每个回归测试点记录 `PASS`、`FAIL`、`BLOCKED` 或 `NOT RUN`。
6. 因登录、浏览器、网络或其他环境问题无法判断业务结果时，记录为 `BLOCKED` 或 `NOT RUN`，不能直接判定为 Bug。
7. 如果需要登录，必须暂停并由用户手动登录后明确确认。
8. 不保存或输出任何账号密码、Token、Cookie、Storage State、验证码或其他敏感信息；普通业务数据的截图和日志可以保留原始状态。

## 测试结束

使用 [`workflow/reporting/prompt.md`](../reporting/prompt.md) 更新同一个 `report/report.md`：

- 本次回归结果单独统计，不与历史正式测试结果混合。
- 回归记录中关联 Bug、Test Point、脚本、历史结果、本次结果和执行时间。
- 如果回归失败，保留 Bug 的历史失败状态并记录新的实际结果。
- 如果回归通过，记录验证依据，但不要删除历史 Bug 或原始失败信息。
- 如果需求已经确认变更，及时同步调整当前 Version 的相关测试脚本，并在报告中说明。
