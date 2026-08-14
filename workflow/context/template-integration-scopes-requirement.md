# 联动范围集合目录契约

## 目录职责

保存同一 Project 下多个 System 一起测试的联动范围。

## 允许内容

- 每个子目录代表一个联动范围。
- 本文件：目录契约。

## 更新规则

只有需求确实需要多个 System 配合验证时才创建。单系统测试继续使用原 Version 目录。

## 禁止事项

- 不放单个 System 的长期 Memory 或 Element Map。
- 不保存账号、密码、Token、Cookie 或其他凭据。

## 阅读策略

先读目标联动范围的 `requirement.md` 和 `scope.yaml`，再读其中列出的 System 与 Version。
