# 策略设计模式

## 1. 策略框架设计

### 1.1 事件驱动模式

**核心事件类型：**

| 事件 | 触发时机 | 处理内容 |
|------|----------|----------|
| on_init | 策略初始化 | 加载参数、订阅行情 |
| on_tick | 收到Tick | 实时信号计算 |
| on_bar | K线完成 | 周期信号计算 |
| on_order | 订单状态变化 | 订单管理 |
| on_trade | 成交回报 | 持仓更新 |
| on_stop | 策略停止 | 资源清理 |

**策略基类设计：**
```python
from abc import ABC, abstractmethod

class StrategyBase(ABC):
    def __init__(self, engine, setting: dict):
        self.engine = engine
        self.symbol = setting.get("symbol")
        self.pos = 0

    @abstractmethod
    def on_tick(self, tick: TickData):
        pass

    @abstractmethod
    def on_bar(self, bar: BarData):
        pass

    def buy(self, price: float, volume: int):
        """买入开仓"""
        return self.engine.send_order(
            self.symbol, Direction.LONG,
            Offset.OPEN, price, volume
        )

    def sell(self, price: float, volume: int):
        """卖出平仓"""
        return self.engine.send_order(
            self.symbol, Direction.SHORT,
            Offset.CLOSE, price, volume
        )
```

### 1.2 策略模板

**双均线策略示例：**
```python
class DoubleMaStrategy(StrategyBase):
    # 策略参数
    fast_window = 10
    slow_window = 20

    def __init__(self, engine, setting):
        super().__init__(engine, setting)
        self.fast_ma = []
        self.slow_ma = []

    def on_bar(self, bar: BarData):
        # 更新均线
        self.fast_ma.append(bar.close)
        self.slow_ma.append(bar.close)

        if len(self.fast_ma) < self.slow_window:
            return

        fast = sum(self.fast_ma[-self.fast_window:]) / self.fast_window
        slow = sum(self.slow_ma[-self.slow_window:]) / self.slow_window

        # 交易信号
        if fast > slow and self.pos == 0:
            self.buy(bar.close, 1)
        elif fast < slow and self.pos > 0:
            self.sell(bar.close, self.pos)
```

---

## 2. 因子计算模式

### 2.1 因子框架

**因子基类：**
```python
class FactorBase(ABC):
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
```

### 2.2 常用因子

| 因子类型 | 示例 | 计算方式 |
|----------|------|----------|
| 动量因子 | 收益率 | (P_t - P_{t-n}) / P_{t-n} |
| 波动因子 | 波动率 | std(returns, window) |
| 价值因子 | PE/PB | 基本面数据 |
| 技术因子 | RSI/MACD | 技术指标公式 |

---

## 3. 回测引擎设计

### 3.1 回测流程

```
┌─────────────────────────────────────────┐
│              回测引擎流程                 │
├─────────────────────────────────────────┤
│  1. 加载历史数据                          │
│       ↓                                  │
│  2. 初始化策略                            │
│       ↓                                  │
│  3. 按时间顺序回放数据                     │
│       ↓                                  │
│  4. 策略处理事件、生成订单                 │
│       ↓                                  │
│  5. 撮合引擎模拟成交                       │
│       ↓                                  │
│  6. 更新持仓和资金                         │
│       ↓                                  │
│  7. 计算绩效指标                          │
└─────────────────────────────────────────┘
```

### 3.2 撮合模型

**简单撮合：**
- 限价单：价格触及即成交
- 市价单：以当前价成交

**真实撮合：**
- 考虑成交量限制
- 考虑滑点影响
- 考虑部分成交

### 3.3 滑点模型

| 模型 | 公式 | 适用场景 |
|------|------|----------|
| 固定滑点 | slippage = fixed | 低频策略 |
| 比例滑点 | slippage = price * rate | 通用 |
| 波动滑点 | slippage = volatility * k | 高频策略 |

---

## 4. 信号生成模式

### 4.1 信号定义

```python
@dataclass
class Signal:
    symbol: str
    direction: Direction  # LONG/SHORT
    strength: float       # 信号强度 [-1, 1]
    timestamp: datetime
```

### 4.2 信号合成

**多因子信号合成：**
```python
def combine_signals(signals: List[Signal], weights: List[float]) -> Signal:
    total_strength = sum(s.strength * w for s, w in zip(signals, weights))
    return Signal(
        symbol=signals[0].symbol,
        direction=Direction.LONG if total_strength > 0 else Direction.SHORT,
        strength=abs(total_strength),
        timestamp=datetime.now()
    )
```

---

## 5. 仓位管理模式

### 5.1 仓位计算

| 方法 | 公式 | 特点 |
|------|------|------|
| 固定仓位 | pos = fixed | 简单 |
| 等权重 | pos = capital / n | 分散 |
| 波动率倒数 | pos = k / volatility | 风险平价 |
| Kelly公式 | pos = (p*b - q) / b | 最优增长 |

### 5.2 仓位限制

```python
def calculate_position(signal: Signal, capital: float) -> int:
    # 基础仓位
    base_pos = int(capital * signal.strength / price)

    # 仓位限制
    max_pos = int(capital * 0.1 / price)  # 单品种最大10%

    return min(base_pos, max_pos)
```

---

## 6. 绩效指标计算

### 6.1 核心指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 年化收益 | (1 + total_return)^(252/days) - 1 | 年化后的收益率 |
| 夏普比率 | (return - rf) / std | 风险调整后收益 |
| 最大回撤 | max(peak - trough) / peak | 最大亏损幅度 |
| 胜率 | win_trades / total_trades | 盈利交易占比 |
| 盈亏比 | avg_win / avg_loss | 平均盈利/亏损 |

### 6.2 绩效计算示例

```python
def calculate_metrics(returns: pd.Series) -> dict:
    total_return = (1 + returns).prod() - 1
    annual_return = (1 + total_return) ** (252 / len(returns)) - 1
    sharpe = returns.mean() / returns.std() * np.sqrt(252)

    cumulative = (1 + returns).cumprod()
    peak = cumulative.expanding().max()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "sharpe_ratio": sharpe,
        "max_drawdown": max_drawdown
    }
```

---

## 7. 框架对比参考

| 特性 | VNPy | Zipline | Backtrader | QuantConnect |
|------|------|---------|------------|--------------|
| 语言 | Python | Python | Python | C#/Python |
| 架构 | 事件驱动 | 事件驱动 | 事件驱动 | 事件驱动 |
| 实盘支持 | ✅ | ❌ | ✅ | ✅ |
| 多品种 | ✅ | ✅ | ✅ | ✅ |
| 社区活跃 | 高 | 中 | 中 | 高 |
