# DataFix Agent

> An autonomous data-quality agent that finds, plans, fixes, and verifies data problems - with humans in control.

## Overview

DataFix Agent is a human-in-the-loop Agentic AI application for detecting and remediating common data-quality problems in CSV datasets.

Instead of immediately modifying uploaded data, DataFix follows an auditable workflow:

**Upload -> Profile -> Detect -> Score -> Plan -> Approve -> Execute -> Validate -> Download**

The agent analyzes the dataset, proposes remediation actions, waits for explicit human approval, executes only approved actions, independently validates the results, and produces a cleaned CSV with a complete audit trail.

## Why DataFix Agent?

Real-world datasets frequently contain missing values, duplicates, inconsistent categories, malformed dates, whitespace problems, and statistical outliers.

Automated cleaning can be risky when systems modify data without explaining what changed.

DataFix addresses this by combining:

- deterministic data-quality detection
- structured remediation planning
- human approval gates
- controlled tool execution
- independent post-fix validation
- before/after quality scoring
- transparent audit logging
- LLM-assisted reasoning with deterministic fallback

## Agentic Workflow

```text
CSV Upload
    ↓
Dataset Profiling
    ↓
Quality Issue Detection
    ↓
Quality Scoring
    ↓
Remediation Planning
    ↓
Reasoning Layer
    ↓
Human Approval
    ↓
Approved Tool Execution
    ↓
Independent Validation
    ↓
Before/After Quality Score
    ↓
Audit Trail
    ↓
Cleaned CSV Download
```

The approval layer is code-gated: DataFix does not execute a proposed modification unless the corresponding action has been explicitly approved.

## Supported Data-Quality Checks

DataFix currently detects:

- Missing values
- Exact duplicate rows
- Leading/trailing whitespace
- Category inconsistencies
- Numeric IQR outliers
- Invalid dates in date/time/timestamp-related columns

Outliers are flagged for human review rather than automatically deleted.

## Remediation Actions

Depending on the detected issue, DataFix can propose:

- Median imputation for numeric missing values
- Mode imputation for categorical missing values
- Exact duplicate removal
- Whitespace trimming
- Category standardization
- Outlier flag generation
- Invalid-date coercion for review

Each action contains an action ID, target column, risk level, description, approval status, and execution result.

## Human-in-the-Loop Safety

DataFix separates **planning** from **execution**.

Users can independently mark each proposed remediation action as:

- `pending`
- `approved`
- `rejected`

Only actions with `approved` status are executable.

Unapproved actions are recorded as skipped in the audit trail.

## Independent Validation

After approved fixes execute, DataFix runs the quality detectors again against the cleaned dataset.

The validator reports:

- resolved approved actions
- approved actions still unresolved
- remaining quality issues
- final quality score

This provides measurable evidence that remediation actually improved the dataset.

## Example Result

Using the included `messy_customers.csv` sample:

```text
Initial quality score: 45/100 - Poor

Approved:
A001 - Impute missing age
A003 - Remove exact duplicates

Result:
2 approved actions executed
2 approved actions resolved
0 approved actions unresolved

Final quality score: 64/100 - Needs Attention
Score improvement: +19
```

Unapproved issues remain unchanged, demonstrating that the human approval boundary is enforced.

## LLM Reasoning

DataFix includes an OpenAI-powered reasoning layer that can summarize detected issues and remediation priorities using only grounded profiling, issue, and plan information.

If the LLM service is unavailable, the workflow can use a deterministic fallback reasoning layer so the core data-quality pipeline remains operational.

The LLM does not directly modify the dataset. Dataset changes are performed by deterministic tools after explicit human approval.

## Tech Stack

- Python 3.12
- Streamlit
- Pandas
- NumPy
- Pydantic
- OpenAI API
- Plotly
- python-dotenv
- pytest
- Git

## Project Structure

```text
DataFix-Agent/
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── datafix/
│   ├── orchestrator.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── approval.py
│   │   ├── workflow.py
│   │   ├── reasoner.py
│   │   ├── fallback_reasoner.py
│   │   └── validator.py
│   ├── models/
│   │   ├── schemas.py
│   │   └── agent_state.py
│   ├── tools/
│   │   ├── profiling.py
│   │   ├── quality.py
│   │   └── fixer.py
│   └── utils/
│       └── scoring.py
├── sample_data/
│   └── messy_customers.csv
└── tests/
    └── test_datafix_core.py
```

## Local Setup

Clone the repository and enter the project directory.

```bash
git clone <repository-url>
cd DataFix-Agent
```

Create and activate a virtual environment.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies.

```powershell
python -m pip install -r requirements.txt
```

## OpenAI Configuration

Copy `.env.example` to `.env` and provide your API key if you want to use the optional LLM reasoning path.

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Never commit `.env` or API credentials to source control.

The deterministic data-quality workflow remains usable independently of successful LLM availability.

## Run the Application

```powershell
streamlit run app.py
```

Then upload a CSV file through the Streamlit interface.

For a demonstration containing intentionally introduced quality problems, use:

```text
sample_data/messy_customers.csv
```

## Run Tests

```powershell
python -m pytest -q
```

Current verified test status:

```text
6 passed
```

## Auditability

For every planned action, DataFix records whether it was:

- executed
- skipped
- failed

The audit message also explains the operation performed or why execution did not occur.

This makes the remediation process inspectable rather than a black-box transformation.

## Hackathon

Built during **WCC Launchpad 30** for the **Agentic AI** track.

DataFix Agent demonstrates an agentic architecture centered on autonomous analysis and planning while retaining explicit human authority over consequential data modifications.

## Future Scope

Potential extensions include:

- multi-file and database ingestion
- configurable quality policies
- schema and business-rule validation
- semantic anomaly detection
- richer agent tool selection
- persistent remediation history
- downloadable quality reports
- enterprise data-source integrations
- production observability and authentication

## Responsible Design

DataFix follows three core principles:

1. **Detect before modifying**
2. **Require human approval before consequential changes**
3. **Validate and audit every executed remediation**

The objective is not merely to automate data cleaning, but to make automated remediation controlled, measurable, and explainable.