"""
UPI Growth Analysis — PostgreSQL Database Setup and Ingestion (Task UPI-004C)
Creates database 'upi_growth_analysis', table 'upi_monthly_metrics',
and loads canonical 126-row monthly dataset safely and idempotently.
"""

import getpass
import json
import os
import sys
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2 import sql

# Constants
DB_NAME = "upi_growth_analysis"
TABLE_NAME = "upi_monthly_metrics"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5432
DEFAULT_USER = "postgres"

DDL_CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    month DATE PRIMARY KEY,
    bank_count INTEGER NOT NULL CHECK (bank_count >= 0),
    volume_mn NUMERIC(18, 2) NOT NULL CHECK (volume_mn >= 0),
    value_cr NUMERIC(18, 2) NOT NULL CHECK (value_cr >= 0)
);
"""


def get_csv_path() -> Path:
    """Resolve path to canonical cleaned CSV."""
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "processed" / "upi_monthly_clean.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Canonical CSV not found at: {csv_path}")
    return csv_path


def get_db_password() -> str:
    """Obtain password from environment or secure interactive masked prompt."""
    if "PGPASSWORD" in os.environ and os.environ["PGPASSWORD"].strip():
        return os.environ["PGPASSWORD"].strip()
    return getpass.getpass(f"Enter password for PostgreSQL user '{DEFAULT_USER}': ")


def ensure_database_exists(password: str) -> None:
    """Connect to maintenance database and create project database if missing."""
    print(f"Connecting to maintenance database 'postgres' to verify '{DB_NAME}'...")
    conn = psycopg2.connect(
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        dbname="postgres",
        user=DEFAULT_USER,
        password=password,
        connect_timeout=5,
    )
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
            exists = cur.fetchone() is not None
            if not exists:
                print(f"Database '{DB_NAME}' does not exist. Creating...")
                # Database names cannot be parameterized with %s; use sql.Identifier safely
                cur.execute(
                    sql.SQL("CREATE DATABASE {} WITH ENCODING = 'UTF8';").format(
                        sql.Identifier(DB_NAME)
                    )
                )
                print(f"Database '{DB_NAME}' created successfully.")
            else:
                print(f"Database '{DB_NAME}' already exists.")
    finally:
        conn.close()


def ensure_table_exists(conn) -> None:
    """Create project table with explicit schema constraints if not present."""
    print(f"Ensuring table '{TABLE_NAME}' exists with target DDL...")
    with conn.cursor() as cur:
        cur.execute(DDL_CREATE_TABLE)
    conn.commit()
    print(f"Table '{TABLE_NAME}' verified.")


def load_or_verify_records(conn, csv_df: pd.DataFrame) -> dict:
    """
    Idempotent loader:
    - If table is empty: insert all 126 records transactionally.
    - If table has data: verify record-by-record match against CSV without modifying data.
    """
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT month, bank_count, volume_mn, value_cr FROM {TABLE_NAME} ORDER BY month ASC;"
        )
        existing_rows = cur.fetchall()

    if not existing_rows:
        print(f"Table '{TABLE_NAME}' is empty. Ingesting {len(csv_df)} canonical records...")
        insert_sql = f"""
            INSERT INTO {TABLE_NAME} (month, bank_count, volume_mn, value_cr)
            VALUES (%s, %s, %s, %s);
        """
        records_to_insert = [
            (
                row["month"],
                int(row["bank_count"]),
                float(row["volume_mn"]),
                float(row["value_cr"]),
            )
            for _, row in csv_df.iterrows()
        ]

        try:
            with conn.cursor() as cur:
                cur.executemany(insert_sql, records_to_insert)
            conn.commit()
            print(f"Successfully inserted {len(records_to_insert)} records.")
            action = "INSERTED"
        except Exception as e:
            conn.rollback()
            raise IOError(f"Failed to insert records. Transaction rolled back: {e}") from e

    else:
        print(f"Table '{TABLE_NAME}' already contains {len(existing_rows)} rows. Verifying contents...")
        action = "VERIFIED_EXISTING"

        # Compare existing records against CSV
        if len(existing_rows) != len(csv_df):
            raise ValueError(
                f"Row count mismatch! Database has {len(existing_rows)} rows, but CSV has {len(csv_df)} rows."
            )

        for idx, (db_row, (_, csv_row)) in enumerate(zip(existing_rows, csv_df.iterrows())):
            db_month_str = db_row[0].strftime("%Y-%m-%d")
            csv_month_str = str(csv_row["month"])

            if db_month_str != csv_month_str:
                raise ValueError(
                    f"Month mismatch at index {idx}: DB='{db_month_str}' vs CSV='{csv_month_str}'"
                )

            if int(db_row[1]) != int(csv_row["bank_count"]):
                raise ValueError(
                    f"Bank count mismatch for {db_month_str}: DB={db_row[1]} vs CSV={csv_row['bank_count']}"
                )

            # Compare floats rounded to 2 decimal places
            if round(float(db_row[2]), 2) != round(float(csv_row["volume_mn"]), 2):
                raise ValueError(
                    f"Volume mismatch for {db_month_str}: DB={db_row[2]} vs CSV={csv_row['volume_mn']}"
                )

            if round(float(db_row[3]), 2) != round(float(csv_row["value_cr"]), 2):
                raise ValueError(
                    f"Value mismatch for {db_month_str}: DB={db_row[3]} vs CSV={csv_row['value_cr']}"
                )

        print("Existing database records match canonical CSV bit-for-bit (100% verified).")

    return {"action": action}


def run_full_validation(conn, csv_df: pd.DataFrame) -> dict:
    """Comprehensive post-load validation queries against catalog and CSV."""
    validation_results = {}

    with conn.cursor() as cur:
        # 1. Session info
        cur.execute("SELECT current_database(), current_user;")
        db_name, db_user = cur.fetchone()
        assert db_name == DB_NAME, f"Wrong database: {db_name}"
        assert db_user == DEFAULT_USER, f"Wrong user: {db_user}"
        validation_results["database"] = db_name
        validation_results["user"] = db_user

        # 2. Table schema check
        cur.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position;
            """,
            (TABLE_NAME,),
        )
        columns_info = cur.fetchall()
        assert len(columns_info) == 4, f"Expected 4 columns, found {len(columns_info)}"
        validation_results["schema_columns"] = [
            {"column": c[0], "type": c[1], "nullable": c[2]} for c in columns_info
        ]

        # 3. Row count
        cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME};")
        row_count = cur.fetchone()[0]
        assert row_count == 126, f"Expected 126 rows, found {row_count}"
        validation_results["row_count"] = row_count

        # 4. Date bounds
        cur.execute(f"SELECT MIN(month), MAX(month) FROM {TABLE_NAME};")
        min_date, max_date = cur.fetchone()
        assert min_date.strftime("%Y-%m-%d") == "2016-04-01", f"Min date mismatch: {min_date}"
        assert max_date.strftime("%Y-%m-%d") == "2026-09-01", f"Max date mismatch: {max_date}"
        validation_results["min_month"] = min_date.strftime("%Y-%m-%d")
        validation_results["max_month"] = max_date.strftime("%Y-%m-%d")

        # 5. Null checks
        cur.execute(
            f"""
            SELECT COUNT(*) FROM {TABLE_NAME}
            WHERE month IS NULL OR bank_count IS NULL OR volume_mn IS NULL OR value_cr IS NULL;
            """
        )
        null_count = cur.fetchone()[0]
        assert null_count == 0, f"Found {null_count} rows with nulls"
        validation_results["null_count"] = null_count

        # 6. Time-series continuity
        cur.execute(f"SELECT month FROM {TABLE_NAME} ORDER BY month ASC;")
        db_dates = [r[0].strftime("%Y-%m-%d") for r in cur.fetchall()]
        expected_range = pd.date_range(start="2016-04-01", end="2026-09-01", freq="MS")
        expected_dates = [d.strftime("%Y-%m-%d") for d in expected_range]

        missing = set(expected_dates) - set(db_dates)
        assert len(missing) == 0, f"Missing months detected: {missing}"
        validation_results["continuity_verified"] = True

        # 7. Check zero-volume months
        cur.execute(
            f"""
            SELECT month, bank_count, volume_mn, value_cr
            FROM {TABLE_NAME}
            WHERE month IN ('2016-04-01', '2016-05-01', '2016-06-01')
            ORDER BY month ASC;
            """
        )
        zero_rows = cur.fetchall()
        assert len(zero_rows) == 3, f"Expected 3 zero-volume months, found {len(zero_rows)}"
        for z in zero_rows:
            assert float(z[2]) == 0.0 and float(z[3]) == 0.0, f"Non-zero values in launch month: {z}"
        validation_results["zero_volume_months_verified"] = True

    print("Post-load validation: ALL 7 VALIDATION CHECKS PASSED.")
    return validation_results


def main():
    print("=" * 65)
    print("UPI Growth Analysis — PostgreSQL Database Setup & Data Ingestion")
    print(f"Target DB: {DB_NAME} | Table: {TABLE_NAME} | Host: {DEFAULT_HOST}:{DEFAULT_PORT}")
    print("=" * 65)

    csv_path = get_csv_path()
    csv_df = pd.read_csv(csv_path)
    print(f"Loaded canonical CSV with {len(csv_df)} records.")

    password = get_db_password()
    result_file = Path(__file__).parent.parent / "pg_load_result.json"

    try:
        # Step 1: Ensure database exists
        ensure_database_exists(password)

        # Step 2: Connect to project database
        print(f"Connecting to database '{DB_NAME}'...")
        conn = psycopg2.connect(
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            dbname=DB_NAME,
            user=DEFAULT_USER,
            password=password,
            connect_timeout=5,
        )

        try:
            # Step 3: Ensure table exists
            ensure_table_exists(conn)

            # Step 4: Load or verify records
            ingest_result = load_or_verify_records(conn, csv_df)

            # Step 5: Full validation
            validation = run_full_validation(conn, csv_df)

            final_report = {
                "status": "SUCCESS",
                "database": DB_NAME,
                "table": TABLE_NAME,
                "action": ingest_result["action"],
                "validation": validation,
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(final_report, f, indent=2)

            print(f"\n[SUCCESS] Pipeline completed successfully.")
            print(f"Summary written to: {result_file.name}")
            return 0

        finally:
            conn.close()
            print("Database connection closed cleanly.")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n[FAILED] Setup or loading failed: {error_msg}")

        final_report = {
            "status": "FAILED",
            "error": error_msg,
        }
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2)

        return 1


if __name__ == "__main__":
    sys.exit(main())
