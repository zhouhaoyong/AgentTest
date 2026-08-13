# 测试规则

## 测试点确认规则

在当前 Version 的 `test-points/test-points.md` 生成测试点后必须停止。真实业务资产路径是 `projects/<project-name>/systems/<system-name>/versions/<version-name>/test-points/test-points.md`，不得在项目根目录直接创建 `test-points/`。正式测试需要用户明确批准。“继续分析”或“看看”不算批准。

## 测试覆盖

对于相关需求，测试以下内容：

- 功能测试：正常、边界、非法输入、校验、错误、状态、持久化和结果。
- 业务流程测试：前置条件、主流程、分支、失败路径、跨页面 / 跨模块衔接、中断和后置结果。
- 角色与权限测试：可见性、操作可用性、数据范围、角色隔离、受限访问和越权风险。

记录未覆盖、开放问题、被阻塞的维度及风险。多步骤或多角色需求不能用单页检查代表完整测试。测试点是清晰的验证目标，不是完整测试用例；前置条件和测试数据按需记录。

## 元素定位

Element Map 和测试脚本优先使用专用测试属性，其次使用语义定位，再使用稳定属性 CSS，稳定文本和 XPath 仅作为后备。禁止依赖动态 class、深层 DOM 路径、`nth-child`、数组下标、坐标或浏览器临时生成的定位值。

## 浏览器与登录

优先使用 Agent 内置浏览器，否则使用 Python Playwright。`BrowserSession` 默认使用 headed 模式，System / Version 的 `test_environment` 负责视口、设备像素比、移动端标识、触摸、语言、时区和超时配置。

登录由用户手动完成：Agent 到达登录页后必须暂停，用户输入账号密码并明确确认完成后才能继续。凭据不保存、不自动填写；不得保存 Cookie、Storage State 或其他会话敏感信息。不同账号或角色使用独立 Browser Context / Session。

## 范围与安全

只执行已批准的测试点，不自动扩大范围，不删除或覆盖资产；未经用户明确指令不执行 Git 命令。Bug 截图和日志应保留足以判断问题的原始页面状态，普通业务数据不要求脱敏，不得为了脱敏而裁剪、遮挡或修改证据；账号密码、Token、Cookie、Storage State、验证码等敏感信息不得出现在代码、脚本、YAML、Markdown、报告、Memory、Element Map、日志、截图、Trace、HAR 或视频中。
