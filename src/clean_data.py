"""
UPI Growth Analysis — Hardened Data Cleaning Pipeline (Task UPI-002)
Source: Official NPCI Monthly Statistics (April 2016 – September 2026)
Output: Canonical processed CSV at data/processed/upi_monthly_clean.csv
"""

import os
import glob
from pathlib import Path
from typing import Tuple
import pandas as pd


# Exact expected source sheet and column definitions
EXPECTED_SHEET_NAME = "Product Statistics"

EXPECTED_SOURCE_COLUMNS = {
    "Month": "month_raw",
    "No. of Banks live on UPI": "bank_count_raw",
    "Volume (In Mn.)": "volume_mn_raw",
    "Value (In Cr.)": "value_cr_raw",
}

CANONICAL_OUTPUT_COLUMNS = ["month", "bank_count", "volume_mn", "value_cr"]


def get_project_paths() -> Tuple[Path, Path]:
    """Resolve project directory paths dynamically."""
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir, processed_dir


def clean_numeric_series(series: pd.Series, col_name: str, target_type=float) -> pd.Series:
    """
    Clean numeric string columns safely handling commas, spaces, and tabs.
    Rejects malformed values explicitly rather than coercing silently.
    """
    if series.isna().any():
        raise ValueError(f"Column '{col_name}' contains null or missing values.")

    # Convert to string and strip outer whitespace
    s_str = series.astype(str).str.strip()

    # Remove thousands separators (standard and Indian grouping), tabs, and whitespace
    cleaned_str = s_str.str.replace(r'[\t\s,]', '', regex=True)

    if (cleaned_str == '').any():
        raise ValueError(f"Column '{col_name}' contains empty strings after cleaning.")

    if target_type is int:
        # Strict integer regex: optional leading sign, digits only
        invalid_mask = ~cleaned_str.str.match(r'^-?\d+$')
        if invalid_mask.any():
            invalid_samples = s_str[invalid_mask].tolist()[:3]
            raise ValueError(
                f"Column '{col_name}' contains non-integer values: {invalid_samples}"
            )
        return cleaned_str.astype(int)

    elif target_type is float:
        # Strict float regex: optional leading sign, digits with optional single decimal point
        invalid_mask = ~cleaned_str.str.match(r'^-?\d+(\.\d+)?$')
        if invalid_mask.any():
            invalid_samples = s_str[invalid_mask].tolist()[:3]
            raise ValueError(
                f"Column '{col_name}' contains non-numeric values: {invalid_samples}"
            )
        return cleaned_str.astype(float)

    else:
        raise TypeError(f"Unsupported target type: {target_type}")


def load_raw_files(raw_dir: Path) -> pd.DataFrame:
    """
    Discover and load all valid raw NPCI Excel workbooks.
    Validates worksheet existence and maps columns by explicit name.
    Ignores Excel temporary lock files (e.g., ~$*.xlsx).
    """
    all_files = sorted(glob.glob(str(raw_dir / "*.xlsx")))
    # Filter out Excel temporary lock files
    valid_files = [f for f in all_files if not Path(f).name.startswith("~$")]

    if not valid_files:
        raise FileNotFoundError(f"No valid Excel workbooks found in {raw_dir}")

    dfs = []
    required_cols = list(EXPECTED_SOURCE_COLUMNS.keys())

    for file_path_str in valid_files:
        file_path = Path(file_path_str)
        
        # Load Excel workbook inspecting sheet names
        try:
            excel_file = pd.ExcelFile(file_path)
        except Exception as e:
            raise IOError(f"Failed to open Excel workbook '{file_path.name}': {e}") from e

        if EXPECTED_SHEET_NAME not in excel_file.sheet_names:
            raise ValueError(
                f"Workbook '{file_path.name}' missing required sheet '{EXPECTED_SHEET_NAME}'. "
                f"Found sheets: {excel_file.sheet_names}"
            )

        df = pd.read_excel(excel_file, sheet_name=EXPECTED_SHEET_NAME)

        # Validate columns
        if df.columns.duplicated().any():
            dup_cols = df.columns[df.columns.duplicated()].tolist()
            raise ValueError(
                f"Workbook '{file_path.name}' contains duplicate columns: {dup_cols}"
            )

        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Workbook '{file_path.name}' missing required columns: {missing_cols}. "
                f"Found columns: {list(df.columns)}"
            )

        # Select only required columns by name (decoupling from index position)
        df_selected = df[required_cols].copy()
        # Rename to standardized internal column names
        df_selected = df_selected.rename(columns=EXPECTED_SOURCE_COLUMNS)

        # Drop rows where all elements or Month are null/empty
        df_selected = df_selected.dropna(how="all")
        df_selected = df_selected[df_selected["month_raw"].notna()]

        dfs.append(df_selected)

    combined = pd.concat(dfs, ignore_index=True)
    return combined


def clean_upi_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw string fields, parse dates to month-start (YYYY-MM-01),
    convert numeric types, and sort chronologically.
    """
    cleaned = pd.DataFrame()

    # 1. Parse reporting month explicitly
    if df["month_raw"].isna().any():
        raise ValueError("Dataset contains null or missing month values.")

    month_series = df["month_raw"].astype(str).str.strip()
    try:
        cleaned["month_date"] = pd.to_datetime(month_series, format="%B-%Y", errors="raise")
    except Exception as e:
        raise ValueError(f"Failed to parse reporting month with format '%B-%Y': {e}") from e

    cleaned["month"] = cleaned["month_date"].dt.strftime("%Y-%m-01")

    # 2. Clean numeric columns safely
    cleaned["bank_count"] = clean_numeric_series(
        df["bank_count_raw"], col_name="bank_count", target_type=int
    )
    cleaned["volume_mn"] = clean_numeric_series(
        df["volume_mn_raw"], col_name="volume_mn", target_type=float
    )
    cleaned["value_cr"] = clean_numeric_series(
        df["value_cr_raw"], col_name="value_cr", target_type=float
    )

    # 3. Sort chronologically from oldest to newest
    cleaned = cleaned.sort_values("month_date").reset_index(drop=True)

    # Return canonical output columns
    return cleaned[CANONICAL_OUTPUT_COLUMNS]


def validate_clean_data(df: pd.DataFrame):
    """
    Run automated time-series and domain integrity validations.
    Uses dynamic date range comparison rather than hardcoded row counts.
    """
    # 1. Dataset not empty
    if df.empty:
        raise AssertionError("Cleaned dataset is empty.")

    # 2. Required columns present and ordered
    if list(df.columns) != CANONICAL_OUTPUT_COLUMNS:
        raise AssertionError(
            f"Columns mismatch. Expected {CANONICAL_OUTPUT_COLUMNS}, got {list(df.columns)}"
        )

    # 3. No nulls or NaN values
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        raise AssertionError(f"Null values detected: {null_counts.to_dict()}")

    # 4. Valid month-start dates
    try:
        dates = pd.to_datetime(df["month"], format="%Y-%m-%d", errors="raise")
    except Exception as e:
        raise AssertionError(f"Invalid date format in 'month' column: {e}") from e

    if not (dates.dt.day == 1).all():
        raise AssertionError("Not all dates represent the first day of the month.")

    # 5. Chronologically sorted
    if not dates.is_monotonic_increasing:
        raise AssertionError("Months are not strictly sorted in chronological order.")

    # 6. No duplicate months
    if df["month"].duplicated().any():
        dups = df["month"][df["month"].duplicated()].tolist()
        raise AssertionError(f"Duplicate months detected: {dups}")

    # 7. Dynamic full continuity (no missing months between min and max)
    expected_range = pd.date_range(start=dates.min(), end=dates.max(), freq="MS")
    expected_set = set(expected_range.strftime("%Y-%m-%d"))
    actual_set = set(df["month"])

    missing_months = expected_set - actual_set
    if missing_months:
        raise AssertionError(
            f"Time-series continuity gap detected. Missing months: {sorted(missing_months)}"
        )

    # 8. Numeric domain validation (no negative values; legitimate zeroes permitted)
    if (df["bank_count"] < 0).any():
        raise AssertionError("Negative values found in 'bank_count'.")

    if (df["volume_mn"] < 0).any():
        raise AssertionError("Negative values found in 'volume_mn'.")

    if (df["value_cr"] < 0).any():
        raise AssertionError("Negative values found in 'value_cr'.")

    print(
        f"Validation passed: {len(df)} records verified from "
        f"{dates.min().strftime('%Y-%m')} to {dates.max().strftime('%Y-%m')}."
    )


def save_canonical_csv(df: pd.DataFrame, output_path: Path):
    """
    Safely write the validated DataFrame to canonical CSV.
    Writes to a temporary file first, verifies write integrity,
    and atomically replaces the target file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(".tmp.csv")

    try:
        df.to_csv(temp_path, index=False)
        if not temp_path.exists() or temp_path.stat().st_size == 0:
            raise IOError("Temporary output file was not created or is empty.")
        # Atomic replace
        os.replace(temp_path, output_path)
    except Exception as e:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass
        raise IOError(f"Failed to safely generate canonical CSV at '{output_path}': {e}") from e


def run_pipeline() -> pd.DataFrame:
    """Execute the end-to-end cleaning pipeline safely."""
    raw_dir, processed_dir = get_project_paths()
    print(f"Loading raw files from: {raw_dir}")
    raw_df = load_raw_files(raw_dir)
    print(f"Loaded {len(raw_df)} raw records across workbooks.")

    print("Cleaning dataset...")
    clean_df = clean_upi_data(raw_df)

    print("Running time-series and domain validation...")
    validate_clean_data(clean_df)

    output_path = processed_dir / "upi_monthly_clean.csv"
    save_canonical_csv(clean_df, output_path)
    print(f"Canonical processed CSV safely saved to: {output_path}")
    return clean_df


def main():
    run_pipeline()


if __name__ == "__main__":
    main()
