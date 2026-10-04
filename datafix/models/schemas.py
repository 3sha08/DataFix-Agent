from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ApprovalDecision = Literal["approved", "rejected", "pending"]


class ActionApproval(BaseModel):
    """Human decision for one proposed remediation action."""

    action_id: str
    decision: ApprovalDecision = "pending"
    reviewer_note: str | None = None


class ApprovalRequest(BaseModel):
    """Collection of human decisions for a remediation plan."""

    approvals: list[ActionApproval] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    """Audit record describing the result of an approved action."""

    action_id: str
    action: str
    column: str | None = None
    status: Literal["executed", "skipped", "failed"]
    message: str