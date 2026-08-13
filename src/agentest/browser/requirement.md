# browser 目录契约

## 目录职责

提供轻量 Python Playwright 兜底能力和环境诊断。

## 允许内容

- `session.py`：BrowserSession 生命周期辅助类。
- `doctor.py`：只读浏览器和环境检查。
- `__init__.py`：导出 BrowserSession。
- 本文件：目录契约。

## 文件职责

BrowserSession 只负责启动、页面创建、跳转和关闭；Agent 仍可直接使用原生 Playwright Page API。

## 更新规则

默认 BrowserSession 使用 headed 模式，同时支持显式 headless 和 slow_mo。

## 禁止事项

- 不构建复杂 Browser Manager。
- 不保存凭据或自动安装 Chromium。
- 不把 Playwright MCP 或 Node.js 变成核心依赖。

## 阅读策略

修改浏览器生命周期或诊断逻辑前先阅读本契约。
