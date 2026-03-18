# Stage 2 Development Log — Database System Setup & SQL Research Layer
# 阶段二开发日志——数据库系统搭建与 SQL 研究层构建

## Date / 日期
2026-03-18

---

# 中文版本

## 1. 阶段背景

阶段二标志着项目从基于 CSV / pandas 的临时分析流程，正式过渡到结构化、可复用、可查询的数据库驱动研究系统。

这一阶段的核心目标不是继续在 notebook 中做零散分析，而是建立一套最小可用的数据库研究基础设施，使后续的特征工程、信号生成和策略研究都能够建立在统一的数据系统之上。

---

## 2. 阶段目标

本阶段的目标是构建以下最小数据库系统链路：

**DuckDB（原始行情数据）  
→ pandas 清洗  
→ PostgreSQL（结构化存储）  
→ SQL 查询（研究层）**

具体目标包括：

1. 搭建 PostgreSQL 数据库服务环境  
2. 设计并创建 `prices_daily` 核心价格表  
3. 建立从 DuckDB 到 PostgreSQL 的加载管道  
4. 学习并实践 SQL 基础查询  
5. 引入时间序列 SQL 方法（尤其是窗口函数）  
6. 构建研究层查询文件，为后续量化研究提供基础

---

## 3. 本阶段涉及的文件

### 3.1 核心基础设施文件
- `docker-compose.yml`
- `scripts/load_prices_to_pg.py`
- `sql/schema/001_create_prices_daily.sql`

### 3.2 SQL 研究层文件
- `sql/research/01_latest_trade_date_snapshot.sql`
- `sql/research/02_latest_day_top_turnover.sql`
- `sql/research/03_daily_stock_coverage.sql`
- `sql/research/04_latest_complete_day_top_turnover.sql`
- `sql/research/05_top_gainers_latest_complete_day.sql`
- `sql/research/06_top_losers_latest_complete_day.sql`
- `sql/research/07_20d_high_breakout_latest_complete_day.sql`
- `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
- `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

### 3.3 阶段文档文件
- `sql-data/2026-03-18_stage2_database.md`
- `sql-data/database_design_stage2.md`
- `sql-data/database_schema.md`

### 3.4 项目中与本阶段相关的辅助检查脚本
- `notebooks/01_inspect_market_data.py`
- `notebooks/db_file.py`

---

## 4. 本阶段具体完成内容

### 4.1 PostgreSQL 环境搭建（Docker）

本阶段首先完成了 PostgreSQL 的服务化部署。

已完成的动作包括：

- 在 Windows 主机安装 Docker Desktop
- 启用 WSL 集成
- 在项目根目录配置 `docker-compose.yml`
- 使用 Docker 启动 PostgreSQL 容器
- 确认数据库服务以容器形式运行，而不是以本地文件形式存在

数据库配置信息如下：

- Container: `quant_postgres`
- Database: `quantdb`
- User: `quant`

在这一过程中，一个关键认知是：

> 数据库是一个服务（service），不是一个普通数据文件（file）。

---

### 4.2 数据表设计：`prices_daily`

本阶段完成了核心行情表 `prices_daily` 的设计与创建。

对应文件：

- `sql/schema/001_create_prices_daily.sql`

表结构如下：

- `symbol` — 股票代码
- `trade_date` — 交易日期
- `open`
- `high`
- `low`
- `close`
- `volume`
- `turnover`

主键定义为：

- `(symbol, trade_date)`

这个设计保证了同一只股票在同一天只存在一条记录，为后续时间序列研究提供了稳定主键基础。

---

### 4.3 数据清洗与加载管道

本阶段建立了从 DuckDB 到 PostgreSQL 的完整加载流程。

对应脚本：

- `scripts/load_prices_to_pg.py`

数据来源为 DuckDB 中的 `daily` 表，原始字段包括：

- `ts_code`
- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `vol`
- `amount`

清洗逻辑包括：

- `ts_code → symbol`
- `vol → volume`
- `amount → turnover`
- 将 `trade_date` 转换为日期类型
- 排序
- 去重
- 删除无效行

最终形成的数据管道为：

**DuckDB  
→ pandas `clean_data()`  
→ PostgreSQL `prices_daily`**

---

### 4.4 数据加载结果验证

完成全量导入后，对数据表进行了基本验证。

验证结果：

- 总行数：`1,235,307`
- 日期范围：`2025-01-09` → `2026-01-23`

说明价格表已经成功承载全市场日频行情，并可供后续 SQL 查询使用。

---

### 4.5 基础 SQL 查询实践

本阶段完成了若干基础研究查询，并保存为 SQL 文件。

对应文件包括：

- `sql/research/01_latest_trade_date_snapshot.sql`
- `sql/research/02_latest_day_top_turnover.sql`
- `sql/research/03_daily_stock_coverage.sql`
- `sql/research/04_latest_complete_day_top_turnover.sql`

通过这些查询，完成了以下研究任务：

1. 查找数据中的最新交易日
2. 查看最新交易日的市场快照
3. 统计每天的股票覆盖数量
4. 识别“最新完整交易日”
5. 在最新完整交易日上按成交额排序

---

### 4.6 关键发现：最新日期不等于可研究日期

在覆盖度分析中，发现最近几天的数据并不完整。

典型结果如下：

- `2026-01-23` → 6 只股票
- `2026-01-22` → 223 只股票
- `2026-01-21` → 398 只股票
- `2026-01-20` → 821 只股票
- `2026-01-19` → 4997 只股票

这说明：

> 数据中的最大日期 `MAX(trade_date)` 并不一定是可以用于横截面研究的有效交易日。

因此本阶段正式引入了“最新完整交易日”的概念，并使用 `n_stocks >= 4900` 作为完整性的经验阈值。

在当前数据中，最新完整交易日为：

- `2026-01-19`

这是本阶段非常重要的研究层认知升级。

---

### 4.7 时间序列 SQL：窗口函数与 `LAG()`

阶段二后半段的核心任务是从静态查询转向时间序列 SQL。

这一部分新增的文件包括：

- `sql/research/05_top_gainers_latest_complete_day.sql`
- `sql/research/06_top_losers_latest_complete_day.sql`
- `sql/research/07_20d_high_breakout_latest_complete_day.sql`
- `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
- `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

本阶段新掌握的 SQL 方法包括：

- `LAG()`
- `AVG() OVER (...)`
- `MAX() OVER (...)`
- `PARTITION BY`
- `ORDER BY`
- `ROWS BETWEEN ... PRECEDING AND CURRENT ROW`

这标志着系统已经从“数据库存储”正式进入“SQL 驱动研究层”。

---

### 4.8 Top Gainers / Top Losers 查询

通过 `LAG(close)`，成功计算了每只股票相对于上一交易日的收益率。

其中：

- `sql/research/05_top_gainers_latest_complete_day.sql`  
  用于筛选最新完整交易日涨幅最大的股票
- `sql/research/06_top_losers_latest_complete_day.sql`  
  用于筛选最新完整交易日跌幅最大的股票

在实现过程中，修正了 PostgreSQL 中 `ROUND(double precision, integer)` 不支持的问题，最终采用：

```sql
ROUND(((close - prev_close) / prev_close * 100)::numeric, 2)
```

这一修改保证了收益率字段 `return_pct` 能够正确保留两位小数。

`06_top_losers_latest_complete_day.sql` 已成功运行并返回合理结果，说明 `LAG()` 时间序列逻辑已跑通。

---

### 4.9 滚动窗口查询：20 日高点 / 5 日成交额 / 20 日成交量

本阶段完成了三个滚动窗口研究查询：

1. `sql/research/07_20d_high_breakout_latest_complete_day.sql`
2. `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
3. `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

它们分别实现了：

- 近 20 日最高收盘价识别
- 近 5 日平均成交额排序
- 近 20 日平均成交量排序

这些查询说明系统已经能够：

- 计算滚动统计量
- 基于窗口函数定义市场活跃度
- 从单日横截面研究扩展到带时间记忆的研究视角

其中，`sql/research/07_20d_high_breakout_latest_complete_day.sql` 返回了 `1321` 行结果，说明当前的 breakout 定义较宽松，本质上更接近：

> “当前收盘价处于最近 20 个交易日窗口最高位置”

而不一定是严格意义上的“突破前高”。

这为下一阶段进一步收紧 breakout 定义提供了明确方向。

---

## 5. 本阶段遇到的问题与解决方案

### 5.1 Docker 端口映射失败

在尝试通过 `docker compose up -d` 启动 PostgreSQL 并发布宿主机端口时，遇到了 Docker Desktop / WSL 端口转发错误：

- `/forwards/expose returned unexpected status: 500`

尝试过：

- `5432:5432`
- `127.0.0.1:5433:5432`

均失败。

最终采用的解决方案是：

- 暂时移除 `docker-compose.yml` 中的 `ports:` 配置
- 仅在容器内部运行 PostgreSQL
- 使用以下命令进入数据库：

```bash
docker exec -it quant_postgres psql -U quant -d quantdb
```

这一方案成功恢复了数据库使用能力，使 Stage 2 能够继续推进。

---

### 5.2 PostgreSQL 的 `ROUND` 类型问题

在收益率 SQL 中，曾出现：

- `function round(double precision, integer) does not exist`

原因是 PostgreSQL 不支持对 `double precision` 直接使用两参数版 `ROUND(x, n)`。

解决方法：

- 将表达式显式转换为 `numeric`

最终修复写法为：

```sql
ROUND(((close - prev_close) / prev_close * 100)::numeric, 2)
```

---

### 5.3 psql 多行粘贴混乱

在终端中手动粘贴长 SQL 时，出现过多行输入被打乱的问题。

解决方式：

- 将 SQL 保存为独立 `.sql` 文件
- 用重定向方式执行

例如：

```bash
docker exec -i quant_postgres psql -U quant -d quantdb < sql/research/06_top_losers_latest_complete_day.sql
```

这一方式比手动粘贴更稳定，也更符合工程化习惯。

---

## 6. 本阶段学到的关键概念

本阶段建立了以下核心理解：

### 数据系统层面
- 数据库是服务，不是文件
- 结构化表设计决定后续研究便利性
- 主键设计非常关键

### SQL 层面
- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `GROUP BY`
- `COUNT(*)`
- `HAVING`
- 子查询
- 窗口函数
- `LAG()`
- 滚动均值与滚动最大值计算

### 研究层面
- 最新日期不等于有效研究日期
- 横截面研究必须先做 coverage validation
- breakout 的定义需要精确控制，否则结果会过宽
- 成交额活跃度与成交量活跃度是两个不同维度

---

## 7. 阶段成果总结

阶段二已经成功完成了以下里程碑：

1. 建立了 PostgreSQL 数据库环境  
2. 创建了 `prices_daily` 核心表  
3. 建立了 DuckDB → pandas → PostgreSQL 的加载管道  
4. 完成了基础 SQL 查询  
5. 识别并引入了“最新完整交易日”概念  
6. 完成了基于 `LAG()` 的涨跌幅研究  
7. 完成了基于窗口函数的滚动统计研究  
8. 将研究查询沉淀为独立 SQL 文件  

因此，本阶段已经实现了从：

**CSV / pandas 临时分析流程**  
到  
**Database + SQL-driven research system**

的正式升级。

---

## 8. 阶段结论

**Stage 2 核心目标已完成。**

当前系统已经具备：

- 结构化价格数据存储能力
- 基础研究查询能力
- 时间序列 SQL 研究能力
- 后续特征表与信号表扩展能力

阶段二的主体工作可以视为完成。后续可以进入：

- breakout 定义 refinement
- `features_daily` 表设计
- `signals_daily` 表设计
- append / upsert 数据更新策略
- 阶段三：特征工程与信号层构建

---

# English Version

## 1. Stage Context

Stage 2 marks the transition from a temporary CSV / pandas-based workflow to a structured, reusable, database-driven research system.

The purpose of this stage was not to continue doing ad hoc analysis in notebooks, but to build a minimal database infrastructure that can support future feature engineering, signal generation, and systematic research.

---

## 2. Stage Objective

The goal of this stage was to build the following minimal data system:

**DuckDB (raw market data)  
→ pandas cleaning  
→ PostgreSQL (structured storage)  
→ SQL queries (research layer)**

More specifically, the objectives were:

1. Set up a PostgreSQL service environment  
2. Design and create the core `prices_daily` table  
3. Build a loading pipeline from DuckDB to PostgreSQL  
4. Learn and practice foundational SQL queries  
5. Introduce time-series SQL logic, especially window functions  
6. Build reusable research-layer SQL files for later quantitative work

---

## 3. Files Involved in This Stage

### 3.1 Core infrastructure files
- `docker-compose.yml`
- `scripts/load_prices_to_pg.py`
- `sql/schema/001_create_prices_daily.sql`

### 3.2 SQL research-layer files
- `sql/research/01_latest_trade_date_snapshot.sql`
- `sql/research/02_latest_day_top_turnover.sql`
- `sql/research/03_daily_stock_coverage.sql`
- `sql/research/04_latest_complete_day_top_turnover.sql`
- `sql/research/05_top_gainers_latest_complete_day.sql`
- `sql/research/06_top_losers_latest_complete_day.sql`
- `sql/research/07_20d_high_breakout_latest_complete_day.sql`
- `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
- `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

### 3.3 Stage documentation files
- `sql-data/2026-03-18_stage2_database.md`
- `sql-data/database_design_stage2.md`
- `sql-data/database_schema.md`

### 3.4 Auxiliary inspection scripts related to this stage
- `notebooks/01_inspect_market_data.py`
- `notebooks/db_file.py`

---

## 4. Work Completed

### 4.1 PostgreSQL environment setup with Docker

This stage began with the service-oriented deployment of PostgreSQL.

Completed actions included:

- Installing Docker Desktop on the Windows host
- Enabling WSL integration
- Configuring `docker-compose.yml` in the project root
- Launching the PostgreSQL container with Docker
- Confirming that the database exists as a service rather than a local file

Database configuration:

- Container: `quant_postgres`
- Database: `quantdb`
- User: `quant`

A key concept learned here was:

> A database is a service, not a file.

---

### 4.2 Core table design: `prices_daily`

The core daily price table `prices_daily` was designed and created.

Corresponding file:

- `sql/schema/001_create_prices_daily.sql`

The table contains:

- `symbol`
- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `turnover`

The primary key is:

- `(symbol, trade_date)`

This guarantees one unique record per stock per trading day and provides a stable structure for time-series research.

---

### 4.3 Data cleaning and loading pipeline

A full data pipeline from DuckDB to PostgreSQL was built.

Corresponding script:

- `scripts/load_prices_to_pg.py`

The source data came from the DuckDB table `daily`, with raw columns:

- `ts_code`
- `trade_date`
- `open`
- `high`
- `low`
- `close`
- `vol`
- `amount`

Cleaning logic included:

- `ts_code → symbol`
- `vol → volume`
- `amount → turnover`
- converting `trade_date` into proper date type
- sorting
- deduplication
- removing invalid rows

Final data pipeline:

**DuckDB  
→ pandas `clean_data()`  
→ PostgreSQL `prices_daily`**

---

### 4.4 Validation of loaded data

After the full load, the resulting table was validated.

Validation results:

- Total rows: `1,235,307`
- Date range: `2025-01-09` → `2026-01-23`

This confirmed that the table successfully holds daily market data and is ready for SQL-based research.

---

### 4.5 Foundational SQL research queries

Several foundational research queries were completed and saved as standalone SQL files.

These files include:

- `sql/research/01_latest_trade_date_snapshot.sql`
- `sql/research/02_latest_day_top_turnover.sql`
- `sql/research/03_daily_stock_coverage.sql`
- `sql/research/04_latest_complete_day_top_turnover.sql`

These queries were used to:

1. Identify the latest trading date in the dataset
2. Inspect the market snapshot on the latest date
3. Measure daily cross-sectional stock coverage
4. Identify the latest complete trading day
5. Rank stocks by turnover on the latest complete day

---

### 4.6 Key finding: latest date is not always a research-valid date

Coverage analysis showed that the most recent dates in the data were incomplete.

Typical results:

- `2026-01-23` → 6 stocks
- `2026-01-22` → 223 stocks
- `2026-01-21` → 398 stocks
- `2026-01-20` → 821 stocks
- `2026-01-19` → 4997 stocks

This led to an important insight:

> `MAX(trade_date)` is not necessarily the latest usable date for cross-sectional research.

Therefore, the concept of a **latest complete trading day** was formally introduced, using `n_stocks >= 4900` as a practical completeness threshold.

In the current data, the latest complete trading day was identified as:

- `2026-01-19`

This was an important upgrade in research-layer thinking.

---

### 4.7 Time-series SQL: window functions and `LAG()`

The core task of the second half of Stage 2 was to move from static queries to time-series SQL.

New files added in this part include:

- `sql/research/05_top_gainers_latest_complete_day.sql`
- `sql/research/06_top_losers_latest_complete_day.sql`
- `sql/research/07_20d_high_breakout_latest_complete_day.sql`
- `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
- `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

New SQL concepts learned and applied:

- `LAG()`
- `AVG() OVER (...)`
- `MAX() OVER (...)`
- `PARTITION BY`
- `ORDER BY`
- `ROWS BETWEEN ... PRECEDING AND CURRENT ROW`

This marked the formal transition from simple database storage to an SQL-driven research layer.

---

### 4.8 Top Gainers / Top Losers queries

Using `LAG(close)`, daily returns relative to the previous trading day were successfully computed.

In particular:

- `sql/research/05_top_gainers_latest_complete_day.sql`  
  identifies the biggest gainers on the latest complete trading day
- `sql/research/06_top_losers_latest_complete_day.sql`  
  identifies the biggest losers on the latest complete trading day

During implementation, a PostgreSQL type issue with `ROUND(double precision, integer)` was fixed by explicitly casting to `numeric`:

```sql
ROUND(((close - prev_close) / prev_close * 100)::numeric, 2)
```

This ensured that the `return_pct` field was correctly rounded to two decimal places.

The successful execution of `06_top_losers_latest_complete_day.sql` confirmed that the `LAG()`-based time-series logic was working correctly.

---

### 4.9 Rolling-window queries: 20-day high / 5-day turnover / 20-day volume

Three rolling-window research queries were also completed:

1. `sql/research/07_20d_high_breakout_latest_complete_day.sql`
2. `sql/research/08_5d_avg_turnover_rank_latest_complete_day.sql`
3. `sql/research/09_20d_avg_volume_rank_latest_complete_day.sql`

These queries respectively implemented:

- identification of 20-day high closing prices
- ranking by 5-day average turnover
- ranking by 20-day average volume

These results show that the system can now:

- compute rolling statistics
- define market activity using window functions
- move from one-day cross-sectional research to time-aware market analysis

Notably, `sql/research/07_20d_high_breakout_latest_complete_day.sql` returned `1321` rows, which indicates that the current breakout definition is still broad. It is closer to:

> “stocks whose current close is at the highest level within the recent 20-day window”

rather than a strict technical breakout above previous highs.

This provides a clear direction for future refinement.

---

## 5. Issues Encountered and Solutions

### 5.1 Docker port publishing failure

When trying to start PostgreSQL with published host ports, Docker Desktop / WSL port forwarding failed with:

- `/forwards/expose returned unexpected status: 500`

Both of the following mappings were attempted and failed:

- `5432:5432`
- `127.0.0.1:5433:5432`

The eventual solution was:

- temporarily remove the `ports:` section from `docker-compose.yml`
- run PostgreSQL only inside the container
- access it using:

```bash
docker exec -it quant_postgres psql -U quant -d quantdb
```

This restored database usability and allowed Stage 2 to continue.

---

### 5.2 PostgreSQL `ROUND` type issue

In the return calculation SQL, the following error occurred:

- `function round(double precision, integer) does not exist`

The reason is that PostgreSQL does not support the two-argument form of `ROUND(x, n)` directly on `double precision`.

The solution was to explicitly cast the expression to `numeric`:

```sql
ROUND(((close - prev_close) / prev_close * 100)::numeric, 2)
```

---

### 5.3 Multi-line SQL paste issues in psql

Long SQL queries pasted manually into the terminal sometimes became corrupted.

The solution was to:

- save queries as independent `.sql` files
- execute them using input redirection

For example:

```bash
docker exec -i quant_postgres psql -U quant -d quantdb < sql/research/06_top_losers_latest_complete_day.sql
```

This proved to be more stable and more aligned with engineering best practice.

---

## 6. Key Concepts Learned

### Data system concepts
- A database is a service, not a file
- Structured table design determines later research convenience
- Primary key design is critical

### SQL concepts
- `SELECT`
- `WHERE`
- `ORDER BY`
- `LIMIT`
- `GROUP BY`
- `COUNT(*)`
- `HAVING`
- subqueries
- window functions
- `LAG()`
- rolling averages and rolling maxima

### Research-layer concepts
- the latest date is not always a valid research date
- cross-sectional research requires coverage validation first
- breakout definitions must be precise, otherwise the results become too broad
- turnover activity and volume activity are two different market dimensions

---

## 7. Stage Outcome Summary

Stage 2 successfully completed the following milestones:

1. Set up the PostgreSQL environment  
2. Created the core `prices_daily` table  
3. Built the DuckDB → pandas → PostgreSQL loading pipeline  
4. Completed foundational SQL research queries  
5. Introduced the concept of the latest complete trading day  
6. Built `LAG()`-based return research queries  
7. Built rolling-window statistical research queries  
8. Materialised research logic into reusable SQL files  

As a result, the system has formally evolved from:

**a temporary CSV / pandas workflow**  
to  
**a database + SQL-driven research system**

---

## 8. Stage Conclusion

**The core objectives of Stage 2 have been completed.**

The current system now has:

- structured daily price storage
- foundational research-query capability
- time-series SQL research capability
- the ability to expand into feature tables and signal tables later

Stage 2 can therefore be considered complete in its core scope.

The natural next steps are:

- breakout definition refinement
- `features_daily` table design
- `signals_daily` table design
- append / upsert data update strategy
- Stage 3: feature engineering and signal-layer construction
