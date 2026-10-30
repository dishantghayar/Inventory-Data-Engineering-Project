SELECT
    inventory_date,
    product_id,
    location_id,
    opening_quantity,
    net_movement,
    closing_quantity
FROM daily_inventory_balances
ORDER BY
    product_id,
    location_id,
    inventory_date;

SELECT *
FROM daily_inventory_balances
WHERE closing_quantity
    <> opening_quantity + net_movement;

SELECT *
FROM daily_inventory_balances
WHERE closing_quantity < 0;

SELECT
    SUM(quantity_delta) AS ledger_total
FROM inventory_ledger;

SELECT
    event_id,
    SUM(quantity_delta) AS transfer_difference
FROM inventory_ledger
WHERE movement_type IN (
    'TRANSFER_OUT',
    'TRANSFER_IN'
)
GROUP BY event_id
HAVING ABS(SUM(quantity_delta)) > 0.001;

SELECT *
FROM pipeline_runs
ORDER BY start_time DESC;

SELECT
    event_id,
    source_file,
    rejection_reason,
    run_id
FROM rejected_records;