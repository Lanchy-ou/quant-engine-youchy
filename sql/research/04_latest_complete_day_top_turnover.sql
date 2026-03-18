SELECT
    symbol,
    trade_date,
    close,
    volume,
    turnover
FROM prices_daily
WHERE trade_date = (
    SELECT MAX(trade_date)
    FROM (
        SELECT
            trade_date,
            COUNT(*) AS n_stocks
        FROM prices_daily
        GROUP BY trade_date
        HAVING COUNT(*) >= 4900
    ) AS valid_dates
)
ORDER BY turnover DESC
LIMIT 20;