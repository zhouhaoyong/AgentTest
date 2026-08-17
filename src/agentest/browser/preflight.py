"""Browser capability checks used before starting an isolated session."""

import os
import shutil
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path
from typing import Literal

BrowserBackend = Literal["agent_browser", "playwright_mcp", "playwright"]


@dataclass(frozen=True)
class BrowserCapabilityReport:
    selected_backend: BrowserBackend | None
    builtin_browser_available: bool
    playwright_mcp_available: bool
    python_playwright_available: bool

    @property
    def install_required(self) -> bool:
        return self.selected_backend is None

    @property
    def install_prompt(self) -> str:
        return (
            "当前没有可用的隔离 Chrome 浏览器能力。是否需要我协助安装或启用 Chrome / Playwright？"
            "在确认前不会打开用户现有浏览器。"
        )


def choose_browser_backend(
    *,
    builtin_browser_available: bool,
    playwright_mcp_available: bool,
    python_playwright_available: bool,
) -> BrowserCapabilityReport:
    """Choose an isolated browser backend in the documented priority order."""

    selected_backend: BrowserBackend | None
    if builtin_browser_available:
        selected_backend = "agent_browser"
    elif playwright_mcp_available:
        selected_backend = "playwright_mcp"
    elif python_playwright_available:
        selected_backend = "playwright"
    else:
        selected_backend = None

    return BrowserCapabilityReport(
        selected_backend=selected_backend,
        builtin_browser_available=builtin_browser_available,
        playwright_mcp_available=playwright_mcp_available,
        python_playwright_available=python_playwright_available,
    )


def has_system_chrome() -> bool:
    """Return whether a system Google Chrome installation can be discovered."""

    if any(shutil.which(command) for command in ("chrome", "chrome.exe", "google-chrome")):
        return True

    relative_paths = (
        Path("Google") / "Chrome" / "Application" / "chrome.exe",
        Path("Google Chrome") / "Application" / "chrome.exe",
    )
    roots = (
        os.environ.get("PROGRAMFILES"),
        os.environ.get("PROGRAMFILES(X86)"),
        os.environ.get("LOCALAPPDATA"),
    )
    return any(
        (Path(root) / relative_path).is_file()
        for root in roots
        if root
        for relative_path in relative_paths
    )


def inspect_local_playwright() -> BrowserCapabilityReport:
    """Check whether local Python Playwright and system Google Chrome are available."""

    if find_spec("playwright") is None or not has_system_chrome():
        return choose_browser_backend(
            builtin_browser_available=False,
            playwright_mcp_available=False,
            python_playwright_available=False,
        )

    return choose_browser_backend(
        builtin_browser_available=False,
        playwright_mcp_available=False,
        python_playwright_available=True,
    )


__all__ = [
    "BrowserBackend",
    "BrowserCapabilityReport",
    "choose_browser_backend",
    "has_system_chrome",
    "inspect_local_playwright",
]
