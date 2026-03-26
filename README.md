# Merchant GMV Benchmarking

**Client Segment:** Merchant
**Category:** Benchmarking
**Owner:** Straive Strategic Analytics
**Year:** 2024

## Objective
Benchmark a merchant client's Gross Merchandise Value (GMV), average order value, and payment mix against anonymised industry peers within the same MCC vertical, identifying performance gaps and growth levers.

## Methodology
1. Peer cohort construction using MCC code, GMV band, and geography
2. Percentile ranking across 12 KPIs
3. Waterfall decomposition of GMV delta vs. top-quartile peer
4. Payment mix analysis: card vs. wallet vs. BNPL penetration
5. Seasonality-adjusted trend comparison (3-year window)

## Key Metrics Benchmarked
| KPI | Description |
|---|---|
| Gross Dollar Volume (GDV) | Total card-present + card-not-present spend |
| Average Order Value (AOV) | Mean transaction size |
| Transactions Per Active Customer | Purchase frequency |
| Card-Present Mix | % of volume at physical POS |
| Digital Wallet Penetration | Apple Pay / Google Pay share |
| Chargeback Rate | Disputes as % of transactions |
| Authorisation Rate | % of attempted transactions approved |

## Assets
- `src/benchmark_analysis.py` — Cohort construction, percentile ranking, waterfall
- `src/payment_mix.py` — Payment method trend analysis
- `sql/merchant_gmv_extract.sql` — GMV and transaction KPI extraction
- `sql/peer_cohort.sql` — Peer cohort definition query

## Requirements
```
pandas>=2.0
scipy>=1.11
plotly>=5.18
sqlalchemy>=2.0
```
