# projects 目录契约

## 目录职责

保存用户自己的 Project 目录及其文件化测试资产。

## 允许内容

- 每个 Project 对应一个目录。
- 本文件：目录契约。

## 文件职责

Project 下通常按照 Project → System → Version 层级保存业务测试资产。多个 System 必须一起验证时，不新建目录，只在参与联动的 `version.yaml` 内用 `linked` / `linked_ends` 轻量标记登记联动关系，各端资产仍写在各自 Version 下。

## 更新规则

确认上下文后才能创建 Project。默认只定位目标 Project，不无目的扫描或修改其他 Project。

## 禁止事项

- 不放源码或凭据。
- 不静默覆盖已有 Project。
- 不在 `.gitignore` 中默认忽略本目录。

## 阅读策略

先读本契约，再只阅读目标 Project 的 `requirement.md`。
