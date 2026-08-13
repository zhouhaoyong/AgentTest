# 系统探索 Prompt

你正在执行 AgentTest 的系统探索阶段。目标是理解当前需求涉及的页面、模块、流程和可复用元素，但不执行未经批准的正式测试。

## 前置阅读

1. 根目录 `AGENTS.md`、[`workflow/README.md`](../README.md) 和当前 Version 的结构化需求。
2. 当前 System 的 `system.yaml`、`element-map/index.md` 和 `memory/index.md`。
3. 只读取与当前需求直接相关的 Element Map / Memory 模块。

## 执行规则

1. 明确区分业务期望、当前页面实现和无法判断的差异；页面存在或缺少入口不改变需求本身。
2. 探索不执行批准范围之外的正式验证，不创建 PASS、FAIL 或 Bug 结论，不修改业务数据。
3. 仅记录长期可复用且已验证的信息到 System 级 Element Map / Memory；不复制到 Version，不记录完整 DOM、临时日志或凭据。
4. Element Map 定位顺序为测试属性、语义定位、稳定属性 CSS、稳定文本、XPath；禁止动态 class、深层路径、`nth-child`、下标和坐标。
5. 遇到登录必须暂停，由用户手动操作并明确确认。完成后移交 `test-points/`；若用户只要求探索，在此阶段结束。
