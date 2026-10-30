
import argparse
import random
from pathlib import Path
from datetime import date, timedelta

import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[1]

def generate_data(rows=500):
    products = pd.DataFrame([
        {
            "product_id": f"P{i:04d}",
            "product_name": f"Product {i}",
            "category": random.choice(
                ["Electronics", "Clothing", "Food"]
            )
        }
        for i in range(1, 21)
    ])

    locations = pd.DataFrame([
        {
            "location_id": f"W{i:03d}",
            "location_name": f"Warehouse {i}",
            "location_type": "WAREHOUSE"
        }
        for i in range(1, 6)
    ])

    movements = []

    start_date = date(2026, 1, 1)

    for i in range(rows):
        movement_type = random.choices(
            ["RECEIPT", "ISSUE", "ADJUSTMENT"],
            weights=[45, 40, 15]
        )[0]

        quantity = random.randint(1, 50)

        if movement_type == "ADJUSTMENT":
            direction = random.choice(["POSITIVE", "NEGATIVE"])
        else:
            direction = None

        movements.append({
            "event_id": f"E{i:07d}",
            "event_date": str(
                start_date + timedelta(days=random.randint(0, 29))
            ),
            "event_timestamp": (
                "2026-01-01T10:00:00"
            ),
            "product_id": random.choice(products["product_id"]),
            "location_id": random.choice(locations["location_id"]),
            "movement_type": movement_type,
            "quantity": quantity,
            "adjustment_direction": direction,
            "source_location_id": None,
            "destination_location_id": None
        })

    movement_df = pd.DataFrame(movements)

    # Add deliberately invalid records.
    if rows >= 10:
        movement_df.loc[0, "quantity"] = -10
        movement_df.loc[1, "product_id"] = "INVALID_PRODUCT"
        movement_df.loc[2, "event_date"] = "INVALID_DATE"
        movement_df.loc[3, "event_id"] = None

        # Deliberate duplicate event
        movement_df.loc[4, "event_id"] = movement_df.loc[5, "event_id"]

    sample_dir = BASE_DIR / "data" / "sample"
    sample_dir.mkdir(parents=True, exist_ok=True)

    products.to_csv(sample_dir / "products.csv", index=False)
    locations.to_csv(sample_dir / "locations.csv", index=False)
    movement_df.to_csv(
        sample_dir / "inventory_movements.csv",
        index=False
    )

    print("Sample data generated successfully.")
    print("Movement records:", len(movement_df))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=500)
    args = parser.parse_args()

    generate_data(args.rows)