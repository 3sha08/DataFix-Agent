from __future__ import annotations

from typing import Any


SEVERITY_PENALTIES = {
    "critical": 20,
    "high": 12,
    "medium": 7,
    "low": 3,
}


def calculate_quality_score(
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Calculate an explainable dataset quality score from 0 to 100.

    Each detected issue group reduces the score according to severity.
    """

    score = 100
    deductions: list[dict[str, Any]] = []

    for issue in issues:
        severity = issue.get("severity", "medium")
        penalty = SEVERITY_PENALTIES.get(severity, 7)

        score -= penalty

        deductions.append(
            {
                "issue_type": issue["issue_type"],
                "column": issue.get("column"),
                "severity": severity,
                "penalty": penalty,
            }
        )

    score = max(0, min(100, score))

    if score >= 90:
        grade = "Excellent"
    elif score >= 75:
        grade = "Good"
    elif score >= 60:
        grade = "Needs Attention"
    else:
        grade = "Poor"

    return {
        "score": score,
        "grade": grade,
        "issue_count": len(issues),
        "deductions": deductions,
    }