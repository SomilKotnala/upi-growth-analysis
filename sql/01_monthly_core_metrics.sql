-- ============================================================================
-- UPI Growth Analysis — Core Monthly Metrics and YoY Growth Analysis
-- Database: upi_growth_analysis
-- Table: upi_monthly_metrics
-- Task ID: UPI-005A
--
-- Computes:
-- 1. Average transaction ticket size in INR: (value_cr / volume_mn) * 10
--    - value_cr is in Crores (10^7 INR), volume_mn is in Millions (10^6 transactions)
--    - Ratio: (value_cr * 10^7) / (volume_mn * 10^6) = (value_cr / volume_mn) * 10
-- 2. Previous year same-month values using LAG(..., 12) window functions.
-- 3. Year-over-Year (YoY) percentage changes in volume and value.
-- 4. Defensive division using NULLIF to prevent division-by-zero on launch pilot months.
-- ============================================================================

WITH monthly_lags AS (
    SELECT
        month,
        bank_count,
        volume_mn,
        value_cr,
        -- Average transaction size in INR; returns NULL for zero-volume months
        ROUND(
            (value_cr / NULLIF(volume_mn, 0)) * 10,
            2
        ) AS avg_ticket_size_inr,
        -- Prior year same-month volume (12 months prior)
        LAG(volume_mn, 12) OVER (ORDER BY month ASC) AS prev_year_volume_mn,
        -- Prior year same-month value (12 months prior)
        LAG(value_cr, 12) OVER (ORDER BY month ASC) AS prev_year_value_cr
    FROM upi_monthly_metrics
)
SELECT
    month,
    bank_count,
    volume_mn,
    value_cr,
    avg_ticket_size_inr,
    prev_year_volume_mn,
    prev_year_value_cr,
    -- YoY Volume Growth %: (current - prev) / prev * 100
    -- Returns NULL if previous year is NULL or 0
    ROUND(
        ((volume_mn - prev_year_volume_mn) / NULLIF(prev_year_volume_mn, 0)) * 100,
        2
    ) AS yoy_volume_growth_pct,
    -- YoY Value Growth %: (current - prev) / prev * 100
    -- Returns NULL if previous year is NULL or 0
    ROUND(
        ((value_cr - prev_year_value_cr) / NULLIF(prev_year_value_cr, 0)) * 100,
        2
    ) AS yoy_value_growth_pct
FROM monthly_lags
ORDER BY month ASC;
