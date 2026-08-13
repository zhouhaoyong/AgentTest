# schemas 目录契约

## 目录职责

使用 Pydantic v2 校验最小 Project、System、Version YAML 配置。

## 允许内容

- `project.py`、`system.py`、`version.py`：资产 Schema。
- `common.py`：共享校验辅助函数。
- `__init__.py`：导出 Schema。
- 本文件：目录契约。

## 文件职责

Schema 只描述当前版本真实需要的配置字段和目录安全 ID 规则。

## 更新规则

Schema 必须与 PRD 保持一致，除非当前版本明确需要，否则拒绝额外字段和复杂状态字段。

## 禁止事项

- 不增加持久化模型、ORM 模型或发布状态机。
- 不增加没有当前用途的字段。

## 阅读策略

先读本契约，再只阅读与当前 YAML 资产相关的 Schema。
