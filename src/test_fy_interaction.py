import pandas as pd

df_m = pd.read_csv(r"D:\upi-growth-analysis\reports\python_eda\monthly_metrics.csv")
df_fy = pd.read_csv(r"D:\upi-growth-analysis\reports\python_eda\financial_year_metrics.csv")

print("FY 2025-26:")
fy25 = df_fy[df_fy["fy_label"] == "2025-26"].iloc[0]
print(f"  Months: {fy25['months_available']}, Complete: {fy25['is_complete']}, Vol: {fy25['total_volume_mn']} Mn ({fy25['total_volume_mn']/1000:.2f} Bn), Val: Rs {fy25['total_value_cr']} Cr ({fy25['total_value_cr']/100000:.2f} Lakh Cr)")

print("\nFY 2026-27:")
fy26 = df_fy[df_fy["fy_label"] == "2026-27"].iloc[0]
print(f"  Months: {fy26['months_available']}, Complete: {fy26['is_complete']}, Vol: {fy26['total_volume_mn']} Mn ({fy26['total_volume_mn']/1000:.2f} Bn), Val: Rs {fy26['total_value_cr']} Cr ({fy26['total_value_cr']/100000:.2f} Lakh Cr)")

# Monthly filter simulation
# FY 2025-26 runs from 2025-04-01 to 2026-03-31
m_25 = df_m[(df_m["month"] >= "2025-04-01") & (df_m["month"] <= "2026-03-31")]
print(f"\nMonths in FY 2025-26: {len(m_25)} (Expected 12)")
assert len(m_25) == 12

# FY 2026-27 runs from 2026-04-01 to 2026-09-30
m_26 = df_m[(df_m["month"] >= "2026-04-01") & (df_m["month"] <= "2026-09-30")]
print(f"Months in FY 2026-27: {len(m_26)} (Expected 6)")
assert len(m_26) == 6
print("FY date filter simulation verified!")
