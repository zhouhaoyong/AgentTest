# AgentTest

AgentTest 是面向现成 AI Agent 的轻量测试脚手架。它使用 Markdown / YAML 文件沉淀 Project、System、Version 测试资产，并使用 Python Playwright 支撑 Web 自动化测试。

## 安装

需要 Python 3.13+ 和 uv：

```bash
uv sync
```

安装 Playwright Chromium：

```bash
uv run playwright install chromium
```

`doctor` 只检查环境，不会自动安装浏览器。

## 环境检查

```bash
uv run AgentTest doctor
```

## CLI 创建资产

CLI 是可选工具。用户可以直接把原始需求交给 Agent，也可以使用 CLI 创建确定的资产：

```bash
uv run AgentTest create-project contact-platform --name "通讯录平台"
uv run AgentTest create-system contact-platform contact-web --name "通讯录 Web"
uv run AgentTest create-version contact-platform contact-web v0.0.1
```

可用命令：

- `AgentTest doctor`
- `AgentTest create-project`
- `AgentTest create-system`
- `AgentTest create-version`

所有创建命令都拒绝覆盖已有资产。

## Agent 使用方式

1. 直接把原始需求交给 Agent，不要求先执行 CLI。
2. Agent 反问并确认 Project、System、Version、测试地址和需求来源。
3. Agent 阅读对应目录的 `requirement.md` 和相关 System 索引。
4. Agent 整理 Requirement，必要时补充 Analysis，并探索目标系统。
5. Agent 生成 Test Points 后必须停止，等待人工审核。
6. 只有用户明确批准后，Agent 才能正式测试。
7. 正式测试应根据需求覆盖功能、业务流和权限 / 角色。
8. 查看 Version 下的 `run/`、`bugs/`、`report/`，以及 System 级 Element Map / Memory。

详细规则见 [AGENTS.md](AGENTS.md)、[prd.md](prd.md) 和 `docs/`。

## BrowserSession

```python
from agentest.browser import BrowserSession

with BrowserSession(headless=False) as browser:
    page = browser.new_page()
    page.goto("http://localhost:3000")
```

默认是 headed 模式；多角色测试应使用隔离的 Browser Context。

## 当前未实现

v0.1 不包含前端、数据库、用户 / 权限管理产品、Agent Runtime、LLM SDK 集成、复杂 RAG、远程服务、复杂调度器或 Git 自动化。
