import pandas as pd
from datetime import timedelta


def calculate_mfn_detractors_weekly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["snapshot_day"] = pd.to_datetime(df["snapshot_day"])

    reference_date = df["snapshot_day"].max()

    python_weekday = reference_date.weekday()
    sunday_based_weekday = (python_weekday + 1) % 7

    days_in_current_week = sunday_based_weekday + 1
    this_week_sunday = reference_date - timedelta(days=sunday_based_weekday)

    earliest_date = df["snapshot_day"].min()

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

    for (merchant_id, merchant_name), g in df.groupby(
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

        max_upper = upper_block["mfn_bo"].max() if not upper_block.empty else 0
        max_lower = lower_block["mfn_bo"].max() if not lower_block.empty else 0

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
