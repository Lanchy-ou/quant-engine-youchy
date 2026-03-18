# Stage 2 Database Design

## Table: prices_daily

One row represents:
A single stock's daily market record on one trade date.

Primary key:
(symbol, trade_date)

Columns:
- symbol
- trade_date
- open
- high
- low
- close
- volume
- turnover