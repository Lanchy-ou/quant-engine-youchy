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
prices_with_20d_avg_volume AS (
    SELECT
        symbol,
        trade_date,
        close,
        volume,
        AVG(volume) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS avg_volume_20d
    FROM prices_daily
)
SELECT
    symbol,
    trade_date,
    close,
    volume,
    ROUND(avg_volume_20d::numeric, 2) AS avg_volume_20d
FROM prices_with_20d_avg_volume
WHERE trade_date = (SELECT trade_date FROM anchor_date)
ORDER BY avg_volume_20d DESC
LIMIT 20;