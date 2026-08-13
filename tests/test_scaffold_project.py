from pathlib import Path

import pytest

from agentest.scaffold.project import ScaffoldError, create_project


def test_create_project_creates_contract_and_project_yaml(tmp_path: Path) -> None:
    project_dir = create_project(tmp_path / "projects", "contact-platform", "通讯录平台")

    assert project_dir == tmp_path / "projects" / "contact-platform"
    assert (project_dir / "project.yaml").is_file()
    assert (project_dir / "requirement.md").is_file()
    assert (project_dir / "systems").is_dir()
    assert (project_dir / "systems" / "requirement.md").is_file()


def test_create_project_rejects_existing_project_without_overwriting(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    project_dir = projects_dir / "contact-platform"
    project_dir.mkdir(parents=True)
    marker = project_dir / "marker.txt"
    marker.write_text("keep", encoding="utf-8")

    with pytest.raises(ScaffoldError, match="already exists"):
        create_project(projects_dir, "contact-platform", "新名称")

    assert marker.read_text(encoding="utf-8") == "keep"
