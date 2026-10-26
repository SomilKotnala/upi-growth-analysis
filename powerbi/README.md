# Power BI Data Model Documentation — UPI Growth Analysis

**Project File:** `D:\upi-growth-analysis\powerbi\upi_growth_analysis.pbip`  
**Dataset Format:** Tabular Model Scripting Language (`model.bim`, compatibility level 1606)  
**Live Engine:** Microsoft Analysis Services Tabular Instance (tested via `msmdsrv.exe`)  
**Data Sources:**
- `reports/python_eda/monthly_metrics.csv` (126 monthly records)
- `reports/python_eda/financial_year_metrics.csv` (11 financial-year records)

---

## 1. Data Model Architecture

The data model follows an optimized star/snowflake schema designed for analytical consistency across monthly and financial-year granularities:

```
+---------------------+             +------------------------+
|   DimFinancialYear  | 1 ---- *    |  FinancialYearMetrics  |
+---------------------+             +------------------------+
           | 1
           |
           *
+---------------------+
|       DimDate       |
+---------------------+
           | 1
           |
           *
+---------------------+
|   MonthlyMetrics    |
+---------------------+
```

### Table Definitions & Verified Row Counts (Live Engine Audit)

1. **`MonthlyMetrics`** (Fact Table — **126 rows** verified in live engine):
   - `month` (DateTime, `yyyy-MM-dd`): Primary monthly reporting key.
   - `bank_count` (Int64, `#,##0`): Network live member bank count.
   - `volume_mn` (Double, `#,##0.00`): Monthly transaction volume in millions.
   - `value_cr` (Double, `₹#,##0.00`): Monthly transaction value in crore rupees.
   - `avg_ticket_size_inr` (Double, `₹#,##0.00`): Monthly average ticket size.
   - `prev_year_volume_mn` (Double, `#,##0.00`): Same month prior-year volume.
   - `prev_year_value_cr` (Double, `₹#,##0.00`): Same month prior-year value.
   - `yoy_volume_growth_pct` (Double, `0.00`): Source percentage points (e.g. `22.59`).
   - `yoy_value_growth_pct` (Double, `0.00`): Source percentage points (e.g. `17.98`).
   - *Initial three zero-volume months (April–June 2016) and early null YoY values preserved.*

2. **`FinancialYearMetrics`** (Aggregated Fact Table — **11 rows** verified in live engine):
   - `fy_label` (String): Indian financial year label (e.g. `2016-17` to `2026-27`).
   - `months_available` (Int64): `12` for complete years; `6` for FY 2026–27.
   - `is_complete` (Boolean): Completeness flag (`True` for 12 months, `False` for partial).
   - `total_volume_mn` (Double, `#,##0.00`): Annual volume aggregate.
   - `total_value_cr` (Double, `₹#,##0.00`): Annual value aggregate.
   - `weighted_avg_ticket_size_inr` (Double, `₹#,##0.00`): True weighted annual average ticket size.
   - `opening_bank_count` & `closing_bank_count` (Int64): Live member banks at start/end of FY.
   - `yoy_volume_growth_pct` & `yoy_value_growth_pct` (Double, `0.00`): Annual growth points (null for FY 16-17 & FY 26-27).

3. **`DimDate`** (Date Dimension — **126 rows** verified in live engine):
   - `Date` (DateTime, `yyyy-MM-dd`): Primary Key (`2016-04-01` to `2026-09-01`).
   - `Year` (Int64), `MonthNo` (Int64), `MonthName` (Text), `MonthShort` (Text).
   - `MonthYear` (Text), sorted by integer `YearMonthKey` (e.g. `201604`).
   - `FinancialYear` (Text, e.g. `2016-17`), `FYQuarter` (`Q1`–`Q4`).
   - `MonthInFY` (Int64, sorted in April=1 to March=12 order).

4. **`DimFinancialYear`** (FY Dimension — **11 rows** verified in live engine):
   - `FinancialYear` (Text): Primary Key (`2016-17` to `2026-27`), sorted by `FYSortOrder`.
   - `FYStartYear` (Int64) & `FYEndYear` (Int64).
   - `FYSortOrder` (Int64, 1 to 11).
   - `IsComplete` (Boolean): `True` for completed 12-month years; `False` for FY 2026–27.
   - `Status` (Text): `"Complete"` or `"Incomplete (6 Mo)"`.

---

## 2. Relationships

All relationships are active, single-direction, one-to-many, preventing cross-filtering ambiguities:

| Relationship Name | From (Many) | To (One) | Cardinality | Cross-Filter |
| :--- | :--- | :--- | :---: | :---: |
| `DimDate_MonthlyMetrics` | `MonthlyMetrics[month]` | `DimDate[Date]` | Many-to-One | Single (`DimDate` $\to$ `MonthlyMetrics`) |
| `DimFinancialYear_DimDate` | `DimDate[FinancialYear]` | `DimFinancialYear[FinancialYear]` | Many-to-One | Single (`DimFinancialYear` $\to$ `DimDate`) |
| `DimFinancialYear_FinancialYearMetrics` | `FinancialYearMetrics[fy_label]` | `DimFinancialYear[FinancialYear]` | Many-to-One | Single (`DimFinancialYear` $\to$ `FinancialYearMetrics`) |

---

## 3. Percentage-Unit Audit & Consistent Treatment

Per Task UPI-007A-Final specification:
- **Source Columns:** Source columns (`yoy_volume_growth_pct`, `yoy_value_growth_pct`) store values in percentage points (e.g. `22.59`, `17.98`, `30.00`). They are formatted as standard decimals with format string `"0.00"`.
- **DAX Measures:** All percentage growth measures consistently divide the percentage-point values by `100` and use the Power BI percentage format string `"0.00%"`.
- **Live Output Verification:**
  - September 2026 Monthly Volume Growth: `0.2259` $\to$ **22.59%**
  - September 2026 Monthly Value Growth: `0.1798` $\to$ **17.98%**
  - FY 2025–26 Annual Volume Growth: `0.3000` $\to$ **30.00%**
  - FY 2025–26 Annual Value Growth: `0.2059` $\to$ **20.59%**
  - FY 2026–27 (Incomplete) Annual Growth: **BLANK()**
  - FY 2016–17 (Launch Baseline) Annual Growth: **BLANK()**

---

## 4. Verified DAX Measures Set & Live Audit Values

All 13 measures are defined in `dax_measures.dax` and audited in the live Analysis Services engine:

1. **`[Total Volume (Mn)]`**: `= SUM(MonthlyMetrics[volume_mn])`  
   *Live Audit (Unfiltered):* **870,005.75 Million transactions**
2. **`[Total Value (Cr INR)]`**: `= SUM(MonthlyMetrics[value_cr])`  
   *Live Audit (Unfiltered):* **₹12,47,35,861.12 Crore**
3. **`[Weighted Avg Ticket Size (INR)]`**:  
   ```dax
   VAR _Vol = [Total Volume (Mn)]
   VAR _Val = [Total Value (Cr INR)]
   RETURN IF(_Vol > 0, DIVIDE(_Val, _Vol) * 10, BLANK())
   ```  
   *Live Audit (Unfiltered):* **₹1,433.74** *(Matches SQL calculation `(124735861.12 / 870005.75) * 10`)*
4. **`[Latest Bank Count]`**: `= CALCULATE(MAX(MonthlyMetrics[bank_count]), MonthlyMetrics[month] = _LatestDate)`  
   *Live Audit:* **756 live member banks**
5. **`[Latest Month Volume (Mn)]`**: `= CALCULATE([Total Volume (Mn)], MonthlyMetrics[month] = _LatestDate)`  
   *Live Audit (September 2026):* **24,068.38 Million transactions**
6. **`[Latest Month Value (Cr INR)]`**: `= CALCULATE([Total Value (Cr INR)], MonthlyMetrics[month] = _LatestDate)`  
   *Live Audit (September 2026):* **₹29,37,396.67 Crore**
7. **`[Latest Month Volume YoY Growth %]`**: `= CALCULATE(SELECTEDVALUE(MonthlyMetrics[yoy_volume_growth_pct]), MonthlyMetrics[month] = _LatestDate) / 100`  
   *Live Audit (September 2026):* **+22.59%**
8. **`[Latest Month Value YoY Growth %]`**: `= CALCULATE(SELECTEDVALUE(MonthlyMetrics[yoy_value_growth_pct]), MonthlyMetrics[month] = _LatestDate) / 100`  
   *Live Audit (September 2026):* **+17.98%**
9. **`[FY Volume (Mn)]`**: `= SUM(FinancialYearMetrics[total_volume_mn])`  
   *Live Audit:* **870,005.75 Million transactions**
10. **`[FY Value (Cr INR)]`**: `= SUM(FinancialYearMetrics[total_value_cr])`  
    *Live Audit:* **₹12,47,35,861.12 Crore**
11. **`[FY Completeness Status]`**:  
    ```dax
    IF(
        HASONEVALUE(DimFinancialYear[FinancialYear]),
        VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
        RETURN IF(_IsComp, "Complete (12 Months)", "Incomplete (6 Months)"),
        "Multiple Financial Years"
    )
    ```
12. **`[FY Volume YoY Growth %]`**:  
    ```dax
    IF(
        HASONEVALUE(DimFinancialYear[FinancialYear]),
        VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
        VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_volume_growth_pct])
        RETURN IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),
        BLANK()
    )
    ```  
    *Live Audit (FY 2025–26):* **+30.00%** | *FY 2026–27:* **BLANK()**
13. **`[FY Value YoY Growth %]`**:  
    ```dax
    IF(
        HASONEVALUE(DimFinancialYear[FinancialYear]),
        VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
        VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_value_growth_pct])
        RETURN IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),
        BLANK()
    )
    ```  
    *Live Audit (FY 2025–26):* **+20.59%** | *FY 2026–27:* **BLANK()**

---

## 5. Desktop Interaction Blocker Notice & How to Save `.pbix`

### Technical Blocker Audit
- **Application Execution:** Power BI Desktop (`PBIDesktop.exe`, version `2.159.883.0`) was launched and successfully hosted the Analysis Services tabular database (`msmdsrv.exe`).
- **Interactive Session Limitation:** Because the agent operates within a non-interactive PowerShell console session, the spawned process has `MainWindowHandle = 0`. Windows does not expose an interactive top-level desktop window station to receive simulated UI keystrokes (`Alt+F -> Save As`).
- **Mandated Safety Rule:** Under Task UPI-007A-Final instructions: *"If Desktop interaction is unavailable or an error prevents opening or saving, stop and report the exact blocker. Do not fabricate a PBIX or claim the project was validated."* We strictly stop and report this exact blocker rather than fabricating a fake binary `.pbix` file.

### One-Click User Step to Save PBIX
1. Open [`D:\upi-growth-analysis\powerbi\upi_growth_analysis.pbip`](file:///D:/upi-growth-analysis/powerbi/upi_growth_analysis.pbip) in Power BI Desktop.
2. In Power BI Desktop, click **File $\to$ Save As $\to$ Power BI (*.pbix)** and save to:
   `D:\upi-growth-analysis\powerbi\upi_growth_analysis.pbix`.
