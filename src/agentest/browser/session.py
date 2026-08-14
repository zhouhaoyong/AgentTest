from typing import Any

from agentest.schemas.system import TestEnvironment


class BrowserSession:
    """Small lifecycle helper that leaves Playwright Page APIs untouched."""

    def __init__(
        self,
        headless: bool = False,
        slow_mo: int = 0,
        test_environment: TestEnvironment | None = None,
    ) -> None:
        self.headless = headless
        self.slow_mo = slow_mo
        self.test_environment = test_environment or TestEnvironment()
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None

    def start(self) -> "BrowserSession":
        if self._browser is not None:
            return self
        from playwright.sync_api import sync_playwright

        environment = self.test_environment
        self._playwright = sync_playwright().start()

        # 无痕（--incognito）：绝不复用用户已登录的 Chrome 会话，也避免缓存引入的 bug。
        # web 端默认真实最大化（--start-maximized + no_viewport）。
        launch_args = ["--incognito"]
        if environment.maximize:
            launch_args.append("--start-maximized")

        launch_kwargs: dict[str, Any] = {
            "headless": self.headless,
            "slow_mo": self.slow_mo,
            "args": launch_args,
        }
        # 优先使用系统真实 Chrome，未安装时回退到 Playwright 自带 Chromium。
        try:
            self._browser = self._playwright.chromium.launch(channel="chrome", **launch_kwargs)
        except Exception:
            self._browser = self._playwright.chromium.launch(**launch_kwargs)

        context_kwargs: dict[str, Any] = {
            "locale": environment.locale,
            "timezone_id": environment.timezone_id,
        }
        if environment.maximize:
            # 真实最大化：不固定 viewport，实际尺寸由窗口决定，跨机器可能不同。
            context_kwargs["no_viewport"] = True
        else:
            context_kwargs["viewport"] = {
                "width": environment.viewport.width,
                "height": environment.viewport.height,
            }
            context_kwargs["device_scale_factor"] = environment.device_scale_factor
            context_kwargs["is_mobile"] = environment.is_mobile
            context_kwargs["has_touch"] = environment.has_touch

        self._context = self._browser.new_context(**context_kwargs)
        self._context.set_default_timeout(environment.action_timeout_ms)
        self._context.set_default_navigation_timeout(environment.navigation_timeout_ms)
        return self

    def new_page(self) -> Any:
        self.start()
        return self._context.new_page()

    def goto(self, url: str) -> Any:
        page = self.new_page()
        page.goto(url)
        return page

    def close(self) -> None:
        try:
            if self._context is not None:
                self._context.close()
        finally:
            try:
                if self._browser is not None:
                    self._browser.close()
            finally:
                try:
                    if self._playwright is not None:
                        self._playwright.stop()
                finally:
                    self._context = None
                    self._browser = None
                    self._playwright = None

    def __enter__(self) -> "BrowserSession":
        return self.start()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
