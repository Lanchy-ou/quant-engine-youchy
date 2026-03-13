from pathlib import Path
import duckdb
import pandas as pd

# 1. 定义数据库路径
DB_PATH = Path("data/raw/market.duckdb")

# 2. 连接数据库
con = duckdb.connect(str(DB_PATH), read_only=True)

# 3. 查看所有表
tables = con.execute("SHOW TABLES").fetchdf()
print("=== 数据库中的表 ===")
print(tables)
print()

# 4. 查看 daily 表结构
schema = con.execute("DESCRIBE daily").fetchdf()
print("=== daily 表结构 ===")
print(schema)
print()

# 5. 查看前 5 行
sample = con.execute("SELECT * FROM daily LIMIT 5").fetchdf()
print("=== daily 前 5 行 ===")
print(sample)
print()

# 6. 查看总行数
row_count = con.execute("SELECT COUNT(*) AS cnt FROM daily").fetchdf()
print("=== daily 总行数 ===")
print(row_count)
print()

# 7. 查看股票数量
stock_count = con.execute("""
    SELECT COUNT(DISTINCT ts_code) AS n_stocks
    FROM daily
""").fetchdf()
print("=== 股票数量 ===")
print(stock_count)
print()

# 8. 查看日期范围
date_range = con.execute("""
    SELECT MIN(trade_date) AS min_date,
           MAX(trade_date) AS max_date
    FROM daily
""").fetchdf()
print("=== 日期范围 ===")
print(date_range)
print()

# 9. 随机看一只股票的前几行（先随便挑一只）
one_stock = con.execute("""
    SELECT *
    FROM daily
    WHERE ts_code = (
        SELECT ts_code
        FROM daily
        LIMIT 1
    )
    ORDER BY trade_date
    LIMIT 10
""").fetchdf()
print("=== 某只股票样例 ===")
print(one_stock)
print()

# 10. 关闭连接
con.close()