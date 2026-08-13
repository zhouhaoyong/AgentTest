# Element Map 目录契约

## 目录职责

保存当前 System 可复用的界面和交互元素知识，帮助后续 Agent 减少重复探索和定位错误。

## 允许内容

- `index.md`：简短模块索引。
- `modules/`：模块级 YAML 或 Markdown 文件。
- 本文件：目录契约。

## 文件职责

模块文件只记录测试真正使用、后续可能复用或有助于理解 System 的元素，例如页面、URL pattern、元素语义和 locator 策略。

定位策略按以下顺序优先：

1. `data-testid`、`data-test` 等专用测试属性。
2. `get_by_role`、`get_by_label` 等语义定位。
3. 基于稳定属性的 CSS Selector。
4. 稳定且唯一的文本定位。
5. XPath 仅作为最后兜底。

每个元素应记录主定位方式、可选备用定位方式、稳定性依据和最后验证的 Version。禁止记录动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标或临时生成的定位值。

## 更新规则

探索或正式测试发现有长期价值的新知识时才更新。模块文件名使用小写连字符格式，例如 `contact-list.yaml`。

## 禁止事项

- 不记录全部 DOM 节点。
- 不在每个 Version 下复制 Element Map。
- 不默认加载所有模块。

## 阅读策略

先读 `index.md`，确定相关模块后，再读取对应模块文件。
