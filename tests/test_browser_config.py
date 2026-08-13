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
