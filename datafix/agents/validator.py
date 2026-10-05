from __future__ import annotations

from typing import Any

import pandas as pd

from datafix.tools.profiling import profile_dataset
from datafix.tools.quality import detect_quality_issues


def _issue_key(issue: dict[str, Any]) -> tuple[str, str | None]:
    """
    Create a comparable identity for a quality issue.
    """
    return (
        issue["issue_type"],
        issue.get("column"),
    )


def validate_remediation(
    before_df: pd.DataFrame,
    after_df: pd.DataFrame,
    plan: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Independently validate whether approved remediation actions
    improved the dataset.

    The validator re-runs profiling and quality detection rather
    than trusting execution messages.
    """

    before_profile = profile_dataset(before_df)
    after_profile = profile_dataset(after_df)

    before_issues = detect_quality_issues(before_df)
    after_issues = detect_quality_issues(after_df)

    before_keys = {
        _issue_key(issue)
        for issue in before_issues
    }

    after_keys = {
        _issue_key(issue)
        for issue in after_issues
    }

    verification_results: list[dict[str, Any]] = []

    for action in plan:
        if action.get("status") != "approved":
            continue

        issue_key = (
            action["issue_type"],
            action.get("column"),
        )

        existed_before = issue_key in before_keys
        exists_after = issue_key in after_keys

        if action["action"] == "flag_outliers":
            flag_column = f"{action.get('column')}_outlier_flag"

            if existed_before and flag_column in after_df.columns:
                verification_status = "resolved"
            elif existed_before:
                verification_status = "remaining"
            else:
                verification_status = "not_detected_before"

        elif existed_before and not exists_after:
            verification_status = "resolved"

        elif existed_before and exists_after:
            verification_status = "remaining"

        else:
            verification_status = "not_detected_before"

        verification_results.append(
            {
                "action_id": action["action_id"],
                "action": action["action"],
                "column": action.get("column"),
                "verification_status": verification_status,
            }
        )

    resolved = sum(
        item["verification_status"] == "resolved"
        for item in verification_results
    )

    remaining = sum(
        item["verification_status"] == "remaining"
        for item in verification_results
    )

    return {
        "before_profile": before_profile,
        "after_profile": after_profile,
        "before_issue_count": len(before_issues),
        "after_issue_count": len(after_issues),
        "resolved_approved_actions": resolved,
        "remaining_approved_actions": remaining,
        "verification_results": verification_results,
        "remaining_issues": after_issues,
    }