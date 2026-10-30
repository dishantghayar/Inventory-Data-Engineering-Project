
from pathlib import Path
from src.database import get_connection

def export_reports():
    base = Path(__file__).resolve().parents[1]
    output = base / "data" / "output"
    output.mkdir(parents=True, exist_ok=True)

    con = get_connection()

    balances = con.execute("""
        SELECT *
        FROM daily_inventory_balances
        ORDER BY inventory_date, product_id, location_id
    """).df()

    runs = con.execute("""
        SELECT *
        FROM pipeline_runs
        ORDER BY start_time DESC
    """).df()

    rejects = con.execute("""
        SELECT *
        FROM rejected_records
    """).df()

    balances.to_parquet(
        output / "daily_inventory_balances.parquet",
        index=False
    )

    balances.to_csv(
        output / "daily_inventory_balances.csv",
        index=False
    )

    runs.to_csv(
        output / "pipeline_run_report.csv",
        index=False
    )

    rejects.to_csv(
        output / "rejected_records.csv",
        index=False
    )

    con.close()

    print("Reports exported successfully.")

if __name__ == "__main__":
    export_reports()
    
def check_negative_stock(ledger):
    stock = {}

    ledger = ledger.sort_values(
        ["event_date", "event_id", "ledger_id"]
    )

    invalid_events = set()

    for _, row in ledger.iterrows():
        key = (
            row["product_id"],
            row["location_id"]
        )

        new_balance = (
            stock.get(key, 0)
            + float(row["quantity_delta"])
        )

        if new_balance < 0:
            invalid_events.add(row["event_id"])
        else:
            stock[key] = new_balance

    return invalid_events