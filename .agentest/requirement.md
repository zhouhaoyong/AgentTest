# .agentest 目录契约

## 目录职责

保存跨 Agent 共享的当前工作上下文和流程状态。

## 允许内容

- `context.yaml`：当前 Project、System、Version、测试地址；多个系统一起测试时，联动关系记录在参与联动的 `version.yaml` 的 `linked` / `linked_ends` 轻量标记里。
- `context.yaml` 中的 `system_type`：当前 System 类型，取值为 `web`、`h5`、`app` 或 `miniapp`。
- `state.yaml`：当前工作阶段和浏览器偏好。
- 本文件：目录契约。

## 文件职责

这些文件只记录可供不同 Agent 接续工作的最小状态，不保存完整需求、凭据或聊天记录。

## 更新规则

Agent 可以在确认上下文或推进工作阶段时更新。用户可以直接编辑 YAML 修正上下文。

## 禁止事项

- 不保存密码、Token、Cookie、Storage State 或其他凭据。
- 不保存完整思考过程或无关临时日志。
- 不执行 Git 操作。

## 阅读策略

开始工作时先读取 `context.yaml` 和 `state.yaml`，再按状态读取目标 Project、相关 System、Version 资产。
