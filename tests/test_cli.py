from pathlib import Path

from typer.testing import CliRunner

from agentest.cli import app


def test_cli_can_create_project_system_and_version(tmp_path: Path) -> None:
    runner = CliRunner()
    root = str(tmp_path)

    result = runner.invoke(app, ["--root", root, "create-project", "demo", "--name", "Demo"])
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(
        app,
        ["--root", root, "create-system", "demo", "web", "--name", "Demo Web"],
    )
    assert result.exit_code == 0, result.stdout

    result = runner.invoke(app, ["--root", root, "create-version", "demo", "web", "v1"])
    assert result.exit_code == 0, result.stdout
    version_yaml = (
        tmp_path / "projects" / "demo" / "systems" / "web" / "versions" / "v1" / "version.yaml"
    )
    assert version_yaml.is_file()


def test_cli_rejects_duplicate_project(tmp_path: Path) -> None:
    runner = CliRunner()
    arguments = ["--root", str(tmp_path), "create-project", "demo", "--name", "Demo"]

    assert runner.invoke(app, arguments).exit_code == 0
    result = runner.invoke(app, arguments)

    assert result.exit_code != 0
    assert "already exists" in result.stdout


def test_doctor_uses_windows_safe_status_output(tmp_path: Path, monkeypatch) -> None:
    import agentest.cli as cli_module

    checks = {
        "check_python": (True, "Python 3.13"),
        "check_playwright_package": (True, "Playwright package"),
        "check_chromium": (True, "Chromium installed"),
        "check_chromium_launch": (True, "Chromium launch"),
        "check_projects_writable": (True, "projects/ writable"),
    }
    for name, result in checks.items():
        if name == "check_projects_writable":
            monkeypatch.setattr(cli_module, name, lambda _path, result=result: result)
        else:
            monkeypatch.setattr(cli_module, name, lambda result=result: result)

    result = CliRunner().invoke(app, ["--root", str(tmp_path), "doctor"])

    assert result.exit_code == 0, result.stdout
    assert "PASS Python 3.13" in result.stdout
    assert "✓" not in result.stdout
