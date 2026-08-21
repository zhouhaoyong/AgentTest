# AgentTest Python 包目录契约

## 目录职责

保存 AgentTest Python 包及其职责明确的实现模块。

## 允许内容

- `browser/`：Playwright 驱动的隔离 Chrome 会话与启动前 pre-flight。
- `schemas/`：Pydantic 资产 Schema。
- `exploration/`：探索期纯逻辑工具（预算熔断、定位打分、单会话发现）。
- `test_cases.py`：测试用例范围指纹与关键覆盖约束解析。
- `asset_audit.py`：Version 资产的只读结构一致性审计。
- `workflow_gates.py`：测试用例确认 / 正式测试启动 / 报告交付三道只读闸门。
- `__init__.py`：包元数据。
- 本文件：目录契约。

## 文件职责

每个子目录只负责一个实现领域，避免增加无意义的抽象层。

## 更新规则

源码修改必须保持在 PRD 定义的文件化、Web 测试和轻量 v0.1 边界内。

## 禁止事项

- 不添加额外的资产创建命令、数据库、Agent Runtime、LLM Provider 或无关应用代码。
- 不从包代码执行 Git 操作。

## 阅读策略

先读本契约，再阅读与当前修改相关的实现区域契约。
