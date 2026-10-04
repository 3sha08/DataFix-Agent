import pandas as pd

from datafix.agents.approval import (
    apply_human_decisions,
    get_executable_actions,
)
from datafix.agents.planner import create_remediation_plan
from datafix.agents.validator import validate_remediation
from datafix.models.schemas import ActionApproval, ApprovalRequest
from datafix.tools.fixer import execute_approved_actions
from datafix.tools.profiling import profile_dataset
from datafix.tools.quality import detect_quality_issues
from datafix.utils.scoring import calculate_quality_score


def sample_messy_dataframe():
    return pd.DataFrame(
        {
            "id": [1, 2, 2],
            "name": ["A", "B", "B"],
            "score": [10.0, None, None],
        }
    )


def test_profiler_detects_basic_metrics():
    df = sample_messy_dataframe()

    profile = profile_dataset(df)

    assert profile["rows"] == 3
    assert profile["columns"] == 3
    assert profile["missing_cells"] == 2
    assert profile["duplicate_rows"] == 1


def test_quality_detector_finds_missing_and_duplicates():
    df = sample_messy_dataframe()

    issues = detect_quality_issues(df)

    issue_types = {issue["issue_type"] for issue in issues}

    assert "missing_values" in issue_types
    assert "duplicate_rows" in issue_types


def test_only_approved_actions_are_executable():
    df = sample_messy_dataframe()

    plan = create_remediation_plan(
        detect_quality_issues(df)
    )

    first_action = plan[0]["action_id"]

    decisions = ApprovalRequest(
        approvals=[
            ActionApproval(
                action_id=first_action,
                decision="approved",
            )
        ]
    )

    updated_plan = apply_human_decisions(
        plan,
        decisions,
    )

    executable = get_executable_actions(updated_plan)

    assert len(executable) == 1
    assert executable[0]["action_id"] == first_action


def test_execution_does_not_modify_original_dataframe():
    df = sample_messy_dataframe()
    original = df.copy(deep=True)

    plan = create_remediation_plan(
        detect_quality_issues(df)
    )

    decisions = ApprovalRequest(
        approvals=[
            ActionApproval(
                action_id=action["action_id"],
                decision="approved",
            )
            for action in plan
        ]
    )

    approved_plan = apply_human_decisions(
        plan,
        decisions,
    )

    execute_approved_actions(
        df,
        approved_plan,
    )

    pd.testing.assert_frame_equal(df, original)


def test_validator_confirms_duplicate_resolution():
    df = sample_messy_dataframe()

    plan = create_remediation_plan(
        detect_quality_issues(df)
    )

    duplicate_action = next(
        action
        for action in plan
        if action["action"] == "remove_duplicates"
    )

    decisions = ApprovalRequest(
        approvals=[
            ActionApproval(
                action_id=duplicate_action["action_id"],
                decision="approved",
            )
        ]
    )

    approved_plan = apply_human_decisions(
        plan,
        decisions,
    )

    cleaned, _ = execute_approved_actions(
        df,
        approved_plan,
    )

    report = validate_remediation(
        df,
        cleaned,
        approved_plan,
    )

    verification = next(
        item
        for item in report["verification_results"]
        if item["action"] == "remove_duplicates"
    )

    assert verification["verification_status"] == "resolved"


def test_quality_score_is_bounded():
    df = sample_messy_dataframe()

    score = calculate_quality_score(
        detect_quality_issues(df)
    )

    assert 0 <= score["score"] <= 100