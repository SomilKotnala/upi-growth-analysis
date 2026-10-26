# UPI Growth Analysis: 10-Year Macro & Network Scale (2016–2026)

A portfolio-grade, reproducible fintech data analytics project tracking the adoption, volume, value trajectory, and banking network expansion of India's **Unified Payments Interface (UPI)** from inception (April 2016) through September 2026.

---

## Executive Summary & Baseline Metrics

Over the 126-month period from April 2016 through September 2026, UPI grew from an experimental pilot to India's dominant digital retail payment infrastructure:

- **Cumulative Transaction Volume:** **870.01 Billion** transactions ($870,005.75\text{ Million}$).
- **Cumulative Transaction Value:** **₹1,247.36 Lakh Crore** (unfiltered ₹12,47,35,861.12 Crore across 126 months).
- **All-Period Weighted Average Ticket Size:** **₹1,433.74** per transaction.
- **Participating Member Banks:** **21 live banks** at launch (April 2016) $\rightarrow$ **756 live banks** (September 2026) — a **36.0× network expansion**.
- **All-Time Full-Year Peak (FY 2025–26):** **241.62 Billion** transactions, **₹314.23 Lakh Crore** value, ₹1,300.54 average ticket, 705 closing banks.
- **Current Fiscal Period (FY 2026–27 H1, April–September 2026):** **140.50 Billion** transactions, **₹176.93 Lakh Crore** value, ₹1,259.30 average ticket, 756 closing banks across 6 months.

---

## The Three-Page Power BI Analytics Report

The primary interactive delivery is built in the modern **Power BI Project (`.pbip`)** format utilizing modular **PBIR (`definition.pbir`)** report definitions and a validated **TMDL** semantic model. The report adheres strictly to official **Microsoft Fabric schemas**, dark-mode fintech aesthetics, and zero visual container collisions across a standard $1280 \times 720$ canvas.

Report location: [`powerbi/upi_growth_analysis_final.pbip`](powerbi/upi_growth_analysis_final.pbip)

### Page 1: Executive Overview — "Scale & Macro Trajectory"
- **Top Metric Cards:** All-period cumulative volume (870.01 Bn), cumulative value (₹1,247.36 Lakh Cr), weighted ticket size (₹1,433.74), latest live banks (756), and September 2026 YoY volume growth (22.59%).
- **Macro Trajectory Visuals:** Dual monthly area charts displaying volume and value curves from inception to mature scale.
- **Network Adoption:** Continuous line chart tracking live bank onboarding from 21 launch banks to 756 member banks.
- **Key Facts & Methodology Panel:** Highlighting volume-to-value decoupling and structural milestone callouts.

### Page 2: Growth & Adoption — "Scaling Dynamics & Network Multiples"
- **Monthly Growth Pulse:** Time-series line chart tracking monthly YoY volume growth (22.59%) and value growth (17.98%). Features an editorial annotation explaining hyper-growth during the 2016–2017 early-adoption phase.
- **Network Multiple KPI Card:** Quantifying the 36.0× banking network expansion multiple.
- **Comparative Fiscal Year Trajectory:** Grouped column chart evaluating annual transaction volume against transaction value.
- **Granular Monthly Audit Matrix:** Formatted monthly detail table ($1,232\text{ px}$ width) detailing volume, value, ticket size, and YoY growth rates without confusing additive total rows.

### Page 3: Financial Year Performance — "The Annual Scorecard"
- **Fiscal-Year Scorecard Matrix:** Multi-year analytical table ($888\text{ px}$ width, 10 column projections) detailing annual volume, value, weighted ticket, opening/closing banks, and YoY growth strictly across complete financial years.
- **Context-Aware Dynamic Cards:** KPI cards that automatically default to the latest complete fiscal year (**FY 2025–26**: 241.62 Bn, ₹314.23L Cr, ₹1,300.54 ticket, 705 banks) when unfiltered, and dynamically display selected year metrics when sliced.
- **Incomplete Year Safeguard:** FY 2026–27 is explicitly labeled as `Incomplete (6 Months)`, withholding annualized YoY growth to prevent misleading comparisons between 6 months and 12 months.
- **Trajectory Deep Dive:** Dedicated visual panel ($332\text{ px}$ width) highlighting the transformation from ₹3,892.58 initial ticket size down to ₹1,259.30 mature ticket size.

---

## Project Architecture & Tech Stack

```
D:\upi-growth-analysis\
├── data\
│   ├── raw\                          # Local: 11 raw official NPCI Excel workbooks (.xlsx) [Excluded from Git]
│   └── processed\
│       └── upi_monthly_clean.csv     # Local: Validated 126-row canonical monthly CSV [Excluded from Git]
├── sql\
│   ├── 01_monthly_core_metrics.sql   -- Monthly window functions, 12-month lags & YoY rates
│   └── 02_financial_year_metrics.sql -- Fiscal year boundaries, weighted tickets & completeness guards
├── src\
│   ├── clean_data.py                 # Ingestion pipeline: schema validation & atomic write
│   ├── load_to_postgres.py           # Idempotent PostgreSQL loader with DDL constraints
│   ├── run_sql_metrics.py            # SQL query executor & monthly metric assertion runner
│   ├── run_fy_metrics.py             # Financial year metric runner & validation
│   ├── analyze_trends.py             # Python EDA, matplotlib chart generation & CSV exports
│   ├── build_final_report.py         # Programmatic PBIR generator & Fabric schema validator
│   ├── validate_pbir_schema.py       # Standalone Microsoft Fabric JSON schema validator
│   ├── query_live_model.py           # Dynamic port detector for live Analysis Services instances
│   └── test_adomd_contexts.ps1       # Live ADOMD DAX context & filter evaluator
├── tests\
│   ├── test_clean_data.py            # 19 tests: date parsing, numeric cleaning & continuity
│   ├── test_analysis.py              # 7 tests: ticket formulas, zero-safety & FY boundaries
│   ├── test_powerbi_model.py         # 9 tests: TMDL tables, DAX measures & relationship checks
│   └── test_final_report.py          # 7 tests: PBIR canvas geometry, 0 overlaps & exact subtitles
├── reports\
│   └── python_eda\
│       ├── insights_summary.md       # Quantitative analytical findings & executive brief
│       ├── monthly_metrics.csv       # Local: EDA monthly table export [Excluded from Git]
│       ├── financial_year_metrics.csv# Local: EDA fiscal-year export [Excluded from Git]
│       └── *.png                     # Local: Generated trend charts [Excluded from Git]
├── powerbi\
│   ├── upi_growth_analysis_final.pbip# Final Portfolio Power BI project root
│   ├── upi_growth_analysis_final.Report/   # PBIR report definitions & visual configurations
│   ├── upi_growth_analysis_final.Dataset/  # TMDL tabular model (tables, columns, measures, parameters)
│   ├── powerquery\*.m                # Modular Power Query M transformations
│   └── dax_measures.dax              # Central DAX measure calculation library
├── DATA_DICTIONARY.md                # Metric specifications, column types, and units
├── DATA_SOURCES_AND_LIMITATIONS.md   # Official NPCI source citation, methodology & caveats
├── PROJECT_STATUS.md                 # Complete stage-by-stage implementation milestones
├── requirements.txt                  # Pinned Python dependencies
└── .gitignore                        # Strict path-based exclusion rules
```

---

## Official Data Source, Methodology & Limitations

### 1. Source Attribution
- **Publisher:** National Payments Corporation of India (NPCI)
- **Source Portal:** [NPCI UPI Product Statistics](https://www.npci.org.in/product/upi/product-statistics)
- **Coverage:** April 2016 through September 2026 (126 continuous reporting months).
- **Official Citation:** *“Data Source: National Payments Corporation of India (NPCI) — Unified Payments Interface (UPI) Product Statistics (Retrieved October 2026).”*

### 2. Units of Measure
- **Volume:** Reported in **Millions** ($10^6$) and converted to **Billions** ($10^9$) in analytical reporting (`volume_mn / 1000`).
- **Value:** Reported in **Crores INR** ($10^7\text{ INR}$) and converted to **Lakh Crores INR** ($10^{12}\text{ INR}$) in analytical reporting (`value_cr / 100000`).
- **Average Ticket Size:** Measured in Indian Rupees (INR):
  $$\text{Average Ticket Size (INR)} = \frac{\text{Value in Crores} \times 10^7}{\text{Volume in Millions} \times 10^6} = \frac{\text{Value in Crores}}{\text{Volume in Millions}} \times 10$$
  *Weighted annual ticket sizes utilize aggregate annual value divided by aggregate annual volume, not an unweighted arithmetic mean of monthly averages.*
- **Bank Count:** Discrete count of live participating member banks on the network during that calendar month.

### 3. Critical Analytical & Methodological Limitations
- **August 2018 Structural Break:** NPCI documentation states:  
  > *“This data excludes the transactions having debit/credit to the same account for the month of August 2018 onwards.”*  
  Prior to August 2018, same-account circular/test transfers were included. This methodological change creates an artificial structural break in Month-over-Month (MoM) growth between July and August 2018.
- **April 2026 Raw Value Formatting:** The raw workbook for FY 2026–27 formats April 2026 monetary value as `'29,029,88.05'`. The cleaning pipeline strips comma formatting to yield `2902988.05` (~₹29.03 Lakh Crore) without altering raw digits or modifying the original Excel file.
- **Incomplete Year Safeguard:** FY 2026–27 contains 6 months of data (April–September 2026). YoY growth is intentionally suppressed (`NULL`/blank) in both SQL and Power BI to prevent comparing 6 months against 12 months.

---

## Data Source Attribution & Publication Notice

### 1. Source of UPI Statistics
The underlying transaction statistics for this project are published by the **National Payments Corporation of India (NPCI)** on the official [NPCI UPI Product Statistics portal](https://www.npci.org.in/product/upi/product-statistics).

### 2. Precautionary Exclusion Policy
- **Excluded Assets:** All raw Excel workbooks (`data/raw/*.xlsx`), source-derived tabular datasets (`data/processed/upi_monthly_clean.csv`, `reports/python_eda/monthly_metrics.csv`, `reports/python_eda/financial_year_metrics.csv`), and generated chart images (`reports/python_eda/*.png`) are excluded from public distribution via `.gitignore` as a precaution because redistribution rights have not been established.
- **Local Availability:** These files remain preserved and available locally to the project owner on disk.
- **Open-Source Code:** The Python data processing pipelines (`src/clean_data.py`), PostgreSQL ingestion scripts (`src/load_to_postgres.py`), analytical SQL queries (`sql/*.sql`), visualization generation scripts (`src/analyze_trends.py`), DAX measure definitions, and Microsoft Fabric PBIR report metadata remain fully present in the repository to enable local reproduction from permitted source data.
- **Licensing Notice:** No open-data licence, public domain dedication, or redistribution permission from NPCI is claimed or implied. This precautionary exclusion is an operational compliance measure, not a formal legal determination regarding the copyrightability or redistributability of regulatory statistics or derived visualizations.

---

## Real End-to-End Reproduction Workflow

### 1. Environment Setup
Requires Python 3.10+ (tested on Python 3.14 on Windows).
```bash
git clone https://github.com/<username>/upi-growth-analysis.git
cd upi-growth-analysis

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Obtain Source Data Locally
1. Visit the official [NPCI UPI Product Statistics Portal](https://www.npci.org.in/product/upi/product-statistics).
2. Under "Product Statistics", select "Monthly" and download the financial year workbooks from **2016-17** through **2026-27** (11 workbooks total).
3. Place all 11 downloaded `.xlsx` files directly into:
   `data/raw/`

### 3. Run Data Cleaning & Ingestion Pipeline
Execute the Python cleaning script:
```bash
python src/clean_data.py
```
- **Input:** `data/raw/*.xlsx`
- **Actions:** Validates header mappings, parses dates to `YYYY-MM-01`, strips whitespace and comma delimiters, sanitizes the April 2026 anomaly, runs dynamic date-continuity assertions, and preserves zero-volume pilot months.
- **Output:** Atomically writes canonical dataset `data/processed/upi_monthly_clean.csv` (local-only, excluded from Git).

### 4. Database Setup & Exploratory Analysis (PostgreSQL Required for Step 4b)

#### 4a. Database Ingestion
Requires a local PostgreSQL instance (version 14+) running on `127.0.0.1:5432`:
```powershell
# Set PostgreSQL password in session environment (never hard-code secrets in files)
$env:PGPASSWORD = Read-Host "Enter PostgreSQL password"

# Idempotently creates database 'upi_growth_analysis', table 'upi_monthly_metrics', and loads 126 records
python src/load_to_postgres.py
```

#### 4b. Execute Trend Modeling & Generate Local EDA Exports
```powershell
# Executes sql/01_monthly_core_metrics.sql and sql/02_financial_year_metrics.sql via psycopg2
python src/analyze_trends.py
```
- **Actions:** Computes 12-month window lags, YoY growth percentages, and fiscal year completeness partitioning.
- **Outputs Generated Locally:**
  - `reports/python_eda/monthly_metrics.csv` (excluded from Git)
  - `reports/python_eda/financial_year_metrics.csv` (excluded from Git)
  - `reports/python_eda/*.png` (high-resolution chart renders)

### 5. Power BI Report Setup & Data Path Parameter

The report model is configured with a central Power Query text parameter:
- **Parameter Name:** `EdaDirectory`
- **Default Value:** `D:\upi-growth-analysis\reports\python_eda`
- **Queries Referencing Parameter:** `MonthlyMetrics` and `FinancialYearMetrics` build their CSV source paths dynamically as `EdaDirectory & "\monthly_metrics.csv"` and `EdaDirectory & "\financial_year_metrics.csv"`.

#### If opening from the default location (`D:\upi-growth-analysis`):
Simply open [`powerbi/upi_growth_analysis_final.pbip`](powerbi/upi_growth_analysis_final.pbip) in Power BI Desktop.

#### If opening from a different clone path:
1. Open [`powerbi/upi_growth_analysis_final.pbip`](powerbi/upi_growth_analysis_final.pbip) in Power BI Desktop.
2. In the ribbon, click **Home $\rightarrow$ Transform Data $\rightarrow$ Edit Parameters**.
3. In the `EdaDirectory` prompt, enter the absolute path to your local clone's EDA directory (e.g., `C:\projects\upi-growth-analysis\reports\python_eda`).
4. Click **OK**, then click **Apply changes** in the yellow warning banner.
*(Alternatively, update via Home $\rightarrow$ Transform Data $\rightarrow$ Data source settings).*

---

## What Can vs. Cannot Be Reproduced Without Raw Data

| Action / Artifact | Without Raw NPCI Workbooks | With Permitted Local NPCI Workbooks |
| :--- | :---: | :---: |
| **Inspect PBIR Report Definitions & Visual JSON** | Yes | Yes |
| **Review TMDL Data Model, Measures & Power Query M** | Yes | Yes |
| **Run Fabric Schema Validation (`build_final_report.py`)** | Yes | Yes |
| **Inspect Pre-Rendered Visuals (`reports/*.png`)** | No (locally generated; excluded from Git) | Yes (reproducible via `src/analyze_trends.py`) |
| **Run Python Cleaning Pipeline (`src/clean_data.py`)** | No (requires `.xlsx` files) | Yes |
| **Load Database & Execute SQL Models (`analyze_trends.py`)**| No (requires cleaned CSV) | Yes (with PostgreSQL) |
| **Refresh Power BI Semantic Model in Desktop** | No (requires generated CSVs) | Yes |

*Tested Verification Notice:* Python cleaning, PostgreSQL loading, SQL metric calculations, Fabric PBIR validation, and live DAX evaluation against `msmdsrv.exe` were verified end-to-end in the active working environment (`D:\upi-growth-analysis`). While the Power Query parameterization syntax and PBIP loading were independently confirmed via test instances, an end-to-end automated refresh on a non-Windows machine without Power BI Desktop has not been tested.

---

## Automated Test Suite & Validation Commands

```bash
# 1. Run all 42 unit, integration, and layout tests
pytest tests -v

# 2. Check Python package dependency compatibility
pip check

# 3. Validate Microsoft Fabric PBIR schemas & canvas geometry
python src/build_final_report.py

# 4. Evaluate live DAX model contexts (when Desktop is open)
powershell -ExecutionPolicy Bypass -File src/test_adomd_contexts.ps1
```
