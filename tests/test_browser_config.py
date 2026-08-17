import playwright.sync_api as playwright_sync_api
import pytest

from agentest.browser.preflight import BrowserCapabilityReport
from agentest.browser.session import BrowserSession
from agentest.schemas.system import TestEnvironment as BrowserTestEnvironment


def test_browser_defaults_to_headed() -> None:
    browser = BrowserSession()

    assert browser.headless is False
    assert browser.slow_mo == 0


def test_browser_accepts_explicit_configuration() -> None:
    browser = BrowserSession(headless=True, slow_mo=150)

    assert browser.headless is True
    assert browser.slow_mo == 150


def test_browser_accepts_test_environment_configuration() -> None:
    environment = BrowserTestEnvironment(viewport={"width": 390, "height": 844}, is_mobile=True)
    browser = BrowserSession(test_environment=environment)

    assert browser.test_environment == environment


def test_browser_start_checks_playwright_preflight_before_launch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    environment = BrowserTestEnvironment(maximize=True)
    browser = BrowserSession(test_environment=environment)
    report = BrowserCapabilityReport(
        selected_backend="playwright",
        builtin_browser_available=False,
        playwright_mcp_available=False,
        python_playwright_available=True,
    )
    monkeypatch.setattr("agentest.browser.session.inspect_local_playwright", lambda: report)

    assert browser.start() is browser
    browser.close()


class FakePage:
    def __init__(self) -> None:
        self.goto_calls: list[str] = []

    def goto(self, url: str) -> None:
        self.goto_calls.append(url)


class FakeContext:
    def __init__(self) -> None:
        self.close_calls = 0
        self.default_timeouts: list[int] = []
        self.navigation_timeouts: list[int] = []
        self.pages: list[FakePage] = []

    def close(self) -> None:
        self.close_calls += 1

    def set_default_timeout(self, timeout: int) -> None:
        self.default_timeouts.append(timeout)

    def set_default_navigation_timeout(self, timeout: int) -> None:
        self.navigation_timeouts.append(timeout)

    def new_page(self) -> FakePage:
        page = FakePage()
        self.pages.append(page)
        return page


class FakeBrowser:
    def __init__(
        self,
        context: FakeContext | None = None,
        context_error: Exception | None = None,
    ) -> None:
        self.context = context or FakeContext()
        self.context_error = context_error
        self.context_kwargs: dict[str, object] | None = None
        self.close_calls = 0

    def close(self) -> None:
        self.close_calls += 1

    def new_context(self, **kwargs: object) -> FakeContext:
        self.context_kwargs = kwargs
        if self.context_error is not None:
            raise self.context_error
        return self.context


class FakeChromium:
    def __init__(self, browser: FakeBrowser, fail_chrome: bool = False) -> None:
        self.browser = browser
        self.fail_chrome = fail_chrome
        self.launch_calls: list[dict[str, object]] = []

    def launch(self, **kwargs: object) -> FakeBrowser:
        self.launch_calls.append(kwargs)
        if self.fail_chrome and kwargs.get("channel") == "chrome":
            raise RuntimeError("Chrome is unavailable")
        return self.browser


class FakePlaywright:
    def __init__(self, chromium: FakeChromium) -> None:
        self.chromium = chromium
        self.stop_calls = 0

    def stop(self) -> None:
        self.stop_calls += 1


class FakePlaywrightFactory:
    def __init__(self, playwright: FakePlaywright) -> None:
        self.playwright = playwright

    def start(self) -> FakePlaywright:
        return self.playwright


def install_fake_playwright(
    monkeypatch: pytest.MonkeyPatch, browser: FakeBrowser, fail_chrome: bool = False
) -> tuple[FakePlaywright, FakeChromium]:
    chromium = FakeChromium(browser, fail_chrome=fail_chrome)
    fake_playwright = FakePlaywright(chromium)
    factory = FakePlaywrightFactory(fake_playwright)
    monkeypatch.setattr(playwright_sync_api, "sync_playwright", lambda: factory)
    monkeypatch.setattr(
        "agentest.browser.session.inspect_local_playwright",
        lambda: BrowserCapabilityReport(
            selected_backend="playwright",
            builtin_browser_available=False,
            playwright_mcp_available=False,
            python_playwright_available=True,
        ),
    )
    return fake_playwright, chromium


def test_browser_releases_resources_when_context_setup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    browser = FakeBrowser(context_error=RuntimeError("context failed"))
    playwright, _ = install_fake_playwright(monkeypatch, browser)
    session = BrowserSession()

    with pytest.raises(RuntimeError, match="context failed"):
        session.start()

    assert browser.close_calls == 1
    assert playwright.stop_calls == 1
    assert session._context is None
    assert session._browser is None
    assert session._playwright is None


def test_browser_requires_chrome_and_applies_maximize_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    browser = FakeBrowser()
    playwright, chromium = install_fake_playwright(monkeypatch, browser, fail_chrome=True)
    session = BrowserSession(test_environment=BrowserTestEnvironment(maximize=True))

    with pytest.raises(RuntimeError, match="Chrome"):
        session.start()

    assert chromium.launch_calls == [
        {
            "channel": "chrome",
            "headless": False,
            "slow_mo": 0,
            "args": ["--incognito", "--start-maximized"],
        },
    ]
    assert browser.context_kwargs is None
    assert browser.close_calls == 0
    assert playwright.stop_calls == 1


def test_browser_reuses_main_page_for_repeated_goto(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    browser = FakeBrowser()
    playwright, _ = install_fake_playwright(monkeypatch, browser)
    session = BrowserSession()

    first_page = session.goto("https://example.test/first")
    second_page = session.goto("https://example.test/second")

    assert second_page is first_page
    assert browser.context.pages == [first_page]
    assert first_page.goto_calls == [
        "https://example.test/first",
        "https://example.test/second",
    ]

    session.close()
    assert playwright.stop_calls == 1
