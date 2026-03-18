SELECT
    trade_date,
    COUNT(*) AS n_stocks
FROM prices_daily
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 20;