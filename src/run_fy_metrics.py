"""
UPI Growth Analysis — Financial-Year Metrics Runner & Validator (Task UPI-005B)
Executes sql/02_financial_year_metrics.sql against database 'upi_growth_analysis',
validates annual aggregations, completeness flags, bank counts, and YoY logic.
"""

import getpass
import json
import os
import sys
from pathlib import Path
import psycopg2

DB_NAME = "upi_growth_analysis"
TABLE_NAME = "upi_monthly_metrics"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres"


def get_sql_path() -> Path:
    """Resolve path to the financial-year SQL query file."""
    base_dir = Path(__file__).resolve().parent.parent
    sql_path = base_dir / "sql" / "02_financial_year_metrics.sql"
    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found at: {sql_path}")
    return sql_path


def get_db_password() -> str:
    """Obtain password from environment or secure hidden prompt."""
    if "PGPASSWORD" in os.environ and os.environ["PGPASSWORD"].strip():
        return os.environ["PGPASSWORD"].strip()
    return getpass.getpass(f"Enter password for PostgreSQL user '{DEFAULT_USER}': ")


def execute_and_validate(password: str) -> dict:
    """Execute FY metrics query and run analytical assertions."""
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

        # Execute query directly with psycopg2 to avoid pandas SQLAlchemy connection warnings
        print(f"Executing '{sql_path.name}' via psycopg2...")
        with conn.cursor() as cur:
            cur.execute(query_sql)
            col_names = [desc[0] for desc in cur.description]
            raw_rows = cur.fetchall()

        rows = [dict(zip(col_names, row)) for row in raw_rows]
        print(f"Query returned {len(rows)} financial-year rows.")

        # Check source table integrity after running query (verify no mutation)
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
            count_after = cur.fetchone()[0]
            assert count_after == 126, f"Source table mutated! Found {count_after} rows"

        # ====================================================================
        # VALIDATIONS
        # ====================================================================

        # 1. Row count check: exactly 11 financial years
        assert len(rows) == 11, f"Expected 11 financial-year rows, got {len(rows)}"

        # 2. Check labels sequence from 2016-17 to 2026-27
        expected_fy_labels = [
            "2016-17", "2017-18", "2018-19", "2019-20", "2020-21",
            "2021-22", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27"
        ]
        actual_labels = [r["fy_label"] for r in rows]
        assert actual_labels == expected_fy_labels, f"FY labels mismatch: {actual_labels}"

        # 3. Check months availability and completeness
        for r in rows:
            if r["fy_label"] == "2026-27":
                assert r["months_available"] == 6, f"FY 2026-27 must have 6 months, got {r['months_available']}"
                assert r["is_complete"] is False, "FY 2026-27 must be marked incomplete (False)!"
                assert r["yoy_volume_growth_pct"] is None, "Incomplete FY 2026-27 must have NULL YoY volume growth!"
                assert r["yoy_value_growth_pct"] is None, "Incomplete FY 2026-27 must have NULL YoY value growth!"
            else:
                assert r["months_available"] == 12, f"{r['fy_label']} must have 12 months, got {r['months_available']}"
                assert r["is_complete"] is True, f"{r['fy_label']} must be marked complete (True)!"

        # First year (2016-17) has no previous year -> YoY growth must be None
        fy_16 = rows[0]
        assert fy_16["yoy_volume_growth_pct"] is None, "FY 2016-17 must have NULL YoY volume growth!"
        assert fy_16["yoy_value_growth_pct"] is None, "FY 2016-17 must have NULL YoY value growth!"

        # 4. Independent cross-verification against raw monthly table in database
        with conn.cursor() as cur:
            # Check FY 2016-17 monthly records
            cur.execute("""
                SELECT 
                    SUM(volume_mn), 
                    SUM(value_cr),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2016-04-01'),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2017-03-01')
                FROM upi_monthly_metrics
                WHERE month BETWEEN '2016-04-01' AND '2017-03-01';
            """)
            vol_16, val_16, open_b_16, close_b_16 = cur.fetchone()
            assert round(float(rows[0]["total_volume_mn"]), 2) == round(float(vol_16), 2)
            assert round(float(rows[0]["total_value_cr"]), 2) == round(float(val_16), 2)
            assert rows[0]["opening_bank_count"] == open_b_16 == 21
            assert rows[0]["closing_bank_count"] == close_b_16 == 44

            # Check FY 2025-26 monthly records
            cur.execute("""
                SELECT 
                    SUM(volume_mn), 
                    SUM(value_cr),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2025-04-01'),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2026-03-01')
                FROM upi_monthly_metrics
                WHERE month BETWEEN '2025-04-01' AND '2026-03-01';
            """)
            vol_25, val_25, open_b_25, close_b_25 = cur.fetchone()
            assert round(float(rows[9]["total_volume_mn"]), 2) == round(float(vol_25), 2)
            assert round(float(rows[9]["total_value_cr"]), 2) == round(float(val_25), 2)
            assert rows[9]["opening_bank_count"] == open_b_25 == 668
            assert rows[9]["closing_bank_count"] == close_b_25 == 705

            # Check partial FY 2026-27 monthly records (Apr to Sep 2026)
            cur.execute("""
                SELECT 
                    SUM(volume_mn), 
                    SUM(value_cr),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2026-04-01'),
                    (SELECT bank_count FROM upi_monthly_metrics WHERE month = '2026-09-01')
                FROM upi_monthly_metrics
                WHERE month BETWEEN '2026-04-01' AND '2026-09-01';
            """)
            vol_26, val_26, open_b_26, close_b_26 = cur.fetchone()
            assert round(float(rows[10]["total_volume_mn"]), 2) == round(float(vol_26), 2)
            assert round(float(rows[10]["total_value_cr"]), 2) == round(float(val_26), 2)
            assert rows[10]["opening_bank_count"] == open_b_26 == 713
            assert rows[10]["closing_bank_count"] == close_b_26 == 756

        # 5. Check ticket size calculation: (total_value_cr / total_volume_mn) * 10
        for r in rows:
            expected_ticket = round((float(r["total_value_cr"]) / float(r["total_volume_mn"])) * 10, 2)
            assert round(float(r["weighted_avg_ticket_size_inr"]), 2) == expected_ticket

        print("\nAll Financial-Year validations passed successfully!")

        report = {
            "status": "SUCCESS",
            "database": DB_NAME,
            "table": TABLE_NAME,
            "sql_file": str(sql_path),
            "rows_returned": len(rows),
            "validations": {
                "row_count_11_years": True,
                "labels_sequence_correct": True,
                "complete_years_12_months": True,
                "partial_year_2026_27_marked_incomplete": True,
                "incomplete_year_yoy_growth_null": True,
                "opening_closing_banks_verified": True,
                "ticket_size_verified": True,
                "source_table_unmodified": True,
            },
            "financial_years": [
                {
                    "fy_label": r["fy_label"],
                    "months": r["months_available"],
                    "is_complete": r["is_complete"],
                    "total_volume_mn": float(r["total_volume_mn"]),
                    "total_value_cr": float(r["total_value_cr"]),
                    "weighted_ticket_size_inr": float(r["weighted_avg_ticket_size_inr"]),
                    "opening_banks": r["opening_bank_count"],
                    "closing_banks": r["closing_bank_count"],
                    "yoy_vol_growth_pct": float(r["yoy_volume_growth_pct"]) if r["yoy_volume_growth_pct"] is not None else None,
                    "yoy_val_growth_pct": float(r["yoy_value_growth_pct"]) if r["yoy_value_growth_pct"] is not None else None,
                }
                for r in rows
            ],
        }

        return report

    finally:
        conn.close()
        print("Database connection closed cleanly.")


def main():
    print("=" * 65)
    print("UPI Growth Analysis — Financial-Year SQL Metrics Runner")
    print(f"Target DB: {DB_NAME} | Source Table: {TABLE_NAME}")
    print("=" * 65)

    password = get_db_password()
    result_file = Path(__file__).parent.parent / "fy_metrics_result.json"

    try:
        report = execute_and_validate(password)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

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
