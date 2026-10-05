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

        .hero-eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.72;
        margin-bottom: 0.7rem;
        }

        .hero-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1.3rem;
        }

        .hero-badges span {
        padding: 0.42rem 0.8rem;
        border-radius: 999px;
        border: 1px solid rgba(120, 120, 120, 0.28);
        font-size: 0.86rem;
        }

        .workflow-box {
            padding: 1rem 1.2rem;
            border-radius: 14px;
            border: 1px solid rgba(120, 120, 120, 0.18);
            text-align: center;
            font-weight: 600;
            margin-bottom: 1.5rem;
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
    """Render adaptive descriptive visualizations for the dataset."""

    st.subheader(title)

    st.caption(
        "Explore the analysis-ready dataset with automatically adapted "
        "visualizations based on available column types."
    )

    numeric_columns = data.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = data.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    analysis_numeric_columns = [
        column
        for column in numeric_columns
        if not column.endswith("_outlier_flag")
    ]

    missing_cells = int(data.isna().sum().sum())
    duplicate_rows = int(data.duplicated().sum())

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Rows", f"{len(data):,}")

    with metric2:
        st.metric("Columns", f"{len(data.columns):,}")

    with metric3:
        st.metric(
            "Numeric Features",
            len(analysis_numeric_columns),
        )

    with metric4:
        st.metric(
            "Missing Cells",
            f"{missing_cells:,}",
        )

    if duplicate_rows == 0:
        st.success(
            "✓ No exact duplicate rows detected in the current dataset."
        )
    else:
        st.warning(
            f"{duplicate_rows} exact duplicate row(s) remain."
        )

    (
        overview_tab,
        missing_tab,
        numeric_tab,
        category_tab,
        relationship_tab,
    ) = st.tabs(
        [
            "Overview",
            "Missing Data",
            "Distributions",
            "Categories",
            "Relationships",
        ]
    )

    with overview_tab:
        st.markdown("#### Dataset Overview")

        overview_rows = []

        for column in data.columns:
            overview_rows.append(
                {
                    "Column": column,
                    "Data Type": str(data[column].dtype),
                    "Non-Null": int(data[column].notna().sum()),
                    "Missing": int(data[column].isna().sum()),
                    "Unique Values": int(
                        data[column].nunique(dropna=True)
                    ),
                }
            )

        st.dataframe(
            pd.DataFrame(overview_rows),
            use_container_width=True,
            hide_index=True,
        )

    with missing_tab:
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
                text="Missing Values",
            )
            fig.update_layout(height=430)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            total_cells = len(data) * len(data.columns)
            missing_percentage = (
                (missing_cells / total_cells) * 100
                if total_cells
                else 0
            )

            st.caption(
                f"{missing_cells:,} of {total_cells:,} cells are "
                f"missing ({missing_percentage:.2f}%)."
            )

    with numeric_tab:
        if not analysis_numeric_columns:
            st.info(
                "No numeric columns are available for distribution analysis."
            )
        else:
            selected_numeric = st.selectbox(
                "Choose a numeric feature",
                analysis_numeric_columns,
                key=f"{title}_numeric",
            )

            chart_type = st.radio(
                "Visualization",
                ["Histogram", "Box Plot"],
                horizontal=True,
                key=f"{title}_numeric_chart",
            )

            if chart_type == "Histogram":
                fig = px.histogram(
                    data,
                    x=selected_numeric,
                    title=f"Distribution of {selected_numeric}",
                )
            else:
                fig = px.box(
                    data,
                    y=selected_numeric,
                    points="outliers",
                    title=f"Box Plot of {selected_numeric}",
                )

            fig.update_layout(height=450)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

            numeric_series = data[selected_numeric].dropna()

            if not numeric_series.empty:
                stat1, stat2, stat3, stat4 = st.columns(4)

                with stat1:
                    st.metric(
                        "Mean",
                        f"{numeric_series.mean():,.2f}",
                    )

                with stat2:
                    st.metric(
                        "Median",
                        f"{numeric_series.median():,.2f}",
                    )

                with stat3:
                    st.metric(
                        "Minimum",
                        f"{numeric_series.min():,.2f}",
                    )

                with stat4:
                    st.metric(
                        "Maximum",
                        f"{numeric_series.max():,.2f}",
                    )

    with category_tab:
        usable_categories = [
            column
            for column in categorical_columns
            if 1 < data[column].nunique(dropna=True) <= 30
        ]

        if not usable_categories:
            st.info(
                "No low-cardinality categorical columns are suitable "
                "for category visualization."
            )
        else:
            selected_category = st.selectbox(
                "Choose a categorical feature",
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

            category_chart_options = ["Bar Chart"]

            if len(category_counts) <= 8:
                category_chart_options.append("Pie Chart")

            category_chart = st.radio(
                "Visualization",
                category_chart_options,
                horizontal=True,
                key=f"{title}_category_chart",
            )

            if category_chart == "Pie Chart":
                fig = px.pie(
                    category_counts,
                    names=selected_category,
                    values="Count",
                    hole=0.35,
                    title=f"{selected_category} Composition",
                )
            else:
                fig = px.bar(
                    category_counts,
                    x=selected_category,
                    y="Count",
                    title=f"{selected_category} Distribution",
                    text="Count",
                )

            fig.update_layout(height=450)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    with relationship_tab:
        if len(analysis_numeric_columns) < 2:
            st.info(
                "At least two numeric features are required "
                "for relationship analysis."
            )
        else:
            relationship_type = st.radio(
                "Analysis",
                ["Scatter Plot", "Correlation Heatmap"],
                horizontal=True,
                key=f"{title}_relationship_type",
            )

            if relationship_type == "Scatter Plot":
                rel_col1, rel_col2 = st.columns(2)

                with rel_col1:
                    x_column = st.selectbox(
                        "X-axis feature",
                        analysis_numeric_columns,
                        index=0,
                        key=f"{title}_scatter_x",
                    )

                y_options = [
                    column
                    for column in analysis_numeric_columns
                    if column != x_column
                ]

                with rel_col2:
                    y_column = st.selectbox(
                        "Y-axis feature",
                        y_options,
                        index=0,
                        key=f"{title}_scatter_y",
                    )

                fig = px.scatter(
                    data,
                    x=x_column,
                    y=y_column,
                    title=f"{y_column} vs {x_column}",
                    hover_data=categorical_columns[:2],
                )

                fig.update_layout(height=480)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
            else:
                correlation = (
                    data[analysis_numeric_columns]
                    .corr(numeric_only=True)
                )

                fig = px.imshow(
                    correlation,
                    text_auto=".2f",
                    aspect="auto",
                    title="Numeric Feature Correlation Heatmap",
                )

                fig.update_layout(height=500)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

                st.caption(
                    "Correlation describes statistical association "
                    "and does not establish causation."
                )


# ---------------------------------------------------------
# Hero
# ---------------------------------------------------------

st.markdown(
    """
<div class="hero">
<div class="hero-eyebrow">AGENTIC DATA QUALITY &amp; INTELLIGENCE PLATFORM</div>
<h1>🧹 DataFix Agent</h1>
<p>Transform messy CSV data into validated, analysis-ready datasets with autonomous issue detection, AI-assisted reasoning, human-controlled remediation, independent verification, and adaptive visual insights.</p>
<div class="hero-badges">
<span>🤖 Agentic Analysis</span>
<span>👤 Human-in-the-Loop</span>
<span>✓ Independent Validation</span>
<span>📊 Adaptive Insights</span>
</div>
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="workflow-box">
        📤 Upload
        &nbsp; → &nbsp;
        🔍 Detect
        &nbsp; → &nbsp;
        🧠 Reason
        &nbsp; → &nbsp;
        👤 Approve
        &nbsp; → &nbsp;
        🛠️ Fix
        &nbsp; → &nbsp;
        ✓ Validate
        &nbsp; → &nbsp;
        📊 Explore
        &nbsp; → &nbsp;
        ⬇️ Export
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.header("🧹 DataFix Agent")
    st.caption("Your guide to using the workspace")

    st.divider()

    st.markdown("### How to Use")

    st.markdown(
        """
**1. Upload your CSV**
Start with the dataset you want to inspect and clean.

**2. Review detected issues**
Check the quality score, detected problems, and the agent's proposed remediation plan.

**3. Make the decision**
Approve or reject each proposed action before anything is changed.

**4. Run remediation**
DataFix executes only your approved actions and independently validates the result.

**5. Explore & export**
Review the cleaned data, adaptive insights, quality improvement, and audit trail — then download the final CSV.
"""
    )

    st.divider()

    st.markdown("### What You'll Get")

    st.markdown(
        """
- Data quality assessment
- AI-assisted remediation plan
- Before vs. after validation
- Cleaned, analysis-ready dataset
- Adaptive visual insights
- Complete execution audit trail
"""
    )

    st.divider()

    st.markdown("### Your Data, Your Control")

    st.caption(
        "No remediation is executed without your approval. "
        "Outliers are preserved and flagged, and every executed "
        "action is independently validated and auditable."
    )

    st.divider()

    st.caption("WCC Launchpad 30 • Agentic AI Track")


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

quality_score_value = state.quality_score["score"]

st.progress(
    quality_score_value / 100,
    text=(
        f"Overall Data Quality: "
        f"{quality_score_value}/100 — "
        f"{state.quality_score['grade']}"
    ),
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
            issue_df.groupby("Issue", as_index=False)["Affected"]
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
                f"**{action['action_id']} — {action['action']}**"
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
        result_state = st.session_state.executed_state

        st.header("5. Remediation Results")

        before_score = result_state.quality_score["score"]
        after_score = result_state.final_score["score"]
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

        st.markdown("#### Data Quality Changes")

        before_missing = int(
            result_state.original_df.isna().sum().sum()
        )
        after_missing = int(
            result_state.cleaned_df.isna().sum().sum()
        )

        before_duplicates = int(
            result_state.original_df.duplicated().sum()
        )
        after_duplicates = int(
            result_state.cleaned_df.duplicated().sum()
        )

        before_rows = len(result_state.original_df)
        after_rows = len(result_state.cleaned_df)

        change1, change2, change3 = st.columns(3)

        with change1:
            st.metric(
                "Missing Cells",
                after_missing,
                delta=after_missing - before_missing,
                delta_color="inverse",
                help=f"Before remediation: {before_missing}",
            )

        with change2:
            st.metric(
                "Duplicate Rows",
                after_duplicates,
                delta=after_duplicates - before_duplicates,
                delta_color="inverse",
                help=f"Before remediation: {before_duplicates}",
            )

        with change3:
            st.metric(
                "Dataset Rows",
                after_rows,
                delta=after_rows - before_rows,
                delta_color="off",
                help=f"Before remediation: {before_rows}",
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
            expanded=False,):
            audit_rows = []
            for entry in result_state.audit_log:
                audit_rows.append(
            {
                "Action ID": entry.action_id,
                "Action": entry.action,
                "Status": entry.status.upper(),
                "Execution Result": entry.message,
            }

            )

            audit_df = pd.DataFrame(audit_rows)
            st.dataframe(
                audit_df,
                use_container_width=True,
                hide_index=True,
            )
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
