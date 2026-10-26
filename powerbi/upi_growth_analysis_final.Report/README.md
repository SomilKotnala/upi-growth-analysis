# UPI Growth Analysis — Portfolio-Grade Power BI Report (`upi_growth_analysis_final`)

This directory contains the modern PBIR (Power BI Enhanced Report Format) definitions for the portfolio-grade 3-page UPI Growth Analysis report.

## Report Overview

- **Format:** Modern PBIR (`definition.pbir`, `definition/pages/`, `definition/RegisteredResources/`)
- **Theme:** Custom Dark Fintech Theme (`#0B1020` canvas, `#131B2E` container cards, `#1E293B` borders, `#2DD4BF` Teal volume, `#A78BFA` Violet value, `#34D399` Emerald growth/banks, `#38BDF8` Sky ticket size)
- **Grid Resolution:** 1280 × 720 (16:9 widescreen, `displayOption: "FitToPage"`)
- **Semantic Model:** TMDL Tabular Model located in `../upi_growth_analysis_final.Dataset` (24 strongly-typed DAX measures)

---

## 3 Cohesive Analytical Pages

### Page 1: `ExecutiveOverview` — "UPI / INDIA'S DIGITAL PAYMENTS SCALE: Scale & Trajectory"
- **Top Row (`y: 16, h: 56`):**
  - Section marker, headline, and subtitle.
  - Native 3-button navigation header (`1. SCALE` [Active], `2. ADOPTION`, `3. SCORECARD`).
  - Compact native Dropdown slicer bound to `DimFinancialYear[FinancialYear]` (sorted Ascending).
- **Row 2 (`y: 84, h: 88`):**
  - 5 High-impact KPI Cards:
    1. Total Volume: `870.01 Billion` (`MonthlyMetrics[Total Volume (Bn)]`, Teal `#2DD4BF`)
    2. Total Value: `₹1,247.36 Lakh Cr` (`MonthlyMetrics[Total Value (Lakh Cr INR)]`, Violet `#A78BFA`)
    3. Avg Ticket Size: `₹1,433.74` (`MonthlyMetrics[Weighted Avg Ticket Size (INR)]`, Sky `#38BDF8`)
    4. Live Member Banks: `756 Banks` (`MonthlyMetrics[Latest Bank Count]`, Emerald `#34D399`)
    5. Sep 2026 Momentum: `+22.59% Vol | +17.98% Val` (`MonthlyMetrics[Latest Month Volume YoY Growth %]`, Emerald `#34D399`)
- **Row 3 (`y: 184, h: 284`):**
  - Two signature trajectory area charts:
    - Monthly Volume (Bn) in Teal (`Jul 2016: 0.09M → Aug 2026 peak: 24,508.96M · Latest: Sep 2026: 24,068.38M`)
    - Monthly Value (Lakh Cr INR) in Violet (`Jul 2016: ₹0.38 Cr → May 2026 peak: ₹29.90L Cr · Latest: Sep 2026: ₹29.37L Cr`)
- **Row 4 (`y: 480, h: 176`):**
  - Line chart: UPI Participating Member Banks Growth (21 pilot banks in Aug 2016 to 756 live banks in Sep 2026).
  - Editorial Callout Textbox: Key Measured Facts summary.
- **Row 5 (`y: 668, h: 44`):**
  - Methodology context footnote (NPCI same-account exclusion from Aug 2018; incomplete FY 2026-27 notice).

### Page 2: `GrowthAndAdoption` — "THE UPI GROWTH ENGINE: Momentum & Adoption"
- **Top Row (`y: 16, h: 56`):**
  - Section marker, headline, and subtitle.
  - Native 3-button navigation header (`1. SCALE`, `2. ADOPTION` [Active], `3. SCORECARD`).
  - Compact native Dropdown slicer.
- **Row 2 (`y: 84, h: 326`):**
  - Hero Line Chart: Mature Scaling Growth Pulse (`2020–2026`, filtered `Date >= 2020-01-01`), comparing Volume YoY % (Teal) and Value YoY % (Violet) on linear scale (0%–250%).
  - Network Adoption Callout Card: `36.0x` Network Expansion Multiple & launch hyper-growth context.
  - Annual Growth Trajectory Clustered Column: FY Volume vs Value YoY % (FY 2018–19 to FY 2025–26).
- **Row 3 (`y: 422, h: 236`):**
  - Monthly Detail Explorer Table (`tableEx`): 126 granular monthly observations with MonthYear labels, explicit column widths summing to 1,165px, alternating dark rows, and totals disabled.
- **Row 4 (`y: 668, h: 44`):**
  - Methodology context footnote.

### Page 3: `FinancialYearPerformance` — "THE ANNUAL SCORECARD: Fiscal Year Performance Matrix"
- **Top Row (`y: 16, h: 56`):**
  - Section marker, headline, and subtitle.
  - Native 3-button navigation header (`1. SCALE`, `2. ADOPTION`, `3. SCORECARD` [Active]).
  - Compact native Dropdown slicer.
- **Row 2 (`y: 84, h: 84`):**
  - 4 Fiscal Year KPI Cards:
    1. Annual Volume (Bn): `241.62 Billion` peak in FY 25–26 (`MonthlyMetrics[FY Volume (Bn)]`, Teal)
    2. Annual Value (Lakh Cr): `₹314.23 Lakh Cr` peak in FY 25–26 (`MonthlyMetrics[FY Value (Lakh Cr INR)]`, Violet)
    3. Avg Ticket Size (INR): `₹1,300.54` in FY 25–26 (`MonthlyMetrics[FY Weighted Avg Ticket Size (INR)]`, Sky)
    4. Member Banks: `705 Closing Banks` in FY 25–26 (`MonthlyMetrics[FY Closing Bank Count]`, Emerald)
- **Row 3 (`y: 178, h: 234`):**
  - Clustered column: Annual Volume Trajectory (Billions) across all financial years.
  - Clustered column: Annual Value Trajectory (Lakh Crore INR) across all financial years.
  - Line chart: Annual Weighted Average Ticket Size Trend (INR) showing evolution from ₹3,892 down to ~₹1,300.
- **Row 4 (`y: 424, h: 234`):**
  - Annual Scorecard Matrix Table (`tableEx`): 10 columns (Financial Year, Months, Status, Volume, Value, Ticket Size, Vol YoY %, Val YoY %, Open Banks, Close Banks), sorted Ascending by Financial Year, totals disabled, explicit column widths summing to 1,165px.
- **Row 5 (`y: 668, h: 44`):**
  - Fiscal-year reporting footnote and methodology notes.

---

## Validation & Verification

1. **Fabric Schema Validation:** 100% compliance across all 39 visual containers against official Microsoft Fabric PBIR schemas (`visualContainer/2.0.0`, `visualConfiguration/2.0.0`, `semanticQuery/1.2.0`, `formattingObjectDefinitions/1.3.0`, `page/2.1.0`, `report/3.3.0`, `pagesMetadata/1.1.0`).
2. **Layout Geometry Audit:** 0 visual bounding box overlaps; all visuals strictly enclosed within 1280 × 720 with >= 8px bottom clearance.
3. **Automated Test Suite:** 40 pytest tests passing across model structure, DAX simulation, schema constraints, and page layout.
4. **Live Analysis Services Audit:** All measures queried and verified via Microsoft ADOMD Client against live Tabular engine.
