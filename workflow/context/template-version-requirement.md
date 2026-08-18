# Version 目录契约

## 目录职责

本目录包含一个 System Version 的全部测试资产。

## 允许内容

- `version.yaml`：Version 元数据、测试地址（唯一事实源）、可选 Playwright 环境覆盖，以及是否端联动的轻量标记（`linked` / `linked_ends`）。
- `requirements/`：原始来源、目录契约和按规范命名的结构化需求文档。
- `test-cases/`：等待审核或已经审核的测试用例。
- `test-scripts/`：可重复执行的测试脚本。
- `evidence/`：本次测试的 Bug 证据（截图、Trace、HAR、录像等），按需创建，不含凭据。
- `report/`：最近一次正式测试或回归测试的建议版报告。
- 本文件：目录契约。

## 文件职责

需求文件描述测试目标，Test Cases 描述可执行范围，Test Scripts 保存可重复执行的脚本，Report 统一描述最近一次正式测试或回归测试的结果、Bug、风险和建议。

## 更新规则

先整理需求，再根据探索决策按需探索并生成测试用例。生成测试用例后必须等待用户明确批准；用户进一步明确说“开始正式测试”后，先批量生成 / 调整测试脚本并分组调试，再执行测试用例和更新 Report。测试用例确认本身不会启动浏览器。

## 禁止事项

- 未经批准不得正式测试。
- 不用另一个 Version 的资产覆盖本 Version。
- 不保存密码、凭据或重复的测试运行历史目录。
- 环境覆盖只记录本次 Version 的差异，最终配置继承 System 默认值；不保存账号、密码、Token、Cookie 或 Storage State。

## 阅读策略

先读本契约和 `version.yaml`，再读取 `requirements/requirement.md` 目录契约、`source.md`、当前命名的结构化需求文档、Test Cases、Test Scripts 和 System 索引。
