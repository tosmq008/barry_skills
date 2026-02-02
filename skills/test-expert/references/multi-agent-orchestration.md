# 多 Agent 调度指南

## 概述

测试专家作为测试总监角色，通过调度多个专业 Agent 并行执行测试任务，显著提高测试执行效率。

## Agent 角色详解

### 1. 测试总监 (Orchestrator)

**职责：**
- 分析测试方案，分解测试任务
- 根据任务类型分配给对应 Agent
- 监控各 Agent 执行状态
- 收集汇总测试结果
- 生成统一测试报告

**能力要求：**
- 理解测试方案和用例设计
- 任务分解和优先级排序
- 并行调度和资源管理
- 结果汇总和报告生成

### 2. 单元测试 Agent

**职责：**
- 执行单元测试用例
- 验证函数/方法级别的正确性
- 收集代码覆盖率数据

**技术栈：**
- Python: pytest, unittest
- JavaScript: jest, mocha
- 覆盖率: coverage, istanbul

**输入：**
```markdown
## 单元测试任务

### 任务信息
- 任务ID: TASK_UNIT_001
- 用例范围: TC_UNIT_001 ~ TC_UNIT_050
- 项目路径: /path/to/project
- 测试目录: tests/unit/

### 执行命令
pytest tests/unit/ -v --cov=src --cov-report=html

### 输出要求
- 测试结果 JSON
- 覆盖率报告
- 失败用例详情
```

**输出：**
```json
{
  "task_id": "TASK_UNIT_001",
  "status": "completed",
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "skipped": 0,
    "coverage": "85%"
  },
  "failed_cases": [
    {
      "case_id": "TC_UNIT_023",
      "name": "test_calculate_total",
      "error": "AssertionError: expected 100, got 99",
      "file": "tests/unit/test_calculator.py",
      "line": 45
    }
  ],
  "execution_time": 1523
}
```

### 3. 集成测试 Agent

**职责：**
- 执行 API 接口测试
- 验证接口参数和返回值
- 检查接口业务逻辑

**技术栈：**
- Python: pytest + requests/httpx
- JavaScript: supertest, axios
- 工具: Postman, Insomnia

**输入：**
```markdown
## 集成测试任务

### 任务信息
- 任务ID: TASK_API_001
- 用例范围: TC_API_001 ~ TC_API_030
- 基础URL: http://localhost:8000
- API文档: docs/api/api-spec.md

### 执行命令
pytest tests/integration/ -v --tb=short

### 输出要求
- 接口测试结果
- 响应时间统计
- 失败接口详情
```

**输出：**
```json
{
  "task_id": "TASK_API_001",
  "status": "completed",
  "summary": {
    "total": 30,
    "passed": 28,
    "failed": 2,
    "skipped": 0
  },
  "api_coverage": {
    "total_endpoints": 25,
    "tested_endpoints": 23,
    "coverage": "92%"
  },
  "failed_cases": [
    {
      "case_id": "TC_API_015",
      "endpoint": "POST /api/users",
      "expected_status": 201,
      "actual_status": 400,
      "error": "Validation error: email format invalid"
    }
  ],
  "performance": {
    "avg_response_time": 125,
    "max_response_time": 890,
    "min_response_time": 15
  }
}
```

### 4. 黑盒测试 Agent

**职责：**
- 执行功能测试用例
- 验证业务流程正确性
- 记录测试步骤和结果

**测试方法：**
- 等价类划分
- 边界值分析
- 场景测试
- 错误推测

**输入：**
```markdown
## 黑盒测试任务

### 任务信息
- 任务ID: TASK_FUNC_001
- 用例范围: TC_FUNC_001 ~ TC_FUNC_020
- 测试环境: http://localhost:3000

### 测试用例
| 用例ID | 用例名称 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|
| TC_FUNC_001 | 用户注册成功 | 1.打开注册页... | 注册成功 |

### 输出要求
- 每个用例的执行结果
- 失败用例的截图
- Bug 记录
```

**输出：**
```json
{
  "task_id": "TASK_FUNC_001",
  "status": "completed",
  "summary": {
    "total": 20,
    "passed": 18,
    "failed": 2,
    "blocked": 0
  },
  "failed_cases": [
    {
      "case_id": "TC_FUNC_008",
      "name": "用户修改密码",
      "actual_result": "修改后无法登录",
      "screenshot": "screenshots/TC_FUNC_008_fail.png",
      "bug_id": "BUG_NEW_001"
    }
  ],
  "bugs_found": [
    {
      "bug_id": "BUG_NEW_001",
      "title": "修改密码后无法登录",
      "severity": "Major",
      "related_case": "TC_FUNC_008"
    }
  ]
}
```

### 5. UI 自动化 Agent

**职责：**
- 执行 Playwright E2E 测试
- 验证用户界面交互
- 截图和录屏

**技术栈：**
- Playwright (推荐)
- Cypress
- Selenium

**输入：**
```markdown
## UI 自动化测试任务

### 任务信息
- 任务ID: TASK_UI_001
- 用例范围: TC_UI_001 ~ TC_UI_015
- 基础URL: http://localhost:3000
- 浏览器: chromium, firefox, webkit

### 执行命令
npx playwright test --reporter=html

### 输出要求
- 测试结果报告
- 失败截图
- 失败录屏
- Trace 文件
```

**输出：**
```json
{
  "task_id": "TASK_UI_001",
  "status": "completed",
  "summary": {
    "total": 15,
    "passed": 13,
    "failed": 2,
    "skipped": 0
  },
  "browser_results": {
    "chromium": {"passed": 13, "failed": 2},
    "firefox": {"passed": 14, "failed": 1},
    "webkit": {"passed": 13, "failed": 2}
  },
  "failed_cases": [
    {
      "case_id": "TC_UI_007",
      "name": "用户登录流程",
      "browser": "chromium",
      "error": "Timeout waiting for selector [data-testid='welcome']",
      "screenshot": "test-results/TC_UI_007-chromium/screenshot.png",
      "video": "test-results/TC_UI_007-chromium/video.webm",
      "trace": "test-results/TC_UI_007-chromium/trace.zip"
    }
  ],
  "report_path": "playwright-report/index.html"
}
```

### 6. 回归测试 Agent

**职责：**
- 验证历史 Bug 修复
- 执行回归用例
- 确认问题是否解决

**输入：**
```markdown
## 回归测试任务

### 任务信息
- 任务ID: TASK_REG_001
- 基准版本: v1.0.0
- 当前版本: v1.0.1

### 回归范围
| Bug ID | 标题 | 原状态 |
|--------|------|--------|
| BUG_001 | 登录失败 | Fixed |
| BUG_002 | 数据丢失 | Fixed |

### 输出要求
- 每个 Bug 的验证结果
- 验证截图
- 新发现问题
```

**输出：**
```json
{
  "task_id": "TASK_REG_001",
  "status": "completed",
  "summary": {
    "total_bugs": 10,
    "verified_fixed": 8,
    "still_open": 2,
    "new_issues": 1
  },
  "bug_results": [
    {
      "bug_id": "BUG_001",
      "title": "登录失败",
      "verification_result": "fixed",
      "screenshot": "screenshots/BUG_001_verified.png"
    },
    {
      "bug_id": "BUG_002",
      "title": "数据丢失",
      "verification_result": "still_open",
      "notes": "问题仍然存在，需要继续修复"
    }
  ],
  "new_issues": [
    {
      "bug_id": "BUG_NEW_002",
      "title": "回归测试发现新问题",
      "severity": "Minor"
    }
  ]
}
```

---

## 调度策略

### 任务分解原则

1. **按测试类型分组**
   - 单元测试 → 单元测试 Agent
   - API 测试 → 集成测试 Agent
   - 功能测试 → 黑盒测试 Agent
   - E2E 测试 → UI 自动化 Agent

2. **按优先级排序**
   - P0 用例优先执行
   - 阻塞性问题优先验证

3. **按依赖关系排序**
   - 无依赖任务并行执行
   - 有依赖任务串行执行

### 并行执行策略

```
┌─────────────────────────────────────────────────────────────────┐
│                      并行执行策略                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  策略1: 全并行 (推荐)                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 所有 Agent 同时启动，互不依赖                           │   │
│  │                                                         │   │
│  │ 单元 ████████████████                                  │   │
│  │ 集成 ████████████████████████                          │   │
│  │ 黑盒 ████████████████████████████████                  │   │
│  │ UI   ████████████████████████████████████████          │   │
│  │      │                                    │             │   │
│  │      开始                                完成           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  策略2: 分阶段并行                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 先执行单元测试，通过后再并行执行其他测试                │   │
│  │                                                         │   │
│  │ 阶段1: 单元 ████████                                   │   │
│  │ 阶段2: 集成 ████████████████                           │   │
│  │        黑盒 ████████████████████████                   │   │
│  │        UI   ████████████████████████████████           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  策略3: 优先级并行                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ P0 用例优先执行，P1/P2 用例后续执行                    │   │
│  │                                                         │   │
│  │ P0用例: 单元P0 ████  集成P0 ████  UI-P0 ████████      │   │
│  │ P1用例:              集成P1 ████████  UI-P1 ████████  │   │
│  │ P2用例:                              黑盒P2 ████████  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 资源分配

| Agent 类型 | CPU 占用 | 内存占用 | 并发建议 |
|------------|----------|----------|----------|
| 单元测试 | 低 | 低 | 可多实例 |
| 集成测试 | 中 | 中 | 2-3 实例 |
| 黑盒测试 | 低 | 低 | 1 实例 |
| UI 自动化 | 高 | 高 | 1-2 实例 |

---

## 结果汇总

### 汇总流程

```
┌─────────────────────────────────────────────────────────────────┐
│                      结果汇总流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 等待所有 Agent 完成                                         │
│     └── 设置超时时间，超时则标记为失败                         │
│                                                                 │
│  2. 收集各 Agent 结果                                           │
│     ├── 单元测试结果                                           │
│     ├── 集成测试结果                                           │
│     ├── 黑盒测试结果                                           │
│     └── UI 自动化结果                                          │
│                                                                 │
│  3. 合并统计数据                                                │
│     ├── 总用例数 = Σ 各 Agent 用例数                          │
│     ├── 总通过数 = Σ 各 Agent 通过数                          │
│     ├── 总失败数 = Σ 各 Agent 失败数                          │
│     └── 总通过率 = 总通过数 / 总用例数                        │
│                                                                 │
│  4. 汇总 Bug 列表                                               │
│     └── 合并各 Agent 发现的 Bug                                │
│                                                                 │
│  5. 生成统一报告                                                │
│     └── 输出 test-report-v[x.x.x].md                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 汇总报告模板

```markdown
# 测试报告: [项目名称]
# 版本: v[x.x.x]

## 执行概览
| 项目 | 值 |
|------|-----|
| 执行模式 | 多 Agent 并行 |
| Agent 数量 | 4 |
| 总耗时 | [n] 分钟 |
| 效率提升 | [n]% |

## Agent 执行结果

### 单元测试 Agent
| 指标 | 值 |
|------|-----|
| 用例数 | [n] |
| 通过 | [n] |
| 失败 | [n] |
| 耗时 | [n] 分钟 |

### 集成测试 Agent
| 指标 | 值 |
|------|-----|
| 用例数 | [n] |
| 通过 | [n] |
| 失败 | [n] |
| 耗时 | [n] 分钟 |

### 黑盒测试 Agent
| 指标 | 值 |
|------|-----|
| 用例数 | [n] |
| 通过 | [n] |
| 失败 | [n] |
| 耗时 | [n] 分钟 |

### UI 自动化 Agent
| 指标 | 值 |
|------|-----|
| 用例数 | [n] |
| 通过 | [n] |
| 失败 | [n] |
| 耗时 | [n] 分钟 |

## 汇总统计
| 测试类型 | 用例数 | 通过 | 失败 | 通过率 |
|----------|--------|------|------|--------|
| 单元测试 | [n] | [n] | [n] | [%] |
| 集成测试 | [n] | [n] | [n] | [%] |
| 黑盒测试 | [n] | [n] | [n] | [%] |
| UI自动化 | [n] | [n] | [n] | [%] |
| **总计** | [n] | [n] | [n] | [%] |

## 发现的 Bug
[汇总各 Agent 发现的 Bug]
```

---

## 错误处理

### Agent 执行失败

| 失败类型 | 处理方式 |
|----------|----------|
| 超时 | 标记为失败，记录已完成部分 |
| 环境错误 | 重试一次，仍失败则跳过 |
| 用例错误 | 记录错误，继续执行其他用例 |
| 系统崩溃 | 终止该 Agent，不影响其他 Agent |

### 重试机制

```python
# 重试配置
RETRY_CONFIG = {
    "max_retries": 2,
    "retry_delay": 30,  # 秒
    "retry_on": ["timeout", "connection_error"]
}
```

---

## 最佳实践

1. **合理分配任务**
   - 根据用例数量均衡分配
   - 避免单个 Agent 负载过重

2. **设置合理超时**
   - 单元测试: 30 分钟
   - 集成测试: 60 分钟
   - UI 自动化: 120 分钟

3. **监控执行状态**
   - 实时查看各 Agent 进度
   - 及时发现和处理问题

4. **结果及时汇总**
   - Agent 完成后立即收集结果
   - 避免结果丢失
