from pathlib import Path

from app.services.data_service import read_daily_data, clean_data, audit_data
from app.services.feature_service import build_features
from app.services.signal_service import generate_signals


def main():
    df = read_daily_data()
    df = clean_data(df)

    # 数据审计
    audit_data(df, save_report=True)

    # 特征工程
    df = build_features(df)

    # 生成信号
    df = generate_signals(df)

    # 只保留触发信号的记录
    signals = df[df["is_signal"]].copy()

    # 输出目录
    output_dir = Path("data/signals")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "signals.csv"

    # 导出
    signals[
        [
            "symbol",
            "trade_date",
            "close",
            "ma_20",
            "return_20d",
            "volume_ratio_5",
            "is_signal",
            "signal_reason",
        ]
    ].to_csv(output_path, index=False)

    print("\n=== Signals summary ===")
    print(f"Total signals: {len(signals)}")
    print(f"Saved to: {output_path}")

    print("\n=== Signal sample ===")
    print(
        signals[
            [
                "symbol",
                "trade_date",
                "close",
                "ma_20",
                "return_20d",
                "volume_ratio_5",
                "signal_reason",
            ]
        ].head(20)
    )


if __name__ == "__main__":
    main()