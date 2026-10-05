from __future__ import annotations

import hashlib

import pandas as pd
import plotly.express as px
import streamlit as st

from datafix.agents.workflow import (
    analyze_state,
    apply_approval_state,
    execute_state,
    reason_state,
    validate_state,
)
from datafix.models.agent_state import create_initial_state
from datafix.models.schemas import ActionApproval, ApprovalRequest


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="DataFix Agent",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "executed_state" not in st.session_state:
    st.session_state.executed_state = None

if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = None


# ---------------------------------------------------------
# Styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        .hero {
            padding: 2.1rem 2.2rem;
            border-radius: 22px;
            background:
                linear-gradient(
                    135deg,
                    rgba(79, 70, 229, 0.16),
                    rgba(14, 165, 233, 0.10)
                );
            border: 1px solid rgba(120, 120, 120, 0.18);
            margin-bottom: 1.4rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.7rem;
        }

        .hero p {
            font-size: 1.08rem;
            margin-top: 0.7rem;
            margin-bottom: 0;
            opacity: 0.85;
        }

        .workflow-box {
            padding: 1rem 1.2rem;
            border-radius: 14px;
            border: 1px solid rgba(120, 120, 120, 0.18);
            text-align: center;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }

        .section-note {
            opacity: 0.75;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def get_file_id(file_bytes: bytes) -> str:
    """Create a stable identifier for the uploaded CSV."""
    return hashlib.sha256(file_bytes).hexdigest()


def show_dataset_insights(
    data: pd.DataFrame,
    title: str,
) -> None:
    """
    Render schema-aware descriptive visualizations.

    Charts are generated only when suitable columns exist.
    """

    st.subheader(title)

    st.caption(
        "Automatically generated descriptive insights based on "
        "the available numeric and categorical columns."
    )

    numeric_columns = data.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = data.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Rows", f"{len(data):,}")

    with metric2:
        st.metric("Columns", f"{len(data.columns):,}")

    with metric3:
        st.metric(
            "Numeric Columns",
            len(numeric_columns),
        )

    with metric4:
        st.metric(
            "Missing Cells",
            f"{int(data.isna().sum().sum()):,}",
        )

    tab1, tab2, tab3 = st.tabs(
        [
            "Missing Data",
            "Numeric Insights",
            "Category Insights",
        ]
    )

    with tab1:
        missing = (
            data.isna()
            .sum()
            .sort_values(ascending=False)
        )

        missing = missing[missing > 0]

        if missing.empty:
            st.success(
                "No missing values are present in this dataset."
            )
        else:
            missing_df = pd.DataFrame(
                {
                    "Column": missing.index,
                    "Missing Values": missing.values,
                }
            )

            fig = px.bar(
                missing_df,
                x="Column",
                y="Missing Values",
                title="Missing Values by Column",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    with tab2:
        if not numeric_columns:
            st.info(
                "No numeric columns are available for "
                "distribution analysis."
            )
        else:
            selected_numeric = st.selectbox(
                "Choose a numeric column",
                numeric_columns,
                key=f"{title}_numeric",
            )

            fig = px.histogram(
                data,
                x=selected_numeric,
                title=f"Distribution of {selected_numeric}",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            if len(numeric_columns) >= 2:
                st.markdown("#### Numeric Correlation")

                correlation = (
                    data[numeric_columns]
                    .corr(numeric_only=True)
                )

                st.dataframe(
                    correlation.round(2),
                    use_container_width=True,
                )

    with tab3:
        usable_categories = [
            column
            for column in categorical_columns
            if 1 < data[column].nunique(dropna=True) <= 20
        ]

        if not usable_categories:
            st.info(
                "No low-cardinality categorical columns "
                "are suitable for a category chart."
            )
        else:
            selected_category = st.selectbox(
                "Choose a categorical column",
                usable_categories,
                key=f"{title}_category",
            )

            category_counts = (
                data[selected_category]
                .fillna("Missing")
                .astype(str)
                .value_counts()
                .head(15)
                .reset_index()
            )

            category_counts.columns = [
                selected_category,
                "Count",
            ]

            fig = px.bar(
                category_counts,
                x=selected_category,
                y="Count",
                title=f"{selected_category} Distribution",
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )


# ---------------------------------------------------------
# Hero
# ---------------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🧹 DataFix Agent</h1>
        <p>
            Autonomous data-quality analysis, human-controlled
            remediation, independent validation, and instant
            data insights.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow-box">
        Upload → Detect → Reason → Approve → Fix →
        Validate → Visualize → Download
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.header("DataFix Agent")

    st.write(
        "Turn messy CSV data into validated, "
        "analysis-ready datasets."
    )

    st.divider()

    st.markdown("### Agent Guardrails")

    st.success("✓ Human approval required")
    st.info("✓ Deterministic validation")
    st.info("✓ Outliers preserved and flagged")
    st.info("✓ Every action is audited")

    st.divider()

    st.caption(
        "WCC Launchpad 30 • Agentic AI Track"
    )


# ---------------------------------------------------------
# Upload
# ---------------------------------------------------------

st.header("1. Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"],
    help="DataFix currently supports CSV datasets.",
)

if uploaded_file is None:
    st.info(
        "Upload a CSV dataset to start the DataFix agent workflow."
    )
    st.stop()


file_bytes = uploaded_file.getvalue()
current_file_id = get_file_id(file_bytes)

if st.session_state.uploaded_file_id != current_file_id:
    st.session_state.uploaded_file_id = current_file_id
    st.session_state.executed_state = None

    for key in list(st.session_state.keys()):
        if key.startswith("approval_"):
            del st.session_state[key]


try:
    df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"Unable to read CSV file: {exc}")
    st.stop()


st.success(
    f"{uploaded_file.name} loaded successfully — "
    f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"
)

with st.expander(
    "View Original Dataset",
    expanded=False,
):
    st.dataframe(
        df,
        use_container_width=True,
    )


# ---------------------------------------------------------
# Agent analysis
# ---------------------------------------------------------

state = create_initial_state(df)
state = analyze_state(state)
state = reason_state(state)

st.header("2. Data Quality Analysis")

score_col, issue_col, missing_col, duplicate_col = st.columns(4)

with score_col:
    st.metric(
        "Quality Score",
        f"{state.quality_score['score']}/100",
    )

with issue_col:
    st.metric(
        "Issue Groups",
        len(state.issues),
    )

with missing_col:
    st.metric(
        "Missing Cells",
        int(df.isna().sum().sum()),
    )

with duplicate_col:
    st.metric(
        "Duplicate Rows",
        int(df.duplicated().sum()),
    )

st.caption(
    f"Quality grade: {state.quality_score['grade']}"
)


# ---------------------------------------------------------
# Issue visualization
# ---------------------------------------------------------

if state.issues:
    issue_rows = []

    for issue in state.issues:
        issue_rows.append(
            {
                "Issue": issue["issue_type"],
                "Column": issue.get("column") or "Dataset-level",
                "Severity": issue.get(
                    "severity",
                    "medium",
                ).upper(),
                "Affected": issue.get("count", 0),
            }
        )

    issue_df = pd.DataFrame(issue_rows)

    left, right = st.columns([1.15, 0.85])

    with left:
        st.subheader("Detected Issues")

        st.dataframe(
            issue_df,
            use_container_width=True,
            hide_index=True,
        )

    with right:
        st.subheader("Issue Distribution")

        issue_counts = (
            issue_df.groupby("Issue", as_index=False)
            ["Affected"]
            .sum()
        )

        fig = px.bar(
            issue_counts,
            x="Affected",
            y="Issue",
            orientation="h",
            title="Affected Values by Issue Type",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    # -----------------------------------------------------
    # Agent reasoning
    # -----------------------------------------------------

    st.header("3. Agent Reasoning")

    st.info(state.reasoning_summary)

    with st.expander(
        "View Proposed Remediation Plan",
        expanded=True,
    ):
        for action in state.remediation_plan:
            st.markdown(
                f"**{action['action_id']} — "
                f"{action['action']}**"
            )

            st.write(
                f"Column: "
                f"`{action.get('column') or 'Dataset-level'}`"
            )

            st.write(
                f"Risk: "
                f"**{action.get('risk', 'medium').upper()}**"
            )

            st.write(action["description"])

            st.divider()


    # -----------------------------------------------------
    # Human approval
    # -----------------------------------------------------

    st.header("4. Human Approval")

    st.warning(
        "DataFix will execute only actions that you explicitly approve."
    )

    approval_items = []

    for action in state.remediation_plan:
        decision = st.radio(
            (
                f"{action['action_id']} — "
                f"{action['action']} "
                f"({action.get('column') or 'Dataset-level'})"
            ),
            options=[
                "pending",
                "approved",
                "rejected",
            ],
            horizontal=True,
            key=f"approval_{action['action_id']}",
        )

        approval_items.append(
            ActionApproval(
                action_id=action["action_id"],
                decision=decision,
            )
        )


    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    if st.button(
        "Run Approved Remediation",
        type="primary",
        use_container_width=True,
    ):
        approval_request = ApprovalRequest(
            approvals=approval_items
        )

        execution_state = apply_approval_state(
            state,
            approval_request,
        )

        approved_count = sum(
            action["status"] == "approved"
            for action in execution_state.approved_plan
        )

        if approved_count == 0:
            st.warning(
                "Approve at least one remediation action "
                "before execution."
            )
        else:
            execution_state = execute_state(
                execution_state
            )

            execution_state = validate_state(
                execution_state
            )

            st.session_state.executed_state = (
                execution_state
            )

            st.success(
                f"Executed {approved_count} approved "
                f"remediation action(s)."
            )


    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    if st.session_state.executed_state is not None:
        result_state = (
            st.session_state.executed_state
        )

        st.header("5. Remediation Results")

        before_score = result_state.quality_score[
            "score"
        ]

        after_score = result_state.final_score[
            "score"
        ]

        improvement = after_score - before_score

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Before",
                f"{before_score}/100",
            )

        with col2:
            st.metric(
                "After",
                f"{after_score}/100",
            )

        with col3:
            st.metric(
                "Improvement",
                f"+{improvement}",
            )

        with col4:
            st.metric(
                "Validated Actions",
                result_state.validation[
                    "resolved_approved_actions"
                ],
            )

        comparison_df = pd.DataFrame(
            {
                "Stage": [
                    "Before Remediation",
                    "After Remediation",
                ],
                "Quality Score": [
                    before_score,
                    after_score,
                ],
            }
        )

        fig = px.bar(
            comparison_df,
            x="Stage",
            y="Quality Score",
            range_y=[0, 100],
            title="Data Quality Improvement",
            text="Quality Score",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

        unresolved = result_state.validation[
            "remaining_approved_actions"
        ]

        if unresolved == 0:
            st.success(
                "All approved remediation actions were "
                "successfully validated."
            )
        else:
            st.warning(
                f"{unresolved} approved action(s) require "
                f"additional review."
            )


        # -------------------------------------------------
        # Cleaned data
        # -------------------------------------------------

        st.header("6. Cleaned Dataset")

        st.dataframe(
            result_state.cleaned_df,
            use_container_width=True,
        )


        # -------------------------------------------------
        # Adaptive insights
        # -------------------------------------------------

        st.header("7. Data Insights Dashboard")

        show_dataset_insights(
            result_state.cleaned_df,
            "Explore the Cleaned Data",
        )


        # -------------------------------------------------
        # Audit
        # -------------------------------------------------

        st.header("8. Audit Trail")

        with st.expander(
            "View Agent Execution Log",
            expanded=False,
        ):
            for entry in result_state.audit_log:
                st.markdown(
                    f"**{entry.action_id} — "
                    f"{entry.action}**"
                )

                st.write(
                    f"Status: **{entry.status.upper()}**"
                )

                st.write(entry.message)

                st.divider()


        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        st.header("9. Export")

        cleaned_csv = (
            result_state.cleaned_df
            .to_csv(index=False)
            .encode("utf-8")
        )

        cleaned_filename = (
            uploaded_file.name.rsplit(".", 1)[0]
            + "_cleaned.csv"
        )

        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_csv,
            file_name=cleaned_filename,
            mime="text/csv",
            use_container_width=True,
            on_click="ignore",
        )

else:
    st.success(
        "No supported data-quality issues were detected."
    )

    show_dataset_insights(
        df,
        "Dataset Insights",
    )