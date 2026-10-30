
import hashlib
import pandas as pd

def deterministic_id(value):
    return hashlib.sha256(
        str(value).encode("utf-8")
    ).hexdigest()

def transform_movements(df):
    ledger = []

    for _, row in df.iterrows():
        event_id = row["event_id"]
        movement_type = row["movement_type"]
        quantity = float(row["quantity"])

        if movement_type == "RECEIPT":
            movements = [
                (
                    row["location_id"],
                    "RECEIPT",
                    quantity
                )
            ]

        elif movement_type == "ISSUE":
            movements = [
                (
                    row["location_id"],
                    "ISSUE",
                    -quantity
                )
            ]

        elif movement_type == "ADJUSTMENT":
            sign = (
                1
                if row["adjustment_direction"] == "POSITIVE"
                else -1
            )

            movements = [
                (
                    row["location_id"],
                    "ADJUSTMENT",
                    sign * quantity
                )
            ]

        elif movement_type == "TRANSFER":
            movements = [
                (
                    row["source_location_id"],
                    "TRANSFER_OUT",
                    -quantity
                ),
                (
                    row["destination_location_id"],
                    "TRANSFER_IN",
                    quantity
                )
            ]

        for index, (location, movement, delta) in enumerate(movements):
            ledger.append({
                "ledger_id": deterministic_id(
                    f"{event_id}:{index}"
                ),
                "event_id": event_id,
                "event_date": pd.to_datetime(
                    row["event_date"]
                ).date(),
                "product_id": row["product_id"],
                "location_id": location,
                "movement_type": movement,
                "quantity_delta": delta
            })

    return pd.DataFrame(ledger)