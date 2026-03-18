from pathlib import Path

import duckdb
import pandas as pd
from sqlalchemy import create_engine


def read_daily_data(db_path: str) -> pd.DataFrame:
    """
    Read raw daily market data from DuckDB.
    """
    query = """
    SELECT *
    FROM daily
    """
    return duckdb.connect(db_path).execute(query).df()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw market data and standardize column names/types.
    """
    df = df.copy()

    df["trade_date"] = pd.to_datetime(df["trade_date"])

    df = df.rename(columns={
        "ts_code": "symbol",
        "vol": "volume",
        "amount": "turnover",
    })

    numeric_cols = ["open", "high", "low", "close", "volume", "turnover"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df = df.sort_values(["symbol", "trade_date"])
    df = df.drop_duplicates(subset=["symbol", "trade_date"])
    df = df.dropna()

    df = df[df["close"] > 0]
    df = df[df["high"] >= df["low"]]

    df = df.reset_index(drop=True)

    keep_cols = [
        "symbol",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
    ]
    df = df[keep_cols]

    return df


def write_prices_to_postgres(df: pd.DataFrame) -> None:
    """
    Write cleaned daily prices into PostgreSQL.
    """
    engine = create_engine(
        "postgresql+psycopg2://quant:quantpass@localhost:5432/quantdb"
    )

    df.to_sql(
        name="prices_daily",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=5000,
    )


def main() -> None:
    db_path = "data/raw/market.duckdb"

    if not Path(db_path).exists():
        raise FileNotFoundError(f"DuckDB file not found: {db_path}")

    print("Reading raw data from DuckDB...")
    raw_df = read_daily_data(db_path)

    print(raw_df.columns.tolist())
    print(raw_df.head())

    print("Cleaning data...")
    clean_df = clean_data(raw_df)

    print(f"Cleaned rows: {len(clean_df):,}")
    print("Writing data to PostgreSQL...")
    write_prices_to_postgres(clean_df)

    print("Done.")


if __name__ == "__main__":
    main()