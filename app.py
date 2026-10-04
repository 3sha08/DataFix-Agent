import streamlit as st
import pandas as pd
from datafix.models.agent_state import create_initial_state
from datafix.agents.workflow import (
    analyze_state,
    apply_approval_state,
    execute_state,
    validate_state,
)
from datafix.models.schemas import ApprovalRequest, ActionApproval

if "executed_state" not in st.session_state:
    st.session_state.executed_state = None

st.set_page_config(
    page_title="DataFix Agent",
    page_icon="🧹",
    layout="wide",
)


st.title("DataFix Agent")

st.subheader(
    "Autonomous Data Quality & Remediation Agent"
)

st.write(
    "Upload a CSV dataset and DataFix will detect quality issues, "
    "propose remediation actions, keep you in control of changes, "
    "validate the results, and generate a cleaned dataset."
)

st.info(
    "Human-in-the-loop: DataFix will never modify your dataset "
    "until you approve the proposed remediation actions."
)

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"],
    help="Choose a CSV dataset for DataFix to analyze.",
)

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    df = pd.read_csv(uploaded_file)

    st.write(
        f"Dataset loaded successfully: "
        f"{df.shape[0]:,} rows × {df.shape[1]:,} columns"
    )

    st.subheader("Dataset Preview")
    st.dataframe(
    df,
    use_container_width=True,)

    state = create_initial_state(df)
    state = analyze_state(state)
    st.subheader("Data Quality Analysis")
    st.write(
    f"DataFix detected {len(state.issues)} quality issue groups.")
    st.write(
    f"Quality Score: {state.quality_score['score']}/100 "
    f"— {state.quality_score['grade']}")
    if state.issues:
        st.subheader("Detected Issues")

        for issue in state.issues:
            column = issue.get("column") or "Dataset-level"
            severity = issue.get("severity", "medium").upper()
            count = issue.get("count", 0)

            st.write(
                f"**{issue['issue_type']}** | "
                f"Column: `{column}` | "
                f"Severity: **{severity}** | "
                f"Affected: **{count}**"
            )

        st.subheader("Proposed Remediation Plan")

        for action in state.remediation_plan:
            st.write(
                f"**{action['action_id']} — {action['action']}**  \n"
                f"Column: `{action.get('column') or 'Dataset-level'}`  \n"
                f"Risk: **{action.get('risk', 'medium').upper()}**  \n"
                f"{action['description']}"
            )

            st.divider()
        st.subheader("Human Approval")

        approval_items = []

        for action in state.remediation_plan:
            decision = st.radio(
                f"{action['action_id']} — {action['action']}",
                options=["pending", "approved", "rejected"],
                horizontal=True,
                key=f"approval_{action['action_id']}",
            )

            approval_items.append(
                ActionApproval(
                    action_id=action["action_id"],
                    decision=decision,
                )
            )

        if st.session_state.executed_state is not None:
            state = st.session_state.executed_state
        
        if st.button(
            "Execute Approved Fixes",
            type="primary",
            use_container_width=True,
        ):
            approval_request = ApprovalRequest(
                approvals=approval_items
            )

            state = apply_approval_state(
                state,
                approval_request,
            )

            approved_count = sum(
                action["status"] == "approved"
                for action in state.approved_plan
            )

            if approved_count == 0:
                st.warning(
                    "No remediation actions were approved. "
                    "Approve at least one action before execution."
                )
            else:
                state = execute_state(state)
                state = validate_state(state)
                st.session_state.executed_state = state

                st.success(
                    f"Executed {approved_count} approved "
                    f"remediation action(s)."
                )

                if st.session_state.executed_state is not None:
                    state = st.session_state.executed_state
            
            st.subheader("Remediation Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Before Quality Score",
                    f"{state.quality_score['score']}/100",
                )

            with col2:
                st.metric(
                    "After Quality Score",
                    f"{state.final_score['score']}/100",
                )

            with col3:
                improvement = (
                    state.final_score["score"]
                    - state.quality_score["score"]
                )

                st.metric(
                    "Score Improvement",
                    f"+{improvement}",
                )
            st.subheader("Validation")

            st.write(
                f"Resolved approved actions: "
                f"**{state.validation['resolved_approved_actions']}**"
            )

            st.write(
                f"Approved actions still unresolved: "
                f"**{state.validation['remaining_approved_actions']}**"
            )
            
            st.subheader("Cleaned Dataset Preview")

            st.dataframe(
                state.cleaned_df,
                use_container_width=True,
            )
            
            st.subheader("Audit Trail")

            for entry in state.audit_log:
                st.write(
                    f"**{entry.action_id} — {entry.action}** | "
                    f"Status: **{entry.status.upper()}** | "
                    f"{entry.message}"
                )
            st.subheader("Download Cleaned Dataset")

            cleaned_csv = state.cleaned_df.to_csv(
                index=False
            ).encode("utf-8")

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
                on_click="ignore"
            )

    else:
        st.success(
            "No supported data-quality issues were detected."
        )