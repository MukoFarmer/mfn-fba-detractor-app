import pandas as pd
from datetime import timedelta


def calculate_fba_detractors_weekly(
    fba_df: pd.DataFrame,
    sellerflex_df: pd.DataFrame
) -> pd.DataFrame:
    """
    FBA Weekly Detractor Calculation

    - SellerFlex merchant'larını FBA datasından çıkarır
    - Hafta Pazar günü başlar
    - Üst dönem: Bu haftada bugüne kadar geçen gün sayısı
    - Alt dönem: Onun hemen öncesindeki maksimum 7 gün
    """

    # -----------------------------
    # Prepare data
    # -----------------------------
    fba_df = fba_df.copy()
    sellerflex_df = sellerflex_df.copy()

    fba_df["snapshot_day"] = pd.to_datetime(fba_df["snapshot_day"])
    sellerflex_df["snapshot_day"] = pd.to_datetime(sellerflex_df["snapshot_day"])

    # -----------------------------
    # Remove SellerFlex merchants
    # -----------------------------
    sellerflex_merchants = set(
        sellerflex_df["merchant_customer_id"]
        .dropna()
        .unique()
    )

    fba_df = fba_df[
        ~fba_df["merchant_customer_id"].isin(sellerflex_merchants)
    ]

    if fba_df.empty:
        return pd.DataFrame()

    # -----------------------------
    # Weekly time logic
    # -----------------------------
    reference_date = fba_df["snapshot_day"].max()

    # Python weekday: Mon=0 ... Sun=6
    # Sunday-based week: Sun=0 ... Sat=6
    python_weekday = reference_date.weekday()
    sunday_based_weekday = (python_weekday + 1) % 7

    days_in_current_week = sunday_based_weekday + 1

    this_week_sunday = reference_date - timedelta(days=sunday_based_weekday)

    earliest_date = fba_df["snapshot_day"].min()

    # -----------------------------
    # Upper block
    # -----------------------------
    upper_end = reference_date
    upper_start = reference_date - timedelta(days=days_in_current_week - 1)
    if upper_start < this_week_sunday:
        upper_start = this_week_sunday

    # -----------------------------
    # Lower block
    # -----------------------------
    lower_end = upper_start - timedelta(days=1)
    lower_start = lower_end - timedelta(days=6)
    if lower_start < earliest_date:
        lower_start = earliest_date

    # -----------------------------
    # Detractor calculation
    # -----------------------------
    results = []

    for (merchant_id, merchant_name), g in fba_df.groupby(
        ["merchant_customer_id", "merchant_name"]
    ):
        g = g.sort_values("snapshot_day")

        upper_block = g[
            (g["snapshot_day"] >= upper_start) &
            (g["snapshot_day"] <= upper_end)
        ]

        lower_block = g[
            (g["snapshot_day"] >= lower_start) &
            (g["snapshot_day"] <= lower_end)
        ]

        if upper_block.empty and lower_block.empty:
            continue

        max_upper = (
            upper_block["prime_eligible_bo"].max()
            if not upper_block.empty else 0
        )

        max_lower = (
            lower_block["prime_eligible_bo"].max()
            if not lower_block.empty else 0
        )

        detractor_score = max_upper - max_lower

        results.append({
            "merchant_customer_id": merchant_id,
            "merchant_name": merchant_name,
            "upper_start": upper_start.date(),
            "upper_end": upper_end.date(),
            "lower_start": lower_start.date(),
            "lower_end": lower_end.date(),
            "max_upper": max_upper,
            "max_lower": max_lower,
            "detractor_score": detractor_score
        })

    return pd.DataFrame(results)
