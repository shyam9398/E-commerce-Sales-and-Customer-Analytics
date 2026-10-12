# E-commerce Sales and Customer Analytics

**A Data Analytics and Business Intelligence Project**

Analyze e-commerce transactions to understand sales performance, profitability, customer behavior, returns, delivery efficiency, and business opportunities using Python and data visualization.

## 1. Project Overview

E-commerce businesses generate large volumes of transactional data, but raw data alone does not provide actionable business insights. This project transforms e-commerce sales and customer records into meaningful KPIs, visualizations, and evidence-based business recommendations.

The project follows a reproducible analytics workflow involving data inspection, cleaning, quality validation, exploratory data analysis (EDA), KPI calculation, and business insight generation.

## 2. Problem Statement

E-commerce businesses face challenges in understanding revenue and profit trends, customer retention, return patterns, delivery performance, and the effectiveness of sales channels.

This project addresses these challenges by:

- Cleaning and validating transaction data before analysis.
- Calculating KPIs with explicit definitions and denominators.
- Analyzing sales and profitability trends across regions, channels, and time.
- Identifying customer behavior patterns and operational issues.
- Translating validated findings into actionable business recommendations.

## 3. Project Objectives

- Inspect and clean the e-commerce dataset.
- Validate data quality and financial calculations.
- Analyze sales, profit, and margin trends from 2021 to 2025.
- Evaluate performance by region, sales channel, customer segment, and currency.
- Measure customer repeat-purchase behavior, returns, delivery performance, and ratings.
- Identify loss-making orders and seasonal profitability patterns.
- Produce reproducible analysis and evidence-based recommendations.

## 4. Dataset Description

**Dataset filename:** `ecommerce_sales_customer_analytics_150k.csv`

| Attribute | Description |
|---|---|
| Original records | 138,116 |
| Original columns | 46 |
| Cleaned columns | 49 |
| Date range | January 1, 2021 – December 31, 2025 |
| Time coverage | 60 months |
| Currencies | USD, GBP, EUR, CAD, AUD, INR, AED |
| Order statuses | Completed, Returned, Cancelled, Pending |
| Cleaned dataset | `data/cleaned_ecommerce.csv` |

The dataset includes order details, customer demographics, sales channels, financial information, payment details, delivery timelines, returns, customer ratings, marketing attribution, and loyalty program data.

**Original dataset source:** To be added after verification. The original source URL has not yet been confirmed.

## 5. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data analysis and automation |
| pandas | Data loading, cleaning, and aggregation |
| NumPy | Numerical operations |
| Matplotlib | Data visualization |
| Seaborn | Statistical visualization |
| Jupyter Notebook | Interactive and reproducible analysis |
| nbformat | Notebook creation and inspection |
| nbconvert | Notebook execution and conversion |

See `requirements.txt` for the project's specified Python dependencies.

## 6. Key Features

### Data Cleaning and Quality Validation
- Dataset structure and data type inspection.
- Duplicate and unique order ID checks.
- Date validation and missing-value analysis.
- Financial formula consistency checks.
- Preservation of negative-profit records and structurally missing values.

### Exploratory Data Analysis
- Monthly sales, profit, and margin trends.
- Regional and sales-channel comparisons.
- Customer segment and repeat-purchase analysis.
- Return rates and return-reason analysis.
- Delivery performance by shipping method.
- Customer rating and sentiment distributions.
- Revenue and profit analysis by currency.

### KPI Calculation and Validation
- Order status distribution.
- Gross sales, net sales, profit, and profit margin.
- Average order value.
- Return and cancellation rates.
- On-time delivery and average delivery duration.
- Customer ratings and repeat-purchase metrics.
- Loyalty point redemption.
- Independent KPI validation.

### Business Insights and Recommendations
Eight validated business insights and eight prioritized recommendations connect analytical findings to potential business actions.

## 7. Methodology

The project follows these stages:

1. **Data Inspection:** Examine dataset shape, data types, missing values, duplicate records, and order identifiers.
2. **Data Cleaning:** Parse dates, prepare data types, preserve valid negative-profit values, and add derived date columns.
3. **Data Quality Checks:** Verify financial formulas, order ID uniqueness, and missing-value patterns.
4. **Exploratory Data Analysis:** Examine trends and patterns using statistical summaries and visualizations.
5. **KPI Calculation:** Calculate business metrics with explicit scopes, denominators, and currency labels.
6. **KPI Validation:** Recalculate reported metrics independently and compare the results against existing reports.
7. **Business Insights:** Interpret validated findings, document limitations, and propose practical recommendations.

## 8. Key Findings

The following findings are based on the project's validated analysis.

| KPI / Finding | Result |
|---|---|
| Total orders | 138,116 |
| Completed orders | 113,559 |
| Return rate | 7.69% |
| Cancellation rate | 6.08% |
| Profit margin | 41.44% of net sales for completed orders, using the reported multi-currency pool |
| Average net order value | 1,269.79 in the reported multi-currency pool |
| On-time delivery rate | 76.54% |
| Average delivery duration | 4.56 days |
| Average customer rating | 3.68 / 5 |
| Customer-level repeat rate | 98.66% |
| Loss-making completed orders | 1,229 |
| KPI validation | 38 checks passed, as documented in the validation report |

**Currency warning:** Monetary totals pooled across currencies are not suitable for direct cross-currency comparisons. Revenue and profit should be interpreted separately by currency unless documented exchange rates are applied.

### Business Insights

- November and December show recurring reductions in profit margin compared with other months.
- July exhibits a recurring lower-margin pattern without a comparable increase in order volume.
- Mobile App and Website account for approximately 75% of completed-order sales in the reported analysis.
- Actual delivery duration averages approximately 0.26 days longer than the estimated duration.
- Average customer ratings indicate opportunities to improve customer experience.
- Return reasons include incorrect products, defective or damaged products, delivery issues, and expectation gaps.
- Approximately half of loyalty points earned on completed orders are redeemed.
- A subset of completed orders records negative profit, with higher average discounts than the overall completed-order group.

These findings identify patterns and areas for investigation; they do not establish every underlying cause.

## 9. Recommendations

The project proposes the following actions based on the validated insights:

1. Evaluate promotional discount thresholds and improve campaign attribution.
2. Review the July discount strategy and measure its impact on order volume and profitability.
3. Diversify sales-channel performance and collect customer acquisition cost data.
4. Improve delivery estimates using measured delivery performance.
5. Investigate relationships between delivery experience, customer ratings, and sentiment.
6. Improve fulfilment accuracy, quality checks, and product descriptions to address returns.
7. Evaluate targeted loyalty redemption campaigns and document the monetary value of points.
8. Investigate loss-making orders and evaluate pricing controls using complete cost information.

These recommendations require business testing and operational validation before implementation.

## 10. Project Structure

The project is organized as follows:

```text
Ecommerce-BI-Project/
├── data/
│   └── cleaned_ecommerce.csv
├── reports/
│   ├── business_insights.csv
│   ├── business_insights_validated.csv
│   ├── data_quality_report.csv
│   ├── kpi_summary.csv
│   ├── kpi_validation_report.csv
│   ├── kpi_monthly_trend.csv
│   ├── kpi_by_region.csv
│   ├── kpi_by_channel.csv
│   ├── kpi_by_segment.csv
│   ├── kpi_by_marketing_channel.csv
│   ├── kpi_revenue_by_currency.csv
│   ├── kpi_delivery_by_method.csv
│   ├── kpi_return_rate_by_region.csv
│   ├── kpi_return_reasons.csv
│   ├── kpi_return_status_breakdown.csv
│   ├── fig_status_currency.png
│   ├── fig_missing_values.png
│   ├── fig_monthly_trend.png
│   ├── fig_region_channel.png
│   ├── fig_repeat_customers.png
│   ├── fig_returns.png
│   ├── fig_delivery.png
│   ├── fig_ratings.png
│   ├── fig_seasonal_margin.png
│   └── fig_return_reasons.png
├── scripts/
│   ├── clean_data.py
│   ├── eda_analysis.py
│   ├── kpi_validation.py
│   ├── build_notebook.py
│   └── check_notebook.py
├── BSyamalaRao_EcommerceBI.ipynb
├── BSyamalaRao_ProjectReport.docx
├── requirements.txt
└── README.md
```

This structure reflects the documented project files. Confirm the actual filenames in your repository before publishing, because some outputs may be absent or named differently in your current workspace.

## 11. Installation and Setup

### Prerequisites

- Python version compatible with the dependencies in `requirements.txt`.
- pip package manager.
- Jupyter Notebook or JupyterLab.

### Clone the Repository

Replace the placeholder with your actual GitHub repository URL.

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Ecommerce-BI-Project
```

### Create a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Run the Notebook

```bash
jupyter notebook BSyamalaRao_EcommerceBI.ipynb
```

Open the notebook in your browser and execute the cells from top to bottom.

Ensure that `data/cleaned_ecommerce.csv` exists at the relative path expected by the notebook.

## 12. Running the Python Scripts

The following commands describe the documented project scripts. Run them from the project root and confirm any required input paths before execution.

```bash
python scripts/clean_data.py
python scripts/eda_analysis.py
python scripts/kpi_validation.py
python scripts/check_notebook.py
```

**Important:** The cleaning script may regenerate the cleaned dataset, and the EDA script may overwrite report outputs. Back up important results before rerunning scripts, and review each script's input/output behavior first.

The notebook builder can be run with:

```bash
python scripts/build_notebook.py
```

Use this command only when you intend to rebuild the notebook; it may replace the existing notebook file.

## 13. Generated Outputs

The project produces:

- A cleaned CSV dataset.
- Data quality and KPI validation reports.
- Monthly trend and category-level KPI summaries.
- Return-reason and delivery-performance summaries.
- Ten analytical figures.
- A reproducible Jupyter Notebook.
- A Word project report.

These outputs support review of the project's calculations and findings.

## 14. Limitations

- **Missing campaign attribution:** Campaign names are absent for approximately 60% of records, limiting promotion-level analysis.
- **No customer acquisition cost data:** True channel return on investment cannot be calculated.
- **No product/SKU dimension:** Product-level return rates and loss-making products cannot be identified.
- **No loyalty point monetary value:** The financial liability of unredeemed points cannot be quantified.
- **No exchange rate data:** Multi-currency totals cannot be converted into a common reporting currency.
- **Incomplete customer satisfaction coverage:** Ratings are available for completed orders only.
- **Return-reason data types:** The return-reason column requires appropriate string handling during analysis.

The analysis is descriptive. The project does not currently include a deployed dashboard or predictive machine-learning model.

## 15. Future Scope

Potential extensions include:

- An interactive dashboard built with Streamlit or Power BI.
- Predictive analysis for return propensity, customer churn, or customer lifetime value, subject to data suitability and validation.
- Integration of product-level data, customer acquisition cost, exchange rates, and loyalty point values.
- Automated periodic reporting and KPI monitoring.

These are proposed enhancements, not completed features.

## 16. References

- Python Documentation: https://docs.python.org/3.11/
- pandas Documentation: https://pandas.pydata.org/docs/
- NumPy Documentation: https://numpy.org/doc/stable/
- Matplotlib Documentation: https://matplotlib.org/stable/
- Seaborn Documentation: https://seaborn.pydata.org/
- Jupyter Documentation: https://docs.jupyter.org/

**Original dataset source:** (https://www.kaggle.com/datasets/datascikhan/e-commerce-sales-and-customer-analytics)

## 17. Author

**B. Syamala Rao**

E-commerce Sales and Customer Analytics — Data Analytics / Business Intelligence Internship Project.
