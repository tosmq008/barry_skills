# 流转至 tech-manager 指南

> S2/S3/S4/S5 场景完成后，必须流转至 tech-manager skill 进行开发管理。
> S1 架构评审不直接流转 tech-manager，交付决策层/技术负责人。

## 交付物清单

| 交付物 | 路径 | 必须/可选 | tech-manager 用途 |
|--------|------|-----------|-------------------|
| 主文档 | `docs/architecture/[按场景].md` | **必须** | 作为整体实施输入与约束来源 |
| 系统分析 | `docs/architecture/system-analysis.md` | 推荐 | 帮助 tech-manager 理解目标、范围、约束、NFR |
| 功能架构 | `docs/architecture/functional-architecture.md` | 推荐 | 作为任务边界和功能闭环拆分依据 |
| 工程架构 | `docs/architecture/engineering-architecture.md` | 推荐 | 作为模块任务拆分和并行开发依据 |
| API契约 | `docs/architecture/api-contract.md` | **必须**(S2/S3/S4) / 可选(S5) | 接口契约与联调基线 |
| 数据字典 | `docs/architecture/data-dictionary.md` | **必须**(S2/S3/S4) / 可选(S5) | 数据模型与后端任务拆分 |
| 架构决策记录 | `docs/architecture/adr/` | 推荐 | 开发过程中的技术约束参考 |

## 输出→输入映射（system-architect → tech-manager）

| system-architect 输出 | tech-manager 输入 | 映射说明 |
|----------------------|-------------------|----------|
| 系统分析结论（Phase 1） | Phase 1 背景、范围、约束 | 业务目标、现状约束、NFR 直接复用 |
| 功能架构与抽象模块（Phase 3） | Phase 1.1 功能需求 + Phase 2 任务边界 | 功能闭环、模块边界、关键协作关系 |
| 工程架构设计（Phase 4） | Phase 2 任务拆分 + Phase 3 并行开发 | 服务/应用/包/目录边界 → 可并行实施单元 |
| 技术架构与 ADR（Phase 5） | Phase 1.2 技术约束 | 架构模式、分层方式、中间件与不可变更约束 |
| 后端架构设计（Phase 6） | Phase 2.2 后端任务 | 服务/API/事务/缓存/MQ → 后端任务单 |
| 前端架构设计（Phase 7） | Phase 2.1 前端任务 | 页面/组件/路由/状态 → 前端任务单 |
| 集成架构与 API 契约（Phase 8） | Phase 1.3 接口契约 | API、错误码、认证链路、联调规则 |
| 数据架构设计（Phase 9） | Phase 2.2 数据模型 | 表/字段/索引/数据归属 → 后端/数据任务 |
| 安全/运维架构（Phase 10-11） | 质量与发布约束 | 安全要求、部署、监控、灰度与回滚 |
| 实施计划与最终交付（Phase 12） | Phase 3 并行开发 + 排期 | 阶段划分、依赖顺序、里程碑 |

## 流转前验证检查清单

> 在调用 tech-manager 之前，必须逐项验证以下条件：

- [ ] **主文档完整** - 所有必须 Phase 的设计成果已写入主文档
- [ ] **功能/工程架构已明确** - 功能边界、抽象模块、工程模块、依赖方向清晰
- [ ] **API契约完整** - 所有接口的路径、方法、参数、响应、错误码已定义
- [ ] **数据字典完整** - 所有数据表、字段、索引、关系已定义
- [ ] **文件存在性** - 验证当前场景对应的交付物文件已生成且非空：
  ```bash
  # 按当前场景验证对应主文档
  # S2/S3: ls -la docs/architecture/technical-architecture-design.md
  # S4:    ls -la docs/architecture/migration-plan.md
  # S5:    ls -la docs/architecture/performance-optimization-plan.md
  # 推荐补充：
  # ls -la docs/architecture/system-analysis.md
  # ls -la docs/architecture/functional-architecture.md
  # ls -la docs/architecture/engineering-architecture.md
  # 通用（S2/S3/S4 必须，S5 可选）:
  # ls -la docs/architecture/api-contract.md
  # ls -la docs/architecture/data-dictionary.md
  ```
- [ ] **架构约束明确** - 技术栈、架构模式、代码分层、认证方案、部署方式已确定
- [ ] **实施优先级排序** - 开发阶段和优先级已明确
- [ ] **风险项已识别** - 高风险项有对应缓解措施

## 流转指令模板

> 验证通过后，使用以下指令调用 tech-manager skill：

```markdown
请使用 tech-manager skill 基于以下技术方案进行开发管理：

### 来源场景
- 场景模式: [S2增量需求/S3新系统/S4重构迁移/S5性能专项]
- 架构方案版本: [v1.0]

### 技术方案文档
- 主文档: docs/architecture/[文档名].md
- 系统分析: docs/architecture/system-analysis.md
- 功能架构: docs/architecture/functional-architecture.md
- 工程架构: docs/architecture/engineering-architecture.md
- API契约: docs/architecture/api-contract.md
- 数据字典: docs/architecture/data-dictionary.md
- 架构决策记录: docs/architecture/adr/

### 关键架构约束（tech-manager 不可变更，需严格遵守）
- 架构模式: [如 模块化单体 / 微服务 / 事件驱动]
- 代码分层: [如 表现层 / 应用层 / 领域层 / 基础设施层]
- 技术栈: [本方案确定的技术栈]
- 认证方案: [本方案确定的认证方案]
- 部署方式: [本方案确定的部署方式]
- 数据库与基础设施: [本方案确定的数据库/缓存/MQ]

### 工程任务拆分依据（来自 Phase 4 工程架构）
- 核心工程模块: [模块列表]
- 并行开发边界: [边界说明]
- 共享能力约束: [共享库/平台能力说明]

### 前端任务概要（来自 Phase 7 前端架构）
- 页面数量: [n] 个
- 核心页面: [页面列表]
- 技术栈: [框架 + UI库 + 状态管理]

### 后端任务概要（来自 Phase 6 后端架构）
- API数量: [n] 个
- 核心服务: [服务列表]
- 数据模型: [模型列表]

### 实施优先级
1. [第一阶段 - 最高优先级任务]
2. [第二阶段 - 次优先级任务]
3. [第三阶段 - 后续阶段]

### 需要特别关注的风险项
- [风险1]: [缓解措施]
- [风险2]: [缓解措施]

### 质量要求
- 单元测试覆盖率 ≥ 80%
- API接口与契约文档严格一致
- 性能指标达到方案要求
- 安全措施按方案实施
```

## 各场景流转差异

| 场景 | 流转目标 | 流转重点 | 特殊说明 |
|------|----------|----------|----------|
| S1 架构评审 | 决策层（不流转 tech-manager） | 评审报告 + 调整建议 | 可衔接 S2/S4/S5 后再流转 |
| S2 增量需求 | tech-manager | 增量变更范围、受影响模块、兼容性风险 | tech-manager 需关注与现有代码的兼容性 |
| S3 新系统 | tech-manager | 功能架构 + 工程架构 + 全量接口和数据模型 | tech-manager 从零搭建，按实施计划分阶段 |
| S4 重构迁移 | tech-manager | 迁移方案 + 目标工程/技术架构 + 灰度切换策略 | tech-manager 需同时维护新旧系统，分批迁移 |
| S5 性能专项 | tech-manager | 优化方案（Quick Win/中期/长期分级） | tech-manager 按优先级分批实施，每批压测验证 |
