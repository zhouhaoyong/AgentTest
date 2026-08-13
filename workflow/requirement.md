# workflow 目录契约

## 目录职责

保存 AgentTest 的公共工作流脚手架，按用户会经历的阶段聚合 Prompt、模板、规则、目录契约和资产映射。

## 允许内容

- `README.md`：用户意图到唯一工作阶段的路由入口。
- `asset-map.md`：公共模板与真实业务资产位置的映射。
- 各阶段目录：该阶段的 Prompt、模板、规则和目录契约。
- 本文件：目录契约。

## 文件职责

本目录只说明 Agent 如何工作和如何创建资产；真实业务需求、测试点、脚本、报告、Memory 和 Element Map 只能写入 `projects/` 下的标准路径。

## 更新规则

公共脚手架调整必须同步更新 `AGENTS.md`、`prd.md`、README、资产映射和结构测试。模板文件使用 `template-` 前缀，不得与真实资产混淆。

## 禁止事项

- 不保存真实 Project、System、Version、需求、测试结果或运行状态。
- 不保存账号、密码、Token、Cookie、Storage State 或其他凭据。
- 不将 `workflow/` 当作 `projects/` 的替代品。

## 阅读策略

先读 `README.md`，根据用户意图和 `.agentest/state.yaml` 选择唯一阶段，再读取该阶段的 `requirement.md` 和 `prompt.md`。
