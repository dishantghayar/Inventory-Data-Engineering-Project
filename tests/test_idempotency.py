
def test_deterministic_ledger_ids():
    from src.transformation import transform_movements
    import pandas as pd

    event = pd.DataFrame([{
        "event_id": "E001",
        "event_date": "2026-01-01",
        "product_id": "P0001",
        "location_id": "W001",
        "movement_type": "RECEIPT",
        "quantity": 100,
        "adjustment_direction": None
    }])

    first = transform_movements(event)
    second = transform_movements(event)

    assert first.iloc[0]["ledger_id"] == (
        second.iloc[0]["ledger_id"]
    )