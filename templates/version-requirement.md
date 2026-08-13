# Version 目录契约

## 目录职责

本目录包含一个 System Version 的全部测试资产。

## 允许内容

- `version.yaml`：Version 元数据和可选测试地址覆盖。
- `requirements/`：原始来源和结构化需求。
- `analysis/`：可选需求分析。
- `test-points/`：等待审核或已经审核的测试点。
- `run/`：最近一次正式测试结果。
- `bugs/`：最近一次正式测试 Bug。
- `report/`：最近一次正式测试报告。
- 本文件：目录契约。

## 文件职责

需求文件描述测试目标，Test Points 描述可执行范围，Result / Bugs / Report 描述最近一次正式测试。

## 更新规则

先整理需求，再探索和生成测试点。生成测试点后必须等待用户明确批准；正式测试后才能更新 Result、Bugs 和 Report。

## 禁止事项

- 未经批准不得正式测试。
- 不用另一个 Version 的资产覆盖本 Version。
- 不保存密码、凭据或重复的 run 历史目录。

## 阅读策略

先读本契约和 `version.yaml`，再读取 `requirements/requirement.md`、相关 Analysis、Test Points 和 System 索引。
