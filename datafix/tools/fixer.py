from __future__ import annotations

from typing import Any

import pandas as pd

from datafix.models.schemas import ExecutionResult


def _impute_missing(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, str]:
    """Impute missing values using median for numeric data or mode for text."""

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    result = df.copy()

    missing_before = int(result[column].isna().sum())

    if missing_before == 0:
        return result, f"No missing values found in '{column}'."

    if pd.api.types.is_numeric_dtype(result[column]):
        fill_value = result[column].median()

        if pd.isna(fill_value):
            raise ValueError(
                f"Cannot calculate median for '{column}'."
            )

        result[column] = result[column].fillna(fill_value)

        return (
            result,
            f"Imputed {missing_before} missing value(s) in "
            f"'{column}' using median={fill_value}.",
        )

    mode = result[column].mode(dropna=True)

    if mode.empty:
        raise ValueError(
            f"Cannot calculate mode for '{column}'."
        )

    fill_value = mode.iloc[0]
    result[column] = result[column].fillna(fill_value)

    return (
        result,
        f"Imputed {missing_before} missing value(s) in "
        f"'{column}' using mode='{fill_value}'.",
    )


def _remove_duplicates(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, str]:
    """Remove exact duplicate rows."""

    result = df.copy()

    duplicates_before = int(result.duplicated().sum())

    result = result.drop_duplicates(
        keep="first"
    ).reset_index(drop=True)

    return (
        result,
        f"Removed {duplicates_before} exact duplicate row(s).",
    )


def _trim_whitespace(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, str]:
    """Trim leading and trailing whitespace from a text column."""

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    result = df.copy()

    if not (
        pd.api.types.is_object_dtype(result[column])
        or pd.api.types.is_string_dtype(result[column])
    ):
        raise ValueError(
            f"Column '{column}' is not a text column."
        )

    non_null = result[column].notna()

    before = result.loc[non_null, column].astype(str)
    after = before.str.strip()

    changed = int((before != after).sum())

    result.loc[non_null, column] = after

    return (
        result,
        f"Trimmed whitespace from {changed} value(s) in '{column}'.",
    )


def _standardize_categories(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, str]:
    """
    Standardize equivalent text categories deterministically.

    Handles:
    - leading/trailing whitespace
    - case differences
    - punctuation/separator differences
    - common semantic aliases

    The most frequent cleaned representation becomes canonical when
    no explicit semantic alias is defined.
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    result = df.copy()

    non_null = result[column].dropna().astype(str)

    if non_null.empty:
        return result, f"No categories found in '{column}'."

    # Explicit conservative aliases for common equivalent categories.
    semantic_aliases = {
        "master": "Masters",
        "masters": "Masters",
        "master degree": "Masters",
        "masters degree": "Masters",
        "phd": "PhD",
        "ph d": "PhD",
        "doctorate": "PhD",
        "bachelor": "Bachelors",
        "bachelors": "Bachelors",
        "bachelor degree": "Bachelors",
        "bachelors degree": "Bachelors",
        "tech": "Technology",
        "technology": "Technology",
        "health": "Healthcare",
        "healthcare": "Healthcare",
        "high": "High",
        "medium": "Medium",
        "moderate": "Medium",
        "low": "Low",
        "employed": "Employed",
        "unemployed": "Unemployed",
    }

    def normalize_key(value: str) -> str:
        value = value.strip().lower()

        # Normalize common separators/punctuation.
        value = value.replace("_", " ")
        value = value.replace("-", " ")
        value = value.replace(".", "")
        value = value.replace("'", "")

        # Collapse repeated whitespace.
        value = " ".join(value.split())

        # Normalize numeric ranges:
        # "18 to 24" and "18-24" -> "18 24"
        value = value.replace(" to ", " ")

        return value

    cleaned = non_null.str.strip()

    groups: dict[str, list[str]] = {}

    for value in cleaned:
        normalized = normalize_key(value)
        groups.setdefault(normalized, []).append(value)

    canonical_map: dict[str, str] = {}

    for normalized, values in groups.items():
        if normalized in semantic_aliases:
            canonical_map[normalized] = semantic_aliases[normalized]
        else:
            counts = pd.Series(values).value_counts()
            canonical_map[normalized] = str(counts.index[0])

    changed = 0

    for index in result[column].dropna().index:
        original = str(result.at[index, column])
        normalized = normalize_key(original)

        canonical = semantic_aliases.get(
            normalized,
            canonical_map.get(normalized, original.strip()),
        )

        if original != canonical:
            changed += 1

        result.at[index, column] = canonical

    return (
        result,
        f"Standardized {changed} categorical value(s) in '{column}'.",
    )

def _flag_outliers(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, str]:
    """
    Flag numeric IQR outliers without deleting or replacing them.
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    if not pd.api.types.is_numeric_dtype(df[column]):
        raise ValueError(
            f"Column '{column}' is not numeric."
        )

    result = df.copy()

    series = result[column].dropna()

    flag_column = f"{column}_outlier_flag"
    result[flag_column] = False

    if len(series) < 4 or series.nunique() < 4:
        return (
            result,
            f"Not enough variation to evaluate outliers in '{column}'.",
        )

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return result, f"No IQR outliers detected in '{column}'."

    lower = q1 - (1.5 * iqr)
    upper = q3 + (1.5 * iqr)

    mask = (
        (result[column] < lower)
        | (result[column] > upper)
    )

    result.loc[mask, flag_column] = True

    count = int(mask.sum())

    return (
        result,
        f"Flagged {count} potential outlier(s) in '{column}'.",
    )


def _coerce_invalid_dates(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, str]:
    """
    Convert invalid date strings to missing values.

    Valid values are normalized to pandas datetime.
    """

    if column not in df.columns:
        raise ValueError(f"Column '{column}' does not exist.")

    result = df.copy()

    original = result[column].copy()

    parsed = pd.to_datetime(
        original,
        errors="coerce",
    )

    invalid_count = int(
        (original.notna() & parsed.isna()).sum()
    )

    result[column] = parsed

    return (
        result,
        f"Converted {invalid_count} invalid date value(s) "
        f"in '{column}' to missing values.",
    )


def execute_approved_actions(
    df: pd.DataFrame,
    plan: list[dict[str, Any]],
) -> tuple[pd.DataFrame, list[ExecutionResult]]:
    """
    Execute ONLY explicitly approved remediation actions.

    Returns:
        cleaned DataFrame
        execution audit trail
    """

    working_df = df.copy(deep=True)
    audit_log: list[ExecutionResult] = []

    for item in plan:

        if item.get("status") != "approved":
            audit_log.append(
                ExecutionResult(
                    action_id=item["action_id"],
                    action=item["action"],
                    column=item.get("column"),
                    status="skipped",
                    message=(
                        "Action was not executed because "
                        "human approval was not granted."
                    ),
                )
            )
            continue

        action = item["action"]
        column = item.get("column")

        try:

            if action == "impute_missing":
                working_df, message = _impute_missing(
                    working_df,
                    column,
                )

            elif action == "remove_duplicates":
                working_df, message = _remove_duplicates(
                    working_df
                )

            elif action == "trim_whitespace":
                working_df, message = _trim_whitespace(
                    working_df,
                    column,
                )

            elif action == "standardize_categories":
                working_df, message = _standardize_categories(
                    working_df,
                    column,
                )

            elif action == "flag_outliers":
                working_df, message = _flag_outliers(
                    working_df,
                    column,
                )

            elif action == "coerce_invalid_dates":
                working_df, message = _coerce_invalid_dates(
                    working_df,
                    column,
                )

            else:
                raise ValueError(
                    f"Unsupported action: {action}"
                )

            audit_log.append(
                ExecutionResult(
                    action_id=item["action_id"],
                    action=action,
                    column=column,
                    status="executed",
                    message=message,
                )
            )

        except Exception as exc:
            audit_log.append(
                ExecutionResult(
                    action_id=item["action_id"],
                    action=action,
                    column=column,
                    status="failed",
                    message=str(exc),
                )
            )

    return working_df, audit_log