"""Browser fallback and preflight helpers."""

from agentest.browser.preflight import (
    BrowserCapabilityReport,
    choose_browser_backend,
    has_system_chrome,
    inspect_local_playwright,
)
from agentest.browser.session import BrowserSession

__all__ = [
    "BrowserCapabilityReport",
    "BrowserSession",
    "choose_browser_backend",
    "has_system_chrome",
    "inspect_local_playwright",
]
