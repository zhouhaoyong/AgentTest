# AgentTest Python 包目录契约

## 目录职责

保存 AgentTest Python 包及其职责明确的实现模块。

## 允许内容

- `browser/`：Playwright 兜底能力。
- `schemas/`：Pydantic 资产 Schema。
- `test_cases.py`：测试用例范围指纹辅助能力。
- `asset_audit.py`：Version 资产的只读结构一致性审计。
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
