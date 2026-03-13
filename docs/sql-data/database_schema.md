# Database Schema

## Table: prices_daily

Meaning of one row:
A single stock's daily OHLCV record on one trade date.

Primary key:
(symbol, trade_date)

Columns:

symbol
    stock code

trade_date
    trading date

open
    open price

high
    highest price

low
    lowest price

close
    close price

volume
    trading volume

turnover
    trading amount