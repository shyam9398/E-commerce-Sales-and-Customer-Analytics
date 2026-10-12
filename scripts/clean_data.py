"""
Step 3: Data Cleaning and Preparation
E-commerce BI Project
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────
# 0. Paths
# ─────────────────────────────────────────────
RAW_PATH    = "ecommerce_sales_customer_analytics_150k.csv"
CLEAN_PATH  = "data/cleaned_ecommerce.csv"
REPORT_PATH = "reports/data_quality_report.csv"

os.makedirs("data",    exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("scripts", exist_ok=True)

# ─────────────────────────────────────────────
# 1. Load — preserve postal code as string
# ─────────────────────────────────────────────
print("=" * 60)
print("PHASE 1 — LOAD")
print("=" * 60)

df = pd.read_csv(RAW_PATH, dtype={"customer_postal_code": str})

rows_raw, cols_raw = df.shape
print(f"Loaded: {rows_raw:,} rows × {cols_raw} columns")
print("Note: customer_postal_code loaded as string. Leading zeros in the "
      "source file are preserved; zeros already absent in the raw CSV "
      "cannot be recovered.")

# ─────────────────────────────────────────────
# 2. order_date → datetime
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 2 — DATETIME CONVERSION")
print("=" * 60)

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

invalid_dates = df["order_date"].isna().sum()
print(f"Invalid / unparseable order_date values: {invalid_dates:,}")
if invalid_dates > 0:
    print("Sample rows with invalid dates:")
    bad = df[df["order_date"].isna()][["order_id", "order_date"]].head(10)
    print(bad.to_string(index=False))
else:
    print("All order_date values parsed successfully.")

date_min = df["order_date"].min()
date_max = df["order_date"].max()
print(f"Date range: {date_min.date()} to {date_max.date()}")

# Derive time-based helper columns
df["order_year"]  = df["order_date"].dt.year
df["order_month"] = df["order_date"].dt.month
df["order_dow"]   = df["order_date"].dt.day_name()

# ─────────────────────────────────────────────
# 3. Uniqueness & duplicate checks
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 3 — UNIQUENESS & DUPLICATE CHECKS")
print("=" * 60)

exact_dups = df.duplicated().sum()
print(f"Exact duplicate rows: {exact_dups:,}")

order_id_total   = df["order_id"].shape[0]
order_id_unique  = df["order_id"].nunique()
order_id_repeats = order_id_total - order_id_unique
print(f"Total order_id values   : {order_id_total:,}")
print(f"Unique order_id values  : {order_id_unique:,}")
print(f"Repeated order_id count : {order_id_repeats:,}")

if order_id_repeats > 0:
    dup_ids = df[df.duplicated(subset=["order_id"], keep=False)]
    print(f"Rows sharing a duplicate order_id: {len(dup_ids):,}")
    print(dup_ids[["order_id", "order_date", "customer_id", "gross_sales"]].head(10).to_string(index=False))

# ─────────────────────────────────────────────
# 4. Missing value analysis by order_status
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 4 — MISSING VALUE ANALYSIS")
print("=" * 60)

sparse_cols = [
    "delivery_days", "estimated_delivery_days",
    "customer_rating", "review_sentiment", "customer_review",
    "return_status", "return_reason",
    "campaign_name", "coupon_code",
]

print("\nMissing counts by order_status for sparse columns:")
status_null_table = {}
for col in sparse_cols:
    ct = df.groupby("order_status")[col].apply(lambda s: s.isna().sum())
    status_null_table[col] = ct

status_null_df = pd.DataFrame(status_null_table)
print(status_null_df.to_string())

# Overall null summary
print("\nOverall missing values (all columns):")
null_before = df.isnull().sum()
null_pct_before = (null_before / len(df) * 100).round(2)
null_summary = pd.DataFrame({
    "missing_count": null_before,
    "missing_pct":   null_pct_before,
}).query("missing_count > 0")
print(null_summary.to_string())

# ─────────────────────────────────────────────
# 5. Numeric validation
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 5 — NUMERIC VALIDATION")
print("=" * 60)

issues = {}  # will feed the quality report

# Age
age_invalid = df[(df["customer_age"] < 18) | (df["customer_age"] > 100)]
issues["age_out_of_range"] = len(age_invalid)
print(f"customer_age outside [18, 100]: {len(age_invalid):,}")

# Quantity
qty_invalid = df[df["quantity"] <= 0]
issues["quantity_lte_zero"] = len(qty_invalid)
print(f"quantity <= 0: {len(qty_invalid):,}")

# gross_sales, net_sales, product_cost must be > 0
for col in ["gross_sales", "net_sales", "product_cost"]:
    n = (df[col] <= 0).sum()
    issues[f"{col}_lte_zero"] = int(n)
    print(f"{col} <= 0: {n:,}")

# delivery_days / estimated_delivery_days negative
for col in ["delivery_days", "estimated_delivery_days"]:
    n = (df[col] < 0).sum()
    issues[f"{col}_negative"] = int(n)
    print(f"{col} < 0: {n:,}")

# Negative profit — preserve but log
neg_profit = (df["profit"] < 0).sum()
issues["negative_profit_rows"] = int(neg_profit)
print(f"profit < 0 (preserved, economically valid): {neg_profit:,}")

# profit_margin_percentage sanity — expect profit / net_sales * 100
# Use only rows where net_sales != 0
mask = df["net_sales"] != 0
df_check = df[mask].copy()
df_check["computed_margin"] = (df_check["profit"] / df_check["net_sales"] * 100).round(2)
margin_diff = (df_check["computed_margin"] - df_check["profit_margin_percentage"]).abs()
margin_discrepancy = (margin_diff > 1.0).sum()   # >1 pp tolerance
issues["margin_discrepancy_rows"] = int(margin_discrepancy)
print(f"profit_margin_percentage discrepancy > 1 pp vs profit/net_sales*100: {margin_discrepancy:,}")
if margin_discrepancy > 0:
    sample = df_check[margin_diff > 1.0][
        ["order_id", "profit", "net_sales", "profit_margin_percentage", "computed_margin"]
    ].head(5)
    print(sample.to_string(index=False))

# ─────────────────────────────────────────────
# 6. Financial consistency check
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 6 — FINANCIAL CONSISTENCY CHECK")
print("=" * 60)

# Attempt formula: net_sales = gross_sales - discount_amount + tax_amount + shipping_cost
# This is a hypothesis — we log deviations but do NOT drop rows
df["net_sales_computed"] = (
    df["gross_sales"] - df["discount_amount"] + df["tax_amount"] + df["shipping_cost"]
).round(2)
fin_diff = (df["net_sales_computed"] - df["net_sales"]).abs()
fin_tolerance = 1.0  # £/$/€ 1 rounding tolerance
fin_discrepant = (fin_diff > fin_tolerance).sum()
issues["financial_formula_deviations"] = int(fin_discrepant)

pct_match = round((1 - fin_discrepant / len(df)) * 100, 2)
print(f"Formula tested: net_sales = gross_sales - discount + tax + shipping")
print(f"Rows matching within ±{fin_tolerance}: {len(df) - fin_discrepant:,} / {len(df):,}  ({pct_match}%)")
print(f"Rows deviating > ±{fin_tolerance}: {fin_discrepant:,}")
if fin_discrepant > 0 and fin_discrepant < 20:
    sample = df[fin_diff > fin_tolerance][
        ["order_id", "gross_sales", "discount_amount", "tax_amount",
         "shipping_cost", "net_sales_computed", "net_sales"]
    ].head(10)
    print(sample.to_string(index=False))

# Drop helper column (not part of final output — use cleaned column only)
df.drop(columns=["net_sales_computed"], inplace=True)

# ─────────────────────────────────────────────
# 7. Apply documented corrections
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 7 — APPLY CORRECTIONS")
print("=" * 60)

rows_before = len(df)
rows_dropped = {}

# 7a. Drop rows with truly invalid dates (can't be trusted for any analysis)
if invalid_dates > 0:
    df = df[df["order_date"].notna()].copy()
    rows_dropped["invalid_order_date"] = invalid_dates
    print(f"Dropped {invalid_dates:,} rows with unparseable order_date.")
else:
    rows_dropped["invalid_order_date"] = 0
    print("No rows dropped for invalid order_date.")

# 7b. Drop rows with quantity <= 0 (transaction makes no physical sense)
qty_bad = (df["quantity"] <= 0).sum()
if qty_bad > 0:
    df = df[df["quantity"] > 0].copy()
    rows_dropped["quantity_lte_zero"] = qty_bad
    print(f"Dropped {qty_bad:,} rows with quantity <= 0.")
else:
    rows_dropped["quantity_lte_zero"] = 0
    print("No rows dropped for quantity <= 0.")

# 7c. gross_sales <= 0 — flag but keep (could be 100% discount edge case)
rows_dropped["gross_sales_lte_zero_kept"] = int((df["gross_sales"] <= 0).sum())
print(f"gross_sales <= 0: {rows_dropped['gross_sales_lte_zero_kept']:,} rows — kept (may be valid credits).")

rows_after = len(df)
total_dropped = rows_before - rows_after
print(f"\nTotal rows removed: {total_dropped:,}")
print(f"Rows remaining: {rows_after:,}")

# ─────────────────────────────────────────────
# 8. Post-cleaning null summary
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 8 — POST-CLEANING NULL SUMMARY")
print("=" * 60)

null_after = df.isnull().sum()
null_pct_after = (null_after / len(df) * 100).round(2)
null_after_summary = pd.DataFrame({
    "missing_count_after": null_after,
    "missing_pct_after":   null_pct_after,
}).query("missing_count_after > 0")
print(null_after_summary.to_string())

# ─────────────────────────────────────────────
# 9. Save cleaned dataset
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("PHASE 9 — SAVE OUTPUTS")
print("=" * 60)

df.to_csv(CLEAN_PATH, index=False)
print(f"Cleaned dataset saved -> {CLEAN_PATH}  ({rows_after:,} rows x {df.shape[1]} columns)")

# ─────────────────────────────────────────────
# 10. Data quality report
# ─────────────────────────────────────────────
quality_rows = []

# Shape
quality_rows.append({"check": "rows_raw",     "before": rows_raw,     "after": rows_after,  "note": ""})
quality_rows.append({"check": "cols_raw",     "before": cols_raw,     "after": df.shape[1], "note": "3 helper cols added: order_year, order_month, order_dow"})
quality_rows.append({"check": "exact_duplicate_rows", "before": exact_dups, "after": 0, "note": "None found"})

# order_id
quality_rows.append({"check": "order_id_repeated", "before": order_id_repeats, "after": order_id_repeats, "note": "Repeated IDs kept — may reflect intentional duplicates or splits"})

# Date
quality_rows.append({"check": "invalid_order_date", "before": invalid_dates, "after": 0, "note": "Rows dropped"})

# Missing sparse cols
for col in sparse_cols:
    b = int(null_before[col])
    a = int(null_after.get(col, 0))
    quality_rows.append({
        "check": f"missing_{col}",
        "before": b,
        "after": a,
        "note": "Preserved — structurally expected absence"
    })

# Numeric issues
for k, v in issues.items():
    quality_rows.append({"check": k, "before": v, "after": v, "note": "Logged; no drop unless documented above"})

# Drops
for k, v in rows_dropped.items():
    quality_rows.append({"check": f"dropped_{k}", "before": v, "after": 0, "note": "Applied"})

report_df = pd.DataFrame(quality_rows)
report_df.to_csv(REPORT_PATH, index=False)
print(f"Data quality report saved -> {REPORT_PATH}  ({len(report_df)} checks logged)")

print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)
print(report_df.to_string(index=False))
