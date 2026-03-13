import pandas as pd


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    基于基础特征生成第一版规则信号。
    """

    df = df.copy()

    # 三个基础条件
    cond_trend = df["close"] > df["ma_20"]
    cond_momentum = df["return_20d"] > 0
    cond_volume = df["volume_ratio_5"] > 1.2

    # 总信号
    df["is_signal"] = cond_trend & cond_momentum & cond_volume

    # 信号原因（便于解释）
    df["signal_reason"] = ""

    df.loc[df["is_signal"], "signal_reason"] = (
        "close > ma_20; return_20d > 0; volume_ratio_5 > 1.2"
    )

    return df