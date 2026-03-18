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
prices_with_5d_avg_turnover AS (
    SELECT
        symbol,
        trade_date,
        close,
        turnover,
        AVG(turnover) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS avg_turnover_5d
    FROM prices_daily
)
SELECT
    symbol,
    trade_date,
    close,
    turnover,
    ROUND(avg_turnover_5d::numeric, 2) AS avg_turnover_5d
FROM prices_with_5d_avg_turnover
WHERE trade_date = (SELECT trade_date FROM anchor_date)
ORDER BY avg_turnover_5d DESC
LIMIT 20;