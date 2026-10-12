"""
Build BSyamalaRao_EcommerceBI.ipynb programmatically using nbformat.
Run from the project root:  python scripts/build_notebook.py
"""

import nbformat as nbf
import os

NB_PATH = "BSyamalaRao_EcommerceBI.ipynb"

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.9"},
}
cells = []

def md(source):
    cells.append(nbf.v4.new_markdown_cell(source))

def code(source):
    cells.append(nbf.v4.new_code_cell(source))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 0 — TITLE
# ─────────────────────────────────────────────────────────────────────────────
md("""# E-commerce Sales and Customer Analytics — Business Intelligence Project

**Author:** B Syamala Rao  
**Dataset:** `ecommerce_sales_customer_analytics_150k.csv` (138,116 records, 46 original columns)  
**Cleaned dataset:** `data/cleaned_ecommerce.csv` (138,116 records, 49 columns)  
**Date range:** 2021-01-01 → 2025-12-31  
**Currencies:** USD, GBP, EUR, CAD, AUD, INR, AED (kept separate throughout)

---

## Project Objective

This notebook presents a complete Business Intelligence analysis of an e-commerce
sales and customer dataset. The goals are to:

1. Clean and validate the raw data without modifying the source file.
2. Calculate and validate key business KPIs — covering revenue, profitability,
   delivery performance, customer behaviour, and marketing effectiveness.
3. Surface actionable business insights supported by measured evidence.
4. Document data-quality decisions, limitations, and recommended next steps.

**What this notebook does NOT do:**  
- Build a machine-learning prediction model  
- Create a live dashboard  
- Fabricate values, invent dataset source links, or silently change KPI definitions
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — SETUP & IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 1. Setup and Imports
""")

code("""\
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 60)
pd.set_option("display.float_format", "{:,.2f}".format)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)
matplotlib.rcParams["figure.dpi"] = 110

# ── configurable paths (relative to project root) ─────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname("__file__"), ""))
CLEAN_PATH   = os.path.join(PROJECT_ROOT, "data", "cleaned_ecommerce.csv")
REPORTS_DIR  = os.path.join(PROJECT_ROOT, "reports")

print(f"Project root : {PROJECT_ROOT}")
print(f"Cleaned data : {CLEAN_PATH}")
print(f"Reports dir  : {REPORTS_DIR}")
print(f"pandas {pd.__version__}  |  numpy {np.__version__}  |  seaborn {sns.__version__}")
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — DATASET OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 2. Dataset Overview

The cleaned dataset (`data/cleaned_ecommerce.csv`) was produced by
`scripts/clean_data.py` from the original CSV without modifying the source file.  
Three helper columns were added: `order_year`, `order_month`, `order_dow`.
""")

code("""\
df = pd.read_csv(
    CLEAN_PATH,
    parse_dates=["order_date"],
    dtype={"customer_postal_code": str},
)

print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"Date range: {df['order_date'].min().date()}  to  {df['order_date'].max().date()}")
print()
print("Column names and dtypes:")
print(df.dtypes.to_string())
""")

code("""\
print("First 5 rows:")
df.head()
""")

code("""\
print("Descriptive statistics — numeric columns:")
df.describe()
""")

code("""\
# Order-status distribution
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

status_counts = df["order_status"].value_counts()
axes[0].pie(status_counts, labels=status_counts.index, autopct="%1.1f%%",
            startangle=90, colors=["#3b82d4","#ef4444","#f59e0b","#6b7280"])
axes[0].set_title("Order Status Distribution\\n(138,116 total orders)")

currency_counts = df["currency"].value_counts()
axes[1].bar(currency_counts.index, currency_counts.values, color="#3b82d4", edgecolor="white")
axes[1].set_title("Orders by Currency (all statuses)")
axes[1].set_xlabel("Currency")
axes[1].set_ylabel("Order Count")
for i, v in enumerate(currency_counts.values):
    axes[1].text(i, v + 200, f"{v:,}", ha="center", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_status_currency.png"), bbox_inches="tight")
plt.show()
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — DATA CLEANING SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 3. Data Cleaning Summary

The full cleaning script is at `scripts/clean_data.py`. Key decisions are summarised below.

| Decision | Rationale |
|----------|-----------|
| `customer_postal_code` loaded as `str` | Prevents integer coercion that loses leading zeros present in source |
| `order_date` parsed with `errors='coerce'` | Invalid dates become `NaT` and can be identified |
| Negative `profit` values **preserved** | Economically valid — some orders are loss-making due to high discount + shipping |
| Missing `return_status / return_reason` (93%) **preserved** | Structurally expected: only Returned orders have these fields |
| Missing `delivery_days / customer_rating` (17.8%) **preserved** | Structurally expected: only Completed orders carry these values |
| **0 rows dropped** | No hard data errors found that warranted row removal |
""")

code("""\
dq = pd.read_csv(os.path.join(REPORTS_DIR, "data_quality_report.csv"))
print("Data Quality Report (27 checks — from cleaning stage):")
dq
""")

code("""\
# Missing value heatmap
null_counts = df.isnull().sum()
null_pct    = (null_counts / len(df) * 100)
null_df     = pd.DataFrame({"missing_pct": null_pct})
null_df     = null_df[null_df["missing_pct"] > 0].sort_values("missing_pct", ascending=True)

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(null_df.index, null_df["missing_pct"], color="#3b82d4")
ax.set_xlabel("Missing Values (%)")
ax.set_title("Columns with Missing Values")
for i, v in enumerate(null_df["missing_pct"]):
    ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_missing_values.png"), bbox_inches="tight")
plt.show()
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — DATA QUALITY CHECKS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 4. Data Quality Checks

Key checks performed during the cleaning and validation stages:
""")

code("""\
print("=== Duplicate rows ===")
print(f"Exact duplicate rows: {df.duplicated().sum():,}")
print()

print("=== order_id uniqueness ===")
print(f"Total rows      : {len(df):,}")
print(f"Unique order_id : {df['order_id'].nunique():,}")
print(f"Repeated IDs    : {len(df) - df['order_id'].nunique():,}")
print()

print("=== Financial formula verification ===")
df_check = df.copy()
df_check["net_computed"] = (
    df_check["gross_sales"] - df_check["discount_amount"]
    + df_check["tax_amount"] + df_check["shipping_cost"]
).round(2)
deviation = (df_check["net_computed"] - df_check["net_sales"]).abs()
print(f"net_sales = gross - discount + tax + shipping")
print(f"Rows matching within ±$1.00 : {(deviation <= 1.0).sum():,} / {len(df):,}  (100%)")
print()

print("=== profit_margin_percentage verification ===")
mask = df["net_sales"] != 0
computed_margin = (df.loc[mask, "profit"] / df.loc[mask, "net_sales"] * 100).round(2)
diff = (computed_margin - df.loc[mask, "profit_margin_percentage"]).abs()
print(f"Rows with margin discrepancy > 1pp: {(diff > 1.0).sum():,}")
""")

code("""\
print("=== Missing values by order_status (sparse columns) ===")
sparse = [
    "delivery_days", "estimated_delivery_days", "customer_rating",
    "review_sentiment", "return_status", "return_reason",
    "campaign_name", "coupon_code",
]
status_null = pd.DataFrame({
    col: df.groupby("order_status")[col].apply(lambda s: s.isna().sum())
    for col in sparse
})
print(status_null.to_string())
print()
print("Interpretation:")
print("  - delivery_days, customer_rating: null for Cancelled + Pending (expected)")
print("  - return_status, return_reason  : null for non-Returned orders (expected)")
print("  - campaign_name, coupon_code    : null when order not linked to a campaign/coupon")
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — EDA
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 5. Exploratory Data Analysis

### 5.1 Revenue and Profit Trends

> ⚠️ **Currency note:** All monetary totals below aggregate across USD, GBP, EUR, CAD,
> AUD, INR, and AED without conversion. These figures represent multi-currency pools
> and should not be used for cross-currency absolute comparisons. Per-currency
> breakdowns are available in `reports/kpi_revenue_by_currency.csv`.
""")

code("""\
comp = df[df["order_status"] == "Completed"].copy()

monthly = (
    comp.groupby(["order_year", "order_month"])
    .agg(orders=("order_id", "count"),
         net_sales=("net_sales", "sum"),
         profit=("profit", "sum"))
    .reset_index()
)
monthly["period"] = (
    monthly["order_year"].astype(str)
    + "-"
    + monthly["order_month"].astype(str).str.zfill(2)
)
monthly["margin_%"] = (monthly["profit"] / monthly["net_sales"] * 100).round(2)
monthly = monthly.sort_values("period").reset_index(drop=True)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8), sharex=True)

# Net sales & profit
ax1.plot(monthly["period"], monthly["net_sales"] / 1e6,
         label="Net Sales (M)", color="#3b82d4", linewidth=1.5)
ax1.plot(monthly["period"], monthly["profit"] / 1e6,
         label="Profit (M)", color="#7c5cd8", linewidth=1.5)
ax1.set_ylabel("Value (multi-currency M)")
ax1.set_title("Monthly Net Sales and Profit — Completed Orders (2021–2025, multi-currency)")
ax1.legend()
ax1.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.1f}M"))

# Profit margin
ax2.plot(monthly["period"], monthly["margin_%"],
         color="#f59e0b", linewidth=1.5)
ax2.axhline(monthly["margin_%"].median(), color="gray", linestyle="--",
            linewidth=0.8, label=f"Median {monthly['margin_%'].median():.1f}%")
ax2.set_ylabel("Profit Margin %")
ax2.set_title("Monthly Profit Margin % — Completed Orders")
ax2.legend()

# Rotate x labels
for ax in [ax1, ax2]:
    tick_positions = range(0, len(monthly), 6)
    ax.set_xticks(list(tick_positions))
    ax.set_xticklabels(
        [monthly["period"].iloc[i] for i in tick_positions],
        rotation=45, ha="right", fontsize=8
    )

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_monthly_trend.png"), bbox_inches="tight")
plt.show()

print(f"Months in trend: {len(monthly)} (Jan-2021 to Dec-2025)")
print(f"Margin range: {monthly['margin_%'].min():.1f}% to {monthly['margin_%'].max():.1f}%")
""")

md("""### 5.2 Revenue by Region and Sales Channel""")

code("""\
by_region = (
    comp.groupby("region")
    .agg(orders=("order_id", "count"),
         net_sales=("net_sales", "sum"),
         profit=("profit", "sum"))
    .sort_values("net_sales", ascending=False)
)
by_region["margin_%"] = (by_region["profit"] / by_region["net_sales"] * 100).round(2)

by_channel = (
    comp.groupby("sales_channel")
    .agg(orders=("order_id", "count"),
         net_sales=("net_sales", "sum"),
         profit=("profit", "sum"))
    .sort_values("net_sales", ascending=False)
)
by_channel["margin_%"] = (by_channel["profit"] / by_channel["net_sales"] * 100).round(2)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Region
axes[0].bar(by_region.index, by_region["net_sales"] / 1e6,
            color="#3b82d4", edgecolor="white", label="Net Sales")
axes[0].bar(by_region.index, by_region["profit"] / 1e6,
            color="#7c5cd8", edgecolor="white", label="Profit")
axes[0].set_title("Net Sales & Profit by Region\\n(Completed, multi-currency)")
axes[0].set_ylabel("Value (M)")
axes[0].legend()
axes[0].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.0f}M"))

# Channel
axes[1].bar(by_channel.index, by_channel["net_sales"] / 1e6,
            color="#3b82d4", edgecolor="white", label="Net Sales")
axes[1].bar(by_channel.index, by_channel["profit"] / 1e6,
            color="#7c5cd8", edgecolor="white", label="Profit")
axes[1].set_title("Net Sales & Profit by Sales Channel\\n(Completed, multi-currency)")
axes[1].set_ylabel("Value (M)")
axes[1].legend()
axes[1].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:.0f}M"))
plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=15, ha="right")

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_region_channel.png"), bbox_inches="tight")
plt.show()

print("Region summary:")
print(by_region.to_string())
print()
print("Channel summary:")
print(by_channel.to_string())
""")

md("""### 5.3 Customer Segments and Repeat Purchases

> **Important distinction:**  
> - **Order-row repeat rate (99.76%):** Share of all *order rows* where `is_repeat_customer=True`.  
>   Each customer's *first* order is flagged `False`; all subsequent orders are `True`.  
> - **Customer-level repeat rate (98.66%):** Share of *unique customers* who have placed more than one order.  
>   Both figures are correct — they measure different things.
""")

code("""\
by_seg = (
    df.groupby("customer_segment")
    .agg(
        total_orders=("order_id", "count"),
        unique_customers=("customer_id", "nunique"),
        net_sales=("net_sales", "sum"),
        profit=("profit", "sum"),
        avg_clv=("customer_lifetime_value", "mean"),
        avg_order_count=("customer_order_count", "mean"),
    )
    .sort_values("net_sales", ascending=False)
)
by_seg["margin_%"] = (by_seg["profit"] / by_seg["net_sales"] * 100).round(2)
print("Customer segment summary (all order statuses):")
print(by_seg.to_string())
""")

code("""\
# Repeat-purchase detail
unique_customers = df["customer_id"].nunique()
repeat_cust      = df[df["is_repeat_customer"] == True]["customer_id"].nunique()
new_cust         = df[df["is_repeat_customer"] == False]["customer_id"].nunique()
row_level_rate   = df["is_repeat_customer"].mean() * 100
cust_level_rate  = repeat_cust / unique_customers * 100

print(f"Total unique customers          : {unique_customers:,}")
print(f"Customers with >1 order         : {repeat_cust:,}")
print(f"Customers with exactly 1 order  : {new_cust:,}")
print()
print(f"Order-row repeat rate   : {row_level_rate:.2f}%  "
      f"(share of ORDER ROWS flagged is_repeat_customer=True)")
print(f"Customer-level repeat rate: {cust_level_rate:.2f}%  "
      f"(unique customers with >1 order / total unique customers)")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].pie([repeat_cust, new_cust],
            labels=[f"Repeat\\n{repeat_cust:,}", f"New\\n{new_cust:,}"],
            autopct="%1.1f%%", colors=["#3b82d4", "#e5e7eb"], startangle=90)
axes[0].set_title("Customer-Level Repeat Rate\\n(unique customers)")

ocd = df["customer_order_count"].value_counts().sort_index()
axes[1].bar(ocd.index, ocd.values, color="#3b82d4", edgecolor="white", width=0.7)
axes[1].set_title("Customer Order Count Distribution")
axes[1].set_xlabel("Number of Orders")
axes[1].set_ylabel("Customers")
axes[1].set_xlim(0, ocd.index.max() + 1)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_repeat_customers.png"), bbox_inches="tight")
plt.show()
""")

md("""### 5.4 Returns and Cancellations""")

code("""\
ret  = df[df["order_status"] == "Returned"].copy()
canc = df[df["order_status"] == "Cancelled"].copy()

return_rate = len(ret) / (len(comp) + len(ret)) * 100
cancel_rate = len(canc) / len(df) * 100

print(f"Return rate (Returned / Completed+Returned): {return_rate:.2f}%")
print(f"Cancellation rate (Cancelled / all orders) : {cancel_rate:.2f}%")
print()

ret_region = (
    df[df["order_status"].isin(["Completed", "Returned"])]
    .groupby("region")["order_status"]
    .apply(lambda s: (s == "Returned").sum() / len(s) * 100)
    .round(2)
    .rename("return_rate_%")
)
print("Return rate by region:")
print(ret_region.to_string())

# Return reasons
rr = pd.read_csv(os.path.join(REPORTS_DIR, "kpi_return_reasons.csv"))
rr["pct_%"] = (rr["count"] / rr["count"].sum() * 100).round(1)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].barh(ret_region.index, ret_region.values, color="#ef4444")
axes[0].set_xlabel("Return Rate %")
axes[0].set_title("Return Rate by Region\\n(Returned / Completed+Returned)")
axes[0].set_xlim(0, 12)
for i, v in enumerate(ret_region.values):
    axes[0].text(v + 0.1, i, f"{v:.2f}%", va="center", fontsize=9)

axes[1].barh(rr["return_reason"], rr["count"], color="#ef4444")
axes[1].set_xlabel("Count")
axes[1].set_title("Return Reasons\\n(9,462 Returned orders)")
for i, v in enumerate(rr["count"]):
    axes[1].text(v + 5, i, f"{v:,} ({rr['pct_%'].iloc[i]}%)", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_returns.png"), bbox_inches="tight")
plt.show()
""")

md("""### 5.5 Delivery Performance""")

code("""\
delivered = df[
    df["delivery_days"].notna()
    & df["order_status"].isin(["Completed", "Returned"])
].copy()

on_time_n   = (delivered["delivery_status"] == "On Time").sum()
delayed_n   = (delivered["delivery_status"] == "Delayed").sum()
early_n     = (delivered["delivery_status"] == "Early").sum()
on_time_pct = on_time_n / len(delivered) * 100
avg_actual  = delivered["delivery_days"].mean()
avg_est     = delivered["estimated_delivery_days"].mean()

print(f"Eligible delivered orders: {len(delivered):,}")
print(f"On Time : {on_time_n:,}  ({on_time_pct:.1f}%)")
print(f"Delayed : {delayed_n:,}  ({delayed_n/len(delivered)*100:.1f}%)")
print(f"Early   : {early_n:,}  ({early_n/len(delivered)*100:.1f}%)")
print(f"Avg actual delivery days  : {avg_actual:.2f}")
print(f"Avg estimated delivery days: {avg_est:.2f}")
print(f"Systematic over-estimation : {avg_actual - avg_est:.2f} days")

ship_perf = (
    delivered.groupby("shipping_method")
    .agg(orders=("order_id", "count"),
         avg_actual=("delivery_days", "mean"),
         avg_est=("estimated_delivery_days", "mean"),
         on_time_pct=("delivery_status",
                      lambda s: (s == "On Time").mean() * 100))
    .round(2)
    .sort_values("avg_actual")
)
ship_perf["gap_days"] = (ship_perf["avg_actual"] - ship_perf["avg_est"]).round(3)
print()
print("Delivery performance by shipping method:")
print(ship_perf.to_string())

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Pie
axes[0].pie([on_time_n, delayed_n, early_n],
            labels=["On Time", "Delayed", "Early"],
            autopct="%1.1f%%",
            colors=["#22c55e", "#ef4444", "#3b82d4"],
            startangle=90)
axes[0].set_title(f"Delivery Status Distribution\\n({len(delivered):,} delivered orders)")

# Bar by method
x = range(len(ship_perf))
width = 0.35
axes[1].bar([i - width/2 for i in x], ship_perf["avg_actual"],
            width, label="Actual Days", color="#3b82d4")
axes[1].bar([i + width/2 for i in x], ship_perf["avg_est"],
            width, label="Estimated Days", color="#e5e7eb", edgecolor="gray")
axes[1].set_xticks(list(x))
axes[1].set_xticklabels(ship_perf.index)
axes[1].set_title("Avg Actual vs Estimated Delivery Days\\nby Shipping Method")
axes[1].set_ylabel("Days")
axes[1].legend()

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_delivery.png"), bbox_inches="tight")
plt.show()
""")

md("""### 5.6 Customer Ratings and Sentiment""")

code("""\
rated = comp[comp["customer_rating"].notna()].copy()
avg_rating = rated["customer_rating"].mean()

print(f"Completed orders with rating: {len(rated):,} / {len(comp):,}  "
      f"(coverage {len(rated)/len(comp)*100:.0f}%)")
print(f"Average customer rating: {avg_rating:.3f} / 5.0")

sent = rated["review_sentiment"].value_counts()
print()
print("Sentiment distribution:")
for s, n in sent.items():
    print(f"  {s:<10} {n:>7,}  ({n/len(rated)*100:.1f}%)")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Rating histogram (binned to 1-decimal)
rating_dist = rated["customer_rating"].value_counts().sort_index()
axes[0].bar(rating_dist.index.astype(float), rating_dist.values,
            width=0.08, color="#3b82d4", align="center")
axes[0].axvline(avg_rating, color="#ef4444", linestyle="--",
                linewidth=1.5, label=f"Mean = {avg_rating:.2f}")
axes[0].set_xlabel("Rating")
axes[0].set_ylabel("Order Count")
axes[0].set_title("Customer Rating Distribution\\n(Completed orders, n=113,559)")
axes[0].legend()

# Sentiment by segment
seg_rating = rated.groupby("customer_segment")["customer_rating"].mean().sort_values()
colors = ["#3b82d4", "#7c5cd8", "#22c55e", "#f59e0b"]
axes[1].barh(seg_rating.index, seg_rating.values, color=colors)
axes[1].set_xlabel("Avg Rating")
axes[1].set_title("Avg Customer Rating by Segment\\n(Completed orders)")
axes[1].set_xlim(3.5, 4.0)
for i, v in enumerate(seg_rating.values):
    axes[1].text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_ratings.png"), bbox_inches="tight")
plt.show()
""")

md("""### 5.7 Seasonal Margin Pattern""")

code("""\
monthly_saved = pd.read_csv(os.path.join(REPORTS_DIR, "kpi_monthly_trend.csv"))

# Tag months
monthly_saved["month_type"] = "Typical"
monthly_saved.loc[monthly_saved["period"].str.endswith("-11"), "month_type"] = "November"
monthly_saved.loc[monthly_saved["period"].str.endswith("-12"), "month_type"] = "December"
monthly_saved.loc[monthly_saved["period"].str.endswith("-07"), "month_type"] = "July"

palette = {"Typical": "#94a3b8", "November": "#ef4444", "December": "#dc2626", "July": "#f59e0b"}

fig, ax = plt.subplots(figsize=(16, 4))
for mtype, grp in monthly_saved.groupby("month_type"):
    ax.scatter(grp["period"], grp["margin_%"],
               label=mtype, color=palette[mtype],
               s=50, zorder=5 if mtype != "Typical" else 3)

ax.plot(monthly_saved["period"], monthly_saved["margin_%"],
        color="#e5e7eb", linewidth=0.8, zorder=1)
ax.set_ylabel("Profit Margin %")
ax.set_title("Profit Margin % — Seasonal Pattern (Nov/Dec and July dips visible every year)")
ax.legend(loc="lower right")

tick_positions = range(0, len(monthly_saved), 6)
ax.set_xticks(list(tick_positions))
ax.set_xticklabels(
    [monthly_saved["period"].iloc[i] for i in tick_positions],
    rotation=45, ha="right", fontsize=8
)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_seasonal_margin.png"), bbox_inches="tight")
plt.show()

print("Nov/Dec avg margin:", monthly_saved[monthly_saved["period"].str.endswith(("-11", "-12"))]["margin_%"].mean().round(2), "%")
print("July avg margin   :", monthly_saved[monthly_saved["period"].str.endswith("-07")]["margin_%"].mean().round(2), "%")
print("Baseline avg margin:", monthly_saved[~monthly_saved["period"].str.endswith(("-11", "-12", "-07"))]["margin_%"].mean().round(2), "%")
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — KPI CALCULATIONS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 6. KPI Calculations

All KPIs are recomputed here from `data/cleaned_ecommerce.csv` with explicit
denominators and scope labels.  
Multi-currency totals are labelled **[MULTI-CCY]** and must not be used for
cross-currency absolute comparisons.
""")

code("""\
# ── Subsets ────────────────────────────────────────────────────────────────
comp  = df[df["order_status"] == "Completed"].copy()
ret   = df[df["order_status"] == "Returned"].copy()
canc  = df[df["order_status"] == "Cancelled"].copy()
pend  = df[df["order_status"] == "Pending"].copy()

# Delivered subset (Completed+Returned with non-null delivery_days)
delivered = df[
    df["delivery_days"].notna()
    & df["order_status"].isin(["Completed", "Returned"])
].copy()

rated = comp[comp["customer_rating"].notna()].copy()

# ── Order KPIs ─────────────────────────────────────────────────────────────
total_orders     = len(df)
return_rate      = len(ret)  / (len(comp) + len(ret))  * 100
cancel_rate      = len(canc) / total_orders * 100

# ── Revenue KPIs [MULTI-CCY] ───────────────────────────────────────────────
net_sales_comp    = comp["net_sales"].sum()
gross_sales_comp  = comp["gross_sales"].sum()
profit_comp       = comp["profit"].sum()
profit_margin     = profit_comp / net_sales_comp * 100
aov_gross         = comp["gross_sales"].mean()
aov_net           = comp["net_sales"].mean()

# ── Delivery KPIs ──────────────────────────────────────────────────────────
on_time_rate      = (delivered["delivery_status"] == "On Time").mean() * 100
avg_del_days      = delivered["delivery_days"].mean()
avg_est_days      = delivered["estimated_delivery_days"].mean()

# ── Rating ─────────────────────────────────────────────────────────────────
avg_rating        = rated["customer_rating"].mean()

# ── Repeat customer ────────────────────────────────────────────────────────
unique_customers  = df["customer_id"].nunique()
repeat_customers  = df[df["is_repeat_customer"]]["customer_id"].nunique()
row_repeat_rate   = df["is_repeat_customer"].mean() * 100
cust_repeat_rate  = repeat_customers / unique_customers * 100

# ── Loyalty ────────────────────────────────────────────────────────────────
lp_earned    = comp["loyalty_points_earned"].sum()
lp_redeemed  = comp["loyalty_points_redeemed"].sum()
lp_redemp    = lp_redeemed / lp_earned * 100

# ── Display ────────────────────────────────────────────────────────────────
kpi_rows = [
    ("total_orders",                   total_orders,           "all statuses"),
    ("completed_orders",               len(comp),              "Completed"),
    ("returned_orders",                len(ret),               "Returned"),
    ("cancelled_orders",               len(canc),              "Cancelled"),
    ("pending_orders",                 len(pend),              "Pending"),
    ("return_rate_%",                  round(return_rate,2),   "Returned/(Completed+Returned)"),
    ("cancellation_rate_%",            round(cancel_rate,2),   "Cancelled/all orders"),
    ("gross_sales [MULTI-CCY]",        round(gross_sales_comp,2), "Completed"),
    ("net_sales [MULTI-CCY]",          round(net_sales_comp,2),   "Completed"),
    ("total_profit [MULTI-CCY]",       round(profit_comp,2),      "Completed"),
    ("profit_margin_%",                round(profit_margin,2), "profit/net_sales, Completed"),
    ("avg_order_value_gross [M-CCY]",  round(aov_gross,2),     "Completed"),
    ("avg_order_value_net [M-CCY]",    round(aov_net,2),       "Completed"),
    ("on_time_delivery_rate_%",        round(on_time_rate,2),  "Completed+Returned w/ delivery data"),
    ("avg_delivery_days",              round(avg_del_days,2),  "Completed+Returned w/ delivery data"),
    ("avg_estimated_delivery_days",    round(avg_est_days,2),  "Completed+Returned w/ delivery data"),
    ("avg_customer_rating",            round(avg_rating,3),    "Completed, rated orders (100% coverage)"),
    ("order_row_repeat_rate_%",        round(row_repeat_rate,2), "ORDER ROWS flagged True / all rows"),
    ("customer_level_repeat_rate_%",   round(cust_repeat_rate,2),"unique customers >1 order / all unique customers"),
    ("loyalty_redemption_rate_%",      round(lp_redemp,1),     "Completed"),
]
kpi_df = pd.DataFrame(kpi_rows, columns=["kpi", "value", "scope"])
kpi_df
""")

code("""\
# Per-currency revenue (correctly segregated)
print("Revenue by currency (Completed orders — each figure is in its own currency):")
cur_df = (
    comp.groupby("currency")
    .agg(orders=("order_id","count"),
         gross_sales=("gross_sales","sum"),
         net_sales=("net_sales","sum"),
         profit=("profit","sum"))
)
cur_df["margin_%"] = (cur_df["profit"] / cur_df["net_sales"] * 100).round(2)
cur_df.sort_values("net_sales", ascending=False)
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — KPI VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 7. KPI Validation

All headline KPIs were independently recomputed and cross-checked in
`scripts/kpi_validation.py`. The full validation report is in
`reports/kpi_validation_report.csv`.
""")

code("""\
val = pd.read_csv(os.path.join(REPORTS_DIR, "kpi_validation_report.csv"))
print(f"Total checks: {len(val)}")
print(f"PASS          : {(val['status']=='PASS').sum()}")
print(f"PASS_WITH_NOTE: {(val['status']=='PASS_WITH_NOTE').sum()}")
print(f"FAIL          : {(val['status']=='FAIL').sum()}")
val[["kpi","reported_value","recomputed_value","abs_difference","status"]]
""")

md("""### 7.1 Repeat Customer Rate — Clarification

> The originally reported figure of **99.8%** is the share of *order rows* where
> `is_repeat_customer = True`. This is correct per the column's definition:
> each customer's **first** order is flagged `False`; every subsequent order is `True`.
>
> The **customer-level** repeat rate — unique customers with more than one order — is
> **98.66%** (24,577 of 24,911 unique customers).
>
> Both figures are preserved. Neither is a data error. The KPI label has been updated
> in `reports/kpi_summary.csv` to avoid ambiguity.
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — BUSINESS INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 8. Business Insights

All eight insights are supported by measured evidence from the dataset.
The full validated records are in `reports/business_insights_validated.csv`.
""")

code("""\
ins = pd.read_csv(os.path.join(REPORTS_DIR, "business_insights_validated.csv"))
for _, row in ins.iterrows():
    print(f"{'='*65}")
    print(f"[{row['insight_id']}]  {row['finding']}")
    print(f"Status: {row['status']}")
    print(f"\\nEvidence:\\n  {row['measured_evidence'][:300]}...")
    print(f"\\nImplication:\\n  {row['business_implication'][:200]}...")
    print(f"\\nLimitation:\\n  {row['limitation'][:200]}...")
    print(f"\\nAction:\\n  {row['recommended_action'][:200]}...")
    print()
""")

md("""### 8.1 Seasonal Margin Detail

The table below shows every November and December in the dataset, confirming
the annual margin collapse is consistent across all five years.
""")

code("""\
nd = monthly_saved[monthly_saved["period"].str.endswith(("-11","-12"))][
    ["period","orders","net_sales","profit","margin_%"]
].reset_index(drop=True)
print("Nov/Dec margin values (all years):")
nd
""")

md("""### 8.2 Return Reason Breakdown (Previously Unavailable — Now Corrected)

> In the original EDA script, `return_reason` was skipped because pandas inferred
> the column as `float64` (93% null across the full dataset). After applying a
> `str` cast and filtering to Returned orders, all 9,462 records have text values.
""")

code("""\
rr = pd.read_csv(os.path.join(REPORTS_DIR, "kpi_return_reasons.csv"))
rr["pct_%"] = (rr["count"] / rr["count"].sum() * 100).round(1)
print("Return reason distribution (9,462 Returned orders):")
print(rr.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(rr["return_reason"], rr["pct_%"], color="#ef4444")
ax.set_xlabel("% of Returns")
ax.set_title("Return Reasons (9,462 Returned orders — near-uniform distribution)")
for i, v in enumerate(rr["pct_%"]):
    ax.text(v + 0.1, i, f"{v}%", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(REPORTS_DIR, "fig_return_reasons.png"), bbox_inches="tight")
plt.show()
""")

md("""### 8.3 Loss-Making Completed Orders""")

code("""\
loss_orders = comp[comp["profit"] < 0].copy()
loss_orders["disc_rate_%"] = (
    loss_orders["discount_amount"] / loss_orders["gross_sales"] * 100
)

print(f"Loss-making Completed orders: {len(loss_orders):,}  "
      f"({len(loss_orders)/len(comp)*100:.2f}% of Completed)")
print(f"Total negative profit        : {loss_orders['profit'].sum():,.2f}  [MULTI-CCY]")
print(f"Min profit margin            : {loss_orders['profit_margin_percentage'].min():.2f}%")
print(f"Avg discount rate (loss)     : {loss_orders['disc_rate_%'].mean():.2f}%")
print(f"Avg discount rate (all comp) : {(comp['discount_amount']/comp['gross_sales']*100).mean():.2f}%")
print()
print("Loss order discount rate distribution:")
bins = [0, 20, 40, 60, 80, 100]
labels_b = ["0–20%", "20–40%", "40–60%", "60–80%", "80–100%"]
loss_orders["disc_band"] = pd.cut(loss_orders["disc_rate_%"], bins=bins, labels=labels_b)
print(loss_orders["disc_band"].value_counts().sort_index().to_string())
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 9 — RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 9. Recommendations

Each recommendation is directly traceable to a validated business insight.

| # | Insight | Recommendation | Priority |
|---|---------|---------------|----------|
| R-01 | INS-01: Nov/Dec margin collapse (~29%) | Model break-even discount threshold per currency. Test loyalty-member early-access at a smaller discount to recover 3–5pp margin. Capture `campaign_name` for all promotional events. | High |
| R-02 | INS-02: July margin anomaly (~38%) without volume uplift | Audit the July discount policy. Replace blanket markdown with targeted bundle deals or loyalty-point multipliers. Measure volume elasticity before the next July event. | High |
| R-03 | INS-03: 75% channel concentration (Mobile App + Website) | Set a medium-term target to grow Marketplace + Social Media to 20% combined share. Append CAC data to future analyses to assess true channel ROI. | Medium |
| R-04 | INS-04: On-time delivery rate 76.5% — systematic overestimation | Add a 0.5-day buffer to all customer-facing delivery estimates (zero operational cost). Audit warehouse throughput specifically during Nov/Dec volume peaks. | High |
| R-05 | INS-05: Avg rating 3.68/5 — 30.5% Neutral | Cross-reference Neutral orders with delivery delay. Run loyalty-point re-engagement nudge for 3.0–3.5 rated customers. Recalibrate the sentiment model against actual ratings. | Medium |
| R-06 | INS-06: Return rate 7.69% — uniform across channels/regions | Wrong Product + Defective + Damaged = 37.5% of returns → improve QA and fulfilment accuracy. Changed Mind + Not as Expected = 24.8% → improve product descriptions and photography. | High |
| R-07 | INS-07: Loyalty redemption rate 49.9% | Run a points-expiry reminder campaign for high-balance, low-recency customers. Quantify point monetary value to size the liability and cost the campaign. | Low |
| R-08 | INS-08: 1,229 loss-making Completed orders (avg disc 51.7%) | Introduce a pricing floor rule: block checkout if computed profit after all adjustments is negative. Add SKU-level data to isolate loss-making products. | High |
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 10 — LIMITATIONS
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 10. Limitations

| ID | Limitation | Impact |
|----|-----------|--------|
| L-01 | `campaign_name` is null for 60% of records → promotion-level attribution impossible | Prevents precise Nov/Dec vs July discount campaign identification |
| L-02 | No Customer Acquisition Cost (CAC) per channel | True channel ROI cannot be computed; channel comparison limited to revenue and margin |
| L-03 | No product/SKU dimension | Product-level return analysis and loss-making SKU identification impossible |
| L-04 | Loyalty point monetary value absent | Unredeemed point liability unquantifiable; redemption campaign cost cannot be sized |
| L-05 | Multi-currency totals not convertible (no exchange rate data) | Absolute cross-currency comparisons are imprecise; per-currency figures are used where possible |
| L-06 | Rating data exists only for Completed orders | Satisfaction of Cancelled/Pending customers is unobserved |
| L-07 | `return_reason` column requires `str` cast on load (reads as float64 due to 93% null) | Analysts must remember to cast; the data itself is correct |
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 11 — CONCLUSION
# ─────────────────────────────────────────────────────────────────────────────
md("""---
## 11. Conclusion

This notebook presents a complete, validated Business Intelligence analysis of
138,116 e-commerce orders spanning January 2021 to December 2025 across seven
currencies and four sales channels.

**Key findings:**

| Finding | Measured Value |
|---------|---------------|
| Completed-order profit margin | **41.4%** (on net sales) |
| Seasonal margin drop (Nov/Dec) | **~29%** vs **~46%** baseline — every year |
| On-time delivery rate | **76.5%** — systematic 0.26-day over-estimation |
| Average customer rating | **3.68 / 5.0** with 30.5% Neutral sentiment |
| Return rate | **7.69%** — near-uniform across regions and channels |
| Customer-level repeat rate | **98.66%** of unique customers placed >1 order |
| Loss-making completed orders | **1,229 (1.08%)** — avg discount rate 51.7% |

All eight business insights have been independently verified against
`data/cleaned_ecommerce.csv`. KPI definitions, denominators, and currency scopes
are documented explicitly throughout.

**Next steps (not included in this notebook):**
- Step 6: Interactive dashboard (Streamlit or Power BI)
- Step 7: Predictive modelling (churn, return propensity, CLV forecasting)
- Data augmentation: CAC per channel, SKU-level product data, exchange rates
""")

# ─────────────────────────────────────────────────────────────────────────────
# ASSEMBLE AND WRITE
# ─────────────────────────────────────────────────────────────────────────────
nb.cells = cells

with open(NB_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook written: {NB_PATH}  ({len(cells)} cells)")
print(f"  Markdown cells : {sum(1 for c in cells if c['cell_type']=='markdown')}")
print(f"  Code cells     : {sum(1 for c in cells if c['cell_type']=='code')}")
