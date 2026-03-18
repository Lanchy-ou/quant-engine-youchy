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
prices_with_20d_high AS (
    SELECT
        symbol,
        trade_date,
        close,
        MAX(close) OVER (
            PARTITION BY symbol
            ORDER BY trade_date
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS high_20d
    FROM prices_daily
)
SELECT
    symbol,
    trade_date,
    close,
    high_20d
FROM prices_with_20d_high
WHERE trade_date = (SELECT trade_date FROM anchor_date)
  AND close = high_20d
ORDER BY symbol;