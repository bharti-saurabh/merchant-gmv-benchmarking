-- Merchant GMV & KPI Extraction
-- Straive Strategic Analytics | Merchant Practice
-- Granularity: one row per merchant per month

SELECT
    m.merchant_id,
    m.merchant_name,
    m.mcc_code,
    m.mcc_description,
    m.country_code,
    m.merchant_category,
    DATE_TRUNC('month', t.txn_date)                             AS month,

    -- Volume KPIs
    SUM(t.amount)                                               AS gross_dollar_volume,
    COUNT(t.txn_id)                                             AS total_transactions,
    SUM(t.amount) / NULLIF(COUNT(t.txn_id), 0)                 AS avg_order_value,

    -- Customer KPIs
    COUNT(DISTINCT t.account_id)                                AS active_customers,
    COUNT(t.txn_id) / NULLIF(COUNT(DISTINCT t.account_id), 0)  AS txn_per_active_customer,
    COUNT(DISTINCT CASE WHEN c.first_txn_month = DATE_TRUNC('month', t.txn_date)
                        THEN t.account_id END) * 1.0
        / NULLIF(COUNT(DISTINCT t.account_id), 0)              AS new_customer_rate,

    -- Payment mix
    SUM(CASE WHEN t.funding_source = 'CREDIT'  THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS credit_card_mix,
    SUM(CASE WHEN t.funding_source = 'DEBIT'   THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS debit_card_mix,
    SUM(CASE WHEN t.wallet_type IS NOT NULL     THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS digital_wallet_penetration,
    SUM(CASE WHEN t.funding_source = 'BNPL'    THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS bnpl_mix,

    -- Channel mix
    SUM(CASE WHEN t.channel = 'POS'            THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS card_present_mix,
    SUM(CASE WHEN t.channel = 'ECOM'           THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS ecommerce_mix,
    SUM(CASE WHEN t.is_cross_border = 1        THEN t.amount ELSE 0 END)
        / NULLIF(SUM(t.amount), 0)                             AS cross_border_mix,

    -- Risk KPIs
    SUM(CASE WHEN t.is_disputed = 1 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(t.txn_id), 0)                          AS chargeback_rate,
    SUM(CASE WHEN t.auth_result = 'APPROVED' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(t.txn_id), 0)                          AS authorisation_rate

FROM dim_merchants m
JOIN fact_transactions t ON m.merchant_id = t.merchant_id
LEFT JOIN (
    SELECT account_id, merchant_id, DATE_TRUNC('month', MIN(txn_date)) AS first_txn_month
    FROM fact_transactions
    WHERE status = 'POSTED'
    GROUP BY account_id, merchant_id
) c ON t.account_id = c.account_id AND t.merchant_id = c.merchant_id

WHERE t.status = 'POSTED'
  AND t.txn_date >= DATEADD('month', -36, CURRENT_DATE)
GROUP BY 1, 2, 3, 4, 5, 6, 7
ORDER BY m.merchant_id, month
