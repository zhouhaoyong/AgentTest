# systems 目录契约

## 目录职责

保存父级 Project 下的 System 目录。

## 允许内容

- 每个 System ID 对应一个目录。
- 本文件：目录契约。

## 文件职责

每个 System 目录保存一个独立系统及其 Element Map、Memory 和 Version。

## 更新规则

System ID 在同一 Project 内唯一。确认 Project 上下文后才能创建 System，不得静默覆盖已有 System。

## 禁止事项

- 不把 Version 资产直接放在这里。
- 不保存凭据、运行状态或无关应用文件。
- 不把 System 目录当成 Git 分支。

## 阅读策略

先读本契约，再只阅读目标 System 的 `requirement.md` 和元数据。
