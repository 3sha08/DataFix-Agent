from __future__ import annotations

from typing import Any

import pandas as pd

from datafix.agents.approval import apply_human_decisions
from datafix.agents.planner import create_remediation_plan
from datafix.agents.validator import validate_remediation
from datafix.models.schemas import ApprovalRequest
from datafix.tools.fixer import execute_approved_actions
from datafix.tools.profiling import profile_dataset
from datafix.tools.quality import detect_quality_issues
from datafix.utils.scoring import calculate_quality_score


class DataFixOrchestrator:
    """
    Coordinates the DataFix analysis, approval,
    remediation, and validation workflow.
    """

    def analyze(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze a dataset and generate a remediation plan."""

        profile = profile_dataset(df)
        issues = detect_quality_issues(df)
        score = calculate_quality_score(issues)
        plan = create_remediation_plan(issues)

        return {
            "profile": profile,
            "issues": issues,
            "score": score,
            "plan": plan,
        }

    def execute(
        self,
        df: pd.DataFrame,
        plan: list[dict[str, Any]],
        approvals: ApprovalRequest,
    ) -> dict[str, Any]:
        """Execute only human-approved actions and validate the result."""

        approved_plan = apply_human_decisions(
            plan,
            approvals,
        )

        cleaned_df, audit_log = execute_approved_actions(
            df,
            approved_plan,
        )

        validation = validate_remediation(
            df,
            cleaned_df,
            approved_plan,
        )

        after_issues = detect_quality_issues(cleaned_df)
        after_score = calculate_quality_score(after_issues)

        return {
            "cleaned_df": cleaned_df,
            "plan": approved_plan,
            "audit_log": audit_log,
            "validation": validation,
            "after_score": after_score,
        }