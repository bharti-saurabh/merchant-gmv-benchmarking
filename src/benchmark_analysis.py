"""
Merchant GMV Benchmarking — Cohort Analysis & Percentile Ranking
Straive Strategic Analytics — Merchant Practice
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Optional
import logging

log = logging.getLogger(__name__)

BENCHMARK_KPIS = [
    "gross_dollar_volume",
    "avg_order_value",
    "txn_per_active_customer",
    "card_present_mix",
    "digital_wallet_penetration",
    "chargeback_rate",
    "authorisation_rate",
    "new_customer_rate",
    "repeat_customer_rate",
    "cross_border_mix",
]


def build_peer_cohort(
    df: pd.DataFrame,
    client_merchant_id: str,
    mcc_code: str,
    gmv_band_tolerance: float = 0.5,
    geography: Optional[str] = None,
) -> pd.DataFrame:
    """
    Construct a peer cohort based on MCC, GMV band (±50%), and optional geography.
    """
    client = df[df["merchant_id"] == client_merchant_id].iloc[0]
    client_gmv = client["gross_dollar_volume"]

    mask = (
        (df["mcc_code"] == mcc_code)
        & (df["gross_dollar_volume"] >= client_gmv * (1 - gmv_band_tolerance))
        & (df["gross_dollar_volume"] <= client_gmv * (1 + gmv_band_tolerance))
        & (df["merchant_id"] != client_merchant_id)
    )
    if geography:
        mask &= df["country_code"] == geography

    cohort = df[mask].copy()
    log.info(f"Peer cohort size: {len(cohort)} merchants")
    return cohort


def percentile_rank(df: pd.DataFrame, client_merchant_id: str) -> pd.DataFrame:
    """
    Compute percentile rank for the client across all benchmark KPIs.
    Higher = better for most metrics; invert for chargeback_rate.
    """
    invert_kpis = {"chargeback_rate"}
    client = df[df["merchant_id"] == client_merchant_id]
    results = []

    for kpi in BENCHMARK_KPIS:
        if kpi not in df.columns:
            continue
        peer_values = df.loc[df["merchant_id"] != client_merchant_id, kpi].dropna()
        client_value = client[kpi].values[0]
        pct = stats.percentileofscore(peer_values, client_value, kind="rank")
        if kpi in invert_kpis:
            pct = 100 - pct
        results.append({
            "kpi": kpi,
            "client_value": client_value,
            "peer_median": peer_values.median(),
            "peer_p75": peer_values.quantile(0.75),
            "peer_p25": peer_values.quantile(0.25),
            "percentile_rank": round(pct, 1),
            "vs_median": client_value - peer_values.median(),
        })

    return pd.DataFrame(results).sort_values("percentile_rank")


def gmv_waterfall(
    client_gmv: float,
    top_quartile_gmv: float,
    aov_delta: float,
    frequency_delta: float,
    customer_count_delta: float,
) -> pd.DataFrame:
    """
    Decompose GMV gap into AOV, frequency, and customer count components.
    """
    aov_contribution = aov_delta * (top_quartile_gmv / client_gmv - 1) * client_gmv * 0.4
    freq_contribution = frequency_delta * (top_quartile_gmv / client_gmv - 1) * client_gmv * 0.35
    cust_contribution = customer_count_delta * (top_quartile_gmv / client_gmv - 1) * client_gmv * 0.25
    total_gap = top_quartile_gmv - client_gmv

    return pd.DataFrame([
        {"component": "Client GMV",              "value": client_gmv,           "type": "base"},
        {"component": "AOV Uplift Opportunity",  "value": aov_contribution,     "type": "positive"},
        {"component": "Frequency Uplift",        "value": freq_contribution,    "type": "positive"},
        {"component": "Customer Acquisition",    "value": cust_contribution,    "type": "positive"},
        {"component": "Top-Quartile Peer GMV",   "value": top_quartile_gmv,     "type": "total"},
    ])


def run(data_path: str, client_merchant_id: str, mcc_code: str):
    df = pd.read_parquet(data_path)
    cohort = build_peer_cohort(df, client_merchant_id, mcc_code)
    full = pd.concat([cohort, df[df["merchant_id"] == client_merchant_id]])
    rankings = percentile_rank(full, client_merchant_id)
    log.info("\nBenchmark Rankings:\n" + rankings.to_string(index=False))
    return rankings
