# 结构化需求规格（AI 可解析 · 可验证）

> 本文档定义 PRD 中三层结构化需求描述的标准格式。
> 读者不是人类，而是下游 AI Agent（架构师、开发、测试），因此所有输出必须：
> ① 使用唯一 ID 交叉引用 ② 结构化可解析 ③ 可自动化验证完整性

---

## 总览：三层需求模型

```
L1 功能架构图（按能力域/模块）     → 回答"系统有什么"
    ↓ 每个 Feature 至少被 1 个 Use Case 覆盖
L2 核心用户场景/用例流（按角色与流程） → 回答"怎么用"
    ↓ 每个 Use Case 至少拆解为 1 个 User Story
L3 User Story + 验收标准（按迭代）   → 回答"怎么做、做到什么程度"
```

### 三层交叉引用关系

```
Feature(F-xxx) ←→ UseCase(UC-xxx) ←→ UserStory(US-xxx) ←→ AcceptanceCriteria(AC-xxx)
     ↕                  ↕                    ↕
  Page(P-xxx)      UIFlow(UF-xxx)       TestCase(TC-xxx)
```

### ID 命名规范

| 实体 | 前缀 | 格式 | 示例 |
|------|------|------|------|
| 能力域 | D- | D-NNN | D-001 |
| 模块 | M- | M-NNN | M-001 |
| 功能 | F- | F-NNN | F-001 |
| 用例 | UC- | UC-NNN | UC-001 |
| 用例替代流 | UC-NNN-A | UC-NNN-AN | UC-001-A1 |
| 用例异常流 | UC-NNN-E | UC-NNN-EN | UC-001-E1 |
| 用户故事 | US- | US-NNN | US-001 |
| 验收标准 | AC- | AC-NNN | AC-001 |
| 页面 | P- | P-[端]-NNN | P-C-001, P-A-001 |
| 迭代 | ITER- | ITER-[名称] | ITER-MVP |

---

## L1：功能架构图（Functional Architecture Map）

> 目标：让 AI Agent 一次性识别产品的全部功能边界、模块划分、优先级分布。

### L1 输出格式

```yaml
# 文件: docs/prd/L1-feature-architecture.yaml
product_name: "[产品名称]"
version: "1.0"
last_updated: "YYYY-MM-DD"

# ── 能力域列表 ──
domains:
  - domain_id: "D-001"
    domain_name: "用户域"
    description: "用户身份认证、个人信息、账号安全"
    modules:
      - module_id: "M-001"
        module_name: "认证模块"
        description: "注册、登录、身份验证"
        endpoints: ["Client", "Admin"]  # 涉及哪些端
        features:
          - feature_id: "F-001"
            feature_name: "手机号注册"
            description: "用户通过手机号+验证码完成注册"
            priority: "P0"           # P0/P1/P2
            kano_type: "basic"       # basic/performance/excitement
            iteration: "ITER-MVP"    # 所属迭代
            endpoints: ["Client"]    # 功能出现在哪些端
            depends_on: []           # 依赖的其他 feature_id
            pages: ["P-C-002"]       # 关联页面 ID
            status: "planned"        # planned/in-dev/done/deprecated

          - feature_id: "F-002"
            feature_name: "验证码登录"
            description: "用户通过手机号+验证码快速登录"
            priority: "P0"
            kano_type: "basic"
            iteration: "ITER-MVP"
            endpoints: ["Client"]
            depends_on: ["F-001"]
            pages: ["P-C-001"]
            status: "planned"

      - module_id: "M-002"
        module_name: "个人中心模块"
        description: "个人信息管理、头像、昵称"
        endpoints: ["Client"]
        features:
          - feature_id: "F-010"
            feature_name: "个人信息编辑"
            description: "用户修改头像、昵称、个人简介"
            priority: "P0"
            kano_type: "basic"
            iteration: "ITER-MVP"
            endpoints: ["Client"]
            depends_on: ["F-001"]
            pages: ["P-C-007"]
            status: "planned"

  - domain_id: "D-002"
    domain_name: "核心业务域"
    description: "[产品核心业务能力]"
    modules:
      - module_id: "M-010"
        module_name: "[核心模块名]"
        # ... 同上结构

# ── 跨域依赖关系 ──
cross_domain_dependencies:
  - from: "F-010"
    to: "F-001"
    type: "requires"        # requires/enhances/conflicts
    description: "编辑个人信息需要先完成注册"

# ── 统计摘要（AI 自动生成） ──
summary:
  total_domains: 0
  total_modules: 0
  total_features: 0
  by_priority:
    P0: 0
    P1: 0
    P2: 0
  by_iteration:
    ITER-MVP: 0
  by_endpoint:
    Client: 0
    Admin: 0
    Operation: 0
  coverage_check:
    features_without_use_case: []   # 应为空
    features_without_page: []       # 应为空
```

### L1 Markdown 可视化（同步输出）

除 YAML 外，同步输出 Markdown 版本供人类快速浏览：

```markdown
# 功能架构图

## D-001 用户域

### M-001 认证模块 [Client, Admin]
| ID | 功能 | 优先级 | Kano | 迭代 | 端 | 依赖 | 状态 |
|----|------|--------|------|------|----|------|------|
| F-001 | 手机号注册 | P0 | 基础 | MVP | Client | - | planned |
| F-002 | 验证码登录 | P0 | 基础 | MVP | Client | F-001 | planned |

### M-002 个人中心模块 [Client]
| ID | 功能 | 优先级 | Kano | 迭代 | 端 | 依赖 | 状态 |
|----|------|--------|------|------|----|------|------|
| F-010 | 个人信息编辑 | P0 | 基础 | MVP | Client | F-001 | planned |
```

---

## L2：核心用户场景 / 用例流（Use Case Flows）

> 目标：让 AI Agent 理解每个功能"怎么被使用"，包括正常流、替代流、异常流。

### L2 输出格式

```yaml
# 文件: docs/prd/L2-use-case-flows.yaml
product_name: "[产品名称]"
version: "1.0"

# ── 角色定义 ──
actors:
  - actor_id: "ACT-001"
    actor_name: "普通用户"
    description: "未付费的C端用户"
    endpoints: ["Client"]
  - actor_id: "ACT-002"
    actor_name: "VIP用户"
    description: "付费订阅的C端用户"
    endpoints: ["Client"]
  - actor_id: "ACT-010"
    actor_name: "管理员"
    description: "后台管理人员"
    endpoints: ["Admin"]
  - actor_id: "ACT-020"
    actor_name: "运营人员"
    description: "运营后台操作人员"
    endpoints: ["Operation"]

# ── 用例列表 ──
use_cases:
  - uc_id: "UC-001"
    uc_name: "新用户注册"
    description: "用户首次使用产品，通过手机号完成注册"
    actor: "ACT-001"
    trigger: "用户点击注册按钮"
    priority: "P0"
    iteration: "ITER-MVP"
    related_features: ["F-001"]
    related_pages: ["P-C-002", "P-C-003"]

    # 前置条件
    preconditions:
      - "用户未登录"
      - "用户手机号未注册过"
      - "网络连接正常"

    # 主流程（Happy Path）
    main_flow:
      - step: 1
        actor_action: "用户打开App，点击'注册'按钮"
        system_response: "显示注册页面，包含手机号输入框"
        ui_ref: "P-C-003"
        data_in: null
        data_out: null
      - step: 2
        actor_action: "用户输入手机号，点击'获取验证码'"
        system_response: "校验手机号格式，发送短信验证码，启动60秒倒计时"
        ui_ref: "P-C-003"
        data_in: { "phone": "string, 11位手机号" }
        data_out: { "sms_code": "string, 6位数字" }
        business_rules: ["BR-001", "BR-002"]
      - step: 3
        actor_action: "用户输入验证码，点击'注册'"
        system_response: "验证码校验通过，创建用户账号，自动登录，跳转首页"
        ui_ref: "P-C-004"
        data_in: { "phone": "string", "code": "string" }
        data_out: { "user_id": "string", "token": "string" }
        business_rules: ["BR-003"]

    # 替代流
    alternative_flows:
      - alt_id: "UC-001-A1"
        alt_name: "手机号已注册"
        branch_from_step: 2
        condition: "输入的手机号已存在于系统中"
        steps:
          - step: 1
            system_response: "提示'该手机号已注册，请直接登录'"
          - step: 2
            system_response: "提供'去登录'按钮，点击跳转登录页"
        result: "用户被引导至登录流程"

      - alt_id: "UC-001-A2"
        alt_name: "第三方账号注册"
        branch_from_step: 1
        condition: "用户选择微信/Apple登录"
        steps:
          - step: 1
            actor_action: "用户点击第三方登录图标"
            system_response: "调起第三方授权页面"
          - step: 2
            actor_action: "用户确认授权"
            system_response: "获取第三方信息，创建账号，跳转首页"
        result: "用户通过第三方账号完成注册"

    # 异常流
    exception_flows:
      - exc_id: "UC-001-E1"
        exc_name: "网络超时"
        condition: "发送验证码或提交注册时网络超时"
        handling: "显示'网络异常，请检查网络后重试'，提供重试按钮"
        recovery: "用户点击重试，重新执行当前步骤"

      - exc_id: "UC-001-E2"
        exc_name: "验证码错误"
        condition: "用户输入的验证码与系统发送的不一致"
        handling: "提示'验证码错误，请重新输入'，允许重新获取"
        recovery: "用户重新输入或重新获取验证码"
        business_rules: ["BR-004"]

      - exc_id: "UC-001-E3"
        exc_name: "验证码过期"
        condition: "验证码超过有效期（5分钟）"
        handling: "提示'验证码已过期，请重新获取'"
        recovery: "用户点击重新获取验证码"

    # 后置条件
    postconditions:
      success:
        - "用户账号已创建（user表新增记录）"
        - "用户处于已登录状态（token已签发）"
        - "用户位于首页"
      failure:
        - "无账号创建"
        - "用户仍在注册页面"

    # 业务规则
    business_rules:
      - rule_id: "BR-001"
        rule: "手机号格式校验：必须为11位数字，以1开头"
      - rule_id: "BR-002"
        rule: "验证码发送频率限制：同一手机号60秒内只能发送1次"
      - rule_id: "BR-003"
        rule: "验证码有效期5分钟，使用后立即失效"
      - rule_id: "BR-004"
        rule: "验证码连续错误3次，锁定该手机号15分钟"

    # 数据变更
    data_changes:
      - entity: "User"
        operation: "CREATE"
        fields: ["user_id", "phone", "created_at", "status"]
      - entity: "UserToken"
        operation: "CREATE"
        fields: ["token", "user_id", "expires_at"]

# ── 用例关系图 ──
use_case_relationships:
  - from: "UC-001"
    to: "UC-002"
    type: "extends"         # extends/includes/precedes
    description: "注册成功后可进入登录流程"

# ── 统计摘要 ──
summary:
  total_use_cases: 0
  by_actor:
    ACT-001: 0
    ACT-010: 0
  by_priority:
    P0: 0
    P1: 0
  coverage_check:
    features_without_use_case: []   # 应为空
```

### L2 Markdown 可视化（同步输出）

```markdown
# 用例流：UC-001 新用户注册

**角色:** 普通用户 | **优先级:** P0 | **迭代:** MVP
**关联功能:** F-001 | **关联页面:** P-C-002, P-C-003

## 前置条件
- 用户未登录
- 手机号未注册

## 主流程
```
用户                          系统
 │                             │
 │──── 1. 点击注册 ──────────▶│
 │                             │──── 显示注册页面
 │◀────────────────────────────│
 │                             │
 │──── 2. 输入手机号 ─────────▶│
 │     点击获取验证码           │──── 校验格式
 │                             │──── 发送短信
 │◀──── 显示60秒倒计时 ────────│
 │                             │
 │──── 3. 输入验证码 ─────────▶│
 │     点击注册                 │──── 校验验证码
 │                             │──── 创建账号
 │◀──── 跳转首页 ──────────────│
```

## 替代流
- **UC-001-A1** 手机号已注册 → 引导登录
- **UC-001-A2** 第三方登录 → 调起授权

## 异常流
- **UC-001-E1** 网络超时 → 重试提示
- **UC-001-E2** 验证码错误 → 重新输入
- **UC-001-E3** 验证码过期 → 重新获取
```

---

## L3：User Story + 验收标准（按迭代）

> 目标：让 AI Agent 精确知道"做什么、做到什么程度"，每条验收标准可自动化测试。

### L3 输出格式

```yaml
# 文件: docs/prd/L3-user-stories.yaml
product_name: "[产品名称]"
version: "1.0"

# ── 迭代定义 ──
iterations:
  - iteration_id: "ITER-MVP"
    iteration_name: "MVP"
    goal: "验证核心价值假设，完成最小可用产品"
    success_metrics:
      - metric: "注册转化率"
        target: ">= 30%"
      - metric: "次日留存率"
        target: ">= 40%"
    scope_features: ["F-001", "F-002", "F-010"]  # 本迭代包含的功能

    stories:
      - story_id: "US-001"
        title: "手机号注册"
        story: "作为 [普通用户]，我想要 [通过手机号快速注册]，以便 [开始使用产品核心功能]"
        actor: "ACT-001"
        priority: "P0"
        story_points: 5
        related_features: ["F-001"]
        related_use_cases: ["UC-001"]
        related_pages: ["P-C-003"]
        depends_on: []                # 依赖的其他 story_id

        # INVEST 检查（AI 自动验证）
        invest_check:
          independent: true           # 可独立交付
          negotiable: true            # 实现方式可协商
          valuable: true              # 对用户有价值
          estimable: true             # 可估算工作量
          small: true                 # 足够小，一个迭代内完成
          testable: true              # 可测试

        # 验收标准（Given-When-Then 格式）
        acceptance_criteria:
          - ac_id: "AC-001"
            title: "正常注册流程"
            type: "happy_path"        # happy_path/edge_case/error_case/performance/security
            given: "用户在注册页面，手机号未注册"
            when: "输入有效手机号(11位)，获取并正确输入6位验证码，点击注册"
            then: "系统创建用户账号，自动登录，跳转至首页，显示欢迎提示"
            testable: true
            automatable: true
            test_type: "functional"   # functional/ui/api/performance/security

          - ac_id: "AC-002"
            title: "手机号已注册"
            type: "edge_case"
            given: "用户在注册页面"
            when: "输入已注册的手机号，点击获取验证码"
            then: "系统提示'该手机号已注册'，显示'去登录'链接"
            testable: true
            automatable: true
            test_type: "functional"

          - ac_id: "AC-003"
            title: "手机号格式错误"
            type: "error_case"
            given: "用户在注册页面"
            when: "输入非11位数字或非1开头的手机号"
            then: "输入框下方实时显示'请输入正确的手机号'红色提示"
            testable: true
            automatable: true
            test_type: "ui"

          - ac_id: "AC-004"
            title: "验证码发送频率限制"
            type: "edge_case"
            given: "用户刚获取过验证码"
            when: "60秒内再次点击获取验证码"
            then: "按钮置灰，显示倒计时'Xs后重新获取'"
            testable: true
            automatable: true
            test_type: "functional"

          - ac_id: "AC-005"
            title: "验证码连续错误锁定"
            type: "security"
            given: "用户在注册页面"
            when: "连续输入错误验证码3次"
            then: "锁定该手机号15分钟，提示'操作过于频繁，请15分钟后重试'"
            testable: true
            automatable: true
            test_type: "security"

          - ac_id: "AC-006"
            title: "注册页面加载性能"
            type: "performance"
            given: "用户在4G网络环境"
            when: "打开注册页面"
            then: "页面首屏加载时间 <= 2秒"
            testable: true
            automatable: true
            test_type: "performance"

        # 完成定义（Definition of Done）
        definition_of_done:
          - "所有 AC 测试通过"
          - "UI 与设计稿像素级一致（误差 <= 2px）"
          - "无 P0/P1 级 Bug"
          - "API 接口文档已更新"
          - "核心埋点已添加（register_page_view, register_submit, register_success）"
          - "Code Review 通过"

      - story_id: "US-002"
        title: "验证码登录"
        story: "作为 [已注册用户]，我想要 [通过手机号+验证码快速登录]，以便 [无需记忆密码即可使用产品]"
        actor: "ACT-001"
        priority: "P0"
        story_points: 3
        related_features: ["F-002"]
        related_use_cases: ["UC-002"]
        related_pages: ["P-C-001"]
        depends_on: ["US-001"]
        # ... 同上结构

  - iteration_id: "ITER-V1.1"
    iteration_name: "V1.1"
    goal: "完善核心体验，提升留存"
    # ... 同上结构
```

### L3 Markdown 可视化（同步输出）

```markdown
# 迭代：MVP

**目标:** 验证核心价值假设
**成功指标:** 注册转化率 >= 30% | 次日留存 >= 40%
**功能范围:** F-001, F-002, F-010

---

## US-001 手机号注册 [P0, 5SP]

> 作为 **普通用户**，我想要 **通过手机号快速注册**，以便 **开始使用产品核心功能**

**关联:** F-001 → UC-001 → P-C-003

| AC-ID | 类型 | Given | When | Then | 测试类型 |
|-------|------|-------|------|------|----------|
| AC-001 | 正常流 | 用户在注册页，手机号未注册 | 输入有效手机号+验证码，点击注册 | 创建账号，跳转首页 | functional |
| AC-002 | 边界 | 用户在注册页 | 输入已注册手机号 | 提示已注册，显示去登录 | functional |
| AC-003 | 异常 | 用户在注册页 | 输入格式错误手机号 | 实时红色提示 | ui |
| AC-004 | 边界 | 刚获取过验证码 | 60秒内再次点击 | 按钮置灰+倒计时 | functional |
| AC-005 | 安全 | 用户在注册页 | 连续错误3次 | 锁定15分钟 | security |
| AC-006 | 性能 | 4G网络 | 打开注册页 | 首屏 <= 2秒 | performance |

**DoD:** 全部AC通过 · UI一致 · 无P0/P1 Bug · API文档更新 · 埋点完成 · CR通过
```

---

## AI 验证规则（Validation Rules）

> 以下规则供 AI Agent 在 PRD 输出后自动执行完整性校验。

### 规则 1：功能全覆盖检查

```
RULE: feature_coverage
FOR EACH feature F in L1:
  ASSERT EXISTS at least 1 use_case UC in L2
    WHERE F.feature_id IN UC.related_features
  ERROR: "功能 {F.feature_id} {F.feature_name} 未被任何用例覆盖"
```

### 规则 2：用例全覆盖检查

```
RULE: use_case_coverage
FOR EACH use_case UC in L2:
  ASSERT EXISTS at least 1 user_story US in L3
    WHERE UC.uc_id IN US.related_use_cases
  ERROR: "用例 {UC.uc_id} {UC.uc_name} 未被任何 User Story 覆盖"
```

### 规则 3：验收标准完整性检查

```
RULE: acceptance_criteria_completeness
FOR EACH user_story US in L3:
  ASSERT US.acceptance_criteria.length >= 3
  ASSERT EXISTS ac WHERE ac.type == "happy_path"
  ASSERT EXISTS ac WHERE ac.type IN ["edge_case", "error_case"]
  ERROR: "User Story {US.story_id} 验收标准不完整：至少需要1个正常流+1个异常/边界"
```

### 规则 4：页面关联检查

```
RULE: page_coverage
FOR EACH feature F in L1:
  ASSERT F.pages IS NOT EMPTY
  FOR EACH page_id IN F.pages:
    ASSERT EXISTS page P in page_list WHERE P.page_id == page_id
  ERROR: "功能 {F.feature_id} 缺少页面关联或关联了不存在的页面"
```

### 规则 5：迭代范围一致性检查

```
RULE: iteration_consistency
FOR EACH iteration ITER in L3:
  FOR EACH story US in ITER.stories:
    FOR EACH feature_id IN US.related_features:
      ASSERT feature.iteration == ITER.iteration_id
  ERROR: "User Story {US.story_id} 关联的功能 {feature_id} 不属于当前迭代"
```

### 规则 6：依赖完整性检查

```
RULE: dependency_integrity
FOR EACH feature F in L1 WHERE F.depends_on IS NOT EMPTY:
  FOR EACH dep_id IN F.depends_on:
    ASSERT EXISTS feature WHERE feature.feature_id == dep_id
    ASSERT dep.iteration <= F.iteration  # 依赖项应在同一或更早迭代
  ERROR: "功能 {F.feature_id} 依赖的 {dep_id} 不存在或迭代顺序错误"
```

### 规则 7：INVEST 合规检查

```
RULE: invest_compliance
FOR EACH user_story US in L3:
  ASSERT US.invest_check.independent == true
  ASSERT US.invest_check.valuable == true
  ASSERT US.invest_check.testable == true
  WARNING IF US.invest_check.small == false:
    "User Story {US.story_id} 可能过大，建议拆分"
```

### 规则 8：AC 可测试性检查

```
RULE: ac_testability
FOR EACH ac IN all acceptance_criteria:
  ASSERT ac.given IS NOT EMPTY
  ASSERT ac.when IS NOT EMPTY
  ASSERT ac.then IS NOT EMPTY
  ASSERT ac.then contains measurable/observable outcome
  ASSERT ac.testable == true
  WARNING IF ac.automatable == false:
    "AC {ac.ac_id} 无法自动化测试，需人工验证"
```

### 规则 9：UI 设计稿关联检查

```
RULE: ui_design_coverage
FOR EACH page P referenced in L1 or L2:
  ASSERT EXISTS design_file for P
    WHERE design_file is .pen file with matching page
  ERROR: "页面 {P.page_id} 缺少 UI 设计稿"
```

### 规则 10：端到端流程完整性

```
RULE: e2e_flow_completeness
FOR EACH use_case UC in L2:
  ASSERT UC.preconditions IS NOT EMPTY
  ASSERT UC.main_flow.length >= 2
  ASSERT UC.postconditions.success IS NOT EMPTY
  ASSERT UC.postconditions.failure IS NOT EMPTY
  ASSERT UC.exception_flows.length >= 1
  ERROR: "用例 {UC.uc_id} 流程不完整：缺少前置/后置条件或异常流"
```

---

## 验证执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRD 完整性验证流程                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 解析 L1 YAML → 提取所有 Feature ID                    │
│     │                                                           │
│     ▼                                                           │
│  Step 2: 解析 L2 YAML → 提取所有 UseCase ID                    │
│     │    检查 Rule 1: 每个 Feature 被 UseCase 覆盖             │
│     ▼                                                           │
│  Step 3: 解析 L3 YAML → 提取所有 UserStory ID                  │
│     │    检查 Rule 2: 每个 UseCase 被 UserStory 覆盖           │
│     │    检查 Rule 3: 每个 UserStory 有完整 AC                  │
│     ▼                                                           │
│  Step 4: 交叉验证                                               │
│     │    检查 Rule 4: 页面关联                                  │
│     │    检查 Rule 5: 迭代一致性                                │
│     │    检查 Rule 6: 依赖完整性                                │
│     │    检查 Rule 7: INVEST 合规                               │
│     │    检查 Rule 8: AC 可测试性                               │
│     │    检查 Rule 9: UI 设计稿关联                             │
│     │    检查 Rule 10: 端到端完整性                              │
│     ▼                                                           │
│  Step 5: 输出验证报告                                           │
│     ├── ✅ PASS: 所有规则通过                                   │
│     ├── ⚠️ WARNING: 有警告项需关注                              │
│     └── ❌ FAIL: 有错误项必须修复                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 验证报告模板

```markdown
# PRD 完整性验证报告

**产品:** [产品名称]
**版本:** [版本号]
**验证时间:** [时间戳]

## 统计概览
| 指标 | 数量 |
|------|------|
| 能力域 | X |
| 模块 | X |
| 功能 | X |
| 用例 | X |
| User Story | X |
| 验收标准 | X |

## 覆盖率
| 检查项 | 结果 | 详情 |
|--------|------|------|
| 功能→用例覆盖率 | X/Y (Z%) | [未覆盖列表] |
| 用例→故事覆盖率 | X/Y (Z%) | [未覆盖列表] |
| 故事→AC覆盖率 | X/Y (Z%) | [不完整列表] |
| 页面→设计稿覆盖率 | X/Y (Z%) | [缺失列表] |

## 验证结果
| 规则 | 状态 | 问题数 | 详情 |
|------|------|--------|------|
| Rule 1: 功能覆盖 | ✅/❌ | N | ... |
| Rule 2: 用例覆盖 | ✅/❌ | N | ... |
| ... | | | |

## 待修复项
1. ❌ [错误描述]
2. ⚠️ [警告描述]
```

---

## 最佳实践

### 编写 L1 的最佳实践

1. **先画能力域边界** — 按业务领域而非技术模块划分
2. **每个功能必须有唯一 ID** — 后续所有引用都基于此 ID
3. **优先级必须明确** — P0 是 MVP 必须，P1 是核心体验，P2 是锦上添花
4. **依赖关系必须显式声明** — 不要假设 AI 能推断隐含依赖
5. **端点标注清晰** — 明确每个功能出现在哪些端（Client/Admin/Operation）

### 编写 L2 的最佳实践

1. **一个用例只描述一个完整场景** — 不要混合多个不相关流程
2. **主流程步骤不超过 10 步** — 超过则拆分为子用例
3. **替代流和异常流必须完整** — 这是开发最容易遗漏的部分
4. **每步都标注 UI 引用** — 让开发知道对应哪个页面/组件
5. **数据变更必须声明** — 让后端知道涉及哪些实体操作

### 编写 L3 的最佳实践

1. **一个 Story 只做一件事** — 遵循 INVEST 原则
2. **AC 必须用 Given-When-Then** — 不要用模糊描述
3. **每个 Story 至少 3 条 AC** — 正常流 + 边界 + 异常
4. **AC 的 Then 必须可观测** — "系统处理成功"不是好的 Then，"跳转首页并显示欢迎弹窗"才是
5. **DoD 不要遗漏非功能项** — 埋点、文档、CR 都是 DoD 的一部分
6. **按迭代分组** — 让开发清楚每个迭代的交付范围
