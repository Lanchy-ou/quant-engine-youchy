import duckdb

con = duckdb.connect("data/raw/market.duckdb")
print(con.execute("SHOW TABLES").fetchall())