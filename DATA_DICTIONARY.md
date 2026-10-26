# Data Dictionary — UPI Monthly Cleaned Dataset

**Canonical Dataset Path:** `data/processed/upi_monthly_clean.csv`  
**Dataset Grain:** One observation per calendar month (monthly aggregated platform statistics).  
**Time Coverage:** April 2016 (`2016-04-01`) through September 2026 (`2026-09-01`).  
**Total Records:** 126 observations.  
**Completeness:** 100% complete (0 nulls, 0 missing months, 0 duplicate periods).

---

## 1. Field Specifications

| Column Name | Source Column (NPCI) | Cleaned Storage Type | Unit / Format | Description & Business Meaning |
| :--- | :--- | :---: | :--- | :--- |
| `month` | `Month` | `string` (`ISO-8601`) | `YYYY-MM-01` | The reporting calendar month, standardized to the first day of that month. |
| `bank_count` | `No. of Banks live on UPI` | `int64` | Integer Count | The total count of operational member banks live on the UPI network during the month. |
| `volume_mn` | `Volume (In Mn.)` | `float64` | Millions ($10^6$) | Total successful transaction volume processed on UPI during the month. One unit represents 1,000,000 transactions. |
| `value_cr` | `Value (In Cr.)` | `float64` | Crore INR ($10^7$ INR) | Total monetary value of transactions processed during the month in Indian Rupees. 1 Crore = 10,000,000 INR. |

---

## 2. Zero Values vs. Missing Data

- **Zero Values (`0.0`):** Present in `volume_mn` and `value_cr` for the initial three months of the platform (`2016-04-01`, `2016-05-01`, and `2016-06-01`). These represent legitimate historical observations during the pre-commercial pilot and bank integration phase (21 banks live, zero public transactions recorded prior to commercial launch in July/August 2016). They must **not** be treated as missing or corrupt data.
- **Missing Data (`NULL` / `NaN`):** There are **zero** missing values in the canonical dataset. Any missing reporting month or null entry triggers an immediate assertion failure during pipeline execution.

---

## 3. Data Integrity & Validation Rules

The pipeline enforces the following validation contract in `src/clean_data.py`:
1. **Uniqueness:** Every `month` value must appear exactly once. Duplicate records are rejected.
2. **Chronological Sorting:** The dataset must be strictly monotonic increasing by date.
3. **Full Time-Series Continuity:** The set of dates in the dataset must exactly match a dynamically generated sequence of month-start dates (`pd.date_range(min, max, freq='MS')`). No monthly gaps are permitted.
4. **Domain Boundaries:**
   - `bank_count >= 0`
   - `volume_mn >= 0.0`
   - `value_cr >= 0.0`
5. **No Derived Metrics in Canonical CSV:** Derived figures (such as Average Ticket Size / Value per Transaction, MoM growth rates, YoY growth rates) are calculated dynamically in downstream SQL and Power BI models, keeping the canonical CSV as an unmodified processed representation of official facts.
