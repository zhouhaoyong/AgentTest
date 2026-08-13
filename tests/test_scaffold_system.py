from pathlib import Path

import pytest

from agentest.scaffold.project import create_project
from agentest.scaffold.system import ScaffoldError, create_system


def test_create_system_creates_system_assets(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    create_project(projects_dir, "contact-platform", "通讯录平台")

    system_dir = create_system(projects_dir, "contact-platform", "contact-web", "通讯录 Web")

    assert (system_dir / "system.yaml").is_file()
    assert (system_dir / "requirement.md").is_file()
    assert (system_dir / "element-map" / "index.md").is_file()
    assert (system_dir / "element-map" / "requirement.md").is_file()
    assert (system_dir / "element-map" / "modules" / "requirement.md").is_file()
    assert (system_dir / "memory" / "index.md").is_file()
    assert (system_dir / "memory" / "requirement.md").is_file()
    assert (system_dir / "memory" / "modules" / "requirement.md").is_file()
    assert (system_dir / "versions" / "requirement.md").is_file()
    assert (system_dir / "versions").is_dir()


def test_create_system_rejects_duplicate_id(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    create_project(projects_dir, "contact-platform", "通讯录平台")
    create_system(projects_dir, "contact-platform", "contact-web", "通讯录 Web")

    with pytest.raises(ScaffoldError, match="already exists"):
        create_system(projects_dir, "contact-platform", "contact-web", "重复系统")
