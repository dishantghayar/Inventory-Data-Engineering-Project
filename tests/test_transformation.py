
import pandas as pd

from src.transformation import transform_movements
from src.inventory_calculation import calculate_daily_balances

def test_receipt_and_issue():
    events = pd.DataFrame([
        {
            "event_id": "E001",
            "event_date": "2026-01-01",
            "product_id": "P0001",
            "location_id": "W001",
            "movement_type": "RECEIPT",
            "quantity": 100,
            "adjustment_direction": None
        },
        {
            "event_id": "E002",
            "event_date": "2026-01-02",
            "product_id": "P0001",
            "location_id": "W001",
            "movement_type": "ISSUE",
            "quantity": 20,
            "adjustment_direction": None
        }
    ])

    ledger = transform_movements(events)

    result = calculate_daily_balances(ledger)

    assert result.iloc[-1]["closing_quantity"] == 80
    

def test_transfer_conserves_inventory():
    events = pd.DataFrame([{
        "event_id": "E003",
        "event_date": "2026-01-01",
        "product_id": "P0001",
        "movement_type": "TRANSFER",
        "quantity": 25,
        "source_location_id": "W001",
        "destination_location_id": "W002"
    }])

    ledger = transform_movements(events)

    assert len(ledger) == 2
    assert ledger["quantity_delta"].sum() == 0

    assert set(ledger["location_id"]) == {
        "W001", "W002"
    }
    

def test_backdated_event_recalculates_balance():
    original = pd.DataFrame([
        {
            "event_id": "E001",
            "event_date": "2026-01-01",
            "product_id": "P0001",
            "location_id": "W001",
            "movement_type": "RECEIPT",
            "quantity": 100,
            "adjustment_direction": None
        },
        {
            "event_id": "E002",
            "event_date": "2026-01-03",
            "product_id": "P0001",
            "location_id": "W001",
            "movement_type": "ISSUE",
            "quantity": 20,
            "adjustment_direction": None
        }
    ])

    correction = pd.DataFrame([{
        "event_id": "E003",
        "event_date": "2026-01-02",
        "product_id": "P0001",
        "location_id": "W001",
        "movement_type": "RECEIPT",
        "quantity": 50,
        "adjustment_direction": None
    }])

    first = calculate_daily_balances(
        transform_movements(original)
    )

    second = calculate_daily_balances(
        transform_movements(
            pd.concat([original, correction])
        )
    )

    assert first.iloc[-1]["closing_quantity"] == 80
    assert second.iloc[-1]["closing_quantity"] == 130