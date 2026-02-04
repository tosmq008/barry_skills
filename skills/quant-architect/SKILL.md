---
name: quant-architect
description: "Quantitative trading system technical architect expert. Designs high-performance trading architectures, optimizes latency and throughput, reviews strategy implementations, analyzes data pipelines, and triages bugs from a quant-system perspective. Covers backtesting, risk control, execution systems, and performance benchmarking."
license: MIT
compatibility: "Works with Python/C++ quantitative projects. Supports vnpy, zipline, backtrader frameworks. Requires understanding of financial markets and trading systems."
metadata:
  category: architecture
  phase: design-and-optimization
  version: "1.0.0"
  author: quant-expert
allowed-tools: bash read_file write_file grep glob
---

# Quant Architect Skill

作为量化交易系统技术架构师，从专业视角进行系统设计、性能优化、策略架构评审、数据分析设计，以及Bug和性能问题的诊断处理。

## When to Use

**适用场景：**
- 量化交易系统架构设计与评审
- 交易系统性能优化（低延迟、高吞吐）
- 量化策略框架设计
- 行情数据与因子计算架构设计
- 风控系统设计
- 从量化视角诊断和处理Bug
- 性能瓶颈分析与优化

**不适用：**
- 纯业务需求分析（无技术架构）
- 非量化领域的系统设计
- 简单的代码修复（无架构影响）

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    量化架构师工作流程                              │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 需求分析          Phase 2: 架构设计                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 业务需求理解    │  ──▶  │ 系统架构设计    │                  │
│  │ 性能指标定义    │       │ 组件拆分设计    │                  │
│  │ 技术约束分析    │       │ 数据流设计      │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 3: 性能优化          Phase 4: 策略设计                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 延迟分析优化    │  ──▶  │ 策略框架设计    │                  │
│  │ 吞吐量优化      │       │ 回测系统设计    │                  │
│  │ 资源利用优化    │       │ 风控集成设计    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 5: 问题诊断          Phase 6: 评审报告                     │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ Bug根因分析     │  ──▶  │ 架构评审报告    │                  │
│  │ 性能瓶颈定位    │       │ 优化建议清单    │                  │
│  │ 量化视角修复    │       │ 风险评估报告    │                  │
│  └─────────────────┘       └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 需求分析 (Requirement Analysis)

### 1.1 业务需求理解

**必须明确的内容：**
- 交易品种：股票、期货、期权、数字货币
- 交易频率：高频（毫秒级）、中频（秒级）、低频（分钟/日级）
- 策略类型：趋势跟踪、均值回归、套利、做市
- 资金规模：影响系统容量设计

### 1.2 性能指标定义

| 指标类型 | 高频系统 | 中频系统 | 低频系统 |
|----------|----------|----------|----------|
| 订单延迟 | <1ms | <100ms | <1s |
| 行情延迟 | <100μs | <10ms | <100ms |
| 吞吐量 | >100K TPS | >10K TPS | >1K TPS |
| 可用性 | 99.99% | 99.9% | 99% |

### 1.3 技术约束分析

**需要评估的约束：**
- 交易所接口限制（频率、连接数）
- 网络环境（机房位置、专线）
- 硬件资源（CPU、内存、存储）
- 合规要求（风控、审计）

---

## Phase 2: 架构设计 (Architecture Design)

> ⚠️ **执行前必须读取 `references/system-architecture-guide.md` 获取完整架构指南**
> ⚠️ **数据架构设计请参考 `references/data-architecture.md`**

### 2.1 系统分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                      量化系统分层架构                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    应用层 (Application)              │   │
│  │  策略管理 | 风控管理 | 监控告警 | 报表分析           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    策略层 (Strategy)                 │   │
│  │  信号生成 | 仓位管理 | 订单生成 | 回测引擎           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    执行层 (Execution)                │   │
│  │  订单路由 | 订单管理 | 成交处理 | 持仓管理           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    数据层 (Data)                     │   │
│  │  行情接收 | 数据清洗 | 因子计算 | 数据存储           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    基础层 (Infrastructure)           │   │
│  │  网络通信 | 消息队列 | 日志系统 | 配置管理           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件设计

| 组件 | 职责 | 关键技术 |
|------|------|----------|
| 行情网关 | 接收交易所行情 | WebSocket/FIX协议 |
| 策略引擎 | 执行交易策略 | 事件驱动/多线程 |
| 风控引擎 | 实时风险控制 | 规则引擎/限额管理 |
| 订单管理 | 订单生命周期管理 | 状态机/持久化 |
| 执行网关 | 订单发送与回报 | 交易所API/FIX |

---

## Phase 3: 性能优化 (Performance Optimization)

> ⚠️ **执行前必须读取 `references/performance-optimization.md` 获取性能优化指南**

### 3.1 延迟优化

**关键技术：**

| 优化层面 | 技术手段 | 预期效果 |
|----------|----------|----------|
| 网络层 | 内核旁路(DPDK/Solarflare) | 减少50%网络延迟 |
| 内存层 | 零拷贝/内存池 | 减少内存分配开销 |
| CPU层 | CPU亲和性/NUMA优化 | 减少上下文切换 |
| 代码层 | 热路径优化/分支预测 | 提升执行效率 |

### 3.2 吞吐量优化

**优化策略：**
- 批处理：合并小消息减少系统调用
- 异步IO：使用epoll/io_uring
- 连接池：复用网络连接
- 无锁队列：减少锁竞争

### 3.3 资源利用优化

**内存优化：**
- 对象池预分配
- 避免GC（C++/Rust优先）
- 内存对齐优化

**CPU优化：**
- 多核并行处理
- SIMD向量化计算
- 缓存友好的数据结构

---

## Phase 4: 策略设计 (Strategy Design)

> ⚠️ **执行前必须读取 `references/strategy-design-patterns.md` 获取策略设计模式**

### 4.1 策略框架设计

**事件驱动架构：**
```python
class Strategy:
    def on_tick(self, tick: TickData):
        """行情Tick事件"""
        pass

    def on_bar(self, bar: BarData):
        """K线Bar事件"""
        pass

    def on_order(self, order: OrderData):
        """订单状态事件"""
        pass

    def on_trade(self, trade: TradeData):
        """成交回报事件"""
        pass
```

### 4.2 回测系统设计

**回测引擎核心组件：**

| 组件 | 职责 |
|------|------|
| 数据回放器 | 按时间顺序回放历史数据 |
| 撮合引擎 | 模拟订单撮合 |
| 滑点模型 | 模拟真实滑点 |
| 手续费模型 | 计算交易成本 |
| 绩效分析 | 计算收益指标 |

### 4.3 风控集成设计

> ⚠️ **执行前必须读取 `references/risk-control-design.md` 获取风控设计指南**

**风控检查点：**
- 下单前检查：限额、持仓、资金
- 成交后检查：盈亏、回撤、敞口
- 定时检查：日终对账、风险报告

---

## Phase 5: 问题诊断 (Problem Diagnosis)

> ⚠️ **执行前必须读取 `references/bug-triage-guide.md` 获取Bug处理指南**

### 5.1 Bug分类（量化视角）

| 类型 | 严重程度 | 示例 |
|------|----------|------|
| 交易逻辑Bug | Critical | 错误下单、重复下单 |
| 数据处理Bug | Critical | 行情丢失、数据错误 |
| 风控失效Bug | Critical | 风控规则未触发 |
| 性能Bug | Major | 延迟抖动、吞吐下降 |
| 计算Bug | Major | 因子计算错误、信号错误 |
| 配置Bug | Minor | 参数配置错误 |

### 5.2 根因分析方法

**分析步骤：**
1. 复现问题：确定触发条件
2. 日志分析：追踪执行路径
3. 数据验证：检查输入输出
4. 代码审查：定位问题代码
5. 影响评估：评估业务影响

### 5.3 性能瓶颈定位

**诊断工具：**
- CPU分析：perf/flamegraph
- 内存分析：valgrind/heaptrack
- 网络分析：tcpdump/wireshark
- 延迟分析：自定义埋点

**常见瓶颈：**
- 锁竞争：使用无锁数据结构
- GC停顿：减少对象分配
- 网络延迟：优化协议/位置
- IO阻塞：异步化处理

---

## Phase 6: 评审报告 (Review Report)

> ⚠️ **执行前必须读取 `references/benchmark-checklist.md` 获取性能基准检查清单**

### 6.1 架构评审报告

**报告结构：**
```markdown
# 架构评审报告: [项目名称]

## 1. 评审概述
- 评审日期：[日期]
- 评审范围：[范围]
- 评审结论：[通过/有条件通过/不通过]

## 2. 架构评估
| 维度 | 评分 | 说明 |
|------|------|------|
| 可扩展性 | [1-5] | [说明] |
| 可维护性 | [1-5] | [说明] |
| 性能 | [1-5] | [说明] |
| 可靠性 | [1-5] | [说明] |
| 安全性 | [1-5] | [说明] |

## 3. 问题清单
| 问题ID | 描述 | 严重程度 | 建议 |
|--------|------|----------|------|

## 4. 优化建议
[详细优化建议]

## 5. 风险评估
[潜在风险及缓解措施]
```

### 6.2 性能基准报告

**关键指标：**

| 指标 | 目标值 | 实测值 | 状态 |
|------|--------|--------|------|
| 订单延迟P99 | <1ms | [实测] | ✅/❌ |
| 行情延迟P99 | <100μs | [实测] | ✅/❌ |
| 吞吐量 | >10K TPS | [实测] | ✅/❌ |
| CPU使用率 | <70% | [实测] | ✅/❌ |
| 内存使用率 | <80% | [实测] | ✅/❌ |

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 架构设计文档 | `docs/architecture/system-design.md` | 系统架构设计 |
| 性能优化报告 | `docs/architecture/performance-report.md` | 性能分析与优化 |
| 架构评审报告 | `docs/architecture/review-report.md` | 架构评审结果 |
| Bug分析报告 | `docs/architecture/bug-analysis.md` | Bug根因分析 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/system-architecture-guide.md` | 系统架构设计指南 |
| `references/performance-optimization.md` | 性能优化指南 |
| `references/strategy-design-patterns.md` | 策略设计模式 |
| `references/data-architecture.md` | 数据架构设计 |
| `references/risk-control-design.md` | 风控系统设计 |
| `references/bug-triage-guide.md` | Bug分类处理指南 |
| `references/benchmark-checklist.md` | 性能基准检查清单 |

---

## Related Skills

- `test-expert` - 测试专家（系统测试）
- `tech-plan-template` - 技术方案模板
- `development-workflow` - 开发工作流
