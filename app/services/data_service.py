from pathlib import Path
import duckdb
import pandas as pd
from datetime import datetime

DB_PATH = Path("data/raw/market.duckdb")

def get_connection():
    return duckdb.connect(str(DB_PATH), read_only=True)

def read_daily_data():
    con = get_connection()

    query = """
    SELECT *
    FROM daily
    """

    df=con.execute(query).fetchdf()

    con.close()

    return df

def clean_data(df):
    df=df.copy()

    df["trade_date"]=pd.to_datetime(df["trade_date"])

    df=df.rename(columns={
        "ts_code":"symbol",
        "vol":"volume",
        "amount":"turnover",
    })

    numeric_cols=["open","high","low","close","volume","turnover"]
    df[numeric_cols]=df[numeric_cols].astype(float)

    df=df.sort_values(["symbol","trade_date"])

    df=df.drop_duplicates(subset=["symbol","trade_date"])

    df=df.dropna()

    df=df[df["close"]>0]
    df=df[df["high"]>=df["low"]]

    df=df.reset_index(drop=True)

    return df

def audit_data(df, save_report=True):
    lines = []

    lines.append("# DATA AUDIT REPORT")
    lines.append("")

    # Dataset size
    lines.append("## Dataset size")
    n_rows = len(df)
    n_stocks = df["symbol"].nunique()
    date_min = df["trade_date"].min()
    date_max = df["trade_date"].max()
    avg_days = df.groupby("symbol").size().mean()

    lines.append(f"Total rows: {n_rows}")
    lines.append(f"Number of stocks: {n_stocks}")
    lines.append(f"Date range: {date_min} to {date_max}")
    lines.append(f"Average trading days per stock: {avg_days:.1f}")
    lines.append("")

    # Missing values
    lines.append("## Missing values ratio")
    missing_ratio = df.isna().mean()
    lines.append(missing_ratio.to_string())
    lines.append("")

    # Suspension
    lines.append("## Suspension statistics")
    zero_volume_ratio = (df["volume"] == 0).mean()
    lines.append(f"Volume = 0 ratio: {zero_volume_ratio:.4f}")
    lines.append("")

    # OHLC consistency
    lines.append("## OHLC consistency check")
    bad_high_low = (df["high"] < df["low"]).sum()
    bad_open = ((df["open"] < df["low"]) | (df["open"] > df["high"])).sum()
    bad_close = ((df["close"] < df["low"]) | (df["close"] > df["high"])).sum()

    lines.append(f"high < low rows: {bad_high_low}")
    lines.append(f"open outside high-low: {bad_open}")
    lines.append(f"close outside high-low: {bad_close}")
    lines.append("")

    # Turnover / volume sanity check
    lines.append("## Turnover / Volume sanity check")
    avg_trade_price = df["turnover"] / df["volume"] / 100
    lines.append(avg_trade_price.describe().to_string())
    lines.append("")
    lines.append("Note: divided by 100 because A-share volume is usually in lots.")
    lines.append("")

    # Distribution
    lines.append("## Price statistics")
    lines.append(df["close"].describe().to_string())
    lines.append("")

    lines.append("## Volume statistics")
    lines.append(df["volume"].describe().to_string())
    lines.append("")

    lines.append("## Turnover statistics")
    lines.append(df["turnover"].describe().to_string())
    lines.append("")

    report_text = "\n".join(lines)

    # 打印到终端
    print(report_text)

    # 保存到 docs/
    if save_report:
        docs_dir = Path("docs/data_reports")
        docs_dir.mkdir(parents=True, exist_ok=True)

        today_str = datetime.now().strftime("%Y-%m-%d")
        report_path = docs_dir / f"data_audit_{today_str}.md"

        report_path.write_text(report_text, encoding="utf-8")
        print(f"\nReport saved to: {report_path}")

    return report_text


