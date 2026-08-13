from typing import Any


class BrowserSession:
    """Small lifecycle helper that leaves Playwright Page APIs untouched."""

    def __init__(self, headless: bool = False, slow_mo: int = 0) -> None:
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright: Any = None
        self._browser: Any = None
        self._context: Any = None

    def start(self) -> "BrowserSession":
        if self._browser is not None:
            return self
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self._context = self._browser.new_context()
        return self

    def new_page(self) -> Any:
        self.start()
        return self._context.new_page()

    def goto(self, url: str) -> Any:
        page = self.new_page()
        page.goto(url)
        return page

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
        self._context = None
        self._browser = None
        self._playwright = None

    def __enter__(self) -> "BrowserSession":
        return self.start()

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
