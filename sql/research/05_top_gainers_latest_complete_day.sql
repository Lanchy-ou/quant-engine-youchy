WITH daily_counts AS (
    SELECT
        trade_date,
        COUNT(*) AS n_stocks
    FROM prices_daily
    GROUP BY trade_date
),
anchor_date AS (
    SELECT MAX(trade_date) AS trade_date
    FROM daily_counts
    WHERE n_stocks >= 4900
),
prices_with_prev AS (
    SELECT
        symbol,
        trade_date,
        close,
        LAG(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
        ) AS prev_close,
        volume,
        turnover
    FROM prices_daily
)
SELECT
    symbol,
    trade_date,
    prev_close,
    close,
    ROUND(((close - prev_close) / prev_close * 100)::numeric, 2) AS return_pct,
    volume,
    turnover
FROM prices_with_prev
WHERE trade_date = (SELECT trade_date FROM anchor_date)
  AND prev_close IS NOT NULL
ORDER BY return_pct DESC
LIMIT 20;