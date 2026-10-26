"""
Independent Automated Test Suite for UPI Cleaning Pipeline (Task UPI-002)
Tests: Data cleaning, schema validation, date parsing, time-series continuity,
and safe atomic output writing using isolated pytest fixtures.
"""

import sys
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Ensure src/ is importable
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from clean_data import (
    clean_numeric_series,
    load_raw_files,
    clean_upi_data,
    validate_clean_data,
    save_canonical_csv,
    EXPECTED_SHEET_NAME,
    CANONICAL_OUTPUT_COLUMNS,
)


# ============================================================================
# 1. NUMERIC & DATE CLEANING UNIT TESTS
# ============================================================================

def test_clean_numeric_standard():
    """Verify standard integers and floats parse accurately."""
    s_int = pd.Series(["21", "142", "756"])
    res_int = clean_numeric_series(s_int, "bank_count", target_type=int)
    assert res_int.tolist() == [21, 142, 756]
    assert res_int.dtype == np.int64 or res_int.dtype == int

    s_float = pd.Series(["6.37", "13440.0", "24068.38"])
    res_float = clean_numeric_series(s_float, "volume_mn", target_type=float)
    assert res_float.tolist() == [6.37, 13440.0, 24068.38]
    assert res_float.dtype == np.float64 or res_float.dtype == float


def test_clean_numeric_with_commas_and_whitespace():
    """Verify Indian/Western commas, tabs, and spaces are cleanly removed."""
    s = pd.Series([" 29,37,396.67 ", "661\t", " 18,301.51\t", "1,33,460.72\n"])
    res = clean_numeric_series(s, "value_cr", target_type=float)
    assert res.tolist() == [2937396.67, 661.0, 18301.51, 133460.72]


def test_clean_numeric_april_2026_normalization():
    """Verify raw April 2026 value with grouping anomaly '29,029,88.05' normalizes correctly."""
    s = pd.Series(["29,029,88.05"])
    res = clean_numeric_series(s, "value_cr", target_type=float)
    assert res.iloc[0] == 2902988.05


def test_clean_numeric_malformed_fails():
    """Verify malformed numeric strings raise explicit ValueError."""
    # Text string
    with pytest.raises(ValueError, match="non-numeric values"):
        clean_numeric_series(pd.Series(["2500.50", "invalid_text"]), "val", target_type=float)

    # Currency symbol
    with pytest.raises(ValueError, match="non-numeric values"):
        clean_numeric_series(pd.Series(["₹ 1200"]), "val", target_type=float)

    # Empty string
    with pytest.raises(ValueError, match="empty strings"):
        clean_numeric_series(pd.Series(["   "]), "val", target_type=float)

    # Null value
    with pytest.raises(ValueError, match="null or missing"):
        clean_numeric_series(pd.Series([10.5, None]), "val", target_type=float)

    # Non-integer in int column
    with pytest.raises(ValueError, match="non-integer values"):
        clean_numeric_series(pd.Series(["10.5"]), "banks", target_type=int)


def test_clean_upi_data_date_parsing_valid():
    """Verify valid MonthName-YYYY strings parse to YYYY-MM-01 month starts."""
    df_raw = pd.DataFrame({
        "month_raw": ["September-2026", "April-2016"],
        "bank_count_raw": ["756", "21"],
        "volume_mn_raw": ["24068.38", "0"],
        "value_cr_raw": ["2937396.67", "0"],
    })
    cleaned = clean_upi_data(df_raw)
    assert cleaned["month"].tolist() == ["2016-04-01", "2026-09-01"]
    assert list(cleaned.columns) == CANONICAL_OUTPUT_COLUMNS


def test_clean_upi_data_date_parsing_invalid_fails():
    """Verify invalid month string raises descriptive ValueError."""
    df_bad = pd.DataFrame({
        "month_raw": ["InvalidMonth-2026"],
        "bank_count_raw": ["100"],
        "volume_mn_raw": ["10.0"],
        "value_cr_raw": ["50.0"],
    })
    with pytest.raises(ValueError, match="Failed to parse reporting month"):
        clean_upi_data(df_bad)


def test_clean_upi_data_chronological_sorting():
    """Verify rows arriving in reverse order are sorted chronologically ascending."""
    df_reversed = pd.DataFrame({
        "month_raw": ["March-2020", "January-2020", "February-2020"],
        "bank_count_raw": ["148", "144", "146"],
        "volume_mn_raw": ["1246.84", "1305.02", "1325.69"],
        "value_cr_raw": ["206462.31", "216242.97", "222516.95"],
    })
    cleaned = clean_upi_data(df_reversed)
    assert cleaned["month"].tolist() == ["2020-01-01", "2020-02-01", "2020-03-01"]


# ============================================================================
# 2. SOURCE SCHEMA & EXCEL WORKBOOK LOADING TESTS
# ============================================================================

def test_load_raw_files_column_mapping_by_name(tmp_path):
    """
    Verify workbooks with scrambled column order map by explicit name,
    not by index position.
    """
    # Create workbook with scrambled column order: Value, Month, Banks, Volume
    data_scrambled = {
        "Value (In Cr.)": ["500.0"],
        "Month": ["May-2019"],
        "No. of Banks live on UPI": ["140"],
        "Volume (In Mn.)": ["100.0"],
    }
    df = pd.DataFrame(data_scrambled)
    wb_path = tmp_path / "test_scrambled.xlsx"
    with pd.ExcelWriter(wb_path) as writer:
        df.to_excel(writer, sheet_name=EXPECTED_SHEET_NAME, index=False)

    loaded = load_raw_files(tmp_path)
    assert len(loaded) == 1
    assert loaded.iloc[0]["month_raw"] == "May-2019"
    assert str(loaded.iloc[0]["bank_count_raw"]) == "140"
    assert str(loaded.iloc[0]["volume_mn_raw"]) in ["100.0", "100"]
    assert str(loaded.iloc[0]["value_cr_raw"]) in ["500.0", "500"]


def test_load_raw_files_missing_column_fails(tmp_path):
    """Verify clear error when a required column is missing."""
    data_missing = {
        "Month": ["May-2019"],
        "No. of Banks live on UPI": ["140"],
        # Missing 'Volume (In Mn.)' and 'Value (In Cr.)'
    }
    wb_path = tmp_path / "test_missing_col.xlsx"
    with pd.ExcelWriter(wb_path) as writer:
        pd.DataFrame(data_missing).to_excel(writer, sheet_name=EXPECTED_SHEET_NAME, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_raw_files(tmp_path)


def test_load_raw_files_missing_sheet_fails(tmp_path):
    """Verify error when required sheet 'Product Statistics' is absent."""
    wb_path = tmp_path / "test_bad_sheet.xlsx"
    with pd.ExcelWriter(wb_path) as writer:
        pd.DataFrame({"A": [1]}).to_excel(writer, sheet_name="Sheet1", index=False)

    with pytest.raises(ValueError, match="missing required sheet 'Product Statistics'"):
        load_raw_files(tmp_path)


def test_load_raw_files_ignores_temp_lock_files(tmp_path):
    """Verify Excel temporary lock files (~$*.xlsx) are ignored."""
    # Real file
    real_data = {
        "Month": ["May-2019"],
        "No. of Banks live on UPI": ["140"],
        "Volume (In Mn.)": ["100.0"],
        "Value (In Cr.)": ["500.0"],
    }
    real_wb = tmp_path / "real_file.xlsx"
    with pd.ExcelWriter(real_wb) as writer:
        pd.DataFrame(real_data).to_excel(writer, sheet_name=EXPECTED_SHEET_NAME, index=False)

    # Temp lock file that would otherwise fail to open
    temp_lock = tmp_path / "~$real_file.xlsx"
    temp_lock.write_text("dummy lock content")

    loaded = load_raw_files(tmp_path)
    assert len(loaded) == 1


def test_load_raw_files_no_files_fails(tmp_path):
    """Verify FileNotFoundError when directory contains no Excel files."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    with pytest.raises(FileNotFoundError, match="No valid Excel workbooks found"):
        load_raw_files(empty_dir)


# ============================================================================
# 3. TIME-SERIES CONTINUITY & DOMAIN VALIDATION TESTS
# ============================================================================

def test_validate_clean_data_valid_sequence():
    """Verify valid chronological continuous time series passes validation."""
    df_valid = pd.DataFrame({
        "month": ["2020-01-01", "2020-02-01", "2020-03-01"],
        "bank_count": [144, 146, 148],
        "volume_mn": [1305.02, 1325.69, 1246.84],
        "value_cr": [216242.97, 222516.95, 206462.31],
    })
    # Should not raise
    validate_clean_data(df_valid)


def test_validate_clean_data_preserves_zero_volume():
    """Verify genuine zero-volume historical months pass validation."""
    df_zero = pd.DataFrame({
        "month": ["2016-04-01", "2016-05-01", "2016-06-01"],
        "bank_count": [21, 21, 21],
        "volume_mn": [0.0, 0.0, 0.0],
        "value_cr": [0.0, 0.0, 0.0],
    })
    validate_clean_data(df_zero)


def test_validate_clean_data_duplicate_month_fails():
    """Verify duplicate months are caught and raise AssertionError."""
    df_dup = pd.DataFrame({
        "month": ["2020-01-01", "2020-01-01", "2020-02-01"],
        "bank_count": [144, 144, 146],
        "volume_mn": [100.0, 100.0, 120.0],
        "value_cr": [1000.0, 1000.0, 1200.0],
    })
    with pytest.raises(AssertionError, match="Duplicate months detected"):
        validate_clean_data(df_dup)


def test_validate_clean_data_missing_month_gap_fails():
    """Verify gap in monthly sequence (missing month) raises AssertionError."""
    # Jan 2020 and Mar 2020, missing Feb 2020
    df_gap = pd.DataFrame({
        "month": ["2020-01-01", "2020-03-01"],
        "bank_count": [144, 148],
        "volume_mn": [100.0, 120.0],
        "value_cr": [1000.0, 1200.0],
    })
    with pytest.raises(AssertionError, match="Time-series continuity gap detected"):
        validate_clean_data(df_gap)


def test_validate_clean_data_negative_numeric_fails():
    """Verify negative values in bank count, volume, or value raise AssertionError."""
    df_neg = pd.DataFrame({
        "month": ["2020-01-01"],
        "bank_count": [-5],
        "volume_mn": [100.0],
        "value_cr": [1000.0],
    })
    with pytest.raises(AssertionError, match="Negative values found in 'bank_count'"):
        validate_clean_data(df_neg)


# ============================================================================
# 4. SAFE ATOMIC OUTPUT GENERATION TESTS
# ============================================================================

def test_save_canonical_csv_atomic_write(tmp_path):
    """Verify safe output writes correctly to target path."""
    df = pd.DataFrame({
        "month": ["2020-01-01"],
        "bank_count": [144],
        "volume_mn": [100.0],
        "value_cr": [1000.0],
    })
    out_file = tmp_path / "canonical.csv"
    save_canonical_csv(df, out_file)
    assert out_file.exists()
    assert (tmp_path / "canonical.tmp.csv").exists() is False

    read_back = pd.read_csv(out_file)
    assert len(read_back) == 1
    assert read_back.iloc[0]["bank_count"] == 144


def test_save_canonical_csv_protects_existing_file_on_error(tmp_path, monkeypatch):
    """
    Verify that if an error occurs during writing/atomic replacement,
    the existing canonical file remains completely intact.
    """
    out_file = tmp_path / "canonical.csv"
    out_file.write_text("original,unbroken,content\n1,2,3\n")

    df_new = pd.DataFrame({"month": ["2020-01-01"]})

    # Monkeypatch os.replace to simulate an unexpected OS error
    def mock_replace(src, dst):
        raise OSError("Simulated disk error during atomic replace")

    monkeypatch.setattr("os.replace", mock_replace)

    with pytest.raises(IOError, match="Failed to safely generate canonical CSV"):
        save_canonical_csv(df_new, out_file)

    # Existing file must remain identical
    assert out_file.read_text() == "original,unbroken,content\n1,2,3\n"
    # Temp file must be cleaned up
    assert (tmp_path / "canonical.tmp.csv").exists() is False
