# 运行环境与工作流可靠性改造设计

## 目标

将 AgentTest 的默认 Python 版本统一为 3.11；确保浏览器兜底能力在启动失败时释放资源；让跨 Agent 状态只接受工作流中已定义的阶段；为多 System 联动范围提供 YAML 校验；将 MCP 保持为 Agent 内部实现细节，不要求业务用户理解或确认该术语。

本次不处理公共检查扫描真实业务资产的问题，也不调整品牌文本检查的范围。

## 约束

- 不新增命令行入口、服务、数据库、Agent Runtime 或 Git 自动化。
- Markdown 与 YAML 继续是事实来源；System、Version 和联动范围资产继续由 Agent 直接读写。
- 浏览器仍优先使用 Agent 已可用的隔离会话，Python Playwright 仍是兜底能力；不得复用用户已登录会话或自动安装、配置浏览器连接。
- 用户只关注测试范围、地址、登录和结果；底层浏览器连接机制不作为用户沟通或状态字段。
- 本次只修改公共实现、公共脚手架和自动化测试，不改 `projects/` 中的真实业务资产。

## Python 3.11 基线

`.python-version` 固定为 `3.11`；`pyproject.toml`、README 与产品规范统一声明最低版本为 Python `>=3.11`。Ruff 继续以 `py311` 为目标版本。

实现不引入高于 Python 3.11 的语言特性。验收时在独立 Python 3.11 环境安装锁定依赖并运行完整 pytest 与 Ruff 检查。历史设计记录不改写，以保留当时的决策上下文。

## BrowserSession 失败清理

`BrowserSession.start()` 在启动 Playwright 后，统一保护 Chrome 启动回退、Context 创建和默认超时设置。

- 系统 Chrome 不可用时，继续回退 Playwright Chromium。
- 回退也失败、创建 Context 失败或设置超时失败时，立即调用既有 `close()`，关闭已创建的 Browser 和 Playwright 服务，并将内部状态还原为空。
- 原始异常继续抛出；清理失败不覆盖启动失败的根因。

通过替身对象测试 Chrome 回退、最大化 Context 参数、失败清理和幂等关闭，不依赖本机实际安装浏览器。

## 跨 Agent 状态

新增由工作流路由定义的阶段集合：`intake`、`context`、`requirements`、`exploration`、`test-cases`、`testing`、`reporting`、`regression`。`WorkspaceState.phase` 只接受这些值，默认值为 `intake`。

浏览器偏好保留 `auto`、`agent_browser` 与 `playwright` 三个内部选择；删除未使用的 `mcp_consent` 字段。公共规则不再要求或提示用户理解 MCP。若运行环境已经提供安全、隔离的浏览器能力，Agent 可以在内部选择它；否则使用 Python Playwright，并只以业务语言说明浏览器是否可用。

## 多 System 联动范围

新增 `IntegrationScopeConfig` 与 `IntegrationScopeMember`：

- 联动范围 ID、System ID、Version ID 复用目录安全 ID 校验。
- 参与项至少两个；每项顺序为正整数且在范围内唯一。
- 测试地址可在上下文确认阶段暂为空，继续由既有工作流确认环境安全性与可达性。

该校验只确认单个 `scope.yaml` 的内部结构；不在 Schema 中读取文件系统交叉验证 System 或 Version 是否存在，避免把轻量 Schema 扩展为资产管理器。

## 验收

- Python 3.11 环境能安装项目依赖，pytest 与 Ruff 都通过。
- `BrowserSession` 的 Chrome 回退和任意启动后失败路径不残留 Browser 或 Playwright 资源。
- 无效工作流阶段和已删除的 `mcp_consent` 字段会被拒绝；所有路由阶段都能被接受。
- 合法联动范围可加载；少于两个参与项、重复顺序和非法 ID 会被拒绝。
- README、PRD、测试规则和 `.agentest` 目录契约不再要求用户了解 MCP。
