
import pandas as pd

from src.inventory_calculation import calculate_daily_balances

def test_empty_ledger():
    ledger = pd.DataFrame(columns=[
        "event_id",
        "event_date",
        "product_id",
        "location_id",
        "quantity_delta"
    ])

    result = calculate_daily_balances(ledger)

    assert result.empty