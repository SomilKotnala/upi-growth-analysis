# Data Sources and Analytical Limitations

**Project:** UPI Growth Analysis  
**Last Verified:** October 2026  

---

## 1. Official Data Source & Attribution

- **Primary Source:** National Payments Corporation of India (NPCI)
- **Official URL:** [https://www.npci.org.in/product/upi/product-statistics](https://www.npci.org.in/product/upi/product-statistics)
- **Publisher Profile:** NPCI is an umbrella organization operating retail payments and settlement systems in India, an initiative of the Reserve Bank of India (RBI) and the Indian Banks' Association (IBA).
- **Required Citation:**  
  *“Data Source: National Payments Corporation of India (NPCI) — Unified Payments Interface (UPI) Product Statistics (Retrieved October 2026).”*

---

## 2. Raw Source Workbooks Inventory

The raw historical data was downloaded directly from the official portal and is preserved unchanged in `data/raw/`:

| Workbook File Name | Financial Year | Reporting Months Covered | Observations |
| :--- | :---: | :---: | :---: |
| `Product-Statistics-UPI-Product-statistics-upi-2016-17-Monthly.xlsx` | 2016-17 | April 2016 – March 2017 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2017-18-Monthly.xlsx` | 2017-18 | April 2017 – March 2018 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2018-19-Monthly.xlsx` | 2018-19 | April 2018 – March 2019 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2019-20-Monthly.xlsx` | 2019-20 | April 2019 – March 2020 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2020-21-Monthly.xlsx` | 2020-21 | April 2020 – March 2021 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2021-22-Monthly.xlsx` | 2021-22 | April 2021 – March 2022 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2022-23-Monthly.xlsx` | 2022-23 | April 2022 – March 2023 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2023-24-Monthly.xlsx` | 2023-24 | April 2023 – March 2024 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2024-25-Monthly.xlsx` | 2024-25 | April 2024 – March 2025 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2025-26-Monthly.xlsx` | 2025-26 | April 2025 – March 2026 | 12 |
| `Product-Statistics-UPI-Product-statistics-upi-2026-27-Monthly.xlsx` | 2026-27 | April 2026 – September 2026 | 6 |
| **Total** | **11 Workbooks** | **April 2016 – September 2026** | **126 Months** |

---

## 3. Reporting Units

The official figures use the Indian numbering and regulatory payment system units:
- **Volume:** Reported **In Millions** ($10^6$ transactions).
- **Value:** Reported **In Crores INR** ($10^7$ Indian Rupees, where $1\text{ Crore} = 10,000,000\text{ INR}$).
- **Bank Count:** Discrete count of member banks live on the network during that reporting period.

---

## 4. Methodological Shift (August 2018 Footnote)

On the official NPCI Product Statistics page, the following official footnote is documented:

> *“This data excludes the transactions having debit/credit to the same account for the month of August 2018 onwards.”*

### Analytical Implications:
1. **Pre-August 2018 (April 2016 – July 2018):** Reported statistics included circular or self-transfers where the debiting and crediting accounts were identical (such as internal bank test pings or same-account verification transfers).
2. **Post-August 2018 (August 2018 – Present):** NPCI revised its filtering logic to strictly report distinct inter-account transactions.
3. **Impact on Metrics:** This structural break artificially deflates Month-over-Month (MoM) growth between July 2018 and August 2018. Analysts evaluating growth trajectories around Q2/Q3 2018 must account for this methodology shift rather than interpreting the change as an organic adoption drop.

---

## 5. Source Value Formatting Anomaly (April 2026)

In the raw workbook for FY 2026-27 (`Product-Statistics-UPI-Product-statistics-upi-2026-27-Monthly.xlsx`), the monetary transaction value for `April-2026` is formatted as:
`'29,029,88.05'`

### Context & Resolution:
- Standard Indian currency formatting follows a 3-2-2 digit grouping (e.g. `29,02,988.05` for twenty-nine lakh two thousand nine hundred eighty-eight Crore).
- The raw cell text contains an extraneous digit in the thousands group (`029`).
- When sanitized by removing comma delimiters, the resulting float is `2902988.05` (~₹29.03 Lakh Crore).
- This aligns with the adjacent verified monthly values:
  - May 2026: `29,90,424.21` (~₹29.90 Lakh Crore)
  - June 2026: `28,92,138.67` (~₹28.92 Lakh Crore)
  - July 2026: `29,87,880.49` (~₹29.88 Lakh Crore)
- **Policy:** The original raw Excel file has been left completely unaltered. The cleaning pipeline handles the formatting discrepancy automatically by sanitizing punctuation before numeric conversion.

---

## 6. Licensing and Terms of Use

- **Copyright Notice:** `© 2025 NPCI. All rights reserved. Corporate Identity Number (CIN): U74990MH2008NPL189067`.
- **Usage Policy:** Statistics are published by NPCI for public informational and regulatory disclosure. Public availability does not imply public domain dedication or unrestricted commercial redistribution.
- **Project Boundary:** This project utilizes the figures solely for educational, non-commercial analytical research and portfolio demonstration. Full attribution to NPCI is retained across all documentation and outputs.
