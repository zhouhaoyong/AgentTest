from agentest.browser.session import BrowserSession


def test_browser_defaults_to_headed() -> None:
    browser = BrowserSession()

    assert browser.headless is False
    assert browser.slow_mo == 0


def test_browser_accepts_explicit_configuration() -> None:
    browser = BrowserSession(headless=True, slow_mo=150)

    assert browser.headless is True
    assert browser.slow_mo == 150
