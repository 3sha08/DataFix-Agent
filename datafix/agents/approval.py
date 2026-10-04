from __future__ import annotations

from typing import Any

from datafix.models.schemas import ApprovalRequest


def apply_human_decisions(
    plan: list[dict[str, Any]],
    approval_request: ApprovalRequest,
) -> list[dict[str, Any]]:
    """
    Apply explicit human decisions to a remediation plan.

    No pending or rejected action is marked executable.
    """

    decisions = {
        item.action_id: item.decision
        for item in approval_request.approvals
    }

    updated_plan: list[dict[str, Any]] = []

    for action in plan:
        updated_action = action.copy()

        decision = decisions.get(
            action["action_id"],
            "pending",
        )

        if decision == "approved":
            updated_action["status"] = "approved"

        elif decision == "rejected":
            updated_action["status"] = "rejected"

        else:
            updated_action["status"] = "pending"

        updated_plan.append(updated_action)

    return updated_plan


def get_executable_actions(
    plan: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Return only actions explicitly approved by a human.
    """

    return [
        action
        for action in plan
        if action.get("status") == "approved"
    ]