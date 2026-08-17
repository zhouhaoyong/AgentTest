# Element Map 目录契约

## 目录职责

保存当前 System 可复用的界面和交互元素知识，帮助后续 Agent 减少重复探索和定位错误。

## 允许内容

- `index.yaml`：Element Map 的机器可读模块索引。
- `index.md`：可选的人工导航摘要，不作为定位事实源。
- `modules/`：模块级 YAML 文件；每个模块与索引中的模块 ID 对应。
- 本文件：目录契约。

## 文件职责

模块 YAML 只记录测试真正使用、后续可能复用或有助于理解 System 的页面和元素。必须包含页面、URL pattern、入口、状态、元素语义、主/备用定位、稳定性依据、操作后的去向、最后验证 Version 和验证视口。

定位策略按以下顺序优先：

1. `data-testid`、`data-test` 等专用测试属性。
2. `get_by_role`、`get_by_label` 等语义定位。
3. 基于稳定属性的 CSS Selector。
4. 稳定且唯一的文本定位。
5. XPath 仅作为最后兜底。

每个元素应记录主定位方式、可选备用定位方式、稳定性依据、操作后的预期状态、最后验证的 Version 和验证视口。禁止使用账号、UID、动态数量、动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标或临时生成的定位值作为主定位依据。

## 更新规则

探索或正式测试发现有长期价值的新知识时才更新。模块文件名使用小写连字符格式，例如 `contact-list.yaml`。Markdown 只能作为人工摘要，不能替代 YAML 模块。

## 禁止事项

- 不记录全部 DOM 节点。
- 不在每个 Version 下复制 Element Map。
- 不默认加载所有模块。

## 阅读策略

先读 `index.yaml`，必要时读取 `index.md` 摘要，再按模块 ID 读取对应 YAML 模块文件。
