from __future__ import annotations

from typing import Any

import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a deterministic quality profile for a pandas DataFrame.

    The profiler only analyzes data. It never modifies the input dataset.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    rows, columns = df.shape
    total_cells = rows * columns

    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    missing_percentage = (
        round((missing_cells / total_cells) * 100, 2)
        if total_cells > 0
        else 0.0
    )

    column_profiles: list[dict[str, Any]] = []

    for column in df.columns:
        series = df[column]

        missing_count = int(series.isna().sum())
        missing_pct = (
            round((missing_count / rows) * 100, 2)
            if rows > 0
            else 0.0
        )

        non_null = series.dropna()
        unique_count = int(non_null.nunique())

        column_profile = {
            "column": str(column),
            "dtype": str(series.dtype),
            "missing_count": missing_count,
            "missing_percentage": missing_pct,
            "unique_count": unique_count,
            "is_constant": bool(
                unique_count <= 1 and len(non_null) > 0
            ),
        }

        column_profiles.append(column_profile)

    return {
        "rows": rows,
        "columns": columns,
        "total_cells": total_cells,
        "missing_cells": missing_cells,
        "missing_percentage": missing_percentage,
        "duplicate_rows": duplicate_rows,
        "column_profiles": column_profiles,
    }