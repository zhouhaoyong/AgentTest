# schemas 目录契约

## 目录职责

使用 Pydantic v2 校验 Project、System、Version 及跨 Agent 上下文 YAML 配置。

## 允许内容

- `project.py`、`system.py`、`version.py`：资产 Schema（多端联动为 `version.py` 内的轻量标记 `linked` / `linked_ends`，不再有独立联动资产）。
- `workspace.py`：跨 Agent 上下文和流程状态 Schema。
- `common.py`：共享校验辅助函数。
- `__init__.py`：导出 Schema。
- 本文件：目录契约。

## 文件职责

Schema 只描述当前版本真实需要的配置字段、系统类型、Playwright 测试环境、端联动轻量标记和目录安全 ID 规则。

## 更新规则

Schema 必须与 PRD 保持一致，除非当前版本明确需要，否则拒绝额外字段和复杂状态字段。

## 禁止事项

- 不增加持久化模型、ORM 模型或发布状态机。
- 不增加没有当前用途的字段。
- 不在 Schema 中保存账号、密码、Token、Cookie 或 Storage State。

## 阅读策略

先读本契约，再只阅读与当前 YAML 资产相关的 Schema。
