"""
Step 4: Exploratory Data Analysis (EDA) and KPI Calculation
E-commerce BI Project
Source: data/cleaned_ecommerce.csv  (138,116 rows x 49 cols)
"""

import pandas as pd
import numpy as np
import os, json

pd.set_option("display.max_columns", 60)
pd.set_option("display.width", 200)
pd.set_option("display.float_format", "{:,.2f}".format)

# ── paths ────────────────────────────────────────────────────────────────────
CLEAN   = "data/cleaned_ecommerce.csv"
REPORTS = "reports"
os.makedirs(REPORTS, exist_ok=True)

# ── load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(CLEAN, parse_dates=["order_date"],
                 dtype={"customer_postal_code": str})

DIVIDER = "=" * 65

def section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1 — DATASET OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
section("TASK 1 — DATASET OVERVIEW")

print(f"\nRows: {len(df):,}   Columns: {df.shape[1]}")
print(f"Date range: {df['order_date'].min().date()}  to  {df['order_date'].max().date()}")

for col in ["order_status", "region", "sales_channel",
            "customer_segment", "currency", "payment_status"]:
    vc = df[col].value_counts()
    print(f"\n--- {col} ---")
    pct = (vc / len(df) * 100).round(1)
    out = pd.DataFrame({"count": vc, "pct": pct})
    print(out.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# TASK 2 & 3 — BUSINESS KPIs  (with financial-correctness discipline)
# ─────────────────────────────────────────────────────────────────────────────
section("TASK 2+3 — BUSINESS KPIs")

# Scope decisions (documented):
#   • "Revenue" KPIs  → Completed orders, any payment_status
#     (Cancelled/Pending/Returned revenue is not yet realised)
#   • "Return rate"   → denominator = Completed + Returned
#   • "Cancel rate"   → denominator = all orders
#   • Currency: computed separately per currency; USD summary shown with label
#   • Negative profit is valid — kept in aggregates

comp  = df[df["order_status"] == "Completed"]
ret   = df[df["order_status"] == "Returned"]
canc  = df[df["order_status"] == "Cancelled"]
pend  = df[df["order_status"] == "Pending"]

print(f"\n{'KPI':<45} {'Value':>15}")
print("-" * 62)

# — Order counts —
total_orders = len(df)
print(f"{'Total orders (all statuses)':<45} {total_orders:>15,}")
for s in ["Completed", "Returned", "Cancelled", "Pending"]:
    n = (df["order_status"] == s).sum()
    p = n / total_orders * 100
    print(f"  {s + ' orders':<43} {n:>12,}  ({p:.1f}%)")

# — Rates —
return_rate = len(ret) / (len(comp) + len(ret)) * 100
cancel_rate = len(canc) / total_orders * 100
print(f"{'Return rate  (Returned / Completed+Returned)':<45} {return_rate:>14.2f}%")
print(f"{'Cancellation rate  (Cancelled / all orders)':<45} {cancel_rate:>14.2f}%")

# — Revenue (Completed only, all currencies pooled, clearly labelled) —
print(f"\n--- Revenue  [Completed orders, multi-currency totals labelled] ---")
gross  = comp["gross_sales"].sum()
disc   = comp["discount_amount"].sum()
tax    = comp["tax_amount"].sum()
ship   = comp["shipping_cost"].sum()
net    = comp["net_sales"].sum()
cost   = comp["product_cost"].sum()
profit = comp["profit"].sum()

print(f"{'Gross sales (Completed)':<45} {gross:>15,.2f}")
print(f"{'Discount amount':<45} {disc:>15,.2f}")
print(f"{'Tax amount':<45} {tax:>15,.2f}")
print(f"{'Shipping cost':<45} {ship:>15,.2f}")
print(f"{'Net sales (= gross - disc + tax + ship)':<45} {net:>15,.2f}")
print(f"{'Product cost':<45} {cost:>15,.2f}")
print(f"{'Total profit':<45} {profit:>15,.2f}")
print(f"{'Profit margin  (profit / net_sales * 100)':<45} {profit/net*100:>14.2f}%")

# — Revenue by currency (Completed) —
print("\n--- Revenue by currency (Completed orders) ---")
cur_rev = comp.groupby("currency").agg(
    orders=("order_id", "count"),
    gross_sales=("gross_sales", "sum"),
    net_sales=("net_sales", "sum"),
    profit=("profit", "sum"),
).sort_values("net_sales", ascending=False)
cur_rev["margin_%"] = (cur_rev["profit"] / cur_rev["net_sales"] * 100).round(2)
print(cur_rev.to_string())
cur_rev.to_csv(f"{REPORTS}/kpi_revenue_by_currency.csv")

# — AOV —
aov_gross = comp["gross_sales"].mean()
aov_net   = comp["net_sales"].mean()
print(f"\n{'Avg Order Value — gross (Completed)':<45} {aov_gross:>15,.2f}")
print(f"{'Avg Order Value — net   (Completed)':<45} {aov_net:>15,.2f}")

# — Profit margin on all Completed orders —
pos_margin = (comp["profit"] >= 0).sum()
neg_margin = (comp["profit"] <  0).sum()
print(f"\n{'Completed orders with positive profit':<45} {pos_margin:>12,}")
print(f"{'Completed orders with negative profit':<45} {neg_margin:>12,}")

# ─────────────────────────────────────────────────────────────────────────────
# Monthly revenue & profit trend (Completed, all currencies pooled)
# ─────────────────────────────────────────────────────────────────────────────
section("MONTHLY REVENUE & PROFIT TREND  (Completed, all currencies)")

monthly = (
    comp.groupby(["order_year", "order_month"])
    .agg(orders=("order_id","count"),
         gross_sales=("gross_sales","sum"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"),
         avg_rating=("customer_rating","mean"))
    .reset_index()
)
monthly["period"] = monthly["order_year"].astype(str) + "-" + monthly["order_month"].astype(str).str.zfill(2)
monthly["margin_%"] = (monthly["profit"] / monthly["net_sales"] * 100).round(2)
monthly = monthly.sort_values("period")
print(monthly[["period","orders","gross_sales","net_sales","profit","margin_%"]].to_string(index=False))
monthly.to_csv(f"{REPORTS}/kpi_monthly_trend.csv", index=False)

# ─────────────────────────────────────────────────────────────────────────────
# Revenue & profit by region
# ─────────────────────────────────────────────────────────────────────────────
section("REVENUE & PROFIT BY REGION  (Completed)")

by_region = (
    comp.groupby("region")
    .agg(orders=("order_id","count"),
         gross_sales=("gross_sales","sum"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"),
         avg_aov=("net_sales","mean"))
    .sort_values("net_sales", ascending=False)
)
by_region["margin_%"] = (by_region["profit"] / by_region["net_sales"] * 100).round(2)
print(by_region.to_string())
by_region.to_csv(f"{REPORTS}/kpi_by_region.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Revenue & profit by sales channel
# ─────────────────────────────────────────────────────────────────────────────
section("REVENUE & PROFIT BY SALES CHANNEL  (Completed)")

by_channel = (
    comp.groupby("sales_channel")
    .agg(orders=("order_id","count"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"),
         avg_aov=("net_sales","mean"))
    .sort_values("net_sales", ascending=False)
)
by_channel["margin_%"] = (by_channel["profit"] / by_channel["net_sales"] * 100).round(2)
print(by_channel.to_string())
by_channel.to_csv(f"{REPORTS}/kpi_by_channel.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Customer segment analysis
# ─────────────────────────────────────────────────────────────────────────────
section("CUSTOMER SEGMENT ANALYSIS  (all statuses)")

by_seg = (
    df.groupby("customer_segment")
    .agg(total_orders=("order_id","count"),
         unique_customers=("customer_id","nunique"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"),
         avg_clv=("customer_lifetime_value","mean"),
         avg_order_count=("customer_order_count","mean"),
         repeat_rate=("is_repeat_customer","mean"))
    .sort_values("net_sales", ascending=False)
)
by_seg["margin_%"] = (by_seg["profit"] / by_seg["net_sales"] * 100).round(2)
by_seg["repeat_rate_%"] = (by_seg["repeat_rate"] * 100).round(1)
by_seg.drop(columns=["repeat_rate"], inplace=True)
print(by_seg.to_string())
by_seg.to_csv(f"{REPORTS}/kpi_by_segment.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Repeat-purchase analysis
# ─────────────────────────────────────────────────────────────────────────────
section("REPEAT PURCHASE ANALYSIS  (all statuses)")

repeat_counts = df["is_repeat_customer"].value_counts()
repeat_pcts   = (repeat_counts / len(df) * 100).round(1)
print(pd.DataFrame({"count": repeat_counts, "pct": repeat_pcts}).to_string())

# order count distribution
print("\nCustomer order count distribution:")
ocd = df["customer_order_count"].value_counts().sort_index()
print(ocd.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# Return analysis
# ─────────────────────────────────────────────────────────────────────────────
section("RETURN ANALYSIS  (Returned orders only)")

print(f"\nTotal Returned orders: {len(ret):,}")
print(f"Return rate vs Completed+Returned: {return_rate:.2f}%")

if "return_reason" in ret.columns:
    # return_reason was read as float (all NaN) for non-returned; cast object
    ret_reason = df[df["return_status"].notna()]["return_reason"]
    if ret_reason.dtype == object:
        rr = ret_reason.value_counts()
        print("\nReturn reasons:")
        print(rr.to_string())
    else:
        print("\nreturn_reason column appears to be non-string; skipping breakdown.")

# Return rate by region
ret_by_region = (
    df[df["order_status"].isin(["Completed","Returned"])]
    .groupby("region")["order_status"]
    .apply(lambda s: (s == "Returned").sum() / len(s) * 100)
    .round(2)
    .rename("return_rate_%")
)
print("\nReturn rate by region:")
print(ret_by_region.to_string())
ret_by_region.to_csv(f"{REPORTS}/kpi_return_rate_by_region.csv")

# Return rate by sales channel
ret_by_ch = (
    df[df["order_status"].isin(["Completed","Returned"])]
    .groupby("sales_channel")["order_status"]
    .apply(lambda s: (s == "Returned").sum() / len(s) * 100)
    .round(2)
    .rename("return_rate_%")
)
print("\nReturn rate by sales channel:")
print(ret_by_ch.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# Delivery performance
# ─────────────────────────────────────────────────────────────────────────────
section("DELIVERY PERFORMANCE  (Completed + Returned where delivery_days populated)")

delivered = df[df["delivery_days"].notna() & df["order_status"].isin(["Completed","Returned"])]
print(f"\nOrders with delivery data: {len(delivered):,}")

avg_delivery  = delivered["delivery_days"].mean()
avg_estimated = delivered["estimated_delivery_days"].mean()
on_time_n     = (delivered["delivery_status"] == "On Time").sum()
delayed_n     = (delivered["delivery_status"] == "Delayed").sum()
on_time_rate  = on_time_n / len(delivered) * 100

print(f"{'Avg actual delivery days':<45} {avg_delivery:>10.2f}")
print(f"{'Avg estimated delivery days':<45} {avg_estimated:>10.2f}")
print(f"{'On-time deliveries':<45} {on_time_n:>10,}  ({on_time_rate:.1f}%)")
print(f"{'Delayed deliveries':<45} {delayed_n:>10,}  ({100-on_time_rate:.1f}%)")

print("\nDelivery status distribution (full dataset with data):")
ds_all = df[df["delivery_days"].notna()]["delivery_status"].value_counts()
print(ds_all.to_string())

# By shipping method
ship_perf = (
    delivered.groupby("shipping_method")
    .agg(orders=("order_id","count"),
         avg_days=("delivery_days","mean"),
         avg_est=("estimated_delivery_days","mean"),
         on_time_pct=("delivery_status", lambda s: (s=="On Time").mean()*100))
    .round(2)
    .sort_values("avg_days")
)
print("\nDelivery performance by shipping method:")
print(ship_perf.to_string())
ship_perf.to_csv(f"{REPORTS}/kpi_delivery_by_method.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Customer ratings
# ─────────────────────────────────────────────────────────────────────────────
section("CUSTOMER RATINGS  (Completed orders only, where rating present)")

rated = comp[comp["customer_rating"].notna()]
print(f"\nOrders with ratings: {len(rated):,}  out of {len(comp):,} Completed")
print(f"Rating coverage: {len(rated)/len(comp)*100:.1f}%")

avg_rating = rated["customer_rating"].mean()
print(f"Average customer rating: {avg_rating:.3f} / 5.0")
print("\nRating distribution:")
rating_dist = rated["customer_rating"].value_counts().sort_index()
rating_pct  = (rating_dist / len(rated) * 100).round(1)
print(pd.DataFrame({"count": rating_dist, "pct_%": rating_pct}).to_string())

print("\nSentiment distribution:")
sent = rated["review_sentiment"].value_counts()
sent_pct = (sent / len(rated) * 100).round(1)
print(pd.DataFrame({"count": sent, "pct_%": sent_pct}).to_string())

# Rating by segment
rating_seg = rated.groupby("customer_segment")["customer_rating"].agg(["mean","count"]).round(3)
print("\nAvg rating by customer segment:")
print(rating_seg.to_string())

# ─────────────────────────────────────────────────────────────────────────────
# Marketing channel analysis
# ─────────────────────────────────────────────────────────────────────────────
section("MARKETING CHANNEL ANALYSIS  (Completed)")

mkt = (
    comp.groupby("marketing_channel")
    .agg(orders=("order_id","count"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"),
         avg_aov=("net_sales","mean"),
         avg_clv=("customer_lifetime_value","mean"))
    .sort_values("net_sales", ascending=False)
)
mkt["margin_%"] = (mkt["profit"] / mkt["net_sales"] * 100).round(2)
print(mkt.to_string())
mkt.to_csv(f"{REPORTS}/kpi_by_marketing_channel.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Payment method & status
# ─────────────────────────────────────────────────────────────────────────────
section("PAYMENT METHOD ANALYSIS  (all statuses)")

pay = (
    df.groupby(["payment_method","payment_status"])
    .agg(orders=("order_id","count"))
    .reset_index()
    .sort_values("orders", ascending=False)
)
print(pay.to_string(index=False))
pay.to_csv(f"{REPORTS}/kpi_payment_methods.csv", index=False)

# ─────────────────────────────────────────────────────────────────────────────
# Discount usage
# ─────────────────────────────────────────────────────────────────────────────
section("DISCOUNT ANALYSIS  (Completed)")

disc_used  = (comp["discount_amount"] > 0).sum()
disc_pct   = disc_used / len(comp) * 100
avg_disc   = comp[comp["discount_amount"] > 0]["discount_amount"].mean()
avg_disc_r = (comp["discount_amount"] / comp["gross_sales"] * 100).mean()

print(f"Orders with discount > 0: {disc_used:,}  ({disc_pct:.1f}%)")
print(f"Avg discount amount (when applied): {avg_disc:,.2f}")
print(f"Avg discount rate vs gross_sales: {avg_disc_r:.2f}%")

coupon_used  = comp["coupon_code"].notna().sum()
coupon_pct   = coupon_used / len(comp) * 100
print(f"Orders with coupon code: {coupon_used:,}  ({coupon_pct:.1f}%)")

# ─────────────────────────────────────────────────────────────────────────────
# Loyalty points
# ─────────────────────────────────────────────────────────────────────────────
section("LOYALTY POINTS  (Completed)")

avg_earned   = comp["loyalty_points_earned"].mean()
avg_redeemed = comp["loyalty_points_redeemed"].mean()
total_earned = comp["loyalty_points_earned"].sum()
total_redeemed = comp["loyalty_points_redeemed"].sum()
redemption_rate = total_redeemed / total_earned * 100

print(f"Total points earned:    {total_earned:>15,}")
print(f"Total points redeemed:  {total_redeemed:>15,}")
print(f"Redemption rate:        {redemption_rate:>14.1f}%")
print(f"Avg points earned/order:{avg_earned:>15.1f}")
print(f"Avg points redeemed/order:{avg_redeemed:>13.1f}")

# ─────────────────────────────────────────────────────────────────────────────
# Age & gender demographics
# ─────────────────────────────────────────────────────────────────────────────
section("DEMOGRAPHICS  (all orders)")

print("\nGender distribution:")
gen = df["gender"].value_counts()
gen_pct = (gen / len(df) * 100).round(1)
print(pd.DataFrame({"count": gen, "pct_%": gen_pct}).to_string())

print(f"\nAge summary:")
print(df["customer_age"].describe().to_string())

age_bins = pd.cut(df["customer_age"],
                  bins=[17,29,39,49,59,74],
                  labels=["18-29","30-39","40-49","50-59","60-74"])
print("\nAge group distribution:")
ag = age_bins.value_counts().sort_index()
ag_pct = (ag / len(df) * 100).round(1)
print(pd.DataFrame({"count": ag, "pct_%": ag_pct}).to_string())

# ─────────────────────────────────────────────────────────────────────────────
# Top countries
# ─────────────────────────────────────────────────────────────────────────────
section("TOP 10 COUNTRIES BY NET SALES  (Completed)")

top_countries = (
    comp.groupby("customer_country")
    .agg(orders=("order_id","count"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"))
    .sort_values("net_sales", ascending=False)
    .head(10)
)
top_countries["margin_%"] = (top_countries["profit"] / top_countries["net_sales"] * 100).round(2)
print(top_countries.to_string())
top_countries.to_csv(f"{REPORTS}/kpi_top_countries.csv")

# ─────────────────────────────────────────────────────────────────────────────
# Warehouse utilisation
# ─────────────────────────────────────────────────────────────────────────────
section("WAREHOUSE UTILISATION  (all orders)")

wh = df["warehouse"].value_counts().reset_index()
wh.columns = ["warehouse","orders"]
wh["pct_%"] = (wh["orders"] / len(df) * 100).round(1)
print(wh.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# SAVE CONSOLIDATED KPI SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
section("SAVING KPI SUMMARY")

kpi_summary = pd.DataFrame([
    {"kpi": "total_orders",                        "value": total_orders,           "scope": "all statuses"},
    {"kpi": "completed_orders",                    "value": len(comp),              "scope": "Completed"},
    {"kpi": "returned_orders",                     "value": len(ret),               "scope": "Returned"},
    {"kpi": "cancelled_orders",                    "value": len(canc),              "scope": "Cancelled"},
    {"kpi": "pending_orders",                      "value": len(pend),              "scope": "Pending"},
    {"kpi": "return_rate_%",                       "value": round(return_rate,2),   "scope": "Returned/(Completed+Returned)"},
    {"kpi": "cancellation_rate_%",                 "value": round(cancel_rate,2),   "scope": "Cancelled/all"},
    {"kpi": "gross_sales_completed_multiccy",      "value": round(gross,2),         "scope": "Completed, multi-currency"},
    {"kpi": "net_sales_completed_multiccy",        "value": round(net,2),           "scope": "Completed, multi-currency"},
    {"kpi": "total_profit_completed_multiccy",     "value": round(profit,2),        "scope": "Completed, multi-currency"},
    {"kpi": "overall_profit_margin_%",             "value": round(profit/net*100,2),"scope": "Completed"},
    {"kpi": "avg_order_value_gross_completed",     "value": round(aov_gross,2),     "scope": "Completed"},
    {"kpi": "avg_order_value_net_completed",       "value": round(aov_net,2),       "scope": "Completed"},
    {"kpi": "negative_profit_completed_orders",    "value": neg_margin,             "scope": "Completed"},
    {"kpi": "avg_delivery_days",                   "value": round(avg_delivery,2),  "scope": "Completed+Returned with data"},
    {"kpi": "avg_estimated_delivery_days",         "value": round(avg_estimated,2), "scope": "Completed+Returned with data"},
    {"kpi": "on_time_delivery_rate_%",             "value": round(on_time_rate,2),  "scope": "Completed+Returned with data"},
    {"kpi": "avg_customer_rating",                 "value": round(avg_rating,3),    "scope": "Completed, rated orders"},
    {"kpi": "rating_coverage_%",                   "value": round(len(rated)/len(comp)*100,1), "scope": "Completed"},
    {"kpi": "discount_usage_rate_%",               "value": round(disc_pct,2),      "scope": "Completed"},
    {"kpi": "avg_discount_rate_%",                 "value": round(avg_disc_r,2),    "scope": "Completed"},
    {"kpi": "coupon_usage_rate_%",                 "value": round(coupon_pct,2),    "scope": "Completed"},
    {"kpi": "loyalty_redemption_rate_%",           "value": round(redemption_rate,1),"scope": "Completed"},
    {"kpi": "repeat_customer_rate_%",              "value": round(df["is_repeat_customer"].mean()*100,1), "scope": "all"},
])

kpi_summary.to_csv(f"{REPORTS}/kpi_summary.csv", index=False)
print(f"\nKPI summary saved -> {REPORTS}/kpi_summary.csv  ({len(kpi_summary)} KPIs)")
print("\n" + kpi_summary.to_string(index=False))

print(f"\n{DIVIDER}")
print("  EDA COMPLETE — all CSVs saved to reports/")
print(DIVIDER)
