# 测试报告 Prompt

你正在执行 AgentTest 的测试报告整理阶段。

## 前置阅读

先阅读：

1. 根目录 `AGENTS.md`。
2. 当前 Version 的 `version.yaml`、`report/requirement.md` 和当前 System 的 `system.yaml`。
3. 已批准的 `test-points/test-points.md`。
4. 本次实际使用的 Test Scripts、测试记录和 Bug 信息。
5. 必要的 System Memory、Element Map 索引和测试环境配置。

## 执行要求

1. 只更新当前 Version 的 `report/report.md`，不得启动浏览器、补充正式测试或修改测试结果。
2. 明确本次执行类型：正式测试或回归测试。
3. 报告统一记录：
   - 测试范围与环境信息
   - Test Scripts
   - 每个 Test Point 的本次执行结果
   - Bug
   - 回归记录
   - 未测试 / 阻塞内容
   - 风险、建议和测试结论
4. Test Point 状态只能为 `PASS`、`FAIL`、`BLOCKED`、`NOT RUN`。
5. 本次结果汇总必须与本次 Test Point 明细一致：
   `本次总数 = PASS + FAIL + BLOCKED + NOT RUN`。
6. 回归测试只统计本次回归执行的测试点；历史正式测试结果只作为对比信息，不得混入本次统计。
7. Bug 必须关联 Test Point，并记录严重程度、测试维度、复现步骤、实际结果和预期结果；状态只能为 `Open`、`Fixed Pending Regression`、`Regressed` 或 `Closed`。
8. 回归记录必须明确区分历史结果、本次回归结果、使用脚本和执行时间；不得删除历史 Bug 或原始失败信息。
9. 未测试或被阻塞的功能、业务流程、角色 / 权限场景必须说明原因。
10. 只记录实际观察和已有证据，不得自行补测、修改测试结果或将推测写成结论。
11. 测试报告默认仅保存在本地，不进入未来 RAG 向量库。
12. 不得记录密码、Token、Cookie、Storage State、验证码或其他敏感信息。普通业务数据的截图和日志可以保留原始状态，以便判断问题。

## 输出要求

向用户简要说明：

- 本次执行类型。
- 本次测试点总数及 `PASS` / `FAIL` / `BLOCKED` / `NOT RUN` 数量。
- 本次新增 Bug 数量及严重程度分布。
- 未测试 / 阻塞内容。
- 主要风险和后续建议。
- `report/report.md` 相对于项目根目录的路径。
