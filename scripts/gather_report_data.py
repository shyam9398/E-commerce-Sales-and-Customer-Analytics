import pandas as pd, os

kpi = pd.read_csv("reports/kpi_summary.csv")
print("=== KPI SUMMARY ===")
print(kpi.to_string(index=False))

print()
print("=== CURRENCY BREAKDOWN ===")
cur = pd.read_csv("reports/kpi_revenue_by_currency.csv", index_col=0)
print(cur.to_string())

print()
print("=== VALIDATION ===")
val = pd.read_csv("reports/kpi_validation_report.csv")
print(f"Checks: {len(val)}  PASS: {(val['status'].isin(['PASS','PASS_WITH_NOTE'])).sum()}  FAIL: {(val['status']=='FAIL').sum()}")

print()
print("=== RETURN REASONS ===")
rr = pd.read_csv("reports/kpi_return_reasons.csv")
rr["pct"] = (rr["count"]/rr["count"].sum()*100).round(1)
print(rr.to_string(index=False))

print()
print("=== INSIGHTS ===")
ins = pd.read_csv("reports/business_insights_validated.csv")
for _, r in ins.iterrows():
    print(f"  {r['insight_id']}: {r['finding']}")
    print(f"    Status: {r['status']}")
    print(f"    Evidence: {str(r['measured_evidence'])[:200]}")
    print(f"    Implication: {str(r['business_implication'])[:180]}")
    print(f"    Limitation: {str(r['limitation'])[:160]}")
    print(f"    Action: {str(r['recommended_action'])[:180]}")
    print()

print()
print("=== FIGURES ===")
figs = sorted([f for f in os.listdir("reports") if f.endswith(".png")])
for f in figs:
    size = round(os.path.getsize(f"reports/{f}")/1024,1)
    print(f"  {f}  ({size} KB)")

print()
print("=== REGION TABLE ===")
reg = pd.read_csv("reports/kpi_by_region.csv", index_col=0)
print(reg.to_string())

print()
print("=== CHANNEL TABLE ===")
ch = pd.read_csv("reports/kpi_by_channel.csv", index_col=0)
print(ch.to_string())

print()
print("=== SEGMENT TABLE ===")
seg = pd.read_csv("reports/kpi_by_segment.csv", index_col=0)
print(seg.to_string())

print()
print("=== DELIVERY TABLE ===")
deliv = pd.read_csv("reports/kpi_delivery_by_method.csv", index_col=0)
print(deliv.to_string())
