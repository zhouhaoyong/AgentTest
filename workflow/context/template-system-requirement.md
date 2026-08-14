# System 目录契约

## 目录职责

本目录包含一个 System、可复用知识和多个 Version。

## 允许内容

- `system.yaml`：System 元数据和默认地址。
- `test_environment`：Playwright 默认视口、设备、语言、时区和超时配置。
- `element-map/`：可复用的界面元素知识。
- `memory/`：可复用的系统知识。
- `versions/`：Version 测试资产。
- 本文件：目录契约。

## 文件职责

`system.yaml` 保存 System 级配置；Element Map 和 Memory 保存跨 Version 可复用内容；Version 保存具体测试范围。

## 更新规则

只有长期可复用的知识才能更新 Element Map 和 Memory。新的测试范围创建新的 Version，不覆盖已有 Version。

## 禁止事项

- 不把完整 Element Map 或 Memory 复制到 Version。
- 不保存密码或凭据。
- 不强制 System ID 带系统类型后缀；类型由 `type` 字段承载，ID 只需目录安全串（区分不同端可自行用不同名字，如 `gumai-pc`、`gumai-h5`）。
- 登录方式固定为 `manual`；不在 YAML 中保存账号、密码、Token、Cookie 或 Storage State。
- 不把 System 或 Version 当成 Git 分支。

## 阅读策略

先读本契约、`element-map/index.md` 和 `memory/index.md`，再按需读取模块文件和 Version。
