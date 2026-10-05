# DataFix Agent

> **Agentic Data Quality & Intelligence Platform** — detect, reason about, remediate, validate, explore, and audit data-quality problems while keeping humans in control.

## Overview

DataFix Agent is a human-in-the-loop Agentic AI application for transforming messy CSV data into validated, analysis-ready datasets.

Rather than immediately modifying uploaded data, DataFix follows a controlled agentic workflow:

```text
Upload
  ↓
Profile
  ↓
Detect
  ↓
Score
  ↓
Reason
  ↓
Plan
  ↓
Human Approval
  ↓
Execute Approved Actions
  ↓
Independent Validation
  ↓
Explore Adaptive Insights
  ↓
Audit
  ↓
Export
```

The system profiles the uploaded dataset, detects quality problems, calculates a quality score, reasons over the findings, generates a structured remediation plan, and pauses for explicit human approval.

Only approved actions are executed.

After remediation, DataFix independently validates the result, recalculates the quality score, provides before/after metrics, generates adaptive visual insights from the cleaned dataset, records every execution in an audit trail, and allows the validated CSV to be downloaded.

---

## Why DataFix Agent?

Real-world datasets frequently contain:

- missing values
- exact duplicate rows
- inconsistent categorical values
- leading or trailing whitespace
- malformed dates
- statistical outliers
- inconsistent representations of the same information

Traditional automated cleaning pipelines can be risky because they may modify data without clearly explaining:

- what was detected
- what will be changed
- why the change is proposed
- whether a human approved it
- whether the remediation actually worked

DataFix addresses this by combining:

- deterministic data profiling
- automated quality-issue detection
- quality scoring
- structured remediation planning
- AI-assisted reasoning
- deterministic fallback reasoning
- explicit human approval gates
- controlled tool execution
- independent post-remediation validation
- before/after quality measurement
- adaptive exploratory data insights
- transparent audit logging
- cleaned-data export

The objective is not simply to automate data cleaning.

The objective is to make automated remediation **controlled, measurable, explainable, and auditable**.

---

## Agentic Architecture

DataFix separates analysis, reasoning, decision-making, execution, and validation rather than treating data cleaning as a single transformation step.

### 1. Dataset Profiling

The uploaded CSV is profiled to understand:

- number of rows
- number of columns
- total cells
- missing cells
- missing percentage
- duplicate rows
- column-level characteristics

Profiling does not modify the original dataset.

### 2. Quality Issue Detection

DataFix runs deterministic quality checks against the uploaded dataset and creates structured issue records.

### 3. Quality Scoring

Detected issues are converted into an overall quality score and grade.

This gives users an immediate measure of dataset health before remediation.

### 4. Reasoning Layer

The reasoning layer examines grounded information from:

- dataset profiling
- detected issues
- severity levels
- proposed remediation actions

When OpenAI API access is available, DataFix can use an LLM to summarize remediation priorities.

If the LLM service is unavailable, DataFix uses deterministic fallback reasoning so the core workflow remains operational.

### 5. Remediation Planning

The planner converts detected issues into structured remediation actions.

Each action contains information such as:

- Action ID
- issue type
- target column
- proposed operation
- risk level
- description
- approval requirement
- execution status

### 6. Human Approval

Every proposed remediation action begins in a pending state.

Users can independently choose:

- `approved`
- `rejected`

No proposed modification is executed unless it has been explicitly approved.

### 7. Controlled Tool Execution

Only approved actions are passed to the deterministic remediation tools.

The LLM does **not** directly modify the dataset.

### 8. Independent Validation

After remediation, DataFix runs the quality checks again against the resulting dataset.

The validator determines whether approved actions were successfully resolved and calculates the final quality score.

### 9. Adaptive Data Insights

Once remediation has been validated, users can explore the cleaned dataset through an adaptive dashboard.

The available visualizations automatically respond to the structure and data types of the uploaded dataset.

### 10. Audit and Export

Every attempted remediation is recorded in the execution log.

Users can inspect the final cleaned dataset and download it as a CSV file.

---

## Supported Data-Quality Checks

DataFix currently detects the following issue types:

### Missing Values

Identifies columns containing missing data.

### Exact Duplicate Rows

Detects completely duplicated records.

### Leading/Trailing Whitespace

Detects unnecessary whitespace in textual values.

### Category Inconsistencies

Identifies inconsistent representations of categorical values.

### Numeric IQR Outliers

Uses the Interquartile Range (IQR) approach to identify potential numeric outliers.

### Invalid Dates

Detects malformed values in columns whose names indicate date, time, or timestamp information.

---

## Remediation Actions

Depending on the detected issue, DataFix can propose:

- median imputation for numeric missing values
- mode imputation for categorical missing values
- exact duplicate removal
- whitespace trimming
- category standardization
- numeric outlier flag generation
- invalid-date coercion for review

### Non-Destructive Outlier Handling

Potential outliers are **not automatically deleted**.

Instead, DataFix adds an outlier flag column so the observation remains available for human review and downstream analysis.

This avoids silently discarding potentially meaningful data.

---

## Human-in-the-Loop Safety

DataFix deliberately separates:

**Planning → Approval → Execution**

Users review every proposed action before execution.

Only actions with an `approved` status are executable.

Rejected or unapproved actions do not modify the dataset.

This creates a code-enforced human approval boundary rather than relying only on an instruction to the AI model.

### Core Guardrails

- Human approval is required before remediation.
- The original dataset is not modified during analysis.
- Only approved actions are executable.
- Outliers are preserved and flagged rather than silently deleted.
- Dataset changes are performed by deterministic tools.
- Remediation results are independently validated.
- Every execution is auditable.

---

## Independent Validation

Execution alone does not mean remediation succeeded.

After approved fixes run, DataFix independently analyzes the resulting dataset again.

The validation stage reports:

- approved actions resolved
- approved actions still unresolved
- remaining quality issues
- final quality score
- quality-score improvement

This provides measurable evidence of whether remediation actually improved the dataset.

For non-destructive outlier handling, validation verifies that the appropriate outlier-flag column was created while preserving the original observation.

---

## Data Quality Analysis

Before remediation, the Streamlit interface presents key quality indicators including:

- overall quality score
- quality grade
- detected issue groups
- missing-cell count
- duplicate-row count
- visual quality progress
- detected-issue table
- issue-distribution visualization

This gives users a concise overview before they decide whether to approve any changes.

---

## Agent Reasoning

DataFix provides a reasoning summary based on the detected quality problems and proposed remediation plan.

The reasoning layer helps communicate:

- the number of detected issue groups
- important remediation priorities
- actions requiring caution
- the requirement for human approval

The reasoning layer is grounded in the profiling, issue, and remediation-plan information generated by DataFix.

It does not independently modify the dataset.

---

## Adaptive Data Insights Dashboard

After approved remediation and independent validation, DataFix provides an adaptive exploratory dashboard for the **cleaned dataset**.

The dashboard adjusts according to the columns and data types available in the uploaded CSV.

It contains five analysis views.

### 1. Overview

Provides:

- dataset row count
- dataset column count
- numeric-feature count
- remaining missing-cell count
- duplicate-row status
- column data types
- non-null counts
- missing counts
- unique-value counts

This provides an immediate structural summary of the cleaned dataset.

### 2. Missing Data

Shows remaining missingness after remediation.

This allows users to identify unresolved completeness issues and understand whether approved remediation removed the expected missing values.

### 3. Distributions

For numeric features, users can select a column and explore:

- Histogram
- Box Plot

The dashboard also provides descriptive statistics including:

- Mean
- Median
- Minimum
- Maximum

This makes it easier to understand numeric spread and inspect potential outliers after remediation.

### 4. Categories

For categorical features, users can select a column and explore frequency distributions.

Depending on the data, visualization options include:

- Bar Chart
- Pie Chart

This is useful for understanding dominant categories and visually inspecting the effect of category standardization.

### 5. Relationships

When multiple numeric features are available, DataFix supports:

- Scatter Plot
- Correlation Heatmap

The scatter plot allows users to explore relationships between selected numeric variables.

The correlation heatmap provides a compact view of statistical relationships across numeric features.

> Correlation describes statistical association and does not establish causation.

---

## Before/After Quality Comparison

After remediation, DataFix presents measurable before/after results including:

- quality score before remediation
- quality score after remediation
- score improvement
- number of validated actions
- missing cells before and after
- duplicate rows before and after
- dataset rows before and after

A visual before/after quality chart makes the impact of remediation easy to interpret.

---

## Audit Trail

Every remediation action is recorded in a structured execution log.

The interface presents the audit trail as a compact table containing:

| Field | Description |
|---|---|
| Action ID | Unique remediation action identifier |
| Action | Tool/action executed |
| Status | Execution status |
| Execution Result | Description of what happened |

Execution states can include:

- executed
- skipped
- failed

The execution result explains what operation was performed or why an action was not executed.

This makes DataFix inspectable rather than a black-box transformation system.

---

## Export

After reviewing:

- validation results
- cleaned data
- adaptive insights
- audit trail

the user can download the cleaned dataset directly as a CSV file.

---

# Verified Demo Results

DataFix Agent has been tested end-to-end against two datasets with different sizes, schemas, and quality patterns.

## Demo 1 — `messy_customers.csv`

This compact dataset contains intentionally introduced data-quality problems and is useful for quickly demonstrating the complete agent workflow.

### Initial Analysis

- Quality score: **45/100 — Poor**
- Detected issue groups: **7**
- Missing cells: **3**
- Exact duplicate rows: **1**

The dataset includes examples of:

- missing numeric values
- duplicate records
- whitespace
- categorical inconsistency
- numeric outlier
- invalid date

### Approved Remediation

All seven proposed remediation actions were approved during the full end-to-end validation.

DataFix performed:

- missing-value imputation
- duplicate removal
- whitespace trimming
- category standardization
- numeric outlier flagging
- invalid-date coercion

### Validated Result

- Approved actions executed: **7**
- Approved actions validated: **7**
- Unresolved approved actions: **0**
- Initial quality score: **45/100**
- Final quality score: **86/100**
- Quality improvement: **+41**
- Duplicate rows after remediation: **0**

The numeric outlier was preserved and explicitly flagged.

The invalid date was safely coerced to a missing value for review, which explains why the final score does not necessarily reach 100.

---

## Demo 2 — `Messy_Employment_India_Dataset.csv`

A second, substantially larger dataset was used to test whether DataFix generalizes beyond the original demonstration dataset.

### Initial Analysis

- Dataset rows: **2,000**
- Detected issue groups: **13**
- Missing cells: **2,801**
- Duplicate rows: **0**
- Initial quality score: **0/100 — Poor**

The agent dynamically detected quality problems across the unfamiliar employment dataset, including:

- missing values across multiple columns
- whitespace inconsistencies
- categorical inconsistencies

For example, the workflow identified a large missing-value problem in `Years of Experience` and generated a corresponding remediation action without relying on dataset-specific hard-coding.

### Remediation and Validation

All 13 proposed remediation actions were approved for the generalization test.

The resulting validation showed:

- Approved actions executed: **13**
- Approved actions validated: **13**
- Missing cells after remediation: **0**
- Duplicate rows after remediation: **0**
- Dataset rows after remediation: **2,000**
- Final quality score: **100/100**
- Quality improvement: **+100**

The audit trail confirmed dataset-specific operations including missing-value imputation, whitespace trimming, and categorical standardization.

The row count remained at 2,000 because the dataset contained no exact duplicate rows requiring removal.

This second test provides evidence that DataFix generates its analysis and remediation plan dynamically from the uploaded dataset rather than following a fixed demonstration script.

> **Note:** Quality scores are dataset-dependent and are calculated against the quality rules currently implemented by DataFix. A 100/100 score means no remaining issues were detected by the supported checks after approved remediation; it does not imply universal semantic or domain-level data correctness. Category remediation uses deterministic normalization and conservative semantic aliases for recognized equivalents, while broader semantic canonicalization remains a potential future extension.

---

## Sample Datasets

Two datasets are included for demonstration and validation.

### Quick Demo Dataset

```text
sample_data/messy_customers.csv
```

Recommended when demonstrating the complete workflow quickly.

It contains several deliberately introduced quality problems and produces a compact remediation plan that is easy to explain during a presentation.

### Extended Validation Dataset

```text
sample_data/Messy_Employment_India_Dataset.csv
```

Recommended for demonstrating that the workflow can operate on a larger dataset with a different schema and significantly more missing and inconsistent data.

---

## LLM Reasoning and Deterministic Fallback

DataFix includes an optional OpenAI-powered reasoning layer.

When OpenAI API access is available, the reasoning component can summarize detected issues and remediation priorities using grounded information generated by the DataFix pipeline.

The LLM receives structured information about:

- dataset profiling
- detected quality issues
- severity
- proposed remediation actions

The LLM does **not** directly modify the uploaded dataset.

All dataset modifications are performed through deterministic remediation tools after explicit human approval.

### Resilient Fallback

If:

- an API key is unavailable
- API quota is unavailable
- the LLM service cannot be reached
- the LLM request otherwise fails

DataFix can use deterministic fallback reasoning.

This means the core application remains functional even when external LLM inference is unavailable.

---

## Tech Stack

- **Python 3.12**
- **Streamlit** — interactive application interface
- **Pandas** — data manipulation and profiling
- **NumPy** — numerical operations
- **Plotly** — interactive visualizations
- **Pydantic** — structured data models
- **OpenAI API** — optional grounded reasoning layer
- **python-dotenv** — local environment configuration
- **pytest** — automated testing
- **Git / GitHub** — version control and source hosting

---

## Project Structure

```text
DataFix-Agent/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── datafix/
│   ├── __init__.py
│   ├── orchestrator.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py
│   │   ├── approval.py
│   │   ├── validator.py
│   │   ├── reasoner.py
│   │   ├── fallback_reasoner.py
│   │   └── workflow.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── agent_state.py
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── profiling.py
│   │   ├── quality.py
│   │   └── fixer.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── scoring.py
│
├── sample_data/
│   ├── messy_customers.csv
│   └── Messy_Employment_India_Dataset.csv
│
└── tests/
    └── test_datafix_core.py
```

---

## Local Setup

Clone the repository:

```powershell
git clone https://github.com/3sha08/DataFix-Agent.git
cd DataFix-Agent
```

Create a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

---

## OpenAI Configuration

The OpenAI reasoning path is optional.

Copy `.env.example` to `.env` and provide an API key if you want to enable OpenAI-powered reasoning:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit `.env` or API credentials to source control.

The deterministic data-quality pipeline and fallback reasoning remain available independently of successful LLM access.

---

## Run the Application

Start Streamlit:

```powershell
streamlit run app.py
```

Then open the Streamlit interface and upload a CSV dataset.

For a quick demonstration, use:

```text
sample_data/messy_customers.csv
```

For the larger validation scenario, use:

```text
sample_data/Messy_Employment_India_Dataset.csv
```

---

## How to Use DataFix Agent

### Step 1 — Upload

Upload the CSV dataset you want to inspect and clean.

### Step 2 — Review Quality Analysis

Inspect:

- quality score
- issue groups
- missing cells
- duplicate rows
- detected issues
- issue distribution

### Step 3 — Review Agent Reasoning

Read the reasoning summary and proposed remediation priorities.

### Step 4 — Review the Remediation Plan

Inspect each proposed action, target column, risk level, and description.

### Step 5 — Approve or Reject Actions

Explicitly approve or reject each proposed remediation.

### Step 6 — Run Approved Remediation

DataFix executes only approved actions.

### Step 7 — Review Independent Validation

Compare the before/after quality scores and verify whether the approved actions were resolved.

### Step 8 — Explore the Cleaned Dataset

Use the adaptive dashboard to inspect:

- dataset overview
- missing data
- numeric distributions
- categorical distributions
- numeric relationships

### Step 9 — Review the Audit Trail

Inspect exactly which actions executed and what each action changed.

### Step 10 — Export

Download the validated cleaned CSV.

---

## Run Tests

Run:

```powershell
python -m pytest -q
```

Current verified test status:

```text
6 passed
```

The automated tests cover core quality detection, remediation, approval, workflow, and validation behavior.

---

## Responsible Agent Design

DataFix follows several design principles intended to make agentic remediation safer and more transparent.

### Detect Before Modifying

The dataset is analyzed before any transformation is allowed.

### Reason Before Acting

Detected problems are converted into an explicit remediation plan rather than immediately executed.

### Human Authority Over Consequential Changes

The user determines which proposed actions may execute.

### Deterministic Execution

Dataset modifications are performed by explicit tools rather than unconstrained LLM-generated transformations.

### Validate After Acting

DataFix independently checks the resulting dataset after remediation.

### Preserve Potentially Important Information

Numeric outliers are flagged rather than automatically deleted.

### Maintain an Audit Trail

Every attempted remediation produces an execution record.

---

## Hackathon

Built during **WCC Launchpad 30** for the **Agentic AI Track**.

DataFix Agent demonstrates an agentic architecture centered on:

- autonomous dataset profiling
- autonomous issue detection
- grounded reasoning
- remediation planning
- tool selection and execution
- explicit human approval
- independent verification
- adaptive post-remediation analysis
- auditable outcomes

The project is designed to demonstrate that useful AI agents do not need unrestricted autonomy.

DataFix combines autonomous analysis with explicit human authority over consequential data modifications.

---

## Future Scope

Potential extensions include:

- multi-file ingestion
- Excel ingestion
- database connectors
- configurable enterprise data-quality policies
- schema validation
- domain-specific business-rule validation
- semantic anomaly detection
- advanced anomaly models
- richer agent tool selection
- configurable remediation strategies
- persistent remediation history
- downloadable data-quality reports
- automated report generation
- enterprise data-source integrations
- authentication and role-based access control
- production observability
- persistent audit storage
- scheduled quality monitoring
- dataset versioning

---

## Responsible Use

DataFix currently focuses on common structural data-quality problems.

Automated remediation should still be reviewed carefully when datasets are used for consequential domains such as:

- healthcare
- finance
- employment
- insurance
- public-sector decisions

DataFix's human approval and audit mechanisms are intended to support review rather than eliminate human responsibility.

---

## Core Principles

DataFix Agent follows three core principles:

1. **Detect and reason before modifying**
2. **Require human approval before consequential changes**
3. **Validate and audit every executed remediation**

The goal is not merely to produce cleaner data.

The goal is to build an **agentic data-quality workflow that is useful, controlled, measurable, explainable, and auditable**.