# modules 目录契约

## 目录职责

保存父级 Element Map 或 Memory 的模块文件；Element Map 与 Memory 的事实格式不同。

## 允许内容

- Element Map：可复用的模块 YAML 文件。
- Memory：带固定章节的模块 Markdown 文件。
- 本文件：目录契约。

## 文件职责

每个模块文件只描述一个大功能模块，并与索引中的模块 ID 对应。Element Map 模块必须能被 YAML 解析；Memory 模块必须包含验证 Version、长期用途和稳定事实。

## 更新规则

只有包含长期有效且与父级 System 相关的知识时才新增模块。

## 禁止事项

- 不保存完整 DOM、Session 日志、密码、Token、Cookie、Storage State 或其他敏感信息。
- 不默认读取全部模块文件。

## 阅读策略

先使用 Element Map 的 `index.yaml` 或 Memory 的 `index.md` 选择模块，再读取对应文件。
