from __future__ import annotations

from typing import Any


def create_remediation_plan(
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Convert detected quality issues into proposed remediation actions.

    This planner creates proposals only.
    It does NOT modify the dataset.
    """

    plan: list[dict[str, Any]] = []

    for index, issue in enumerate(issues, start=1):
        issue_type = issue["issue_type"]
        column = issue.get("column")

        action: dict[str, Any] = {
            "action_id": f"A{index:03d}",
            "issue_type": issue_type,
            "column": column,
            "status": "pending",
            "requires_approval": True,
        }

        if issue_type == "missing_values":
            action.update(
                {
                    "action": "impute_missing",
                    "strategy": "auto",
                    "risk": "medium",
                    "description": (
                        f"Impute missing values in '{column}'. "
                        "Use median for numeric columns and mode "
                        "for categorical columns."
                    ),
                }
            )

        elif issue_type == "duplicate_rows":
            action.update(
                {
                    "action": "remove_duplicates",
                    "strategy": "exact_duplicates",
                    "risk": "medium",
                    "description": (
                        "Remove exact duplicate rows while retaining "
                        "the first occurrence."
                    ),
                }
            )

        elif issue_type == "whitespace":
            action.update(
                {
                    "action": "trim_whitespace",
                    "strategy": "strip",
                    "risk": "low",
                    "description": (
                        f"Remove leading and trailing whitespace "
                        f"from '{column}'."
                    ),
                }
            )

        elif issue_type == "category_inconsistency":
            action.update(
                {
                    "action": "standardize_categories",
                    "strategy": "canonicalize",
                    "risk": "medium",
                    "description": (
                        f"Standardize equivalent text categories "
                        f"in '{column}'."
                    ),
                }
            )

        elif issue_type == "numeric_outlier":
            action.update(
                {
                    "action": "flag_outliers",
                    "strategy": "iqr",
                    "risk": "low",
                    "description": (
                        f"Flag potential outliers in '{column}' "
                        "for human review without deleting them."
                    ),
                }
            )

        elif issue_type == "invalid_date":
            action.update(
                {
                    "action": "coerce_invalid_dates",
                    "strategy": "invalid_to_missing",
                    "risk": "high",
                    "description": (
                        f"Convert invalid values in '{column}' to "
                        "missing values so they can be reviewed."
                    ),
                }
            )

        else:
            action.update(
                {
                    "action": "manual_review",
                    "strategy": "none",
                    "risk": "high",
                    "description": (
                        "No safe automatic remediation is available. "
                        "Manual review required."
                    ),
                }
            )

        plan.append(action)

    return plan