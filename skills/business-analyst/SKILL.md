---
name: business-analyst
description: "This skill enables comprehensive business analysis as a senior business analyst expert. It performs market research, competitive analysis, business model evaluation, financial feasibility assessment, and strategic recommendations using professional frameworks (SWOT, Porter's Five Forces, Business Model Canvas, PESTEL, Value Chain Analysis). It analyzes product designs, feature specifications, and business ideas to produce actionable business analysis reports with data-driven insights."
license: MIT
compatibility: "Requires web search capability for market research. Works with PRD documents, product designs, and business ideas. Supports Chinese and English output."
metadata:
  category: business-analysis
  phase: planning
  version: "1.0.0"
  author: business-expert
allowed-tools: bash read_file write_file web_search web_fetch
---

# Business Analyst Skill

作为资深商业分析专家，运用专业的分析框架和方法论，对产品设计、功能规格、商业创意进行系统性的商业分析评估，产出专业的商业分析报告。

## When to Use

**适用场景：**
- 评估新产品/功能的商业可行性
- 分析商业创意的市场潜力
- 进行竞品分析和市场调研
- 评估商业模式的可持续性
- 制定市场进入策略
- 进行投资回报分析
- 识别商业风险和机会

**不适用：**
- 纯技术实现评审
- 代码质量检查
- UI/UX 设计评审（非商业角度）

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    商业分析专家工作流程                           │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1: 需求理解 ──▶ Phase 2: 市场调研 ──▶ Phase 3: 竞品分析  │
│       │                     │                      │            │
│       ▼                     ▼                      ▼            │
│  Phase 4: 商业评估 ──▶ Phase 5: 战略分析 ──▶ Phase 6: 报告生成  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 需求理解 (Requirement Understanding)

### 1.1 输入文档分析

**支持的输入类型：**
- PRD 文档（产品需求文档）
- 功能规格说明书
- 商业计划书/BP
- 商业创意描述
- 产品设计文档

**必须提取的信息：**

| 信息类型 | 说明 | 重要性 |
|----------|------|--------|
| 产品定位 | 产品是什么，解决什么问题 | 必须 |
| 目标用户 | 谁会使用这个产品 | 必须 |
| 核心价值 | 产品的核心价值主张 | 必须 |
| 商业目标 | 期望达成的商业目标 | 必须 |
| 市场范围 | 目标市场和地区 | 重要 |
| 盈利模式 | 如何赚钱（如有） | 重要 |


### 1.2 分析目标确认

**分析类型选择：**

| 分析类型 | 适用场景 | 输出重点 |
|----------|----------|----------|
| 全面商业分析 | 新产品/新业务 | 完整商业分析报告 |
| 市场可行性分析 | 验证市场需求 | 市场规模、需求验证 |
| 竞品分析 | 了解竞争格局 | 竞品对比、差异化策略 |
| 商业模式评估 | 评估盈利能力 | 商业模式画布、财务分析 |
| 风险评估 | 识别潜在风险 | 风险清单、缓解策略 |

---

## Phase 2: 市场调研 (Market Research)

> ⚠️ **执行前必须读取 `references/market-research-guide.md` 获取市场调研指南**

### 2.1 行业趋势分析

**调研内容：**
- 行业发展阶段（萌芽/成长/成熟/衰退）
- 技术发展趋势
- 政策法规影响
- 行业增长率预测

**信息来源：**
- 行业研究报告（艾瑞、易观、Gartner、IDC）
- 政府统计数据
- 上市公司财报
- 行业新闻和分析

### 2.2 市场规模评估

**评估维度：**

| 维度 | 说明 | 数据来源 |
|------|------|----------|
| TAM | 总可触达市场 | 行业报告 |
| SAM | 可服务市场 | 细分市场数据 |
| SOM | 可获得市场 | 竞争分析 |

### 2.3 目标用户研究

**用户画像要素：**
- 人口统计特征
- 行为特征
- 需求痛点
- 消费能力
- 决策因素

---

## Phase 3: 竞品分析 (Competitive Analysis)

> ⚠️ **执行前必须读取 `references/competitive-analysis-template.md` 获取竞品分析模板**

### 3.1 竞品识别

**竞品分类：**

| 类型 | 定义 | 分析重点 |
|------|------|----------|
| 直接竞品 | 相同产品/服务 | 功能、定价、市场份额 |
| 间接竞品 | 替代解决方案 | 用户迁移成本、差异化 |
| 潜在竞品 | 可能进入的玩家 | 进入壁垒、威胁程度 |

### 3.2 竞品对比矩阵

**对比维度：**

| 维度 | 子项 |
|------|------|
| 产品功能 | 核心功能、特色功能、功能完整度 |
| 用户体验 | 易用性、界面设计、响应速度 |
| 定价策略 | 价格区间、定价模式、性价比 |
| 市场表现 | 市场份额、用户规模、增长趋势 |
| 技术能力 | 技术架构、创新能力、专利 |
| 品牌影响 | 品牌知名度、用户口碑、媒体曝光 |

### 3.3 差异化分析

**差异化策略评估：**
- 功能差异化
- 价格差异化
- 服务差异化
- 品牌差异化
- 渠道差异化

---

## Phase 4: 商业评估 (Business Evaluation)

> ⚠️ **执行前必须读取 `references/business-model-canvas.md` 获取商业模式画布模板**

### 4.1 商业模式画布分析

**九大模块：**
1. 客户细分 (Customer Segments)
2. 价值主张 (Value Propositions)
3. 渠道通路 (Channels)
4. 客户关系 (Customer Relationships)
5. 收入来源 (Revenue Streams)
6. 关键资源 (Key Resources)
7. 关键活动 (Key Activities)
8. 关键合作 (Key Partnerships)
9. 成本结构 (Cost Structure)

### 4.2 盈利模式评估

**常见盈利模式：**

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| 订阅制 | 按周期收费 | SaaS、内容服务 |
| 交易佣金 | 按交易抽成 | 平台、电商 |
| 广告收入 | 流量变现 | 媒体、社交 |
| 增值服务 | 基础免费+付费增值 | 工具类产品 |
| 授权费 | 技术/内容授权 | 技术、IP |
| 硬件销售 | 产品销售 | 硬件产品 |

### 4.3 财务可行性分析

**关键财务指标：**

| 指标 | 说明 | 健康标准 |
|------|------|----------|
| CAC | 客户获取成本 | 行业平均以下 |
| LTV | 客户生命周期价值 | > 3x CAC |
| LTV/CAC | 单位经济效益 | > 3 |
| 毛利率 | 毛利润率 | > 50% (SaaS) |
| 回本周期 | 投资回收期 | < 12个月 |


---

## Phase 5: 战略分析 (Strategic Analysis)

> ⚠️ **执行前必须读取 `references/strategic-frameworks.md` 获取战略分析框架**

### 5.1 SWOT 分析

| 维度 | 分析要点 |
|------|----------|
| Strengths | 内部优势、核心竞争力、资源优势 |
| Weaknesses | 内部劣势、能力短板、资源缺口 |
| Opportunities | 外部机会、市场趋势、政策利好 |
| Threats | 外部威胁、竞争压力、政策风险 |

### 5.2 Porter's Five Forces 分析

| 力量 | 评估维度 |
|------|----------|
| 供应商议价能力 | 供应商集中度、替代品、转换成本 |
| 买方议价能力 | 买方集中度、价格敏感度、转换成本 |
| 新进入者威胁 | 进入壁垒、资本需求、品牌忠诚度 |
| 替代品威胁 | 替代品可用性、性价比、转换成本 |
| 行业竞争程度 | 竞争者数量、行业增长、差异化程度 |

### 5.3 PESTEL 分析

| 因素 | 分析内容 |
|------|----------|
| Political | 政策法规、政府态度、贸易政策 |
| Economic | 经济周期、利率汇率、消费能力 |
| Social | 人口结构、消费习惯、文化趋势 |
| Technological | 技术发展、创新趋势、数字化程度 |
| Environmental | 环保要求、可持续发展、碳中和 |
| Legal | 法律法规、知识产权、数据隐私 |

### 5.4 风险评估

**风险矩阵：**

| 风险类型 | 评估维度 |
|----------|----------|
| 市场风险 | 需求变化、市场萎缩、用户流失 |
| 技术风险 | 技术可行性、技术迭代、安全风险 |
| 运营风险 | 供应链、人才、流程效率 |
| 财务风险 | 现金流、融资、成本控制 |
| 法规风险 | 合规要求、政策变化、诉讼风险 |

---

## Phase 6: 报告生成 (Report Generation)

> ⚠️ **执行前必须读取 `references/report-template.md` 获取报告模板**

### 6.1 商业分析报告结构

```markdown
# 商业分析报告: [项目名称]

## 执行摘要
[核心发现和建议的一段话总结]

## 1. 项目概述
## 2. 市场分析
## 3. 竞争分析
## 4. 商业模式分析
## 5. 战略分析
## 6. 风险评估
## 7. 综合评估
## 8. 战略建议
## 9. 行动计划
## 附录
```

### 6.2 商业可行性评分

**评分维度：**

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 市场吸引力 | 25% | 市场规模、增长率、进入时机 |
| 竞争优势 | 20% | 差异化程度、护城河、竞争壁垒 |
| 商业模式 | 20% | 盈利能力、可持续性、可扩展性 |
| 执行可行性 | 20% | 资源匹配、团队能力、技术可行性 |
| 风险可控性 | 15% | 风险程度、可缓解性 |

**评分等级：**
- 90-100: 强烈推荐 ⭐⭐⭐⭐⭐
- 75-89: 推荐 ⭐⭐⭐⭐
- 60-74: 有条件推荐 ⭐⭐⭐
- 45-59: 需要改进 ⭐⭐
- 0-44: 不推荐 ⭐

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 商业分析报告 | `docs/business/business-analysis-report.md` | 完整商业分析报告 |
| 市场调研报告 | `docs/business/market-research.md` | 市场调研详情 |
| 竞品分析报告 | `docs/business/competitive-analysis.md` | 竞品分析详情 |
| 商业模式画布 | `docs/business/business-model-canvas.md` | 商业模式分析 |
| 风险评估报告 | `docs/business/risk-assessment.md` | 风险评估详情 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/market-research-guide.md` | 市场调研指南 |
| `references/competitive-analysis-template.md` | 竞品分析模板 |
| `references/business-model-canvas.md` | 商业模式画布模板 |
| `references/strategic-frameworks.md` | 战略分析框架 |
| `references/financial-analysis-guide.md` | 财务分析指南 |
| `references/report-template.md` | 报告模板 |

## Related Skills

- `prd-review` - PRD 评审
- `prd-template` - PRD 模板
- `tech-plan-template` - 技术方案模板
