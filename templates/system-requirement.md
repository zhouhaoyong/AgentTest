# System 目录契约

## 目录职责

本目录包含一个 System、可复用知识和多个 Version。

## 允许内容

- `system.yaml`：System 元数据和默认地址。
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
- 不把 System 或 Version 当成 Git 分支。

## 阅读策略

先读本契约、`element-map/index.md` 和 `memory/index.md`，再按需读取模块文件和 Version。
