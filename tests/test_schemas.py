from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from agentest.schemas.project import ProjectConfig, load_yaml_model
from agentest.schemas.system import SystemConfig
from agentest.schemas.version import VersionConfig


def test_project_config_accepts_minimal_valid_data() -> None:
    config = ProjectConfig(id="contact-platform", name="通讯录平台")

    assert config.id == "contact-platform"
    assert config.description == ""


@pytest.mark.parametrize("invalid_id", ["", "../escape", "contact/platform", "contact platform"])
def test_project_config_rejects_unsafe_ids(invalid_id: str) -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(id=invalid_id, name="通讯录平台")


def test_system_config_allows_empty_base_url() -> None:
    config = SystemConfig(id="contact-web", name="通讯录 Web", base_url="")

    assert config.type == "web"
    assert config.base_url == ""


def test_version_config_allows_empty_test_url() -> None:
    config = VersionConfig(id="v0.0.1", name="v0.0.1", test_url="")

    assert config.test_url == ""


def test_load_yaml_model_validates_file(tmp_path: Path) -> None:
    path = tmp_path / "project.yaml"
    path.write_text(yaml.safe_dump({"id": "demo", "name": "Demo"}), encoding="utf-8")

    config = load_yaml_model(path, ProjectConfig)

    assert config == ProjectConfig(id="demo", name="Demo")
