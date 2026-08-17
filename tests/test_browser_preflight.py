import agentest.browser.preflight as preflight
from agentest.browser.preflight import (
    BrowserCapabilityReport,
    choose_browser_backend,
)


def test_browser_preflight_prefers_isolated_builtin_browser() -> None:
    report = choose_browser_backend(
        builtin_browser_available=True,
        playwright_mcp_available=True,
        python_playwright_available=True,
    )

    assert report.selected_backend == "agent_browser"
    assert report.install_required is False


def test_browser_preflight_uses_isolated_playwright_capability_before_python_fallback() -> None:
    report = choose_browser_backend(
        builtin_browser_available=False,
        playwright_mcp_available=True,
        python_playwright_available=True,
    )

    assert report.selected_backend == "playwright_mcp"
    assert report.install_required is False


def test_browser_preflight_requests_install_consent_when_no_backend_exists() -> None:
    report = choose_browser_backend(
        builtin_browser_available=False,
        playwright_mcp_available=False,
        python_playwright_available=False,
    )

    assert isinstance(report, BrowserCapabilityReport)
    assert report.selected_backend is None
    assert report.install_required is True
    assert "Chrome" in report.install_prompt
    assert "是否需要我协助安装" in report.install_prompt


def test_browser_preflight_does_not_count_edge_as_chrome(
    monkeypatch,
    tmp_path,
) -> None:
    for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        monkeypatch.setenv(variable, str(tmp_path))

    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda command: "C:/msedge.exe" if command in {"msedge", "msedge.exe"} else None,
    )

    assert preflight.has_system_chrome() is False


def test_browser_preflight_detects_chrome_command(monkeypatch) -> None:
    monkeypatch.setattr(
        preflight.shutil,
        "which",
        lambda command: "C:/chrome.exe" if command == "chrome.exe" else None,
    )

    assert preflight.has_system_chrome() is True
