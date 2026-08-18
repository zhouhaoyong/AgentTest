# modules 目录契约（示例）

## 目录职责

保存父级 Element Map 的模块文件；由同级 `element-map.yaml`（对应真实 `index.yaml`）索引。本目录为平铺 Demo 的一部分，仅用于阅读，不代表真实业务目录。

## 允许内容

- Element Map 可复用的模块 YAML 文件（如 `contacts.yaml`）。
- 本文件：目录契约。

## 文件职责

每个模块文件只描述一个大功能模块，并与索引中的模块 ID 对应，必须能被 YAML 解析。

## 禁止事项

不保存完整 DOM、Session 日志、密码、Token、Cookie、Storage State 或其他敏感信息。
