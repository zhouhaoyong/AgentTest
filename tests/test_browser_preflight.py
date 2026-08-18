import agentest.browser.preflight as preflight
from agentest.browser.preflight import (
    EnvironmentProbe,
    probe_environment,
)


def test_environment_probe_is_ready_only_with_chrome_and_playwright() -> None:
    ready = EnvironmentProbe(
        os_name="Windows",
        chrome_available=True,
        playwright_available=True,
        chrome_version="126.0.0.0",
    )

    assert ready.ready is True
    assert ready.install_required is False


def test_environment_probe_requests_install_when_chrome_missing() -> None:
    probe = EnvironmentProbe(
        os_name="Linux",
        chrome_available=False,
        playwright_available=True,
    )

    assert probe.ready is False
    assert probe.install_required is True
    assert "系统 Google Chrome" in probe.install_prompt
    assert "是否需要我协助安装" in probe.install_prompt


def test_environment_probe_requests_install_when_playwright_missing() -> None:
    probe = EnvironmentProbe(
        os_name="Darwin",
        chrome_available=True,
        playwright_available=False,
    )

    assert probe.install_required is True
    assert "Playwright" in probe.install_prompt


def test_probe_environment_collects_all_six_facts(monkeypatch) -> None:
    monkeypatch.setattr(preflight.platform, "system", lambda: "Windows")
    monkeypatch.setattr(preflight, "has_system_chrome", lambda: True)
    monkeypatch.setattr(preflight, "has_local_playwright", lambda: True)
    monkeypatch.setattr(preflight, "system_chrome_version", lambda: "126.0.6478.127")

    probe = probe_environment()

    assert probe.os_name == "Windows"
    assert probe.chrome_available is True
    assert probe.playwright_available is True
    assert probe.chrome_version == "126.0.6478.127"
    # 屏幕可用尺寸与 DPR 依赖浏览器内查询，探测阶段留空。
    assert probe.screen is None


def test_probe_environment_skips_chrome_version_when_chrome_absent(monkeypatch) -> None:
    monkeypatch.setattr(preflight.platform, "system", lambda: "Linux")
    monkeypatch.setattr(preflight, "has_system_chrome", lambda: False)
    monkeypatch.setattr(preflight, "has_local_playwright", lambda: True)

    def _fail_version() -> str:  # pragma: no cover - must not be called
        raise AssertionError("chrome_available=False 时不应查询版本")

    monkeypatch.setattr(preflight, "system_chrome_version", _fail_version)

    probe = probe_environment()

    assert probe.chrome_available is False
    assert probe.chrome_version is None


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
