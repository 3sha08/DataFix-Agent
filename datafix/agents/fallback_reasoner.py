from __future__ import annotations

from typing import Any


def generate_fallback_reasoning(
    issues: list[dict[str, Any]],
    plan: list[dict[str, Any]],
) -> str:
    """Generate a deterministic assessment when the LLM is unavailable."""

    if not issues:
        return (
            "No data-quality issues were detected. "
            "No remediation is currently required."
        )

    severity_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    prioritized = sorted(
        issues,
        key=lambda issue: severity_order.get(
            issue.get("severity", "medium"),
            0,
        ),
        reverse=True,
    )

    top_issues = prioritized[:3]

    issue_summary = ", ".join(
        f"{issue['issue_type']} "
        f"({issue.get('severity', 'medium')})"
        for issue in top_issues
    )

    high_risk_actions = [
        action["action"]
        for action in plan
        if action.get("risk") == "high"
    ]

    caution = (
        ", ".join(high_risk_actions)
        if high_risk_actions
        else "No high-risk remediation actions were proposed"
    )

    return (
        f"DataFix detected {len(issues)} quality issue groups. "
        f"Highest-priority findings: {issue_summary}. "
        f"The remediation plan contains {len(plan)} proposed actions. "
        f"Human approval is required before any modification is executed. "
        f"Extra caution: {caution}. "
        f"Outliers are flagged for review rather than automatically removed."
    )