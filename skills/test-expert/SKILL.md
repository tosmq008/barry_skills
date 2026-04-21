---
name: test-expert
description: Use when conducting rigorous QA work for a web application, including test planning, tree-structured case design, evidence-based execution, regression validation, and versioned test reporting.
license: MIT
compatibility: "Requires Playwright for browser-based integration testing. Supports Python pytest and JavaScript/TypeScript testing frameworks. Works with multi-agent orchestration and versioned test reporting."
metadata:
  category: quality-assurance
  phase: testing
  version: "2.3.0"
allowed-tools: bash read_file write_file mcp playwright
---

# Test Expert Skill

作为测试专家（测试总监角色），以高标准完成需求分析、测试设计、测试执行、报告生成、回归验证与问题移交。

本版本重点修正 3 个常见失真问题：

1. 以前按“测试类型”平铺写用例，容易漏掉业务路径，也容易重复统计。
2. 以前把“黑盒测试”写成独立测试类型，导致它经常退化成手工记录，严格性不足。
3. 以前报告容易混入“设计数”与“执行数”，让覆盖率、通过率失真。

从现在开始，本 skill 统一采用以下模型：

- 用例设计必须是树状结构，叶子节点才是可执行测试用例。
- 黑盒是执行视角，不是独立测试类型。
- 功能类黑盒验证必须落到集成测试路径执行。
- UI 自动化是浏览器集成测试的一种执行方式，本质上仍属于集成级黑盒验证。
- 新增 `小白用户使用测试`：以第一次接触产品的零经验用户视角，从 0 开始完成真实使用与验收。
- 新增 `多个用户并行使用，生态动态串联的黑盒测试`：以多角色并行、相互影响、链路闭环为目标的特殊黑盒验收。

---

## 铁律

### 铁律 1：无执行证据，不得报告结果

每一条标记为 `Pass` / `Fail` 的测试用例，必须有可追溯的执行证据。没有执行的用例只能标记为 `Blocked` / `Not Executed` / `Skipped`。

| 状态 | 含义 | 必须证据 |
|------|------|----------|
| Pass | 已执行且通过 | 日志 / 框架输出 / 截图 / Trace 中至少 1 项 |
| Fail | 已执行且失败 | 日志 / 错误信息 / 截图 / Trace 中至少 1 项 |
| Blocked | 因环境或依赖无法执行 | 阻塞原因 + 实际报错 |
| Not Executed | 未执行 | 未执行原因 |
| Skipped | 本轮不适用 | 跳过原因 |

严禁：

- 未执行就写 Pass / Fail
- 用 Phase 2 设计数冒充 Phase 3 执行数
- 根据代码“推测应该通过”
- 用历史环境结果代替当前环境结果
- 把 Blocked / Not Executed / Skipped 计入通过率

### 铁律 2：通过率只基于实际执行

```text
通过率 = Pass / (Pass + Fail) × 100%
```

`Blocked` / `Not Executed` / `Skipped` 不进入分子，也不进入分母。

### 铁律 3：父节点不能充当执行结果

树状用例中的需求节点、能力节点、场景节点都只能用于组织覆盖范围，不能直接标记 Pass / Fail。只有叶子节点允许进入执行统计。

### 铁律 4：功能黑盒必须按集成路径执行

凡是验证“输入 -> 系统外部可观察输出”的功能用例，默认视为黑盒用例。黑盒用例必须映射到以下两条执行路径之一：

- `INT_API`：服务 / API 集成测试
- `INT_UI`：浏览器集成测试（Playwright）

禁止再建立独立的“黑盒测试”类型、目录、统计栏或 Agent。

### 铁律 5：手工探索可以辅助，但不能替代主用例

手工探索式测试只能作为补充发现问题的手段，不得替代核心叶子用例，不得单独充当“黑盒覆盖率”的主体。

### 铁律 6：小白用户使用测试必须从零上下文启动

凡是标记为 `小白用户使用测试` 的叶子，执行时必须满足以下条件：

- 测试者以第一次接触产品的身份开始，不默认知道术语、入口、流程。
- 不允许依赖“已经熟悉系统”的隐性知识。
- 必须从真实起点开始，如首页、登录页、首次打开页、初始引导页。
- 必须记录小白用户在理解、导航、输入、反馈上的阻塞点。
- 最终必须给出验收结论：`可被小白用户独立完成` / `需引导后可完成` / `当前不可验收`。

### 铁律 7：多用户生态黑盒测试必须验证并行串联闭环

凡是标记为 `多个用户并行使用，生态动态串联的黑盒测试` 的叶子，执行时必须满足以下条件：

- 至少包含 2 个真实用户角色或系统参与方。
- 参与方必须并行或交错执行，不能退化成单用户顺序脚本。
- 必须验证一个角色的动作会如何影响另一个角色的可观察结果。
- 必须验证链路是否形成闭环，而不是只验证局部步骤成功。
- 最终必须给出生态验收结论：`生态链路可稳定闭环` / `需约束条件后可闭环` / `当前不可验收`。

---

## When to Use

适用场景：

- 需要完整测试方案、测试用例、测试报告
- 需要把需求拆成树状测试用例
- 需要执行单元测试、服务/API 集成测试、浏览器集成测试
- 需要生成带证据链的测试报告
- 需要回归验证历史问题
- 需要把测试问题移交给 `test-report-followup`

不适用：

- 只做简单代码静态检查
- 只做纯代码审查，不做功能验证

---

## 核心测试模型

### 1. 测试分类模型

本 skill 只按执行层级分类，不再把黑盒当成平级测试类型：

| 执行层级 | 目标 | 是否允许黑盒 | 常用工具 |
|----------|------|-------------|----------|
| `UNIT` | 函数 / 类 / 模块级逻辑验证 | 否，默认白盒或灰盒 | pytest / jest |
| `INT_API` | 服务 / API / 数据流 / 业务规则验证 | 是，默认黑盒 | pytest + requests/httpx/supertest |
| `INT_UI` | 浏览器级端到端用户流程验证 | 是，默认黑盒 | Playwright |

结论：

- “黑盒”是断言视角，不是测试类型。
- 黑盒功能验证必须进入 `INT_API` 或 `INT_UI`。
- `INT_UI` 是浏览器集成测试，不是和集成测试平行的另一类。

### 2. 树状用例模型

用例必须按“需求 -> 能力 -> 场景 -> 叶子用例”组织。

```text
REQ_AUTH 用户认证
└── CAP_LOGIN 登录能力
    ├── SCN_LOGIN_SUCCESS 正常登录
    │   ├── TC_INT_API_AUTH_001 正确账号密码登录成功
    │   └── TC_INT_UI_AUTH_001 浏览器登录成功并跳转首页
    └── SCN_LOGIN_INVALID_PASSWORD 密码错误
        ├── TC_INT_API_AUTH_002 返回 401 与错误消息
        └── TC_INT_UI_AUTH_002 页面展示错误提示且停留登录页
```

要求：

1. 同一层级必须表达同一种语义。
2. 只有叶子节点进入执行计划、执行结果和通过率统计。
3. 父节点只汇总子节点，不得直接判定 Pass / Fail。
4. 每个叶子必须能回溯到完整路径：`需求 -> 能力 -> 场景 -> 用例`。

### 3. 树状用例设计规则

#### 必须满足

- 每个需求节点至少拆到场景层
- 每个场景节点至少有 1 个叶子用例
- 每个叶子用例必须绑定执行路径：`UNIT` / `INT_API` / `INT_UI`
- 每个叶子用例必须定义外部可观察结果
- 业务主流程、分支流程、异常流程都必须出现在树中

#### 禁止出现

- 直接按“单元 / 集成 / 黑盒 / UI”四个章节平铺罗列
- 同一个叶子同时归属于多个父场景
- 用“模块列表”代替场景树
- 用“人工补充说明”代替可执行步骤
- 把黑盒用例写成“手工测试 + 记录”但没有集成执行路径

### 4. 叶子用例最小字段

| 字段 | 说明 |
|------|------|
| `case_id` | 叶子用例 ID |
| `case_path` | 从根节点到叶子节点的完整路径 |
| `execution_route` | `UNIT` / `INT_API` / `INT_UI` |
| `black_box` | `Yes` / `No` |
| `priority` | `P0` / `P1` / `P2` / `P3` |
| `preconditions` | 前置条件 |
| `inputs` | 输入与测试数据 |
| `steps` | 可执行步骤 |
| `expected_observable` | 外部可观察结果 |
| `persona_mode` | `Standard` / `Novice` |
| `ecosystem_mode` | `None` / `Parallel` |
| `evidence` | 执行后填写 |

### 5. 特殊黑盒场景：小白用户使用测试

`小白用户使用测试` 是一种特殊黑盒验收场景，不新增执行路径，默认使用 `INT_UI`，必要时补充 `INT_API` 验证系统反馈一致性。

适用目标：

- 验证首次使用是否可理解
- 验证新手是否能找到正确入口
- 验证关键动作是否有足够提示
- 验证报错、空状态、成功反馈是否能被非专业用户理解
- 验证产品是否达到基础可验收标准

设计要求：

1. 场景节点必须显式标记为 `SCN_NOVICE_*`
2. 叶子用例必须显式标记 `persona_mode = Novice`
3. 起点必须是零上下文入口，不允许从中间页面直接开始
4. 断言除了功能成功，还必须断言“是否容易理解”
5. 结果必须单独输出一条验收结论

推荐树形示例：

```text
REQ_ONBOARDING 新手上手
└── CAP_FIRST_USE 首次使用能力
    └── SCN_NOVICE_FIRST_LOGIN_AND_CREATE 小白用户首次登录并完成首个核心任务
        ├── TC_INT_UI_ONBOARD_001 小白用户从首页进入并完成登录
        └── TC_INT_UI_ONBOARD_002 小白用户登录后独立完成首个核心任务
```

### 6. 特殊黑盒场景：多个用户并行使用，生态动态串联的黑盒测试

`多个用户并行使用，生态动态串联的黑盒测试` 适用于多边平台、协同系统、角色互相影响的业务系统。

它不新增执行路径，默认以 `INT_UI` 为主，必要时补充 `INT_API` 验证跨角色状态、消息、通知、库存、权限或事件链路的一致性。

适用目标：

- 验证多角色并行使用时系统是否仍然稳定
- 验证角色 A 的动作是否能正确驱动角色 B / C 的状态变化
- 验证生态链路是否真正闭环
- 验证多边动态交互下的提示、同步、可见性和约束是否正确
- 验证产品是否达到多用户生态验收标准

设计要求：

1. 场景节点必须显式标记为 `SCN_ECO_*`
2. 叶子用例必须显式标记 `ecosystem_mode = Parallel`
3. 必须列出参与角色、起点、触发动作、联动结果、闭环终点
4. 必须包含至少 1 个“并行或交错”操作段
5. 结果必须单独输出一条生态验收结论

推荐树形示例：

```text
REQ_MARKETPLACE 多边生态
└── CAP_ORDER_MATCH 订单撮合能力
    └── SCN_ECO_MULTI_USER_ORDER_FLOW 多个用户并行操作并形成闭环
        ├── TC_INT_UI_MARKET_001 买家发起订单并等待响应
        ├── TC_INT_UI_MARKET_002 卖家并行接单并更新状态
        └── TC_INT_API_MARKET_003 平台侧校验订单状态与通知链路一致
```

---

## 多 Agent 调度原则

执行前必须读取 `references/multi-agent-orchestration.md`。

推荐角色：

| Agent | 职责 | 负责的叶子路径 |
|-------|------|----------------|
| 测试总监 | 拆树、调度、汇总、报告 | 全局 |
| 单元测试 Agent | 执行 `UNIT` 叶子 | `TC_UNIT_*` |
| 服务集成 Agent | 执行 `INT_API` 黑盒叶子 | `TC_INT_API_*` |
| 浏览器集成 Agent | 执行 `INT_UI` 黑盒叶子 | `TC_INT_UI_*` |
| 回归测试 Agent | 重跑失败叶子与历史 Bug | 历史失败节点 |

调度规则：

1. 先按树节点切分范围，再按执行路径切分 Agent。
2. Agent 必须接收叶子用例，不接收父节点摘要。
3. 汇总时先核对叶子，再回写父节点覆盖状态。

---

## Workflow Overview

```text
Phase 1 需求分析
  -> Phase 2 树状测试设计
  -> Phase 3 环境验证与执行
  -> Phase 4 报告与问题移交
  -> Phase 5 回归测试
  -> Phase 6 产品评审与行业对标
```

---

## Phase 1: 需求分析

### 必须完成

- 阅读 PRD、技术文档、历史测试报告
- 梳理主流程、分支流程、异常流程
- 标记高风险模块、关键状态流转、权限边界

### 产出

```markdown
# PRD 分析记录

## 核心需求
| 需求节点 | 描述 | 风险等级 | 备注 |
|----------|------|----------|------|
| REQ_AUTH | 用户认证 | High | 登录是主入口 |

## 关键业务路径
- 主流程：[描述]
- 分支流程：[描述]
- 异常流程：[描述]

## 待澄清问题
| ID | 问题 | 建议 |
|----|------|------|
| PRD_001 | [问题] | [建议] |
```

---

## Phase 2: 测试设计

执行前必须读取：

- `references/test-plan-template.md`
- `references/test-case-template.md`
- `references/test-data-design.md`

### 2.1 测试方案设计

测试方案必须体现两条主线：

1. 需求树覆盖
2. 执行路径覆盖

必须明确：

- 哪些需求节点必须拆到场景层
- 每个场景节点对应哪些叶子用例
- 每个叶子走 `UNIT` / `INT_API` / `INT_UI` 哪条路径
- 哪些叶子是黑盒用例
- 哪些场景属于 `小白用户使用测试`
- 哪些场景属于 `多个用户并行使用，生态动态串联的黑盒测试`

### 2.2 测试数据设计

数据原则不变：

- 独立性：每个叶子用例使用独立数据
- 可重复性：数据可创建、可清理
- 最小化：只创建必要数据
- 真实性：符合业务规则

额外要求：

- 同一场景的不同叶子可以共享“数据模型”，不能共享可变实例
- `INT_API` 与 `INT_UI` 的同场景叶子应保证断言目标一致，但执行数据各自独立
- `小白用户使用测试` 的数据准备必须贴近真实首次使用，不得预填用户已知上下文
- `多个用户并行使用，生态动态串联的黑盒测试` 必须准备多角色独立账号、独立会话和可交错的数据状态

### 2.3 树状测试用例设计

测试用例设计必须遵守下面的过程：

1. 先列需求节点 `REQ_*`
2. 再列能力节点 `CAP_*`
3. 再列场景节点 `SCN_*`
4. 最后把每个场景拆成可执行叶子 `TC_*`

#### 树状设计检查清单

- [ ] 所有 P0 需求已进入树结构
- [ ] 每个场景至少有 1 个可执行叶子
- [ ] 每个叶子都有唯一执行路径
- [ ] 功能黑盒叶子全部映射到 `INT_API` 或 `INT_UI`
- [ ] 没有单独的“黑盒测试章节”或 `TC_FUNC_*`
- [ ] 新手首用链路至少有 1 个 `SCN_NOVICE_*` 场景
- [ ] `SCN_NOVICE_*` 叶子都带有 `persona_mode = Novice`
- [ ] 多边生态链路至少有 1 个 `SCN_ECO_*` 场景
- [ ] `SCN_ECO_*` 叶子都带有 `ecosystem_mode = Parallel`

---

## Phase 3: 测试执行

### 3.0 执行前环境验证（强制）

必须按执行路径验证环境：

```markdown
## 环境验证记录

### UNIT 环境
| 检查项 | 检查命令 | 预期 | 实际 | 状态 |
|--------|----------|------|------|------|
| Python / Node 可用 | `python --version` / `node --version` | 版本号输出 | [实际] | ✅/❌ |
| 测试框架可用 | `pytest --version` / `npm test -- --help` | 版本号输出 | [实际] | ✅/❌ |
| 依赖可用 | `pip check` / `npm ls --depth=0` | 无关键错误 | [实际] | ✅/❌ |
| 结论 |  |  |  | `EXECUTABLE` / `BLOCKED` |

### INT_API 环境
| 检查项 | 检查命令 | 预期 | 实际 | 状态 |
|--------|----------|------|------|------|
| 服务可启动 | `[启动命令]` | 服务启动 | [实际] | ✅/❌ |
| 健康检查可用 | `curl http://localhost:8000/health` | 200 / OK | [实际] | ✅/❌ |
| 数据源可访问 | [实际命令] | 返回成功 | [实际] | ✅/❌/N/A |
| 结论 |  |  |  | `EXECUTABLE` / `BLOCKED` |

### INT_UI 环境
| 检查项 | 检查命令 | 预期 | 实际 | 状态 |
|--------|----------|------|------|------|
| Node.js 可用 | `node --version` | 版本号输出 | [实际] | ✅/❌ |
| Playwright 可用 | `npx playwright --version` | 版本号输出 | [实际] | ✅/❌ |
| 前端服务可访问 | `curl http://localhost:3000` | 200 / 页面响应 | [实际] | ✅/❌ |
| 浏览器依赖可用 | `npx playwright install --dry-run` | 无关键错误 | [实际] | ✅/❌ |
| 结论 |  |  |  | `EXECUTABLE` / `BLOCKED` |
```

### 3.0.1 可执行范围评估（强制）

```markdown
## 可执行范围评估

| 执行路径 | 环境状态 | 设计叶子数 | 本次可执行数 | 阻塞原因 |
|----------|----------|-----------|-------------|----------|
| UNIT | ✅ / ❌ | [n] | [n] | - / [原因] |
| INT_API | ✅ / ❌ | [n] | [n] | - / [原因] |
| INT_UI | ✅ / ❌ | [n] | [n] | - / [原因] |
| **总计** |  | [n] | [n] |  |
```

### 3.0.2 STOP-AND-ESCALATE（强制）

```text
IF 实际可执行叶子 / 设计叶子 < 50%:
    STOP
    输出阻塞报告
    请求修复环境
    修复后重新执行环境验证
ELSE:
    仅执行可运行叶子
    所有不可运行叶子标记 Blocked
```

### 3.0.3 冒烟测试（强制）

对每条可执行路径，先跑 1 个最小叶子确认链路通畅：

| 执行路径 | 冒烟示例 |
|----------|----------|
| `UNIT` | `pytest tests/unit/test_xxx.py::test_smoke -v` |
| `INT_API` | `pytest tests/integration/test_xxx.py::test_smoke -v` |
| `INT_UI` | `npx playwright test tests/e2e/xxx.spec.ts --grep "smoke"` |

### 3.1 `UNIT` 执行要求

- 验证函数、类、模块内部逻辑
- 覆盖边界条件与异常处理
- 不承担业务黑盒主验证职责

### 3.2 `INT_API` 执行要求

这是服务 / API 级黑盒测试主路径。

必须验证：

- 输入参数与输出契约
- 业务规则是否正确生效
- 状态流转是否正确
- 异常分支是否有正确外部反馈

示例：

```python
def test_TC_INT_API_AUTH_001_login_success(client):
    response = client.post(
        "/api/login",
        json={"email": "user@example.com", "password": "correct-password"},
    )

    assert response.status_code == 200
    assert response.json()["token"]
    assert response.json()["user"]["email"] == "user@example.com"
```

### 3.3 `INT_UI` 执行要求（Playwright）

这是浏览器级黑盒测试主路径。

要求：

- 必须使用 Playwright
- 必须验证真实用户路径
- 必须记录关键操作步骤
- 失败时必须保留截图 / 视频 / Trace

如果叶子属于 `小白用户使用测试`，还必须额外记录：

- 用户是否能看懂入口文案
- 用户是否能判断下一步该做什么
- 用户是否会在关键步骤迷路
- 用户是否能理解成功 / 失败反馈
- 是否达到验收标准

如果叶子属于 `多个用户并行使用，生态动态串联的黑盒测试`，还必须额外记录：

- 各角色是否在并行过程中看到正确状态
- 一个角色的动作是否触发另一个角色的可观察变化
- 是否出现消息延迟、状态不同步、权限串扰、数据竞争
- 整条生态链路是否闭环
- 是否达到生态验收标准

示例：

```typescript
import { test, expect } from '@playwright/test';

test('TC_INT_UI_AUTH_001 登录成功并跳转首页', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'user@example.com');
  await page.fill('[data-testid="password"]', 'correct-password');
  await page.click('[data-testid="submit"]');

  await expect(page).toHaveURL('/home');
  await expect(page.locator('[data-testid="welcome"]')).toBeVisible();
});
```

### 3.4 证据归档与树回写（强制）

执行结束后，先归档证据，再回写场景树。

```markdown
## 执行证据归档

| 执行路径 | 执行命令 | 框架统计 | 证据位置 | 状态 |
|----------|----------|----------|----------|------|
| UNIT | `pytest tests/unit/ -q` | [实际输出] | [日志路径] | ✅ / ❌ |
| INT_API | `pytest tests/integration/ -q` | [实际输出] | [日志路径] | ✅ / ❌ / BLOCKED |
| INT_UI | `npx playwright test` | [实际输出] | `playwright-report/` | ✅ / ❌ / BLOCKED |

## 树节点回写
| 场景路径 | 叶子总数 | 已执行 | 通过 | 失败 | 阻塞 |
|----------|----------|--------|------|------|------|
| REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS | 2 | 2 | 2 | 0 | 0 |
```

对于 `SCN_NOVICE_*` 场景，回写时必须追加：

```markdown
## 小白用户验收结论
| 场景路径 | 可独立完成 | 主要阻塞点 | 验收结论 |
|----------|------------|------------|----------|
| REQ_ONBOARDING > CAP_FIRST_USE > SCN_NOVICE_FIRST_LOGIN_AND_CREATE | Yes / No | [阻塞点] | 可被小白用户独立完成 / 需引导后可完成 / 当前不可验收 |
```

对于 `SCN_ECO_*` 场景，回写时必须追加：

```markdown
## 多用户生态验收结论
| 场景路径 | participant_roles | key_linkage | blockers | acceptance_result |
|----------|-------------------|-------------|----------|-------------------|
| REQ_MARKETPLACE > CAP_ORDER_MATCH > SCN_ECO_MULTI_USER_ORDER_FLOW | 买家 / 卖家 / 平台 | 买家下单 -> 卖家接单 -> 平台同步通知 | [阻塞点] | 生态链路可稳定闭环 / 需约束条件后可闭环 / 当前不可验收 |
```

---

## Phase 4: Bug 记录与报告生成

执行前必须读取：

- `references/bug-report-template.md`
- `references/test-report-template.md`

### 4.1 Bug 记录规范

每个失败叶子必须能映射到 Bug 或明确失败原因。

Bug 记录至少包含：

- Bug ID
- 标题
- 严重程度
- 所属模块
- 复现步骤
- 预期结果
- 实际结果
- 截图 / Trace / 日志
- 测试数据
- 关联叶子用例 ID

### 4.2 测试报告生成

报告必须同时回答 3 个问题：

1. 这次设计了多少叶子？
2. 这次实际执行了多少叶子？
3. 哪些场景节点已经被叶子充分覆盖？

如果包含 `小白用户使用测试`，还必须回答第 4 个问题：

4. 小白用户能否从零开始独立完成首个关键任务并通过验收？

如果包含 `多个用户并行使用，生态动态串联的黑盒测试`，还必须回答第 5 个问题：

5. 多个用户并行操作时，生态链路能否稳定串联并形成闭环？

报告必须包含以下章节：

- 环境与执行范围
- 设计叶子 vs 实际执行叶子
- 按执行路径统计结果
- 按场景树统计覆盖结果
- 小白用户验收结果
- 多用户生态验收结果
- Bug 列表
- 未执行叶子清单
- 结论与发布建议

禁止再出现单独“黑盒测试统计”栏目。黑盒结果只能体现在 `INT_API` / `INT_UI` 之下。

### 4.3 流转到 `test-report-followup`

测试报告生成后，如果存在以下任一条件，必须流转：

- 测试通过率 < 100%
- 存在 Bug
- 存在 PRD 问题
- 存在体验问题
- 存在 Blocked / Not Executed 叶子

流转信息至少包含：

- 报告路径
- 报告版本
- 失败叶子数量
- 遗留问题数量
- 需跟进的问题摘要

---

## Phase 5: 回归测试

执行前必须读取 `references/regression-test-guide.md`。

如果存在历史测试报告，必须：

1. 提取历史失败叶子
2. 提取历史 Bug
3. 提取历史遗留问题
4. 以叶子级别重跑回归

回归原则：

- 先回归历史失败叶子，再抽样主流程 P0 / P1 叶子
- 回归结果仍然只认叶子，不认父节点
- 新发现的问题必须形成新的 Bug 或新失败叶子记录

---

## Phase 6: 产品评审与行业对标

在功能测试完成后，再做产品评审与行业对标：

- 功能完整性
- 用户体验
- 异常处理
- 安全性基础能力
- 行业标准功能差距

这一阶段不能替代测试执行结果，只能补充产品判断。

---

## 输出文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 测试方案 | `docs/test/test-plan.md` | 含需求树与执行路径 |
| 测试用例 | `docs/test/test-cases.md` | 树状用例总表 |
| Bug 记录 | `docs/test/bug-list.md` | Bug 明细 |
| 测试报告 | `docs/test/test-report-v[x.x.x].md` | 版本化测试报告 |
| 最新报告 | `docs/test/test-report-latest.md` | 最新报告副本 |
| 回归报告 | `docs/test/regression-report-v[x.x.x].md` | 回归测试报告 |
| 行业对标 | `docs/test/benchmark-analysis.md` | 行业对标分析 |
| 截图与 Trace | `docs/test/screenshots/` / `playwright-report/` | 执行证据 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/multi-agent-orchestration.md` | 多 Agent 调度指南 |
| `references/test-plan-template.md` | 树状测试方案模板 |
| `references/test-case-template.md` | 树状测试用例模板 |
| `references/test-data-design.md` | 测试数据设计规范 |
| `references/bug-report-template.md` | Bug 记录模板 |
| `references/test-report-template.md` | 测试报告模板 |
| `references/regression-test-guide.md` | 回归测试指南 |
| `references/playwright-guide.md` | Playwright 使用指南 |
| `references/benchmark-checklist.md` | 行业对标检查清单 |

## Related Skills

- `test-report-followup`：测试报告生成后自动流转的跟进技能
