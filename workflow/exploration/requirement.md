# exploration 阶段目录契约

## 目录职责

保存按需系统探索、Element Map 和 Memory 沉淀的公共 Prompt 与模板。

## 允许内容

- `prompt.md`：探索与长期知识沉淀规则。
- `template-*`：Element Map YAML、Memory Markdown、模块目录和索引模板。
- 本文件：目录契约。

## 禁止事项

- 不将系统探索当作正式测试。
- Element Map 的模块事实源使用 YAML；Memory 使用固定章节的 Markdown。
- 不记录完整 DOM、临时推理、凭据或一次性 Session 日志。

## 阅读策略

需求整理后先读取真实 System 的 `element-map/index.yaml` 和 `memory/index.md`，必要时读取人工摘要 `element-map/index.md`，判断复用已有知识、目标探索或必须探索；仅在后两种结果下加载相关模块并启动探索。
