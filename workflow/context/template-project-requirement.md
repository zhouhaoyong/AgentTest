# Project 目录契约

## 目录职责

本目录包含一个 Project 及其 System；多个系统需要一起测试时，联动关系在参与联动的 `version.yaml` 用轻量标记登记，不新建独立目录。

## 允许内容

- `project.yaml`：Project 元数据。
- `systems/`：子 System 目录。
- 本文件：目录契约。

## 文件职责

`project.yaml` 只保存 Project 的最小元数据。所有测试资产放在子 System 和 Version 中；多端联动只在参与联动的 `version.yaml` 用 `linked` / `linked_ends` 轻量标记登记，不新建独立联动目录。

## 更新规则

确认 Project 上下文后，Agent 才能创建或更新资产。不得静默覆盖已有文件。

## 禁止事项

- 不把 Version 资产直接放在本目录。
- 不保存凭据、运行状态或无关应用代码；不保存账号、密码、Token、Cookie 或 Storage State。
- 不自动执行 Git 操作。

## 阅读策略

阅读本契约后，再阅读相关 System 的契约和资产。
