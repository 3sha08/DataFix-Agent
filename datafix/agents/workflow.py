from __future__ import annotations

from datafix.agents.planner import create_remediation_plan
from datafix.models.agent_state import DataFixAgentState
from datafix.tools.profiling import profile_dataset
from datafix.tools.quality import detect_quality_issues
from datafix.utils.scoring import calculate_quality_score


def analyze_state(state: DataFixAgentState) -> DataFixAgentState:
    """Run deterministic analysis and update the shared agent state."""

    df = state.original_df

    state.profile = profile_dataset(df)
    state.issues = detect_quality_issues(df)
    state.quality_score = calculate_quality_score(state.issues)
    state.remediation_plan = create_remediation_plan(state.issues)

    return state

from datafix.agents.approval import apply_human_decisions
from datafix.models.schemas import ApprovalRequest


def apply_approval_state(
    state: DataFixAgentState,
    approvals: ApprovalRequest,
) -> DataFixAgentState:
    """Apply human approval decisions to the proposed remediation plan."""

    state.approved_plan = apply_human_decisions(
        state.remediation_plan,
        approvals,
    )

    return state

from datafix.tools.fixer import execute_approved_actions


def execute_state(state: DataFixAgentState) -> DataFixAgentState:
    """Execute only the remediation actions approved by the human."""

    cleaned_df, audit_log = execute_approved_actions(
        state.original_df,
        state.approved_plan,
    )

    state.cleaned_df = cleaned_df
    state.audit_log = audit_log

    return state

from datafix.agents.validator import validate_remediation


def validate_state(state: DataFixAgentState) -> DataFixAgentState:
    """Independently verify the results of approved remediation actions."""

    if state.cleaned_df is None:
        raise RuntimeError(
            "No cleaned dataset exists. Execute approved actions before validation."
        )

    state.validation = validate_remediation(
        state.original_df,
        state.cleaned_df,
        state.approved_plan,
    )

    remaining_issues = detect_quality_issues(state.cleaned_df)

    state.final_score = calculate_quality_score(
        remaining_issues
    )

    return state