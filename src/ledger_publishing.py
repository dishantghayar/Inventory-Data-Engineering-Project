
def publish_ledger(con, ledger, run_id):
    inserted = 0

    for _, row in ledger.iterrows():
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM inventory_ledger
            WHERE ledger_id = ?
            """,
            [row["ledger_id"]]
        ).fetchone()[0]

        if exists:
            continue

        con.execute(
            """
            INSERT INTO inventory_ledger (
                ledger_id,
                event_id,
                event_date,
                product_id,
                location_id,
                movement_type,
                quantity_delta,
                run_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                row["ledger_id"],
                row["event_id"],
                row["event_date"],
                row["product_id"],
                row["location_id"],
                row["movement_type"],
                row["quantity_delta"],
                run_id
            ]
        )

        inserted += 1

    return inserted