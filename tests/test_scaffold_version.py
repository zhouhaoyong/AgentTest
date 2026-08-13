from pathlib import Path

import pytest

from agentest.scaffold.project import create_project
from agentest.scaffold.system import create_system
from agentest.scaffold.version import ScaffoldError, create_version


def _system_root(tmp_path: Path) -> Path:
    projects_dir = tmp_path / "projects"
    create_project(projects_dir, "contact-platform", "通讯录平台")
    create_system(projects_dir, "contact-platform", "contact-web", "通讯录 Web")
    return projects_dir


def test_create_version_creates_complete_asset_tree(tmp_path: Path) -> None:
    version_dir = create_version(
        _system_root(tmp_path), "contact-platform", "contact-web", "v0.0.1"
    )

    expected_files = [
        "version.yaml",
        "requirement.md",
        "requirements/source.md",
        "requirements/requirement.md",
        "requirements/attachments/requirement.md",
        "analysis/analysis.md",
        "analysis/requirement.md",
        "test-points/test-points.md",
        "test-points/requirement.md",
        "run/result.md",
        "run/requirement.md",
        "bugs/bugs.md",
        "bugs/requirement.md",
        "report/report.md",
        "report/requirement.md",
    ]

    assert all((version_dir / relative_path).is_file() for relative_path in expected_files)


def test_same_version_id_is_rejected_but_other_system_can_reuse_it(tmp_path: Path) -> None:
    projects_dir = _system_root(tmp_path)
    create_version(projects_dir, "contact-platform", "contact-web", "v0.0.1")

    with pytest.raises(ScaffoldError, match="already exists"):
        create_version(projects_dir, "contact-platform", "contact-web", "v0.0.1")

    create_system(projects_dir, "contact-platform", "admin-web", "管理 Web")
    other_version = create_version(projects_dir, "contact-platform", "admin-web", "v0.0.1")

    assert other_version.name == "v0.0.1"


def test_invalid_version_id_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ScaffoldError, match="directory-safe"):
        create_version(_system_root(tmp_path), "contact-platform", "contact-web", "bad/version")


def test_create_version_removes_partial_tree_when_template_creation_fails(
    tmp_path: Path, monkeypatch
) -> None:
    projects_dir = _system_root(tmp_path)
    import agentest.scaffold.version as version_module

    def missing_template(_name: str) -> str:
        raise RuntimeError("template missing")

    monkeypatch.setattr(version_module, "read_template", missing_template)

    with pytest.raises(RuntimeError, match="template missing"):
        create_version(projects_dir, "contact-platform", "contact-web", "v0.0.1")

    version_dir = (
        projects_dir
        / "contact-platform"
        / "systems"
        / "contact-web"
        / "versions"
        / "v0.0.1"
    )
    assert not version_dir.exists()
