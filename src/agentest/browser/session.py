from typing import Any

from agentest.browser.preflight import inspect_local_playwright
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
        self._main_page: Any = None

    def start(self) -> "BrowserSession":
        if self._browser is not None:
            return self

        preflight = inspect_local_playwright()
        if not preflight.python_playwright_available:
            raise RuntimeError(preflight.install_prompt)

        from playwright.sync_api import sync_playwright

        environment = self.test_environment
        self._playwright = sync_playwright().start()

        try:
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
            # 所有业务测试统一使用系统 Google Chrome，不回退到 Edge 或 Playwright Chromium。
            try:
                self._browser = self._playwright.chromium.launch(channel="chrome", **launch_kwargs)
            except Exception as exc:
                raise RuntimeError(
                    "无法启动系统 Google Chrome，请确认 Chrome 已安装并可用。"
                ) from exc

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
        except Exception:
            try:
                self.close()
            except Exception:
                pass
            raise

    def new_page(self) -> Any:
        self.start()
        return self._context.new_page()

    def main_page(self) -> Any:
        """Return the reusable primary page for the current test group."""
        if self._main_page is None:
            self._main_page = self.new_page()
        return self._main_page

    @property
    def is_closed(self) -> bool:
        """Return whether all Playwright resources have been released."""

        return self._playwright is None and self._browser is None and self._context is None

    def goto(self, url: str) -> Any:
        page = self.main_page()
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
                    self._main_page = None
                    self._browser = None
                    self._playwright = None

    def __enter__(self) -> "BrowserSession":
        return self.start()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
