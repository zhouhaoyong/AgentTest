from pathlib import Path
from re import fullmatch
from typing import Any, TypeVar

import yaml
from pydantic import BaseModel, ConfigDict

SAFE_ID_PATTERN = r"^[A-Za-z0-9._-]+$"

ModelT = TypeVar("ModelT", bound=BaseModel)


class AssetModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


def validate_asset_id(value: str) -> str:
    if not value or value in {".", ".."} or fullmatch(SAFE_ID_PATTERN, value) is None:
        raise ValueError("must be a non-empty directory-safe ID matching ^[A-Za-z0-9._-]+$")
    return value


def load_yaml_model(path: Path, model_type: type[ModelT]) -> ModelT:
    with path.open(encoding="utf-8") as stream:
        data: Any = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ValueError(f"YAML asset must contain a mapping: {path}")
    return model_type.model_validate(data)
