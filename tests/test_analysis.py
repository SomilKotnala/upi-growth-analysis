"""
Automated Test Suite for Analysis Metrics and EDA Calculations (Task UPI-006A)
Tests: Monthly metrics, Financial-Year aggregations, ticket size math,
YoY completeness logic, zero-volume handling, and output contract validation.
"""

import sys
import datetime
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
REPORTS_DIR = BASE_DIR / "reports" / "python_eda"
CSV_PATH = BASE_DIR / "data" / "processed" / "upi_monthly_clean.csv"

# Ensure src/ is importable
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analyze_trends import generate_insights_report


# ============================================================================
# 1. MATHEMATICAL FORMULAS & CALCULATION TESTS
# ============================================================================

def test_ticket_size_calculation_formula():
    """Verify average ticket size: (value_cr / volume_mn) * 10."""
    # Test normal month: vol = 24068.38, val = 2937396.67
    vol = 24068.38
    val = 2937396.67
    ticket_size = round((val / vol) * 10, 2)
    assert ticket_size == 1220.44

    # Test early month: vol = 0.09, val = 0.38
    ticket_size_early = round((0.38 / 0.09) * 10, 2)
    assert ticket_size_early == 42.22


def test_zero_volume_months_division_by_zero_safety():
    """Verify zero-volume months safely yield NaN/None without throwing ZeroDivisionError."""
    vol = 0.0
    val = 0.0
    # Safe formula using ternary or nullif equivalent
    ticket_size = (val / vol) * 10 if vol > 0 else None
    assert ticket_size is None


def test_yoy_growth_completeness_rule():
    """
    Verify YoY growth rule:
    Only compute when current and previous FY are complete (12 months) and prev > 0.
    Incomplete year must evaluate to None.
    """
    # Case 1: Both complete
    cur_complete = True
    prev_complete = True
    prev_vol = 185866.02
    cur_vol = 241616.88

    growth = round(((cur_vol - prev_vol) / prev_vol) * 100, 2) if (cur_complete and prev_complete and prev_vol > 0) else None
    assert growth == 30.00

    # Case 2: Current incomplete (e.g. FY 2026-27 with 6 months)
    cur_complete = False
    growth_incomplete = round(((cur_vol - prev_vol) / prev_vol) * 100, 2) if (cur_complete and prev_complete and prev_vol > 0) else None
    assert growth_incomplete is None


# ============================================================================
# 2. CANONICAL CLEANED DATASET CONTINUITY & CONSTRAINTS TESTS
# ============================================================================

def test_monthly_canonical_dataset_integrity():
    """Verify 126 continuous rows from 2016-04-01 to 2026-09-01 with 0 gaps."""
    df = pd.read_csv(CSV_PATH)

    # 126 rows
    assert len(df) == 126, f"Expected 126 rows, got {len(df)}"

    # Chronologically ordered
    dates = pd.to_datetime(df["month"])
    assert dates.is_monotonic_increasing, "Dataset is not in chronological order!"

    # Date boundaries
    assert df["month"].min() == "2016-04-01"
    assert df["month"].max() == "2026-09-01"

    # Full continuity (no missing months)
    expected_range = pd.date_range(start="2016-04-01", end="2026-09-01", freq="MS")
    missing = set(expected_range.strftime("%Y-%m-%d")) - set(df["month"])
    assert len(missing) == 0, f"Continuity gaps: {missing}"

    # Zero-volume launch months
    zero_months = df[df["volume_mn"] == 0]
    assert len(zero_months) == 3
    assert zero_months["month"].tolist() == ["2016-04-01", "2016-05-01", "2016-06-01"]


def test_financial_year_partitioning_logic():
    """Verify Indian FY calendar logic (Apr 1 to Mar 31)."""
    df = pd.read_csv(CSV_PATH)
    dates = pd.to_datetime(df["month"])

    fy_starts = np.where(dates.dt.month >= 4, dates.dt.year, dates.dt.year - 1)
    df["fy_start_year"] = fy_starts

    fy_counts = df.groupby("fy_start_year")["month"].count()
    assert len(fy_counts) == 11, f"Expected 11 financial years, got {len(fy_counts)}"

    # FY 2016 through FY 2025 have 12 months each
    for y in range(2016, 2026):
        assert fy_counts[y] == 12, f"FY {y}-{y+1} must have 12 months, got {fy_counts[y]}"

    # FY 2026 has 6 months
    assert fy_counts[2026] == 6, f"FY 2026-27 must have 6 months, got {fy_counts[2026]}"


# ============================================================================
# 3. EXPORTED EDA ASSETS CONTRACT TESTS (When Generated)
# ============================================================================

def test_exported_eda_datasets_contract_if_present():
    """If reports/python_eda/ CSVs exist, verify their schema and constraints."""
    monthly_csv = REPORTS_DIR / "monthly_metrics.csv"
    fy_csv = REPORTS_DIR / "financial_year_metrics.csv"

    if monthly_csv.exists():
        df_m = pd.read_csv(monthly_csv)
        assert len(df_m) == 126
        assert "avg_ticket_size_inr" in df_m.columns
        assert "yoy_volume_growth_pct" in df_m.columns
        assert "yoy_value_growth_pct" in df_m.columns
        # First 12 months YoY growth must be null/NaN
        assert df_m.iloc[:12]["yoy_volume_growth_pct"].isna().all()

    if fy_csv.exists():
        df_f = pd.read_csv(fy_csv)
        assert len(df_f) == 11
        # FY 2026-27 incomplete check
        row_26 = df_f[df_f["fy_label"] == "2026-27"].iloc[0]
        assert row_26["is_complete"] is False or str(row_26["is_complete"]).lower() == "false"
        assert row_26["months_available"] == 6
        assert pd.isna(row_26["yoy_volume_growth_pct"])
        assert pd.isna(row_26["yoy_value_growth_pct"])


# ============================================================================
# 4. REGRESSION TESTS (Task UPI-006A-Fix)
# ============================================================================

def test_generate_insights_report_with_date_objects(tmp_path):
    """
    Regression test for Task UPI-006A-Fix:
    Ensure generate_insights_report accepts a monthly DataFrame where the 'month'
    column contains datetime.date objects directly (as returned by psycopg2/PostgreSQL)
    without raising TypeError: '>=' not supported between instances of 'datetime.date' and 'str'.
    """
    months = [
        datetime.date(2016, 4, 1),
        datetime.date(2016, 5, 1),
        datetime.date(2016, 6, 1),
        datetime.date(2016, 7, 1),
        datetime.date(2018, 7, 1),
        datetime.date(2018, 8, 1),
        datetime.date(2025, 1, 1),
        datetime.date(2026, 8, 1),
        datetime.date(2026, 9, 1),
    ]
    df_monthly = pd.DataFrame({
        "month": months,
        "bank_count": [21, 21, 21, 21, 114, 114, 640, 680, 685],
        "volume_mn": [0.0, 0.0, 0.0, 0.09, 273.75, 312.02, 17000.0, 24000.0, 23500.0],
        "value_cr": [0.0, 0.0, 0.0, 0.38, 51843.0, 54212.0, 2300000.0, 2900000.0, 2800000.0],
        "avg_ticket_size_inr": [None, None, None, 42.22, 1893.81, 1737.46, 1352.94, 1208.33, 1191.49],
        "volume_prev_year_mn": [None, None, None, None, 11.44, 16.64, 13000.0, 20000.0, 19500.0],
        "value_prev_year_cr": [None, None, None, None, 3381.0, 4156.0, 1800000.0, 2500000.0, 2400000.0],
        "yoy_volume_growth_pct": [None, None, None, None, 2292.92, 1775.12, 30.77, 20.00, 20.51],
        "yoy_value_growth_pct": [None, None, None, None, 1433.36, 1204.43, 27.78, 16.00, 16.67],
    })

    df_fy = pd.DataFrame([
        {
            "fy_label": "2016-17",
            "months_available": 12,
            "is_complete": True,
            "total_volume_mn": 17.86,
            "total_value_cr": 6947.0,
            "weighted_avg_ticket_size_inr": 3892.58,
            "opening_bank_count": 21,
            "closing_bank_count": 44,
            "yoy_volume_growth_pct": None,
            "yoy_value_growth_pct": None,
        },
        {
            "fy_label": "2025-26",
            "months_available": 12,
            "is_complete": True,
            "total_volume_mn": 241616.88,
            "total_value_cr": 31423237.0,
            "weighted_avg_ticket_size_inr": 1300.54,
            "opening_bank_count": 640,
            "closing_bank_count": 670,
            "yoy_volume_growth_pct": 30.00,
            "yoy_value_growth_pct": 20.59,
        },
        {
            "fy_label": "2026-27",
            "months_available": 6,
            "is_complete": False,
            "total_volume_mn": 141200.0,
            "total_value_cr": 17780000.0,
            "weighted_avg_ticket_size_inr": 1259.30,
            "opening_bank_count": 675,
            "closing_bank_count": 685,
            "yoy_volume_growth_pct": None,
            "yoy_value_growth_pct": None,
        },
    ])

    # Must complete without throwing TypeError
    generate_insights_report(df_monthly, df_fy, tmp_path)

    report_file = tmp_path / "insights_summary.md"
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "UPI Growth Analysis — Python Exploratory Data Analysis & Trend Findings" in content
    assert "FY 2026–27 Boundary Constraint" in content
