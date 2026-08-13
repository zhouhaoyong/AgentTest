import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

CHROMIUM_EXECUTABLE_PATTERN = {
    "win32": ("chrome-win64", "chrome.exe"),
    "darwin": ("chrome-mac", "Chromium.app", "Contents", "MacOS", "Chromium"),
    "linux": ("chrome-linux", "chrome"),
}


def check_python() -> tuple[bool, str]:
    ok = sys.version_info >= (3, 13)
    return ok, f"Python {sys.version_info.major}.{sys.version_info.minor}"


def check_playwright_package() -> tuple[bool, str]:
    available = importlib.util.find_spec("playwright") is not None
    return available, "Playwright package"


def check_chromium() -> tuple[bool, str]:
    if not check_playwright_package()[0]:
        return False, "Chromium unavailable because Playwright package is missing"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            check=True,
            text=True,
            encoding="utf-8",
        )
        match = re.search(r"Install location:\s*(.+)", result.stdout)
        if match is None:
            return False, "Chromium install location unavailable"
        install_root = Path(os.path.expandvars(match.group(1).strip()))
        executable_parts = CHROMIUM_EXECUTABLE_PATTERN.get(sys.platform)
        if executable_parts is None:
            return False, f"Chromium check unsupported on {sys.platform}"
        installed = (install_root.joinpath(*executable_parts)).is_file()
        return installed, "Chromium installed" if installed else "Chromium not installed"
    except Exception as exc:  # Playwright reports multiple installation-specific errors.
        return False, f"Chromium unavailable: {exc}"


def check_chromium_launch() -> tuple[bool, str]:
    if not check_chromium()[0]:
        return False, "Chromium launch skipped"
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser: Any = playwright.chromium.launch(headless=True)
            browser.close()
        return True, "Chromium launch"
    except Exception as exc:
        return False, f"Chromium launch failed: {exc}"


def check_projects_writable(projects_root: Path) -> tuple[bool, str]:
    try:
        projects_root.mkdir(parents=True, exist_ok=True)
        probe = projects_root / ".agentest-write-check"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True, "projects/ writable"
    except OSError as exc:
        return False, f"projects/ not writable: {exc}"
