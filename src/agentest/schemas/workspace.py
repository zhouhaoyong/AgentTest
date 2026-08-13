from typing import Literal

from pydantic import Field, field_validator

from agentest.schemas.common import AssetModel, validate_asset_id

WorkspaceSystemType = Literal["", "web", "h5", "app", "miniapp"]


class BrowserPreferences(AssetModel):
    selected: str = "auto"
    mcp_consent: str = "pending"


class WorkspaceContext(AssetModel):
    project_id: str
    system_id: str
    system_type: WorkspaceSystemType = ""
    version_id: str = ""
    test_url: str = ""

    @field_validator("project_id", "system_id")
    @classmethod
    def validate_required_id(cls, value: str) -> str:
        return validate_asset_id(value)

    @field_validator("version_id")
    @classmethod
    def validate_optional_id(cls, value: str) -> str:
        return validate_asset_id(value) if value else value


class WorkspaceState(AssetModel):
    phase: str = "requirement"
    context_confirmed: bool = False
    test_points_approved: bool = False
    last_action: str = ""
    pending_questions: list[str] = Field(default_factory=list)
    browser: BrowserPreferences = Field(default_factory=BrowserPreferences)
