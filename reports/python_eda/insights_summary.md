# UPI Growth Analysis — Python Exploratory Data Analysis & Trend Findings

**Analysis Date:** October 2026  
**Source Database:** `upi_growth_analysis` (Table: `upi_monthly_metrics`)  
**Data Timeline:** April 2016 through September 2026 (126 continuous monthly records)  
**Output Directory:** `reports/python_eda/`  

---

## 1. Key Observed Trends (Direct Evidence)

### A. Transaction Volume and Monetary Value
- **Initial Soft Launch (Apr – Jun 2016):** 3 consecutive months with **0.00 Mn** volume and **₹0.00 Cr** value during the initial bank pilot integration.
- **First Commercial Recording (July 2016):** **0.09 Million transactions** valued at **₹0.38 Crore**.
- **Peak Monthly Volume:** **24,508.96 Million transactions** recorded in **2026-08-01** (August 2026).
- **Peak Monthly Value:** **₹2,990,424.21 Crore** recorded in **2026-05-01** (May 2026).
- **Latest Verified Month (2026-09-01):**
  - Volume: **24,068.38 Million transactions** (+22.59% YoY).
  - Value: **₹2,937,396.67 Crore** (+17.98% YoY).

### B. Banking Network Expansion
- **Network Inception (April 2016):** **21 live member banks**.
- **Network Current (September 2026):** **756 live member banks**.
- **Net Ecosystem Growth:** **+735 member banks** (a **3,500.0% increase**).

### C. Financial-Year Aggregations
| Financial Year | Status | Months | Total Volume (Mn) | Total Value (Cr INR) | Weighted Avg Ticket (INR) | YoY Vol Growth | YoY Val Growth |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2016-17** | Complete | 12 | 17.86 | ₹6,952.14 | ₹3,892.58 | — | — |
| **2017-18** | Complete | 12 | 915.22 | ₹109,831.80 | ₹1,200.06 | +5024.41% | +1479.83% |
| **2018-19** | Complete | 12 | 5,391.52 | ₹876,970.72 | ₹1,626.57 | +489.10% | +698.47% |
| **2019-20** | Complete | 12 | 12,518.61 | ₹2,131,730.14 | ₹1,702.85 | +132.19% | +143.08% |
| **2020-21** | Complete | 12 | 22,330.65 | ₹4,103,653.58 | ₹1,837.68 | +78.38% | +92.50% |
| **2021-22** | Complete | 12 | 45,967.53 | ₹8,417,572.48 | ₹1,831.20 | +105.85% | +105.12% |
| **2022-23** | Complete | 12 | 83,751.14 | ₹13,920,676.35 | ₹1,662.15 | +82.20% | +65.38% |
| **2023-24** | Complete | 12 | 131,129.83 | ₹19,995,085.51 | ₹1,524.83 | +56.57% | +43.64% |
| **2024-25** | Complete | 12 | 185,866.02 | ₹26,056,954.65 | ₹1,401.92 | +41.74% | +30.32% |
| **2025-26** | Complete | 12 | 241,616.88 | ₹31,423,249.71 | ₹1,300.54 | +30.00% | +20.59% |
| **2026-27** | Incomplete (6 Mo) | 6 | 140,500.49 | ₹17,693,184.04 | ₹1,259.30 | — | — |

> [!IMPORTANT]
> **FY 2026–27 Boundary Constraint:** FY 2026–27 currently covers only **6 months (April – September 2026)** with total volume of **140,500.49 Mn** and value of **₹17,693,184.04 Cr**. YoY growth is strictly marked **NULL/Undefined** because comparing 6 months of data against 12-month historical baselines produces invalid growth figures.

---

## 2. Core Business Observations (Grounded in Verified Data)

1. **Decoupling of Volume Growth and Ticket Size (P2M Shift):**
   - In early commercial adoption (FY 2016–17), weighted average ticket size was **₹3,892.58**.
   - As transaction volumes scaled exponentially past 100 Billion annually (FY 2023–24 onwards), average ticket size progressively compressed to **₹1,401.92 in FY 2024–25**, **₹1,300.54 in FY 2025–26**, and **₹1,259.30 in FY 2026–27 (H1)**.
   - *Observation:* This steady downward trend in average ticket size reflects widespread micro-transaction adoption (Person-to-Merchant retail payments, low-denomination daily transactions) rather than high-value P2P transfers alone.

2. **Transition from Hyper-Growth to Stable Macro Expansion:**
   - Following the initial rollout surge (FY 2017–18 YoY volume growth of +5,024.41%), UPI maintained triple-digit expansion through FY 2021–22 (+105.85% YoY volume growth).
   - In recent complete financial years, growth has moderated to a mature, compounding trajectory:
     - FY 2023–24: **+56.57% Volume**, **+43.64% Value**.
     - FY 2024–25: **+41.74% Volume**, **+30.32% Value**.
     - FY 2025–26: **+30.00% Volume**, **+20.59% Value**.
   - *Observation:* Despite the percentage moderation, absolute annual volume increments remain immense (+55.75 Billion transactions added in FY 2025–26 alone).

3. **Impact of the August 2018 Methodology Filter:**
   - In August 2018, NPCI implemented an operational exclusion of circular same-account debit/credit transactions (*Footnote: "this data excludes the transactions having debit/credit to the same account for the month of August 2018 onwards"*).
   - Reported volume rose from **273.75 Mn (July 2018)** to **312.02 Mn (August 2018)** (+13.98% MoM), while average ticket size shifted from **₹1,893.81** to **₹1,737.46**.
   - *Observation:* The platform's strong organic momentum absorbed the exclusion without an absolute contraction, but analysts must recognize that pre-August 2018 figures contain intra-account transfers absent from post-August 2018 metrics.

---

## 3. Generated Analysis Assets

The following files were created in `reports/python_eda/`:
- `monthly_metrics.csv` — Full 126-month SQL output dataset.
- `financial_year_metrics.csv` — 11-row financial year SQL aggregation dataset.
- `01_monthly_volume_trend.png` — High-resolution monthly transaction volume chart.
- `02_monthly_value_trend.png` — High-resolution monthly transaction value chart.
- `03_bank_count_trend.png` — Network bank adoption growth chart.
- `04_monthly_yoy_growth.png` — Two-panel monthly YoY volume and value percentage growth chart.
