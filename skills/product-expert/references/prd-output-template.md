# PRD 输出模板（v6 对齐）

> 本模板与 `product-expert` v6 的工作流对齐。目标不是让 PRD “更厚”，而是让它更像产品经理真正可交付、下游 AI Agent 真能消费的主线方案。

---

## 0. 核心规则

1. **先决策，后落盘。** 在 Phase 3 的 MVP 未批准前，默认只在对话中输出结论，不写入 `docs/prd/` 主线。
2. **批准后再同步。** `02-user-research.md` 和 `03-competitive-analysis.md` 不是“探索过程草稿”，而是 **Phase 7 对已批准结论的正式沉淀**。
3. **单一主线。** `docs/prd/` 只能保留一套当前有效主线，不并存 `v2`、`final`、`backup`、`old` 等平行版本。
4. **L1/L2/L3 最终写入归口到 Phase 7。** Phase 4/5 允许先给树和路径预览，但不要在不同阶段反复写多个主线版本。
5. **支撑能力不强行造路径。** 权限、日志、通知、风控、审核、配置等可作为 supporting capability，被路径、页面、角色规则或业务规则引用即可。
6. **UI 是条件触发。** 只有存在明显的体验风险、页面复杂度或用户明确要求时，才要求视觉规范/设计稿。
7. **所有结论标注证据等级。** 统一使用：`事实` / `推断` / `假设`。

---

## 1. 三种交付深度

### D1：决策结论 / 可行性判断

适用：快速评估、需求真伪判断、机会筛选、是否值得做。

产物默认在对话中完成，不生成正式主线 PRD。建议至少包含：

```markdown
## Decision Snapshot
- Recommendation: [go / iterate / stop]
- Target user & job: [...]
- Why now: [...]
- Success metric: [...]
- Scope in (MVP): [...]
- Scope out (not now): [...]
- Key assumptions: [...]
- Key risks / dependencies: [...]
- Validation plan: [...]
```

### D2：MVP Brief / 增量规格

适用：微迭代、小范围规则调整、局部体验优化、单模块更新。

原则：**只更新受影响的主线文件**，不要为了一个小改动重写整套 PRD，也不要长期并存“补丁 PRD”。

建议额外包含一个更新卡片：

```markdown
## Update Card
- Change type: [copy / rule / flow / page / metric / permission / data]
- Why change now: [...]
- Impacted users / roles: [...]
- Impacted IDs: [F-xxx / UC-xxx / US-xxx / P-xxx]
- Mainline files to update: [...]
- Scope added / changed / removed: [...]
- Validation after change: [...]
```

### D3：完整主线 PRD

适用：新产品、重大迭代、需要给 `system-architect` / `tech-manager` / dev / QA 消费。

---

## 2. D3 主线文件结构

```text
docs/prd/
├── 01-project-overview.md          # 项目概述 + Decision Snapshot + 主线判定
├── 02-user-research.md             # 用户研究（批准后同步）
├── 03-competitive-analysis.md      # 竞品 / 替代方案分析（批准后同步）
├── L1-feature-architecture.yaml    # L1：功能架构树（AI 消费）
├── L1-feature-architecture.md      # L1：树状可视化（人类浏览）
├── 05-role-permission.md           # 角色权限
├── 06-information-architecture.md  # 信息架构
├── 07-page-list.md                 # 页面清单
├── L2-use-case-flows.yaml          # L2：用例/路径（AI 消费）
├── L2-use-case-flows.md            # L2：路径可视化（人类浏览）
├── 09-interaction-spec.md          # 交互规格
├── 10-visual-style.md              # 视觉规范（条件触发）
├── L3-user-stories.yaml            # L3：User Story + AC（AI 消费）
├── L3-user-stories.md              # L3：人类浏览
├── 12-data-spec.md                 # 数据规格
├── 13-acceptance-criteria.md       # 验收标准汇总
├── 14-release-plan.md              # 发布计划
├── 15-metrics-plan.md              # 指标与实验计划
└── validation-report.md            # PRD 验证报告
```

### 必填 vs 条件触发

| 文件 | 是否必填 | 说明 |
|---|---|---|
| `01-project-overview.md` | 必填 | 作为主线入口文件 |
| `02-user-research.md` | 必填（D3） | 但只在批准后写入 |
| `03-competitive-analysis.md` | 视场景而定 | 如果决策依赖外部市场事实，则必填 |
| `L1-*` / `L2-*` / `L3-*` | 必填（D3） | 最终由 Phase 7 统一生成 |
| `05-role-permission.md` | 必填（多角色/多端） | 单角色简单工具可精简 |
| `06-information-architecture.md` | 必填 | 即使是后台工具也要有信息结构 |
| `07-page-list.md` | 必填 | 无 UI 产品可退化为入口/出口/界面容器清单 |
| `09-interaction-spec.md` | 必填 | 至少覆盖关键页面状态和异常流 |
| `10-visual-style.md` | 条件触发 | 复杂 UI / 用户明确要求时填 |
| `12-data-spec.md` | 必填 | 至少覆盖关键实体、状态、权限和数据流 |
| `14-release-plan.md` | 必填 | 最少要有范围、节奏、风险、回滚 |
| `15-metrics-plan.md` | 必填 | 指标必须在 feature freeze 前明确 |
| `validation-report.md` | 必填 | 最终 handoff 前检查 |

---

## 3. 写作规范

### 3.1 决策信息的落盘位置

| 信息 | 推荐落盘位置 |
|---|---|
| Decision Snapshot | `01-project-overview.md` |
| 用户价值 / Kano / 非目标 / 假设 | `02-user-research.md` |
| 竞品结论 / 不可照搬点 | `03-competitive-analysis.md` |
| 主线 PRD 判定（原位更新或重建） | `01-project-overview.md` |
| 支撑能力说明 | `L1-*`、`05-role-permission.md`、`09-interaction-spec.md` |
| 指标定义 / 埋点 / 实验 | `15-metrics-plan.md` |

### 3.2 证据标签规范

在用户研究、竞品分析、决策结论中，建议对核心判断使用标签：

```markdown
- [事实] 用户近 30 天重复提到“XX 流程太慢”
- [推断] 说明该问题更像效率瓶颈而不是功能缺失
- [假设] 若缩短到 3 步内，提交完成率会提升
```

### 3.3 增量更新规范（D2）

- 优先保留现有 `F-xxx / UC-xxx / US-xxx / P-xxx` 的稳定 ID。
- 功能被下线或移出本期时，优先改 `status` 或在主线中显式标注“延后 / deprecated”，不要整体重编号。
- 只更新受影响文件，但必须保证引用闭环仍成立。

---

## 4. 关键文档模板

### 4.1 项目概述（01-project-overview.md）

```markdown
# 项目概述

## 文档信息
| 字段 | 内容 |
|---|---|
| 项目名称 | [项目名] |
| 文档状态 | 草稿 / 已批准 / 已更新 |
| 当前阶段 | Discovery / Approved / Build-ready |
| 主线类型 | 新建 / 原位更新 |
| 更新时间 | [YYYY-MM-DD] |
| 作者 | [作者] |

## 主线 PRD 判定
- 判定：[沿用现有主线并原位更新 / 删除旧主线后重建]
- 理由：[为什么]
- 保留内容：[继续沿用的章节 / ID / 页面 / 路径]
- 执行动作：[如何保证 docs/prd/ 最终只有一套主线]

## Decision Snapshot
- Recommendation: [go / iterate / stop]
- Target user & job: [...]
- Why now: [...]
- Success metric: [北极星 / 过程指标 / 护栏指标]
- Scope in (MVP): [...]
- Scope out (not now): [...]
- Prioritization: [RICE / ICE / 其他]
- Key assumptions: [...]
- Key risks / dependencies: [...]
- Validation plan: [...]

## 项目背景
### 1. 业务背景
[为什么会有这个项目]

### 2. 用户问题
| 问题 | 影响人群 | 当前替代方案 | 痛点级别 | 证据等级 |
|---|---|---|---|---|
| | | | 高/中/低 | 事实/推断/假设 |

### 3. 项目目标
| 类型 | 指标 | 当前值 | 目标值 | 时间窗口 |
|---|---|---|---|---|
| 北极星 | | | | |
| 过程指标 | | | | |
| 护栏指标 | | | | |

## 范围定义
### Scope In
- [...]

### Scope Out / Non-goals
- [...]

## 风险与依赖
| 类别 | 内容 | 缓解方式 | Owner |
|---|---|---|---|
| 业务 | | | |
| 技术 | | | |
| 合规/隐私 | | | |
| 运营 | | | |

## 相关文档
| 文档 | 链接 |
|---|---|
| 用户研究 | `02-user-research.md` |
| 竞品分析 | `03-competitive-analysis.md` |
| L1/L2/L3 | `L1-*` / `L2-*` / `L3-*` |
| 指标计划 | `15-metrics-plan.md` |
```

### 4.2 用户研究（02-user-research.md）

> 该文件是 **已批准结论的整理版**，不是探索过程流水账。

```markdown
# 用户研究

## 1. 目标用户与分层
| 角色 | 是否核心 | 主要任务 | 关键限制 |
|---|---|---|---|
| | 是/否 | | |

## 2. 关键场景与 JTBD
| 场景 | 触发条件 | 用户想完成的任务 | 当前替代方式 |
|---|---|---|---|
| | | | |

## 3. 用户价值分析
- 新体验：[...]
- 旧体验：[...]
- 替换成本：[...]
- 结论：[用户价值为正 / 不足以成立 / 需进一步验证]

## 4. 需求真伪判断
| 维度 | 结论 | 证据等级 |
|---|---|---|
| 来源 | | 事实/推断/假设 |
| 频率 | | |
| 痛感 | | |
| 愿付成本 / 愿投入成本 | | |
| 价值判断 | | |

## 5. Kano 分级
| 需求项 | Kano 分类 | 理由 |
|---|---|---|
| | basic/performance/excitement/indifferent/reverse | |

## 6. Non-goals
- [...]

## 7. 关键假设与待验证问题
| 假设 | 为什么重要 | 如何验证 |
|---|---|---|
| | | |
```

### 4.3 竞品 / 替代方案分析（03-competitive-analysis.md）

```markdown
# 竞品 / 替代方案分析

## 1. 对标范围说明
- 直接竞品：[...]
- 间接替代：[...]
- 标杆参考：[...]
- 本次不纳入比较的对象：[...]

## 2. 对标对象清单
| 对象 | 类型 | 服务对象 | 核心场景 | 价值点 | 迁移成本 | 定价/变现 | 可借鉴点 | 不可照搬点 | 来源 |
|---|---|---|---|---|---|---|---|---|---|
| | direct / substitute / benchmark | | | | | | | | |

## 3. 定位结论
- 我们跟谁比：[...]
- 我们不跟谁比：[...]
- 差异化来源：[...]
- 为什么现在不做某些能力：[...]
```

### 4.4 角色权限（05-role-permission.md）

```markdown
# 角色权限

## 角色清单
| 角色 | 端 | 主要目标 | 关键限制 |
|---|---|---|---|
| | Client/Admin/Operation | | |

## 权限矩阵
| Feature ID | Feature 名称 | 普通用户 | 管理员 | 运营 | 备注 |
|---|---|---|---|---|---|
| F-001 | | 查看/编辑/审批/无权限 | | | |

## 支撑能力说明
| Supporting Feature | 被谁引用 | 说明 |
|---|---|---|
| F-090 | UC-001 / 角色规则 / 页面状态 | 例如权限校验、审计日志、风控拦截 |
```

### 4.5 信息架构（06-information-architecture.md）

```markdown
# 信息架构

## 导航结构
- Client
  - ...
- Admin
  - ...
- Operation
  - ...

## 实体关系
| 实体 | 描述 | 与谁关联 | 关键状态 |
|---|---|---|---|
| | | | |

## 关键对象生命周期
| 对象 | 状态流转 | 触发条件 |
|---|---|---|
| | Draft -> Submitted -> Approved | |
```

### 4.6 页面清单（07-page-list.md）

```markdown
# 页面清单

## 页面总览
| Page ID | 页面名称 | 端 | 入口场景 | 关联 Feature | 优先级 | 设计稿 |
|---|---|---|---|---|---|---|
| P-C-001 | | Client | | F-001 | P0 | |

## 页面状态
| Page ID | 默认态 | 加载态 | 空态 | 错误态 | 权限受限态 | 备注 |
|---|---|---|---|---|---|---|
| P-C-001 | ✅ | ✅ | ✅ | ✅ | - | |
```

### 4.7 交互规格（09-interaction-spec.md）

```markdown
# 交互规格

## 关键交互
| 页面 | 触发动作 | 系统响应 | 失败处理 | 关联 UseCase | 关联 Feature |
|---|---|---|---|---|---|
| | | | | UC-001 | F-001 |

## 异常与恢复
| 场景 | 提示文案 | 恢复方式 | 埋点 |
|---|---|---|---|
| 网络失败 | | 重试 / 返回 / 草稿保存 | |
```

### 4.8 L1 / L2 / L3

- `L1-*`：回答“系统有什么”。
- `L2-*`：回答“用户如何完成目标”。
- `L3-*`：回答“按完整路径做到什么程度并如何验收”。

> 详细 YAML / Markdown 模板统一以 `references/structured-requirement-spec.md` 为准。

### 4.9 数据规格（12-data-spec.md）

```markdown
# 数据规格

## 核心实体
| 实体 | 描述 | 关键字段 | 状态 | 权限约束 |
|---|---|---|---|---|
| | | | | |

## 数据变化
| UseCase | 实体 | 操作 | 影响 |
|---|---|---|---|
| UC-001 | User | CREATE | 新建账号 |

## 埋点 / 事件
| 事件名 | 触发时机 | 属性 | 对应指标 |
|---|---|---|---|
| register_submit | 点击提交 | phone_type, source | 注册转化率 |
```

### 4.10 验收标准汇总（13-acceptance-criteria.md）

> 本文件建议从 `L3-user-stories.yaml` 生成或同步整理，不要与 L3 脱节。

```markdown
# 验收标准汇总

## 按迭代汇总
### ITER-MVP
| Story | AC-ID | 类型 | Given | When | Then | 自动化 |
|---|---|---|---|---|---|---|
| US-001 | AC-001 | happy_path | | | | ✅ |

## 非功能验收
| 类别 | AC-ID | Given | When | Then |
|---|---|---|---|---|
| 性能 | AC-P01 | | | |
| 安全 | AC-S01 | | | |
| 合规 | AC-C01 | | | |
```

### 4.11 发布计划（14-release-plan.md）

```markdown
# 发布计划

## 发布目标
- 本次发布要验证的核心假设：[...]

## 范围与节奏
| 批次 | 范围 | 目标用户 | 发布时间 | 开关 / 灰度策略 |
|---|---|---|---|---|
| Alpha | | | | |
| Beta | | | | |
| GA | | | | |

## 风险与回滚
| 风险 | 触发信号 | 应对方案 | 是否需要回滚 |
|---|---|---|---|
| | | | 是/否 |
```

### 4.12 指标计划（15-metrics-plan.md）

```markdown
# 指标计划

## 指标框架
| 类型 | 指标 | 定义 | 当前值 | 目标值 | 观测周期 |
|---|---|---|---|---|---|
| 北极星 | | | | | |
| 过程指标 | | | | | |
| 护栏指标 | | | | | |

## 埋点映射
| 事件 | 触发位置 | 属性 | 对应指标 |
|---|---|---|---|
| | | | |

## 验证计划
| 阶段 | 要看什么 | 判定阈值 | 后续动作 |
|---|---|---|---|
| 上线前 | | | |
| 上线后 24h | | | |
| 上线后 7d | | | |
```

### 4.13 验证报告（validation-report.md）

```markdown
# PRD 验证报告

## 结构校验
- [ ] L1 Feature 是唯一叶子节点
- [ ] 全部核心价值闭环 Feature 被 UseCase 覆盖
- [ ] supporting capability 已被路径 / 角色规则 / 页面 / 业务规则引用
- [ ] 每条 UseCase 被完整 Story 覆盖
- [ ] 每个 Story >= 3 条 AC，且含 happy path + edge/error
- [ ] `feature_path` 与 `ordered_unique(main_flow.feature_id)` 一致
- [ ] `docs/prd/` 只有一套主线

## 产品质量校验
- [ ] 目标用户与关键场景清楚
- [ ] Scope in / Scope out 清楚
- [ ] 北极星 / 过程指标 / 护栏指标存在
- [ ] 风险、依赖、假设明确
- [ ] 隐私 / 合规 / 滥用问题（如适用）已记录

## 结论
- Result: PASS / WARNING / FAIL
- Next step: `system-architect` / `tech-manager` / 返回产品决策
```

---

## 5. 评审检查清单

### 产品质量
- [ ] 不是“功能堆叠”，而是明确回答了问题、目标、范围、指标、风险
- [ ] Decision Snapshot 可独立阅读
- [ ] Non-goals 明确
- [ ] 没有把未批准方案写进主线

### 结构质量
- [ ] L1/L2/L3 只保留一套正式主线版本
- [ ] ID 稳定，无无意义重编号
- [ ] 支撑能力没有被机械强制成伪路径
- [ ] UI 产出与产品复杂度匹配，而不是默认拉满
