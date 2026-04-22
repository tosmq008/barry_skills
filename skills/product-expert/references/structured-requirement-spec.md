# 结构化需求规格（v6 对齐 · AI 可解析 · 可验证）

> 本文档定义 `product-expert` v6 的 L1 / L2 / L3 结构化规格。目标是：
> 1）能被下游 AI Agent 直接消费；
> 2）能被程序化验证；
> 3）更符合真实产品建模方式，允许“核心闭环能力”和“支撑能力”并存，而不是机械制造伪路径。

---

## 0. 核心原则

1. **Problem -> Scope -> L1 -> L2 -> L3**
2. **Feature 是唯一叶子节点**，但叶子节点分两类：
   - `core_journey`：核心价值闭环功能
   - `supporting_capability`：支撑能力，如权限、日志、通知、审核、配置、风控
3. **核心闭环功能必须进入至少 1 条完整路径。**
4. **支撑能力不必单独变成目标路径**，但必须被路径、步骤、业务规则、页面或 Story/AC 引用。
5. **一个 Story = 一条完整主路径。**
6. **Then 必须可观测 / 可度量。**
7. **增量更新时优先保留稳定 ID。**

---

## 1. 三层模型总览

```text
L1 功能架构树（系统有什么）
  ├─ core_journey feature        → 至少被 1 条 UseCase feature_path 覆盖
  └─ supporting_capability       → 至少被 1 个路径 / 规则 / 页面 / Story / AC 引用
        ↓
L2 用例与路径（用户如何完成目标）
        ↓
L3 User Story + AC（沿完整路径做到什么程度）
```

### 1.1 三层交叉引用关系

```text
Feature(F-xxx) ←→ UseCase(UC-xxx) ←→ UserStory(US-xxx) ←→ AcceptanceCriteria(AC-xxx)
     ↕                  ↕                    ↕
   Page(P-xxx)     Rule/State refs        Metric/Event refs
```

### 1.2 ID 命名规范

| 实体 | 前缀 | 格式 | 示例 |
|---|---|---|---|
| 能力域 | D- | D-NNN | D-001 |
| 模块 | M- | M-NNN | M-001 |
| 子模块 | SM- | SM-NNN | SM-001 |
| 功能 | F- | F-NNN | F-001 |
| 用例 | UC- | UC-NNN | UC-001 |
| 用例替代流 | UC-NNN-A | UC-NNN-A1 | UC-001-A1 |
| 用例异常流 | UC-NNN-E | UC-NNN-E1 | UC-001-E1 |
| 用户故事 | US- | US-NNN | US-001 |
| 验收标准 | AC- | AC-NNN | AC-001 |
| 页面 | P- | P-[端]-NNN | P-C-001 |
| 迭代 | ITER- | ITER-[NAME] | ITER-MVP |
| 指标 | MET- | MET-NNN | MET-001 |
| 事件 | EVT- | EVT-NNN | EVT-001 |

---

## 2. 更新与 ID 稳定性规则

增量迭代（D2）时，额外遵守：

1. 不要因为顺序变化而重排稳定 ID。
2. 新增功能只追加新的 `F-xxx`，不要整体重编号。
3. 移出当前范围的功能优先改 `status: deferred` 或 `deprecated`，不要先删再重排。
4. 旧路径被替代时，优先保留旧 `UC-xxx` 并标记为 `deprecated`。
5. 若重构导致 ID 体系不可持续，应在 `01-project-overview.md` 写明“主线重建”。

---

## 3. L1：功能架构树（Functional Architecture Tree）

> 目标：定义系统边界、功能层级、优先级、端边界，以及功能是“核心闭环能力”还是“支撑能力”。

### 3.1 L1 YAML 模板

```yaml
# 文件: docs/prd/L1-feature-architecture.yaml
product_name: "[产品名称]"
version: "1.0"
last_updated: "YYYY-MM-DD"
change_mode: "full_mainline" # full_mainline / partial_update

domains:
  - domain_id: "D-001"
    domain_name: "用户域"
    description: "身份、账号、权限、安全"
    modules:
      - module_id: "M-001"
        module_name: "认证模块"
        description: "注册、登录、身份校验"
        endpoints: ["Client", "Admin"]
        submodules:
          - submodule_id: "SM-001"
            submodule_name: "注册子模块"
            description: "新用户进入系统前的注册相关能力"
            features:
              - feature_id: "F-001"
                feature_name: "手机号注册"
                feature_kind: "core_journey"
                description: "用户通过手机号发起注册"
                user_goal: "完成账号创建"
                primary_actor: "ACT-001"
                tree_path: ["产品", "用户域", "认证模块", "注册子模块", "手机号注册"]
                priority: "P0"
                kano_type: "basic"
                iteration: "ITER-MVP"
                endpoints: ["Client"]
                pages: ["P-C-003"]
                depends_on: []
                status: "planned"

      - module_id: "M-009"
        module_name: "治理与支撑"
        description: "日志、风控、通知等支撑能力"
        endpoints: ["Client", "Admin", "Operation"]
        features:
          - feature_id: "F-090"
            feature_name: "注册频控"
            feature_kind: "supporting_capability"
            description: "限制短时间内重复获取验证码"
            user_goal: "降低滥用与成本浪费"
            primary_actor: "ACT-001"
            tree_path: ["产品", "用户域", "治理与支撑", "注册频控"]
            priority: "P0"
            kano_type: "basic"
            iteration: "ITER-MVP"
            endpoints: ["Client", "Operation"]
            pages: ["P-C-003", "P-O-010"]
            depends_on: []
            status: "planned"

summary:
  total_domains: 0
  total_modules: 0
  total_submodules: 0
  total_features: 0
  by_kind:
    core_journey: 0
    supporting_capability: 0
  coverage_check:
    journey_features_without_use_case: []
    supporting_features_without_reference: []
    features_without_page: []
    non_leaf_feature_refs: []
```

### 3.2 L1 Markdown 模板

```markdown
# 功能架构图

## 树状视图
- 产品名称
  - D-001 用户域
    - M-001 认证模块
      - SM-001 注册子模块
        - F-001 手机号注册 [core_journey]
    - M-009 治理与支撑
      - F-090 注册频控 [supporting_capability]

## 叶子功能点明细
| ID | 功能 | 类型 | 树路径 | 优先级 | 迭代 | 端 | 页面 | 依赖 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| F-001 | 手机号注册 | core_journey | 产品/用户域/认证模块/注册子模块/手机号注册 | P0 | ITER-MVP | Client | P-C-003 | - | planned |
| F-090 | 注册频控 | supporting_capability | 产品/用户域/治理与支撑/注册频控 | P0 | ITER-MVP | Client,Operation | P-C-003,P-O-010 | - | planned |
```

---

## 4. L2：用例与路径（Use Case Flows）

> 目标：定义用户目标闭环、关键步骤、异常恢复，以及哪些支撑能力参与其中。

### 4.1 L2 YAML 模板

```yaml
# 文件: docs/prd/L2-use-case-flows.yaml
product_name: "[产品名称]"
version: "1.0"

actors:
  - actor_id: "ACT-001"
    actor_name: "普通用户"
    description: "C 端普通用户"
    endpoints: ["Client"]
  - actor_id: "ACT-020"
    actor_name: "运营人员"
    description: "负责监控与治理"
    endpoints: ["Operation"]

use_cases:
  - uc_id: "UC-001"
    uc_name: "新用户注册"
    status: "planned"
    description: "用户首次使用产品，通过手机号完成注册"
    journey_goal: "让新用户完成注册并进入首页开始使用"
    actor: "ACT-001"
    trigger: "用户点击注册按钮"
    entry_point: "P-C-001"
    exit_point: "P-C-004"
    priority: "P0"
    iteration: "ITER-MVP"

    related_features: ["F-001"]
    supporting_features: ["F-090"]
    related_pages: ["P-C-001", "P-C-003", "P-C-004"]
    feature_path: ["F-001"]

    preconditions:
      - "用户未登录"
      - "网络连接正常"

    main_flow:
      - step: 1
        step_id: "UC-001.step1"
        actor_action: "用户点击注册"
        system_response: "展示注册页"
        feature_id: "F-001"
        ui_ref: "P-C-003"
        supporting_feature_refs: []

      - step: 2
        step_id: "UC-001.step2"
        actor_action: "输入手机号并获取验证码"
        system_response: "系统发送验证码并触发频控检查"
        feature_id: "F-001"
        ui_ref: "P-C-003"
        supporting_feature_refs: ["F-090"]
        business_rules: ["BR-001", "BR-002"]

      - step: 3
        step_id: "UC-001.step3"
        actor_action: "输入验证码并提交"
        system_response: "系统创建账号并建立登录态"
        feature_id: "F-001"
        ui_ref: "P-C-003"
        supporting_feature_refs: ["F-090"]

    alternative_flows:
      - alt_id: "UC-001-A1"
        alt_name: "手机号已注册"
        branch_from_step: 2
        condition: "手机号已存在"
        result: "引导去登录"

    exception_flows:
      - exc_id: "UC-001-E1"
        exc_name: "网络超时"
        condition: "获取验证码或提交注册超时"
        handling: "提示网络异常并提供重试"
        recovery: "重试当前步骤"

      - exc_id: "UC-001-E2"
        exc_name: "触发频控限制"
        condition: "短时间内重复获取验证码"
        handling: "提示稍后重试"
        recovery: "等待限制结束"
        supporting_feature_refs: ["F-090"]

    postconditions:
      success:
        - "用户账号已创建"
        - "用户已登录"
      failure:
        - "账号未创建"
        - "用户停留在注册流程内"
```

### 4.2 L2 Markdown 模板

```markdown
# 用例流：UC-001 新用户注册

**角色:** 普通用户
**路径目标:** 完成注册并进入首页
**入口 / 出口:** P-C-001 → P-C-004
**功能链:** F-001
**支撑能力:** F-090 注册频控

## 主流程
1. 用户点击注册 → 系统展示注册页（F-001）
2. 用户输入手机号并获取验证码 → 系统发送验证码并执行频控检查（F-001 + F-090）
3. 用户输入验证码并提交 → 系统创建账号并登录（F-001 + F-090）
```

---

## 5. L3：User Story + Acceptance Criteria

> 目标：让 AI Agent 清楚知道“沿哪条路径做到什么程度，以及如何验收”。

### 5.1 L3 YAML 模板

```yaml
# 文件: docs/prd/L3-user-stories.yaml
product_name: "[产品名称]"
version: "1.0"

iterations:
  - iteration_id: "ITER-MVP"
    iteration_name: "MVP"
    goal: "验证核心价值假设，完成最小可用闭环"

    success_metrics:
      - metric_id: "MET-001"
        metric: "注册完成率"
        target: ">= 30%"

    guardrail_metrics:
      - metric_id: "MET-101"
        metric: "异常拦截率"
        target: "明确记录并持续观测"

    scope_features: ["F-001", "F-090"]

    stories:
      - story_id: "US-001"
        status: "planned"
        title: "完成手机号注册并进入首页"
        story: "作为普通用户，我想通过手机号完成注册并进入首页，以便开始使用产品核心功能"
        actor: "ACT-001"
        priority: "P0"
        story_points: 5

        related_features: ["F-001"]
        related_supporting_features: ["F-090"]
        related_use_cases: ["UC-001"]
        related_pages: ["P-C-001", "P-C-003", "P-C-004"]

        primary_use_case: "UC-001"
        source_use_cases: ["UC-001"]
        path_steps_ref: ["UC-001.step1", "UC-001.step2", "UC-001.step3"]

        journey_contract:
          journey_goal: "让新用户完成注册并进入首页开始使用"
          journey_entry: "P-C-001"
          journey_exit: "P-C-004"
          success_outcome: "账号创建成功并建立登录态"
          failure_outcome: "账号未创建，用户停留在注册流程中"
          covers_full_journey: true

        invest_check:
          independent: true
          negotiable: true
          valuable: true
          estimable: true
          small: true
          testable: true

        acceptance_criteria:
          - ac_id: "AC-001"
            type: "happy_path"
            given: "用户在注册页面，手机号未注册"
            when: "输入有效手机号、正确验证码并点击注册"
            then: "系统创建账号、自动登录并跳转首页"
            testable: true
            automatable: true
            test_type: "functional"

          - ac_id: "AC-002"
            type: "edge_case"
            given: "用户在注册页面"
            when: "输入已注册手机号并尝试获取验证码"
            then: "系统提示手机号已注册并展示去登录入口"
            testable: true
            automatable: true
            test_type: "functional"

          - ac_id: "AC-003"
            type: "error_case"
            given: "用户短时间内多次获取验证码"
            when: "再次点击获取验证码"
            then: "系统阻止发送并提示稍后重试"
            testable: true
            automatable: true
            test_type: "functional"
```

### 5.2 L3 Markdown 模板

```markdown
# 迭代：MVP

**目标:** 验证核心价值假设
**成功指标:** 注册完成率 >= 30%
**范围:** F-001, F-090

## US-001 完成手机号注册并进入首页
- 来源路径：UC-001
- 路径步骤：UC-001.step1 → step2 → step3
- 关联功能：F-001
- 支撑能力：F-090
- 完整路径约束：covers_full_journey = true
```

---

## 6. AI 验证规则（v6 对齐）

### 规则 1：功能树完整性

```text
RULE: feature_tree_integrity
FOR EACH domain D in L1:
  ASSERT D.modules IS NOT EMPTY
FOR EACH module M in all domains:
  ASSERT (M.features IS NOT EMPTY) OR (M.submodules IS NOT EMPTY)
  ASSERT NOT (M.features IS NOT EMPTY AND M.submodules IS NOT EMPTY)
FOR EACH feature F in L1:
  ASSERT F.tree_path IS NOT EMPTY
  ASSERT F.feature_kind IN ["core_journey", "supporting_capability"]
  ASSERT F is leaf node
ERROR: "L1 功能树不完整：模块结构错误、缺少 tree_path、缺少 feature_kind 或出现非叶子 Feature 引用"
```

### 规则 2：核心闭环功能覆盖

```text
RULE: core_journey_feature_coverage
FOR EACH feature F in L1 WHERE F.feature_kind == "core_journey" AND F.status != "deprecated":
  ASSERT EXISTS at least 1 use_case UC in L2
    WHERE F.feature_id IN UC.feature_path
ERROR: "核心功能 {F.feature_id} 未进入任何完整用户路径"
```

### 规则 3：支撑能力引用完整性

```text
RULE: supporting_capability_reference
FOR EACH feature F in L1 WHERE F.feature_kind == "supporting_capability" AND F.status != "deprecated":
  ASSERT EXISTS at least 1 reference in L2 or L3
    WHERE F.feature_id IN UC.supporting_features
       OR F.feature_id IN UC.main_flow[].supporting_feature_refs
       OR F.feature_id IN UC.exception_flows[].supporting_feature_refs
       OR F.feature_id IN US.related_supporting_features
ERROR: "支撑能力 {F.feature_id} 未被任何路径或故事引用"
```

### 规则 4：用例覆盖

```text
RULE: use_case_coverage
FOR EACH use_case UC in L2 WHERE UC.status != "deprecated":
  ASSERT EXISTS at least 1 user_story US in L3
    WHERE US.primary_use_case == UC.uc_id
      AND US.journey_contract.covers_full_journey == true
ERROR: "用例 {UC.uc_id} 未被任何完整 User Story 覆盖"
```

### 规则 5：AC 完整性

```text
RULE: acceptance_criteria_completeness
FOR EACH user_story US in L3 WHERE US.status != "deprecated":
  ASSERT US.acceptance_criteria.length >= 3
  ASSERT EXISTS ac WHERE ac.type == "happy_path"
  ASSERT EXISTS ac WHERE ac.type IN ["edge_case", "error_case"]
ERROR: "User Story {US.story_id} 验收标准不完整：至少要有 happy path + edge/error"
```

### 规则 6：路径绑定

```text
RULE: path_binding
FOR EACH use_case UC in L2 WHERE UC.status != "deprecated":
  ASSERT UC.feature_path IS NOT EMPTY
  LET normalized_flow_feature_path = ordered_unique(UC.main_flow[].feature_id)
  ASSERT normalized_flow_feature_path == UC.feature_path
ERROR: "用例 {UC.uc_id} 的 feature_path 与主流程不一致"
```

### 规则 7：迭代一致性

```text
RULE: iteration_consistency
FOR EACH iteration ITER in L3:
  FOR EACH story US in ITER.stories:
    FOR EACH feature_id in US.related_features + US.related_supporting_features:
      ASSERT feature.iteration == ITER.iteration_id
ERROR: "Story {US.story_id} 关联的功能不属于当前迭代"
```

### 规则 8：依赖完整性

```text
RULE: dependency_integrity
FOR EACH feature F in L1 WHERE F.depends_on IS NOT EMPTY:
  FOR EACH dep_id IN F.depends_on:
    ASSERT EXISTS feature WHERE feature.feature_id == dep_id
    ASSERT dep.iteration <= F.iteration
ERROR: "功能 {F.feature_id} 的依赖 {dep_id} 不存在或迭代顺序错误"
```

### 规则 9：完整路径 Story 约束

```text
RULE: story_path_traceability
FOR EACH user_story US in L3 WHERE US.status != "deprecated":
  ASSERT US.primary_use_case IS NOT EMPTY
  ASSERT US.source_use_cases IS NOT EMPTY
  ASSERT US.primary_use_case IN US.source_use_cases
  ASSERT US.path_steps_ref IS NOT EMPTY
  ASSERT US.journey_contract.covers_full_journey == true
ERROR: "User Story {US.story_id} 不是一条完整用户路径"
```

### 规则 10：AC 可测试性

```text
RULE: ac_testability
FOR EACH ac IN all acceptance_criteria:
  ASSERT ac.given IS NOT EMPTY
  ASSERT ac.when IS NOT EMPTY
  ASSERT ac.then IS NOT EMPTY
  ASSERT ac.then contains measurable_or_observable_outcome
  ASSERT ac.testable == true
WARNING IF ac.automatable == false:
  "AC {ac.ac_id} 无法自动化测试，需要人工验证"
```

### 规则 11：端到端完整性

```text
RULE: e2e_flow_completeness
FOR EACH use_case UC in L2 WHERE UC.status != "deprecated":
  ASSERT UC.entry_point IS NOT EMPTY
  ASSERT UC.exit_point IS NOT EMPTY
  ASSERT UC.preconditions IS NOT EMPTY
  ASSERT UC.main_flow.length >= 2
  ASSERT UC.postconditions.success IS NOT EMPTY
  ASSERT UC.postconditions.failure IS NOT EMPTY
  ASSERT UC.exception_flows.length >= 1
ERROR: "用例 {UC.uc_id} 流程不完整：缺少入口/出口、前后置条件或异常流"
```

### 规则 12：ID 稳定性（增量更新）

```text
RULE: id_stability_for_incremental_updates
IF L1.change_mode == "partial_update":
  ASSERT existing stable IDs are preserved whenever semantics are unchanged
  WARNING IF many unchanged items are renumbered
WARNING: "检测到增量更新中存在大规模重编号，可能导致主线引用漂移"
```

---

## 7. 验证报告模板

```markdown
# PRD 完整性验证报告

**产品:** [产品名称]
**版本:** [版本号]
**验证时间:** [时间戳]

## 统计概览
| 指标 | 数量 |
|---|---|
| 能力域 | X |
| 模块 | X |
| 子模块 | X |
| core_journey Feature | X |
| supporting_capability Feature | X |
| UseCase | X |
| User Story | X |
| AC | X |

## 覆盖率
| 检查项 | 结果 | 详情 |
|---|---|---|
| core_journey Feature → UseCase 覆盖率 | X/Y | [未覆盖列表] |
| supporting capability → 引用覆盖率 | X/Y | [未引用列表] |
| UseCase → Story 覆盖率 | X/Y | [未覆盖列表] |
| Story → AC 覆盖率 | X/Y | [不完整列表] |
| feature_path → main_flow 一致率 | X/Y | [异常列表] |

## 结果
| 规则 | 状态 | 详情 |
|---|---|---|
| Rule 1 功能树完整性 | ✅/⚠️/❌ | |
| Rule 2 核心功能覆盖 | ✅/⚠️/❌ | |
| Rule 3 支撑能力引用 | ✅/⚠️/❌ | |
| Rule 4 用例覆盖 | ✅/⚠️/❌ | |
| Rule 5 AC 完整性 | ✅/⚠️/❌ | |
| Rule 6 路径绑定 | ✅/⚠️/❌ | |
| Rule 7 迭代一致性 | ✅/⚠️/❌ | |
| Rule 8 依赖完整性 | ✅/⚠️/❌ | |
| Rule 9 完整路径约束 | ✅/⚠️/❌ | |
| Rule 10 AC 可测试性 | ✅/⚠️/❌ | |
| Rule 11 端到端完整性 | ✅/⚠️/❌ | |
| Rule 12 ID 稳定性 | ✅/⚠️/❌ | |

## 结论
- Overall Result: PASS / WARNING / FAIL
- Next step: handoff to `system-architect` / `tech-manager` / return to product decision
```

---

## 8. 最佳实践

### 写 L1 时

1. 先画树，再写明细。
2. 先判断是 `core_journey` 还是 `supporting_capability`。
3. 不要把 supporting capability 硬塞成伪主路径。
4. 每个 Feature 都要有页面、端和依赖信息。

### 写 L2 时

1. 路径按“用户目标闭环”切，不按“一个功能一个路径”切。
2. `feature_path` 只放核心主链 Feature。
3. supporting capability 放到 `supporting_features` 或步骤引用，不污染主链。
4. 异常流一定写恢复方式。

### 写 L3 时

1. 一个 Story 对应一条完整主路径。
2. `path_steps_ref` 必须覆盖主路径全部步骤。
3. AC 先保证可测试，再追求丰富。
4. 护栏指标不能缺席，否则上线风险不可控。
