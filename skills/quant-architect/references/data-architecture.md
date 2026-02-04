# 数据架构设计

## 1. 行情数据架构

### 1.1 数据类型

| 类型 | 频率 | 用途 |
|------|------|------|
| Tick | 毫秒级 | 高频策略 |
| 分钟K线 | 1/5/15/30/60分钟 | 日内策略 |
| 日K线 | 日级 | 中长期策略 |
| 基本面 | 季度/年度 | 价值投资 |

### 1.2 数据流架构

```
┌─────────────────────────────────────────────────────┐
│                   行情数据流                          │
├─────────────────────────────────────────────────────┤
│  交易所 ──▶ 行情网关 ──▶ 数据清洗 ──▶ 数据分发      │
│                              │                       │
│                              ▼                       │
│                         数据存储                      │
│                    ┌─────────┴─────────┐            │
│                    ▼                   ▼            │
│               实时缓存            历史存储           │
│               (Redis)         (TimescaleDB)         │
└─────────────────────────────────────────────────────┘
```

---

## 2. 数据库选型

### 2.1 时序数据库对比

| 数据库 | 写入性能 | 查询性能 | 适用场景 |
|--------|----------|----------|----------|
| InfluxDB | 高 | 中 | 监控数据 |
| TimescaleDB | 中 | 高 | 金融数据 |
| QuestDB | 极高 | 高 | 高频数据 |
| ClickHouse | 极高 | 极高 | 大数据分析 |

### 2.2 存储方案

**Tick数据存储：**
```sql
CREATE TABLE tick_data (
    symbol VARCHAR(20),
    datetime TIMESTAMPTZ,
    last_price DOUBLE PRECISION,
    volume BIGINT,
    bid_price_1 DOUBLE PRECISION,
    ask_price_1 DOUBLE PRECISION,
    PRIMARY KEY (symbol, datetime)
);

-- 创建时间分区
SELECT create_hypertable('tick_data', 'datetime');
```

**K线数据存储：**
```sql
CREATE TABLE bar_data (
    symbol VARCHAR(20),
    datetime TIMESTAMPTZ,
    interval VARCHAR(10),
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume BIGINT,
    PRIMARY KEY (symbol, datetime, interval)
);
```

---

## 3. 因子存储设计

### 3.1 因子表结构

```sql
CREATE TABLE factor_data (
    symbol VARCHAR(20),
    datetime DATE,
    factor_name VARCHAR(50),
    factor_value DOUBLE PRECISION,
    PRIMARY KEY (symbol, datetime, factor_name)
);

-- 索引优化
CREATE INDEX idx_factor_name ON factor_data(factor_name, datetime);
```

### 3.2 因子计算流程

```
原始数据 ──▶ 因子计算 ──▶ 因子存储 ──▶ 因子服务
    │                                      │
    └──────────── 定时更新 ────────────────┘
```

---

## 4. 数据管道设计

### 4.1 ETL流程

| 阶段 | 任务 | 工具 |
|------|------|------|
| Extract | 数据采集 | API/爬虫 |
| Transform | 数据清洗 | Pandas/Spark |
| Load | 数据入库 | 批量写入 |

### 4.2 数据质量检查

**检查项：**
- 数据完整性：是否有缺失
- 数据准确性：是否有异常值
- 数据时效性：是否及时更新
- 数据一致性：多源数据是否一致

```python
def check_data_quality(df: pd.DataFrame) -> dict:
    return {
        "missing_rate": df.isnull().sum() / len(df),
        "outlier_count": detect_outliers(df),
        "duplicate_count": df.duplicated().sum()
    }
```

---

## 5. 缓存策略

### 5.1 多级缓存

```
┌─────────────────────────────────────────┐
│              多级缓存架构                 │
├─────────────────────────────────────────┤
│  L1: 进程内缓存 (最近N条Tick)            │
│       ↓ 未命中                           │
│  L2: Redis缓存 (当日数据)                │
│       ↓ 未命中                           │
│  L3: 数据库 (历史数据)                   │
└─────────────────────────────────────────┘
```

### 5.2 缓存更新策略

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| Write-Through | 同步写入缓存和DB | 一致性要求高 |
| Write-Behind | 异步批量写入DB | 写入性能要求高 |
| Cache-Aside | 读时加载缓存 | 读多写少 |
