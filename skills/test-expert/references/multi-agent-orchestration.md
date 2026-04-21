# 多 Agent 调度指南

## 概述

测试专家作为测试总监角色，通过“先拆树、再分叶子、后并行执行”的方式调度多个 Agent。

本版本的关键约束：

- Agent 接收的最小执行单位是叶子用例，不是模块摘要。
- 黑盒不是独立 Agent 类型。
- 功能黑盒叶子只能分配到 `INT_API` 或 `INT_UI` 执行路径。
- `小白用户使用测试` 属于特殊黑盒验收叶子，默认分配到 `INT_UI`。
- `多个用户并行使用，生态动态串联的黑盒测试` 属于特殊生态黑盒验收叶子，默认由 `INT_UI` 主导，必要时联合 `INT_API`。

---

## Agent 角色

### 1. 测试总监

职责：

- 梳理需求树与场景树
- 生成叶子用例清单
- 按执行路径调度 Agent
- 汇总日志、证据与报告

### 2. 单元测试 Agent

职责：

- 执行 `UNIT` 叶子
- 验证模块级逻辑、边界条件、异常处理

输入示例：

```markdown
## UNIT 任务
- task_id: TASK_UNIT_001
- cases:
  - TC_UNIT_AUTH_001
  - TC_UNIT_AUTH_002
- case_paths:
  - REQ_AUTH > CAP_PASSWORD_RULE > SCN_PASSWORD_TOO_SHORT > TC_UNIT_AUTH_001
- command: pytest tests/unit/ -v
```

### 3. 服务集成 Agent

职责：

- 执行 `INT_API` 叶子
- 负责服务/API 级黑盒验证

输入示例：

```markdown
## INT_API 任务
- task_id: TASK_INT_API_001
- cases:
  - TC_INT_API_AUTH_001
  - TC_INT_API_AUTH_002
- case_paths:
  - REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS > TC_INT_API_AUTH_001
  - REQ_AUTH > CAP_LOGIN > SCN_LOGIN_INVALID_PASSWORD > TC_INT_API_AUTH_002
- base_url: http://localhost:8000
- command: pytest tests/integration/ -v --tb=short
```

### 4. 浏览器集成 Agent

职责：

- 执行 `INT_UI` 叶子
- 负责 Playwright 浏览器级黑盒验证
- 负责 `SCN_NOVICE_*` 小白用户使用验收场景
- 负责 `SCN_ECO_*` 多用户生态动态串联验收场景

输入示例：

```markdown
## INT_UI 任务
- task_id: TASK_INT_UI_001
- cases:
  - TC_INT_UI_AUTH_001
  - TC_INT_UI_ONBOARD_001
  - TC_INT_UI_MARKET_001
- case_paths:
  - REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS > TC_INT_UI_AUTH_001
  - REQ_ONBOARDING > CAP_FIRST_USE > SCN_NOVICE_FIRST_LOGIN_AND_CREATE > TC_INT_UI_ONBOARD_001
  - REQ_MARKETPLACE > CAP_ORDER_MATCH > SCN_ECO_MULTI_USER_ORDER_FLOW > TC_INT_UI_MARKET_001
- base_url: http://localhost:3000
- command: npx playwright test --reporter=html
```

### 5. 回归测试 Agent

职责：

- 重跑历史失败叶子
- 重跑历史 Bug 对应场景
- 输出回归验证结果

---

## 调度流程

```text
Step 1: 测试总监梳理需求树
Step 2: 把场景拆成叶子用例
Step 3: 每个叶子绑定执行路径
Step 4: 按 `UNIT` / `INT_API` / `INT_UI` 分派 Agent
Step 5: 汇总叶子结果
Step 6: 按场景树回写覆盖状态
Step 7: 生成测试报告
```

---

## 任务分派规则

### 分派维度

| 维度 | 规则 |
|------|------|
| 业务范围 | 按需求树 / 场景树切分 |
| 执行路径 | 按 `UNIT` / `INT_API` / `INT_UI` 切分 |
| 优先级 | `P0` 先于 `P1/P2/P3` |
| 阻塞情况 | `BLOCKED` 叶子不进入执行队列 |

### 禁止分派方式

- 把整棵需求树直接丢给一个 Agent
- 把“黑盒测试”单独建 Agent
- 用“模块 A 全量测试”替代叶子清单
- 只给出用例 ID，不给 `case_path`
- 把 `SCN_NOVICE_*` 场景当成普通功能回归而不输出验收结论
- 把 `SCN_ECO_*` 场景拆成互不关联的单用户脚本而不验证串联闭环

---

## 结果上报格式

```json
{
  "task_id": "TASK_INT_API_001",
  "execution_route": "INT_API",
  "status": "completed",
  "summary": {
    "total": 2,
    "passed": 1,
    "failed": 1,
    "blocked": 0
  },
  "case_results": [
    {
      "case_id": "TC_INT_API_AUTH_001",
      "case_path": "REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS > TC_INT_API_AUTH_001",
      "status": "Pass",
      "evidence": "logs/int-api-auth-001.txt"
    },
    {
      "case_id": "TC_INT_API_AUTH_002",
      "case_path": "REQ_AUTH > CAP_LOGIN > SCN_LOGIN_INVALID_PASSWORD > TC_INT_API_AUTH_002",
      "status": "Fail",
      "evidence": "logs/int-api-auth-002.txt",
      "bug_id": "BUG_001"
    }
  ]
}
```

---

## 汇总规则

测试总监汇总时必须：

1. 先核对每个叶子的证据
2. 再统计执行路径结果
3. 最后回写父节点覆盖状态

示例：

```markdown
## 场景树回写
| node_path | leaf_total | executed | passed | failed | blocked |
|-----------|------------|----------|--------|--------|---------|
| REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS | 2 | 2 | 1 | 1 | 0 |

## 小白用户验收结论
| node_path | can_finish_independently | blockers | acceptance_result |
|-----------|--------------------------|----------|-------------------|
| REQ_ONBOARDING > CAP_FIRST_USE > SCN_NOVICE_FIRST_LOGIN_AND_CREATE | No | 看不懂“工作台”入口含义 | 需引导后可完成 |

## 多用户生态验收结论
| node_path | participant_roles | key_linkage | blockers | acceptance_result |
|-----------|-------------------|-------------|----------|-------------------|
| REQ_MARKETPLACE > CAP_ORDER_MATCH > SCN_ECO_MULTI_USER_ORDER_FLOW | 买家 / 卖家 / 平台 | 买家下单 -> 卖家接单 -> 平台通知 -> 买家看到更新 | 状态同步延迟 | 需约束条件后可闭环 |
```

---

## 资源建议

| 执行路径 | 推荐并发度 | 说明 |
|----------|------------|------|
| UNIT | 中-高 | 相对稳定，可并发 |
| INT_API | 中 | 受服务与数据库资源影响 |
| INT_UI | 低-中 | 浏览器资源重，优先保证稳定 |

---

## 检查清单

- [ ] 所有任务都细化到叶子用例
- [ ] 所有 `INT_API` / `INT_UI` 叶子都属于黑盒验证
- [ ] 没有单独黑盒测试 Agent
- [ ] 汇总结果能回写到场景树
- [ ] `SCN_NOVICE_*` 场景有单独验收结论
- [ ] `SCN_ECO_*` 场景有单独生态验收结论
