
import pandas as pd

REQUIRED_COLUMNS = [
    "event_id",
    "event_date",
    "product_id",
    "location_id",
    "movement_type",
    "quantity"
]

VALID_MOVEMENT_TYPES = {
    "RECEIPT",
    "ISSUE",
    "ADJUSTMENT",
    "TRANSFER"
}

def validate_movements(df, products, locations):
    df = df.copy()

    rejected = []
    accepted = []

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Unexpected source schema. Missing columns: "
            f"{sorted(missing_columns)}"
        )

    product_ids = set(products["product_id"])
    location_ids = set(locations["location_id"])

    seen = set()

    for _, row in df.iterrows():
        reason = None

        event_id = row["event_id"]

        if pd.isna(event_id) or str(event_id).strip() == "":
            reason = "MISSING_EVENT_ID"

        elif event_id in seen:
            reason = "DUPLICATE_EVENT_ID"

        elif pd.isna(row["product_id"]):
            reason = "MISSING_PRODUCT_ID"

        elif row["product_id"] not in product_ids:
            reason = "INVALID_PRODUCT_REFERENCE"

        elif pd.isna(row["quantity"]):
            reason = "MISSING_QUANTITY"

        elif row["movement_type"] not in VALID_MOVEMENT_TYPES:
            reason = "INVALID_MOVEMENT_TYPE"

        elif row["movement_type"] != "TRANSFER" and (
            pd.isna(row["location_id"])
            or row["location_id"] not in location_ids
        ):
            reason = "INVALID_LOCATION_REFERENCE"

        elif row["movement_type"] == "TRANSFER":
            if (
                pd.isna(row["source_location_id"])
                or pd.isna(row["destination_location_id"])
            ):
                reason = "MISSING_TRANSFER_LOCATION"

            elif (
                row["source_location_id"] not in location_ids
                or row["destination_location_id"] not in location_ids
            ):
                reason = "INVALID_TRANSFER_REFERENCE"

            elif (
                row["source_location_id"]
                == row["destination_location_id"]
            ):
                reason = "SAME_TRANSFER_LOCATION"

        elif row["movement_type"] == "ADJUSTMENT" and (
            row.get("adjustment_direction")
            not in ["POSITIVE", "NEGATIVE"]
        ):
            reason = "INVALID_ADJUSTMENT_DIRECTION"

        try:
            pd.to_datetime(row["event_date"], errors="raise")
        except (ValueError, TypeError):
            reason = reason or "INVALID_EVENT_DATE"

        try:
            quantity = float(row["quantity"])

            if quantity <= 0:
                reason = reason or "NON_POSITIVE_QUANTITY"

        except (ValueError, TypeError):
            reason = reason or "INVALID_QUANTITY"

        if reason:
            rejected.append({
                "event_id": event_id,
                "source_row": row.get("source_row"),
                "source_file": row.get("source_file"),
                "raw_record": row.to_json(default_handler=str),
                "rejection_reason": reason
            })
        else:
            seen.add(event_id)
            accepted.append(row.to_dict())

    return (
        pd.DataFrame(accepted),
        pd.DataFrame(rejected)
    )