SELECT *
FROM prices_daily
WHERE trade_date = (
    SELECT MAX(trade_date) FROM prices_daily
)
LIMIT 20;