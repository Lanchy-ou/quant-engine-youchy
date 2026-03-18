SELECT
    symbol,
    trade_date,
    close,
    volume,
    turnover
FROM prices_daily
WHERE trade_date = (
    SELECT MAX(trade_date) FROM prices_daily
)
ORDER BY turnover DESC
LIMIT 20;