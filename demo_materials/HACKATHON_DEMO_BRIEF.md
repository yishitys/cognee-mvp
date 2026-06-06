# Hackathon Demo Brief

## Recommended Demo Dataset

Use `retail_sales_forecasting` as the main demo material.

Downloaded files:

- `demo_materials/retail_sales_forecasting/raw/sales.csv`
- `demo_materials/retail_sales_forecasting/raw/online.csv`
- `demo_materials/retail_sales_forecasting/raw/discounts_history.csv`
- `demo_materials/retail_sales_forecasting/raw/price_history.csv`
- `demo_materials/retail_sales_forecasting/raw/catalog.csv`
- `demo_materials/retail_sales_forecasting/raw/stores.csv`
- `demo_materials/retail_sales_forecasting/raw/actual_matrix.csv`
- `demo_materials/retail_sales_forecasting/raw/markdowns.csv`

Backup warm-up dataset:

- `demo_materials/customer_churn/raw/customer_churn.csv`

## Simulated Hackathon Scenario

You are working with a supermarket retailer that operates four stores. The business wants a practical demand forecasting system for daily item-store sales. The data includes historical offline sales, online sales, product catalog metadata, store metadata, price history, promotion history, markdowns, and an actual matrix that identifies item-store-date combinations that should be forecast or evaluated.

The business problem is not just to predict quantities. The judges will expect you to explain which signals matter, how promotions and price changes affect demand, and how the solution could be used by store operations.

## Your Task

Build a prototype that predicts daily demand at the item-store level and turns those predictions into an operational recommendation.

Minimum deliverables:

1. Data understanding: summarize table relationships, grain, date coverage, missingness, and leakage risks.
2. Baseline model: create a simple benchmark such as trailing average by item-store, optionally with weekday and recent sales features.
3. Improved model: add price, promotion, catalog, store, and online/offline features.
4. Evaluation: use a time-based validation split and report an interpretable metric such as MAE, RMSE, WAPE, or SMAPE.
5. Business output: identify high-risk stockout or overstock item-store pairs and recommend operational actions.
6. Demo artifact: prepare a concise notebook, dashboard, or report that explains the approach and shows 3-5 concrete examples.

## Constraints For The Demo

- Timebox the whole exercise to 4-6 hours.
- Avoid training an overly heavy model first; start with a reliable baseline.
- Treat future information carefully. Features derived from future sales, future discounts, or post-period actuals should be excluded.
- Sample the data first if local compute is slow, then scale up only after the pipeline is correct.

## Suggested Success Criteria

- A naive baseline is implemented and documented.
- The improved model beats the baseline on a time-based validation period.
- The team can explain at least three demand drivers.
- The final output includes an action list, not only a score.
