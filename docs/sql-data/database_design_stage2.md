# Stage 2 Database Design

## Table: prices_daily

One row represents:
- one stock
- on one trade date
- one daily OHLCV market record

Primary key:
- (symbol, trade_date)

Candidate columns:
- symbol
- trade_date
- open
- high
- low
- close
- volume
- turnover