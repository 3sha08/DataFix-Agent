from __future__ import annotations

from typing import Any

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field


class DataFixAgentState(BaseModel):
    """Shared state carried through the DataFix agent workflow."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_df: pd.DataFrame

    profile: dict[str, Any] = Field(default_factory=dict)
    issues: list[dict[str, Any]] = Field(default_factory=list)
    quality_score: dict[str, Any] = Field(default_factory=dict)
    remediation_plan: list[dict[str, Any]] = Field(default_factory=list)

    reasoning_summary: str | None = None

    approved_plan: list[dict[str, Any]] = Field(default_factory=list)
    cleaned_df: pd.DataFrame | None = None
    audit_log: list[Any] = Field(default_factory=list)
    validation: dict[str, Any] = Field(default_factory=dict)
    final_score: dict[str, Any] = Field(default_factory=dict)

def create_initial_state(df: pd.DataFrame) -> DataFixAgentState:
    """Create a fresh DataFix agent state for an uploaded dataset."""

    return DataFixAgentState(
        original_df=df.copy(deep=True),
    )