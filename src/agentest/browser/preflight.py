"""Environment probing before starting an isolated browser session.

统一后端：所有业务测试都用本机 Playwright 驱动系统 Google Chrome 的隔离（无痕）会话，
不再区分内置浏览器 / MCP / Python 三种后端。需要内置浏览器时由用户自然语言指示对应 agent，
不写进脚手架。

前置探测收集 6 项环境信息（操作系统、屏幕可用尺寸、Chrome 可用性、Playwright 可用性、
Chrome 版本、设备像素比 DPR）。其中屏幕可用尺寸与 DPR 依赖浏览器内查询，在会话启动后回填。
"""

import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path


@dataclass(frozen=True)
class ScreenMetrics:
    """浏览器内查询得到的屏幕指标（零依赖，跨机器透明）。"""

    avail_width: int
    avail_height: int
    device_pixel_ratio: float


@dataclass(frozen=True)
class EnvironmentProbe:
    """启动隔离会话前的环境探测结果。"""

    os_name: str
    chrome_available: bool
    playwright_available: bool
    chrome_version: str | None = None
    # 屏幕可用尺寸与 DPR 由浏览器内查询回填，探测阶段为 None。
    screen: ScreenMetrics | None = None

    @property
    def ready(self) -> bool:
        """是否具备启动隔离 Chrome 会话的最低能力。"""

        return self.chrome_available and self.playwright_available

    @property
    def install_required(self) -> bool:
        return not self.ready

    @property
    def install_prompt(self) -> str:
        missing = []
        if not self.chrome_available:
            missing.append("系统 Google Chrome")
        if not self.playwright_available:
            missing.append("本机 Playwright")
        detail = "、".join(missing) if missing else "隔离浏览器能力"
        return (
            f"当前缺少可用的隔离 Chrome 能力（需要：{detail}）。"
            "是否需要我协助安装或启用？在确认前不会打开用户现有浏览器。"
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


def system_chrome_version() -> str | None:
    """Best-effort read of the system Chrome version string.

    通过命令行执行 `--version`；不同平台命令名不同，任一成功即返回版本号。
    读取失败（如仅通过固定路径安装、命令不支持 --version）时返回 None，不阻断流程。
    """

    for command in ("google-chrome", "chrome", "chrome.exe"):
        executable = shutil.which(command)
        if executable is None:
            continue
        try:
            output = subprocess.run(
                [executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        match = re.search(r"\d+(?:\.\d+){1,3}", output.stdout or "")
        if match:
            return match.group(0)
    return None


def has_local_playwright() -> bool:
    """Return whether the Python Playwright package is importable."""

    return find_spec("playwright") is not None


def probe_environment() -> EnvironmentProbe:
    """Collect the pre-launch environment facts used to decide session startup."""

    chrome_available = has_system_chrome()
    return EnvironmentProbe(
        os_name=platform.system(),
        chrome_available=chrome_available,
        playwright_available=has_local_playwright(),
        chrome_version=system_chrome_version() if chrome_available else None,
    )


__all__ = [
    "EnvironmentProbe",
    "ScreenMetrics",
    "has_local_playwright",
    "has_system_chrome",
    "probe_environment",
    "system_chrome_version",
]
