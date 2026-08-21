# browser 目录契约

## 目录职责

提供轻量 Python Playwright 隔离 Chrome 会话能力。

## 允许内容

- `session.py`：BrowserSession 生命周期辅助类，并在每次启动前执行本地 Playwright / Chrome pre-flight。
- `preflight.py`：系统 Chrome 与本地 Playwright 可用性检查（启动隔离会话前的 pre-flight）。
- `__init__.py`：导出 BrowserSession 和 Chrome pre-flight 辅助能力。
- 本文件：目录契约。

## 文件职责

BrowserSession 只负责按测试环境配置启动浏览器、创建并复用主 Page、显式创建辅助 Page、跳转和关闭；Agent 仍可直接使用原生 Playwright Page API。普通 `goto()` 复用主 Page，业务明确打开新页签时才调用 `new_page()` 或原生 Playwright 的新页签监听能力。

## 更新规则

默认 BrowserSession 使用 headed 模式和系统 Google Chrome，同时支持显式 headless 和 slow_mo。

## 禁止事项

- 不构建复杂 Browser Manager。
- 不回退到 Edge 或 Playwright bundled Chromium。
- 不保存凭据、Cookie、Storage State 或自动安装 Chromium。
- 不把 Node.js 运行时变成核心依赖。

## 阅读策略

修改浏览器生命周期或诊断逻辑前先阅读本契约。
