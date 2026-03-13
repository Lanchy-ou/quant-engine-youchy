import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    基于 clean 后的数据构建第一版基础特征。
    输入要求：
    - 已经完成列名统一：symbol, date, open, high, low, close, volume, turnover
    - 已经按 symbol, date 排序
    """

    df = df.copy()

    # -------------------------
    # 1. 日收益率
    # -------------------------
    df["return_1d"] = df.groupby("symbol")["close"].pct_change()

    # -------------------------
    # 2. 5日均线
    # -------------------------
    df["ma_5"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=5, min_periods=5).mean()
    )

    # -------------------------
    # 3. 20日均线
    # -------------------------
    df["ma_20"] = df.groupby("symbol")["close"].transform(
        lambda x: x.rolling(window=20, min_periods=20).mean()
    )

    # -------------------------
    # 4. 20日涨跌幅
    # -------------------------
    df["return_20d"] = df.groupby("symbol")["close"].pct_change(periods=20)

    # -------------------------
    # 5. 20日波动率
    # -------------------------
    df["volatility_20"] = df.groupby("symbol")["return_1d"].transform(
        lambda x: x.rolling(window=20, min_periods=20).std()
    )

    # -------------------------
    # 6. 5日成交量均值
    # -------------------------
    df["volume_ma_5"] = df.groupby("symbol")["volume"].transform(
        lambda x: x.rolling(window=5, min_periods=5).mean()
    )

    # -------------------------
    # 7. 成交量放大倍数
    # -------------------------
    df["volume_ratio_5"] = df["volume"] / df["volume_ma_5"]

    return df