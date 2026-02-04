# 风控系统设计

## 1. 风控架构

### 1.1 风控层次

```
┌─────────────────────────────────────────────────────┐
│                   风控系统架构                        │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │              事前风控 (Pre-Trade)            │   │
│  │  订单校验 | 限额检查 | 合规检查              │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │              事中风控 (Real-Time)            │   │
│  │  持仓监控 | 盈亏监控 | 风险指标监控          │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │              事后风控 (Post-Trade)           │   │
│  │  对账核查 | 风险报告 | 归因分析              │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 2. 事前风控

### 2.1 订单校验

| 检查项 | 规则 | 处理 |
|--------|------|------|
| 价格合理性 | 偏离度<5% | 拒绝/告警 |
| 数量合理性 | 不超过限额 | 拒绝 |
| 资金充足性 | 可用资金>=保证金 | 拒绝 |
| 持仓限制 | 不超过持仓上限 | 拒绝 |

### 2.2 限额管理

```python
@dataclass
class RiskLimit:
    # 单笔限额
    max_order_value: float = 100000
    max_order_volume: int = 1000

    # 持仓限额
    max_position_value: float = 1000000
    max_position_ratio: float = 0.1

    # 日内限额
    max_daily_turnover: float = 5000000
    max_daily_loss: float = 50000

def check_order(order: Order, limit: RiskLimit) -> bool:
    if order.price * order.volume > limit.max_order_value:
        return False
    if order.volume > limit.max_order_volume:
        return False
    return True
```

---

## 3. 事中风控

### 3.1 实时监控指标

| 指标 | 计算方式 | 阈值 |
|------|----------|------|
| 持仓盈亏 | 市值 - 成本 | 动态 |
| 日内回撤 | 最高点回落 | <5% |
| 敞口风险 | 净持仓市值 | <限额 |
| VaR | 历史模拟法 | <限额 |

### 3.2 熔断机制

```python
class CircuitBreaker:
    def __init__(self):
        self.daily_loss_limit = -50000
        self.drawdown_limit = -0.05

    def check(self, pnl: float, drawdown: float) -> bool:
        if pnl < self.daily_loss_limit:
            self.trigger_stop("日亏损超限")
            return False
        if drawdown < self.drawdown_limit:
            self.trigger_stop("回撤超限")
            return False
        return True

    def trigger_stop(self, reason: str):
        # 停止所有策略
        # 撤销所有挂单
        # 发送告警通知
        pass
```

---

## 4. 事后风控

### 4.1 对账核查

**对账内容：**
- 持仓对账：本地持仓 vs 交易所持仓
- 资金对账：本地资金 vs 交易所资金
- 成交对账：本地成交 vs 交易所成交

### 4.2 风险报告

```markdown
# 日度风险报告

## 1. 持仓概况
| 品种 | 持仓量 | 市值 | 盈亏 |
|------|--------|------|------|

## 2. 风险指标
| 指标 | 数值 | 限额 | 状态 |
|------|------|------|------|
| 日内盈亏 | | | |
| 最大回撤 | | | |
| VaR(95%) | | | |

## 3. 异常事件
[异常事件记录]

## 4. 改进建议
[风控改进建议]
```

---

## 5. 风控规则引擎

### 5.1 规则定义

```python
class RiskRule:
    def __init__(self, name: str, condition: Callable, action: Callable):
        self.name = name
        self.condition = condition
        self.action = action

    def evaluate(self, context: dict) -> bool:
        if self.condition(context):
            self.action(context)
            return True
        return False

# 示例规则
loss_limit_rule = RiskRule(
    name="日亏损限制",
    condition=lambda ctx: ctx["daily_pnl"] < -50000,
    action=lambda ctx: stop_all_strategies()
)
```

### 5.2 规则优先级

| 优先级 | 规则类型 | 处理方式 |
|--------|----------|----------|
| P0 | 强制平仓 | 立即执行 |
| P1 | 禁止开仓 | 立即执行 |
| P2 | 减仓警告 | 通知+限制 |
| P3 | 风险提示 | 仅通知 |
