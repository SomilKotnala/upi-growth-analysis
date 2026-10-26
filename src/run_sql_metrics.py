"""
UPI Growth Analysis — SQL Metrics Runner & Validator (Task UPI-005A)
Executes sql/01_monthly_core_metrics.sql against database 'upi_growth_analysis',
validates window functions, YoY metrics, and ticket size calculations safely.
"""

import getpass
import json
import os
import sys
from pathlib import Path
import pandas as pd
import psycopg2

DB_NAME = "upi_growth_analysis"
TABLE_NAME = "upi_monthly_metrics"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres"


def get_sql_path() -> Path:
    """Resolve path to the SQL query file."""
    base_dir = Path(__file__).resolve().parent.parent
    sql_path = base_dir / "sql" / "01_monthly_core_metrics.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found at: {sql_path}")
    return sql_path


def get_db_password() -> str:
    """Obtain password from environment or secure hidden prompt."""
    if "PGPASSWORD" in os.environ and os.environ["PGPASSWORD"].strip():
        return os.environ["PGPASSWORD"].strip()
    return getpass.getpass(f"Enter password for PostgreSQL user '{DEFAULT_USER}': ")


def execute_and_validate(password: str) -> dict:
    """Execute SQL metrics query and run analytical assertions."""
    sql_path = get_sql_path()
    with open(sql_path, "r", encoding="utf-8") as f:
        query_sql = f.read()

    print(f"Connecting to database '{DB_NAME}' at {DEFAULT_HOST}:{DEFAULT_PORT}...")
    conn = psycopg2.connect(
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        dbname=DB_NAME,
        user=DEFAULT_USER,
        password=password,
        connect_timeout=5,
    )

    try:
        # Check source table integrity before running query
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            count_before = cur.fetchone()[0]
            assert count_before == 126, f"Expected 126 source rows, found {count_before}"

        # Execute read-only analysis query
        print(f"Executing '{sql_path.name}'...")
        df = pd.read_sql_query(query_sql, conn)
        print(f"Query returned {len(df)} rows.")

        # Check source table integrity after running query (verify no mutation)
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            count_after = cur.fetchone()[0]
            assert count_after == 126, f"Source table mutated! Found {count_after} rows"

        # ====================================================================
        # VALIDATIONS
        # ====================================================================

        # 1. Row count check
        assert len(df) == 126, f"Expected exactly 126 rows, got {len(df)}"

        # 2. Chronological order & date range continuity
        dates = pd.to_datetime(df["month"])
        assert dates.is_monotonic_increasing, "Output rows are not in chronological order!"

        min_month = df["month"].min().strftime("%Y-%m-%d") if hasattr(df["month"].min(), "strftime") else str(df["month"].min())
        max_month = df["month"].max().strftime("%Y-%m-%d") if hasattr(df["month"].max(), "strftime") else str(df["month"].max())
        assert min_month == "2016-04-01", f"Min month mismatch: {min_month}"
        assert max_month == "2026-09-01", f"Max month mismatch: {max_month}"

        expected_dates = pd.date_range(start="2016-04-01", end="2026-09-01", freq="MS")
        assert len(expected_dates) == 126, "Unexpected date range interval length"
        missing = set(expected_dates.strftime("%Y-%m-%d")) - set(dates.dt.strftime("%Y-%m-%d"))
        assert len(missing) == 0, f"Continuity gaps detected: {missing}"

        # 3. First 12 months have no prior year comparison
        first_12 = df.iloc[:12]
        assert first_12["prev_year_volume_mn"].isna().all(), "First 12 months must have NULL prev_year_volume_mn!"
        assert first_12["prev_year_value_cr"].isna().all(), "First 12 months must have NULL prev_year_value_cr!"
        assert first_12["yoy_volume_growth_pct"].isna().all(), "First 12 months must have NULL yoy_volume_growth_pct!"
        assert first_12["yoy_value_growth_pct"].isna().all(), "First 12 months must have NULL yoy_value_growth_pct!"

        # 4. Zero-volume months have NULL average ticket size
        zero_vol_months = df[df["volume_mn"] == 0]
        assert len(zero_vol_months) == 3, f"Expected 3 zero-volume months, found {len(zero_vol_months)}"
        assert zero_vol_months["avg_ticket_size_inr"].isna().all(), "Zero-volume months must have NULL ticket size!"

        # 5. Check calculation accuracy for specific non-zero months
        # July 2016: vol = 0.09, val = 0.38 -> ticket size = (0.38 / 0.09) * 10 = 42.22
        jul_2016 = df[df["month"].astype(str).str.startswith("2016-07")].iloc[0]
        expected_jul_16_ticket = round((0.38 / 0.09) * 10, 2)
        assert round(float(jul_2016["avg_ticket_size_inr"]), 2) == expected_jul_16_ticket, (
            f"July 2016 ticket size mismatch: expected {expected_jul_16_ticket}, got {jul_2016['avg_ticket_size_inr']}"
        )

        # September 2026: vol = 24068.38, val = 2937396.67 -> ticket size = 1220.44
        sep_2026 = df[df["month"].astype(str).str.startswith("2026-09")].iloc[0]
        expected_sep_26_ticket = round((2937396.67 / 24068.38) * 10, 2)
        assert round(float(sep_2026["avg_ticket_size_inr"]), 2) == expected_sep_26_ticket, (
            f"September 2026 ticket size mismatch: expected {expected_sep_26_ticket}, got {sep_2026['avg_ticket_size_inr']}"
        )

        # Check YoY calculation for September 2026 vs September 2025:
        # Sep 2025: vol = 19633.43, val = 2489736.54
        # Sep 2026: vol = 24068.38, val = 2937396.67
        expected_sep_vol_growth = round(((24068.38 - 19633.43) / 19633.43) * 100, 2)
        expected_sep_val_growth = round(((2937396.67 - 2489736.54) / 2489736.54) * 100, 2)
        assert round(float(sep_2026["yoy_volume_growth_pct"]), 2) == expected_sep_vol_growth
        assert round(float(sep_2026["yoy_value_growth_pct"]), 2) == expected_sep_val_growth

        print("\nAll SQL metric validations passed successfully!")

        # Format sample rows for display and export
        df_display = df.copy()
        df_display["month"] = df_display["month"].astype(str)

        sample_rows = {
            "initial_months_2016": df_display.iloc[:4].to_dict(orient="records"),
            "post_aug_2018_sample": df_display[df_display["month"].isin(["2018-07-01", "2018-08-01", "2018-09-01"])].to_dict(orient="records"),
            "latest_months_2026": df_display.iloc[-3:].to_dict(orient="records"),
        }

        report = {
            "status": "SUCCESS",
            "database": DB_NAME,
            "table": TABLE_NAME,
            "sql_file": str(sql_path),
            "rows_returned": len(df),
            "min_month": min_month,
            "max_month": max_month,
            "validations": {
                "chronological_order": True,
                "continuity_verified": True,
                "first_12_months_lags_null": True,
                "zero_volume_division_safe": True,
                "ticket_size_accuracy_verified": True,
                "yoy_growth_accuracy_verified": True,
                "source_table_unmodified": True,
            },
            "sample_rows": sample_rows,
        }

        return report

    finally:
        conn.close()
        print("Database connection closed cleanly.")


def main():
    print("=" * 65)
    print("UPI Growth Analysis — Core Monthly SQL Metrics Runner")
    print(f"Target DB: {DB_NAME} | Source Table: {TABLE_NAME}")
    print("=" * 65)

    password = get_db_password()
    result_file = Path(__file__).parent.parent / "sql_metrics_result.json"

    try:
        report = execute_and_validate(password)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\nReport written to: {result_file.name}")
        return 0

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n[FAILED] Query or validation failed: {error_msg}")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({"status": "FAILED", "error": error_msg}, f, indent=2)
        return 1


if __name__ == "__main__":
    sys.exit(main())
