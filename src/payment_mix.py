"""
Payment Mix Trend Analysis — Merchant Benchmarking
Straive Strategic Analytics
"""

import pandas as pd
import numpy as np


PAYMENT_METHODS = ["credit_card", "debit_card", "digital_wallet", "bnpl", "other"]


def compute_payment_mix(df: pd.DataFrame, period_col: str = "month") -> pd.DataFrame:
    """Compute monthly payment method mix as % of total volume."""
    mix = df.groupby(period_col)[PAYMENT_METHODS].sum()
    mix_pct = mix.div(mix.sum(axis=1), axis=0) * 100
    return mix_pct.round(2)


def wallet_penetration_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Track digital wallet penetration vs. peer median over time."""
    client_trend = compute_payment_mix(df[df["is_client"] == 1])["digital_wallet"]
    peer_trend = (
        df[df["is_client"] == 0]
        .groupby("month")
        .apply(lambda g: (g["digital_wallet"].sum() / g[PAYMENT_METHODS].sum().sum()) * 100)
    )
    return pd.DataFrame({
        "client_wallet_pct": client_trend,
        "peer_median_wallet_pct": peer_trend,
        "gap_ppt": client_trend - peer_trend,
    })


def bnpl_adoption_index(df: pd.DataFrame) -> float:
    """BNPL adoption index: client share / peer median share."""
    client_bnpl = df[df["is_client"] == 1]["bnpl"].sum() / df[df["is_client"] == 1][PAYMENT_METHODS].sum().sum()
    peer_bnpl = df[df["is_client"] == 0].groupby("merchant_id").apply(
        lambda g: g["bnpl"].sum() / g[PAYMENT_METHODS].sum().sum()
    ).median()
    return round(client_bnpl / peer_bnpl, 2) if peer_bnpl > 0 else None
