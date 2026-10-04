from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _issue(
    issue_type: str,
    column: str | None,
    severity: str,
    message: str,
    count: int,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a consistent issue record."""
    return {
        "issue_type": issue_type,
        "column": column,
        "severity": severity,
        "message": message,
        "count": count,
        "details": details or {},
    }


def detect_missing_values(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Detect columns containing missing values."""
    issues = []

    for column in df.columns:
        count = int(df[column].isna().sum())

        if count == 0:
            continue

        percentage = round((count / len(df)) * 100, 2) if len(df) else 0.0

        severity = (
            "critical"
            if percentage >= 50
            else "high"
            if percentage >= 25
            else "medium"
        )

        issues.append(
            _issue(
                issue_type="missing_values",
                column=str(column),
                severity=severity,
                message=f"{column} contains {count} missing value(s).",
                count=count,
                details={"missing_percentage": percentage},
            )
        )

    return issues


def detect_duplicates(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Detect exact duplicate rows."""
    count = int(df.duplicated().sum())

    if count == 0:
        return []

    return [
        _issue(
            issue_type="duplicate_rows",
            column=None,
            severity="high",
            message=f"Dataset contains {count} exact duplicate row(s).",
            count=count,
        )
    ]


def detect_whitespace(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Detect leading or trailing whitespace in text columns."""
    issues = []

    for column in df.select_dtypes(include=["object", "string"]).columns:
        series = df[column].dropna().astype(str)

        mask = series != series.str.strip()
        count = int(mask.sum())

        if count > 0:
            issues.append(
                _issue(
                    issue_type="whitespace",
                    column=str(column),
                    severity="low",
                    message=f"{column} contains {count} value(s) with surrounding whitespace.",
                    count=count,
                )
            )

    return issues


def detect_category_inconsistencies(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Detect text values that become identical after trimming whitespace
    and converting to lowercase.

    Example:
    Hyderabad / hyderabad / HYDERABAD
    """
    issues = []

    for column in df.select_dtypes(include=["object", "string"]).columns:
        series = df[column].dropna().astype(str)

        groups: dict[str, set[str]] = {}

        for value in series:
            normalized = value.strip().lower()
            groups.setdefault(normalized, set()).add(value)

        inconsistent_groups = {
            normalized: sorted(values)
            for normalized, values in groups.items()
            if len(values) > 1
        }

        if inconsistent_groups:
            count = sum(
                len(values) - 1
                for values in inconsistent_groups.values()
            )

            issues.append(
                _issue(
                    issue_type="category_inconsistency",
                    column=str(column),
                    severity="medium",
                    message=f"{column} contains inconsistent text representations.",
                    count=count,
                    details={"groups": inconsistent_groups},
                )
            )

    return issues


def detect_numeric_outliers(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Detect numeric outliers using the IQR rule."""
    issues = []

    for column in df.select_dtypes(include=np.number).columns:
        series = df[column].dropna()

        if len(series) < 4 or series.nunique() < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        mask = (series < lower_bound) | (series > upper_bound)
        outliers = series[mask]

        if not outliers.empty:
            issues.append(
                _issue(
                    issue_type="numeric_outlier",
                    column=str(column),
                    severity="medium",
                    message=f"{column} contains {len(outliers)} potential numeric outlier(s).",
                    count=int(len(outliers)),
                    details={
                        "lower_bound": round(float(lower_bound), 2),
                        "upper_bound": round(float(upper_bound), 2),
                        "values": [float(value) for value in outliers.tolist()],
                    },
                )
            )

    return issues


def detect_date_issues(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """
    Inspect columns whose names suggest dates and identify values
    that cannot be parsed as dates.
    """
    issues = []

    date_keywords = ("date", "time", "timestamp")

    for column in df.columns:
        column_name = str(column).lower()

        if not any(keyword in column_name for keyword in date_keywords):
            continue

        series = df[column].dropna()

        if series.empty:
            continue

        parsed = pd.to_datetime(series, errors="coerce")

        invalid_mask = parsed.isna()
        invalid_count = int(invalid_mask.sum())

        if invalid_count > 0:
            invalid_values = (
                series[invalid_mask]
                .astype(str)
                .drop_duplicates()
                .tolist()
            )

            issues.append(
                _issue(
                    issue_type="invalid_date",
                    column=str(column),
                    severity="high",
                    message=f"{column} contains {invalid_count} invalid date value(s).",
                    count=invalid_count,
                    details={"invalid_values": invalid_values},
                )
            )

    return issues


def detect_quality_issues(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Run all deterministic quality checks."""

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    issues = []

    issues.extend(detect_missing_values(df))
    issues.extend(detect_duplicates(df))
    issues.extend(detect_whitespace(df))
    issues.extend(detect_category_inconsistencies(df))
    issues.extend(detect_numeric_outliers(df))
    issues.extend(detect_date_issues(df))

    return issues