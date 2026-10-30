
import pandas as pd

def calculate_daily_balances(ledger):
    if ledger.empty:
        return pd.DataFrame(columns=[
            "inventory_date",
            "product_id",
            "location_id",
            "opening_quantity",
            "net_movement",
            "closing_quantity"
        ])

    daily = (
        ledger.groupby(
            ["event_date", "product_id", "location_id"],
            as_index=False
        )["quantity_delta"]
        .sum()
        .sort_values(
            ["product_id", "location_id", "event_date"]
        )
    )

    daily = daily.rename(columns={
        "event_date": "inventory_date",
        "quantity_delta": "net_movement"
    })

    daily["closing_quantity"] = (
        daily.groupby(
            ["product_id", "location_id"]
        )["net_movement"].cumsum()
    )

    daily["opening_quantity"] = (
        daily["closing_quantity"]
        - daily["net_movement"]
    )

    return daily[[
        "inventory_date",
        "product_id",
        "location_id",
        "opening_quantity",
        "net_movement",
        "closing_quantity"
    ]]