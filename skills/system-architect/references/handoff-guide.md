# 流转至 tech-manager 指南

> S2/S3/S4/S5 场景完成后，必须流转至 tech-manager skill 进行开发管理。
> S1 架构评审不直接流转 tech-manager，交付决策层/技术负责人。

## 交付物清单

| 交付物 | 路径 | 必须/可选 | tech-manager 用途 |
|--------|------|-----------|-------------------|
| 主文档 | `docs/architecture/[按场景].md` | **必须** | Phase 1 需求分析的核心输入 |
| API契约 | `docs/architecture/api-contract.md` | **必须**(S2/S3/S4) / 可选(S5) | Phase 1.3 接口契约 + Phase 2 任务分解 |
| 数据字典 | `docs/architecture/data-dictionary.md` | **必须**(S2/S3/S4) / 可选(S5) | Phase 2.2 后端任务拆分 |
| 架构决策记录 | `docs/architecture/adr/` | 可选 | 开发过程中的技术约束参考 |

## 输出→输入映射（system-architect → tech-manager）

| system-architect 输出 | tech-manager 输入 | 映射说明 |
|----------------------|-------------------|----------|
| 功能分解矩阵（Phase 1） | Phase 1.1 功能需求 | 功能清单直接复用 |
| 前端架构设计（Phase 5） | Phase 1.1 前端需求 + Phase 2.1 前端任务 | 页面/组件/路由 → 前端任务单 |
| 后端架构设计（Phase 4） | Phase 1.1 后端需求 + Phase 2.2 后端任务 | 服务/模块/API → 后端任务单 |
| API接口契约（Phase 6） | Phase 1.3 接口契约 | 直接复用，tech-manager 不重新定义 |
| 数据架构设计（Phase 7） | Phase 2.2 数据模型 | 数据表/字段 → 后端任务单 |
| 实施计划（Phase 10） | Phase 2.3 依赖关系 + Phase 3 并行开发 | 阶段划分 → 开发排期 |

## 流转前验证检查清单

> 在调用 tech-manager 之前，必须逐项验证以下条件：

- [ ] **主文档完整** - 所有必须 Phase 的设计成果已写入主文档
- [ ] **API契约完整** - 所有接口的路径、方法、参数、响应、错误码已定义
- [ ] **数据字典完整** - 所有数据表、字段、索引、关系已定义
- [ ] **文件存在性** - 验证当前场景对应的交付物文件已生成且非空：
  ```bash
  # 按当前场景验证对应主文档
  # S2/S3: ls -la docs/architecture/technical-architecture-design.md
  # S4:    ls -la docs/architecture/migration-plan.md
  # S5:    ls -la docs/architecture/performance-optimization-plan.md
  # 通用（S2/S3/S4 必须，S5 可选）:
  # ls -la docs/architecture/api-contract.md
  # ls -la docs/architecture/data-dictionary.md
  ```
- [ ] **架构约束明确** - 技术栈、架构模式、认证方案、部署方式已确定
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
- API契约: docs/architecture/api-contract.md
- 数据字典: docs/architecture/data-dictionary.md
- 架构决策记录: docs/architecture/adr/
- 补充文档（按场景）:
  - S4: 灰度切换策略、数据迁移脚本清单
  - S5: 压测验证计划、SLA 目标定义

### 关键架构约束（tech-manager 不可变更，需严格遵守）
- 技术栈: [本方案确定的技术栈，如 Python/FastAPI + Vue 3]
- 架构模式: [本方案确定的架构模式，如分层架构/微服务]
- 认证方案: [本方案确定的认证方案，如 JWT]
- 部署方式: [本方案确定的部署方式，如 Docker + K8s]
- 数据库: [本方案确定的数据库，如 PostgreSQL + Redis]

### 前端任务概要（来自 Phase 5 前端架构）
- 页面数量: [n] 个
- 核心页面: [页面列表]
- 技术栈: [框架 + UI库 + 状态管理]

### 后端任务概要（来自 Phase 4 后端架构）
- API数量: [n] 个
- 核心服务: [服务列表]
- 数据模型: [模型列表]

### 实施优先级
1. [Phase 1 - 最高优先级任务]
2. [Phase 2 - 次优先级任务]
3. [Phase 3 - 后续阶段]

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
| S2 增量需求 | tech-manager | 增量变更范围、受影响的现有服务/接口 | tech-manager 需关注与现有代码的兼容性 |
| S3 新系统 | tech-manager | 完整架构方案、全量API和数据模型 | tech-manager 从零搭建，按实施计划分阶段 |
| S4 重构迁移 | tech-manager | 迁移方案 + 目标架构、灰度切换策略 | tech-manager 需同时维护新旧系统，分批迁移 |
| S5 性能专项 | tech-manager | 优化方案（Quick Win/中期/长期分级） | tech-manager 按优先级分批实施，每批压测验证 |
