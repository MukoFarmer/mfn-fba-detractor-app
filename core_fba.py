import pandas as pd
from datetime import timedelta


def calculate_fba_detractors_weekly(
    fba_df: pd.DataFrame,
    sellerflex_df: pd.DataFrame
) -> pd.DataFrame:

    fba_df = fba_df.copy()
    sellerflex_df = sellerflex_df.copy()

    fba_df["snapshot_day"] = pd.to_datetime(fba_df["snapshot_day"])
    sellerflex_df["snapshot_day"] = pd.to_datetime(sellerflex_df["snapshot_day"])

    sellerflex_merchants = set(
        sellerflex_df["merchant_customer_id"].dropna().unique()
    )

    fba_df = fba_df[
        ~fba_df["merchant_customer_id"].isin(sellerflex_merchants)
    ]

    if fba_df.empty:
        return pd.DataFrame()

    reference_date = fba_df["snapshot_day"].max()
    python_weekday = reference_date.weekday()
    sunday_based_weekday = (python_weekday + 1) % 7

    days_in_current_week = sunday_based_weekday + 1
    this_week_sunday = reference_date - timedelta(days=sunday_based_weekday)

    earliest_date = fba_df["snapshot_day"].min()

    upper_end = reference_date
    upper_start = max(
        reference_date - timedelta(days=days_in_current_week - 1),
        this_week_sunday
    )

    lower_end = upper_start - timedelta(days=1)
    lower_start = max(
        lower_end - timedelta(days=6),
        earliest_date
    )

    results = []

    for (merchant_id, merchant_name), g in fba_df.groupby(
        ["merchant_customer_id", "merchant_name"]
    ):
        upper_block = g[
            (g["snapshot_day"] >= upper_start) &
            (g["snapshot_day"] <= upper_end)
        ]
        lower_block = g[
            (g["snapshot_day"] >= lower_start) &
            (g["snapshot_day"] <= lower_end)
        ]

        max_upper = (
            upper_block["prime_eligible_bo"].max()
            if not upper_block.empty else 0
        )
        max_lower = (
            lower_block["prime_eligible_bo"].max()
            if not lower_block.empty else 0
        )

        results.append({
            "merchant_customer_id": merchant_id,
            "merchant_name": merchant_name,
            "upper_start": upper_start.date(),
            "upper_end": upper_end.date(),
            "lower_start": lower_start.date(),
            "lower_end": lower_end.date(),
            "max_upper": max_upper,
            "max_lower": max_lower,
            "detractor_score": max_upper - max_lower
        })

    return pd.DataFrame(results)
