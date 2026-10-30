
import pandas as pd

def publish_events(con, events, run_id):
    inserted = 0
    duplicates = 0

    for _, row in events.iterrows():
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM inventory_events
            WHERE event_id = ?
            """,
            [row["event_id"]]
        ).fetchone()[0]

        if exists:
            duplicates += 1
            continue

        con.execute(
            """
            INSERT INTO inventory_events (
                event_id,
                event_date,
                event_timestamp,
                product_id,
                movement_type,
                quantity,
                adjustment_direction,
                source_location_id,
                destination_location_id,
                source_file,
                run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row["event_id"],
                pd.to_datetime(row["event_date"]).date(),
                pd.to_datetime(
                    row.get("event_timestamp"),
                    errors="coerce"
                ),
                row["product_id"],
                row["movement_type"],
                float(row["quantity"]),
                row.get("adjustment_direction"),
                row.get("source_location_id"),
                row.get("destination_location_id"),
                row["source_file"],
                run_id
            ]
        )

        inserted += 1

    return inserted, duplicates