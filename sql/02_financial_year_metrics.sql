-- ============================================================================
-- UPI Growth Analysis — Financial-Year Growth Analysis
-- Database: upi_growth_analysis
-- Table: upi_monthly_metrics
-- Task ID: UPI-005B
--
-- Summarizes UPI transaction metrics by Indian Financial Year (April 1 to March 31):
-- 1. Aggregates monthly volumes and values to annual totals.
-- 2. Calculates weighted average ticket size in INR: (total_value_cr / total_volume_mn) * 10
-- 3. Identifies opening bank count (April/first month) and closing bank count (March/latest month).
-- 4. Computes Year-over-Year (YoY) growth strictly between complete financial years (12 months).
-- 5. Preserves partial FY 2026-27 (6 months) as incomplete, setting its YoY growth to NULL.
-- ============================================================================

WITH monthly_with_fy AS (
    SELECT
        month,
        bank_count,
        volume_mn,
        value_cr,
        -- Indian Financial Year Start Year:
        -- April (month 4) to December (month 12) belongs to current calendar year.
        -- January (month 1) to March (month 3) belongs to previous calendar year.
        CASE
            WHEN EXTRACT(MONTH FROM month) >= 4 THEN EXTRACT(YEAR FROM month)::INT
            ELSE (EXTRACT(YEAR FROM month) - 1)::INT
        END AS fy_start_year,
        -- Formatted FY label (e.g. '2016-17', '2026-27')
        CASE
            WHEN EXTRACT(MONTH FROM month) >= 4 THEN
                TO_CHAR(EXTRACT(YEAR FROM month), 'FM9999') || '-' ||
                TO_CHAR(MOD((EXTRACT(YEAR FROM month) + 1)::INT, 100), 'FM00')
            ELSE
                TO_CHAR(EXTRACT(YEAR FROM month) - 1, 'FM9999') || '-' ||
                TO_CHAR(MOD((EXTRACT(YEAR FROM month))::INT, 100), 'FM00')
        END AS fy_label,
        -- Opening and closing bank counts using window functions across the entire FY partition
        FIRST_VALUE(bank_count) OVER (
            PARTITION BY (
                CASE
                    WHEN EXTRACT(MONTH FROM month) >= 4 THEN EXTRACT(YEAR FROM month)::INT
                    ELSE (EXTRACT(YEAR FROM month) - 1)::INT
                END
            )
            ORDER BY month ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS fy_opening_banks,
        LAST_VALUE(bank_count) OVER (
            PARTITION BY (
                CASE
                    WHEN EXTRACT(MONTH FROM month) >= 4 THEN EXTRACT(YEAR FROM month)::INT
                    ELSE (EXTRACT(YEAR FROM month) - 1)::INT
                END
            )
            ORDER BY month ASC
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS fy_closing_banks
    FROM upi_monthly_metrics
),
fy_aggregated AS (
    SELECT
        fy_start_year,
        fy_label,
        COUNT(*)::INT AS months_available,
        (COUNT(*) = 12) AS is_complete,
        ROUND(SUM(volume_mn), 2) AS total_volume_mn,
        ROUND(SUM(value_cr), 2) AS total_value_cr,
        -- Weighted average ticket size: (total_value_cr / total_volume_mn) * 10
        -- Returns NULL if total_volume_mn is 0
        ROUND(
            (SUM(value_cr) / NULLIF(SUM(volume_mn), 0)) * 10,
            2
        ) AS weighted_avg_ticket_size_inr,
        -- Take the min/max of the window values (constant within each FY group)
        MIN(fy_opening_banks) AS opening_bank_count,
        MAX(fy_closing_banks) AS closing_bank_count
    FROM monthly_with_fy
    GROUP BY fy_start_year, fy_label
),
fy_lags AS (
    SELECT
        fy_start_year,
        fy_label,
        months_available,
        is_complete,
        total_volume_mn,
        total_value_cr,
        weighted_avg_ticket_size_inr,
        opening_bank_count,
        closing_bank_count,
        -- Lag of previous financial year's totals and completeness
        LAG(is_complete, 1) OVER (ORDER BY fy_start_year ASC) AS prev_is_complete,
        LAG(total_volume_mn, 1) OVER (ORDER BY fy_start_year ASC) AS prev_volume_mn,
        LAG(total_value_cr, 1) OVER (ORDER BY fy_start_year ASC) AS prev_value_cr
    FROM fy_aggregated
)
SELECT
    fy_label,
    months_available,
    is_complete,
    total_volume_mn,
    total_value_cr,
    weighted_avg_ticket_size_inr,
    opening_bank_count,
    closing_bank_count,
    -- Calculate YoY Volume Growth % only when both current and previous FY are complete (12 months)
    -- and previous volume > 0. For incomplete years (e.g. FY 2026-27), returns NULL.
    CASE
        WHEN is_complete = TRUE AND prev_is_complete = TRUE AND prev_volume_mn > 0 THEN
            ROUND(((total_volume_mn - prev_volume_mn) / prev_volume_mn) * 100, 2)
        ELSE NULL
    END AS yoy_volume_growth_pct,
    -- Calculate YoY Value Growth % under the same strict completeness conditions
    CASE
        WHEN is_complete = TRUE AND prev_is_complete = TRUE AND prev_value_cr > 0 THEN
            ROUND(((total_value_cr - prev_value_cr) / prev_value_cr) * 100, 2)
        ELSE NULL
    END AS yoy_value_growth_pct
FROM fy_lags
ORDER BY fy_start_year ASC;
