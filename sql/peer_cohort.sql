-- Peer Cohort Definition for Merchant Benchmarking
-- Straive Strategic Analytics | Merchant Practice

WITH client_profile AS (
    SELECT
        merchant_id,
        mcc_code,
        country_code,
        SUM(amount) AS trailing_12m_gmv
    FROM fact_transactions t
    JOIN dim_merchants m USING (merchant_id)
    WHERE t.txn_date >= DATEADD('month', -12, CURRENT_DATE)
      AND t.status = 'POSTED'
      AND m.merchant_id = :client_merchant_id
    GROUP BY 1, 2, 3
),

gmv_bands AS (
    SELECT
        merchant_id,
        mcc_code,
        country_code,
        SUM(amount) AS trailing_12m_gmv
    FROM fact_transactions t
    JOIN dim_merchants m USING (merchant_id)
    WHERE t.txn_date >= DATEADD('month', -12, CURRENT_DATE)
      AND t.status = 'POSTED'
    GROUP BY 1, 2, 3
)

SELECT
    g.merchant_id,
    g.mcc_code,
    g.country_code,
    g.trailing_12m_gmv,
    NTILE(4) OVER (PARTITION BY g.mcc_code ORDER BY g.trailing_12m_gmv) AS gmv_quartile,
    CASE WHEN g.merchant_id = :client_merchant_id THEN 1 ELSE 0 END      AS is_client
FROM gmv_bands g
CROSS JOIN client_profile cp
WHERE g.mcc_code = cp.mcc_code
  AND g.country_code = cp.country_code
  AND g.trailing_12m_gmv BETWEEN cp.trailing_12m_gmv * 0.5
                              AND cp.trailing_12m_gmv * 2.0
ORDER BY g.trailing_12m_gmv DESC
