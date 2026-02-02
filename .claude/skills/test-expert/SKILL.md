---
name: test-expert
description: "This skill enables comprehensive software testing as a QA expert. It analyzes PRD and technical documents to design test strategies, execute multiple test types (unit, integration, black-box, UI automation with Playwright), record bugs with reproduction steps and screenshots, and generate detailed test reports. It also identifies product gaps by comparing with industry standards and competitor products."
license: MIT
compatibility: "Requires Playwright for UI automation testing. Supports Python pytest, JavaScript/TypeScript testing frameworks. Works with any web application."
metadata:
  category: quality-assurance
  phase: testing
  version: "1.0.0"
allowed-tools: bash read_file write_file mcp playwright
---

# Test Expert Skill

作为测试专家，系统性地进行软件质量保障工作，从需求分析到测试执行再到报告生成的完整测试流程。

## When to Use

**适用场景：**
- 需要对系统进行全面测试
- 需要设计测试方案和测试用例
- 需要执行自动化测试（包括 UI 自动化）
- 需要生成测试报告和 Bug 记录
- 需要评审产品完整性和行业对标

**不适用：**
- 仅需要简单的代码检查
- 不涉及功能测试的代码审查

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      测试专家工作流程                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 需求分析          Phase 2: 测试设计                    │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 阅读 PRD        │  ──▶  │ 测试方案设计    │                  │
│  │ 阅读技术文档    │       │ 测试数据设计    │                  │
│  │ 了解功能交互    │       │ 测试用例设计    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│           │                         │                           │
│           ▼                         ▼                           │
│  Phase 3: 测试执行          Phase 4: 报告生成                    │
│  ┌─────────────────┐       ┌─────────────────┐                  │
│  │ 单元测试        │  ──▶  │ Bug 记录汇总    │                  │
│  │ 集成测试        │       │ 测试报告生成    │                  │
│  │ 黑盒测试        │       │ 产品评审建议    │                  │
│  │ UI 自动化测试   │       │ 行业对标分析    │                  │
│  └─────────────────┘       └─────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: 需求分析 (Requirement Analysis)

### 1.1 阅读 PRD 文档

**必须了解的内容：**
- 产品定位和目标用户
- 核心功能和业务流程
- 用户角色和权限设计
- 页面交互和状态流转
- 业务规则和边界条件

**分析输出：**
```markdown
# PRD 分析记录

## 产品概述
- 产品名称：[名称]
- 产品定位：[定位描述]
- 目标用户：[用户群体]

## 核心功能清单
| 模块 | 功能点 | 优先级 | 测试重点 |
|------|--------|--------|----------|
| [模块名] | [功能描述] | P0/P1/P2 | [测试关注点] |

## 业务流程梳理
- 主流程：[流程描述]
- 分支流程：[分支描述]
- 异常流程：[异常处理]

## 发现的问题/不完善之处
| 问题编号 | 问题描述 | 建议 |
|----------|----------|------|
| PRD_001 | [问题描述] | [改进建议] |
```

### 1.2 阅读技术实现文档

**必须了解的内容：**
- 系统架构设计
- API 接口定义
- 数据库设计
- 技术栈和依赖

### 1.3 了解功能交互

**必须了解的内容：**
- 页面跳转关系
- 用户操作流程
- 状态变化逻辑
- 错误处理机制

---

## Phase 2: 测试设计 (Test Design)

> ⚠️ **执行前必须读取 `references/test-plan-template.md` 获取完整测试方案模板**

### 2.1 测试方案设计

**测试方案必须包含：**

```markdown
# 测试方案: [项目名称]

## 1. 测试目标
- 验证功能正确性
- 验证业务流程完整性
- 验证异常处理能力
- 验证 UI 交互体验

## 2. 测试范围
| 测试类型 | 覆盖范围 | 工具 |
|----------|----------|------|
| 单元测试 | 核心业务逻辑 | pytest / jest |
| 集成测试 | API 接口 | pytest + requests |
| 黑盒测试 | 功能验证 | 手工 + 自动化 |
| UI 自动化 | 核心流程 | Playwright |

## 3. 测试环境
- 操作系统：[OS]
- 浏览器：Chrome / Firefox / Safari
- 后端环境：[环境描述]
- 测试数据库：[数据库]

## 4. 测试策略
- 冒烟测试：核心流程验证
- 功能测试：全功能覆盖
- 回归测试：Bug 修复验证
- 兼容性测试：多浏览器验证

## 5. 风险评估
| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| [风险描述] | [影响程度] | [措施] |
```

### 2.2 测试数据设计

> ⚠️ **执行前必须读取 `references/test-data-design.md` 获取测试数据设计规范**

**测试数据原则：**
- 独立性：每个用例使用独立数据
- 可重复性：数据可重复创建和清理
- 最小化：只创建必要的测试数据
- 真实性：数据符合业务规则

### 2.3 测试用例设计

> ⚠️ **执行前必须读取 `references/test-case-template.md` 获取测试用例模板**

**测试用例必须包含：**

| 字段 | 说明 | 必填 |
|------|------|------|
| 用例ID | 唯一标识 TC_[模块]_[编号] | ✅ |
| 用例名称 | 简洁描述测试目的 | ✅ |
| 测试类型 | 单元/集成/黑盒/UI自动化 | ✅ |
| 优先级 | P0/P1/P2 | ✅ |
| 前置条件 | 执行前必须满足的条件 | ✅ |
| 测试步骤 | 详细操作步骤 | ✅ |
| 预期结果 | 期望的输出或状态 | ✅ |
| 测试数据 | 使用的测试数据 | ✅ |
| 实际结果 | 执行后的实际结果 | 执行时填写 |
| 状态 | Pass/Fail/Block | 执行时填写 |

---

## Phase 3: 测试执行 (Test Execution)

### 3.1 单元测试

**执行要求：**
- 覆盖核心业务逻辑
- 覆盖边界条件
- 覆盖异常处理

**Python 示例：**
```python
# tests/unit/test_[module].py
import pytest
from src.[module] import [function]

class Test[Module]:
    """[模块名]单元测试"""
    
    def test_[function]_success(self):
        """TC_UNIT_001: [测试描述]"""
        # Arrange
        input_data = [...]
        
        # Act
        result = [function](input_data)
        
        # Assert
        assert result == expected
```

### 3.2 集成测试

**执行要求：**
- 覆盖所有 API 接口
- 验证接口参数校验
- 验证接口返回格式
- 验证接口业务逻辑

**Python 示例：**
```python
# tests/integration/test_api_[module].py
import pytest
from fastapi.testclient import TestClient

class TestAPI[Module]:
    """[模块名]API集成测试"""
    
    def test_[endpoint]_success(self, client, db_session):
        """TC_API_001: [测试描述]"""
        # Arrange
        request_data = {...}
        
        # Act
        response = client.post("/api/[endpoint]", json=request_data)
        
        # Assert
        assert response.status_code == 200
        assert response.json()["key"] == expected
```

### 3.3 黑盒测试

**执行要求：**
- 基于需求进行功能验证
- 不关注内部实现
- 关注输入输出正确性

**测试方法：**
- 等价类划分
- 边界值分析
- 错误推测
- 场景测试

### 3.4 UI 自动化测试 (Playwright)

> ⚠️ **UI 自动化测试必须使用 Playwright**
> ⚠️ **每个用例必须有详细的操作步骤记录**

**Playwright 测试示例：**
```typescript
// tests/e2e/[module].spec.ts
import { test, expect } from '@playwright/test';

test.describe('[模块名] UI 自动化测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 测试前置操作
    await page.goto('/');
  });
  
  test('TC_UI_001: [测试描述]', async ({ page }) => {
    /**
     * 测试步骤记录：
     * 1. 打开登录页面
     * 2. 输入用户名: test@example.com
     * 3. 输入密码: ******
     * 4. 点击登录按钮
     * 5. 验证跳转到首页
     */
    
    // Step 1: 打开登录页面
    await page.goto('/login');
    await expect(page).toHaveURL('/login');
    
    // Step 2: 输入用户名
    await page.fill('[data-testid="username"]', 'test@example.com');
    
    // Step 3: 输入密码
    await page.fill('[data-testid="password"]', 'password123');
    
    // Step 4: 点击登录按钮
    await page.click('[data-testid="login-btn"]');
    
    // Step 5: 验证跳转到首页
    await expect(page).toHaveURL('/home');
    await expect(page.locator('[data-testid="welcome"]')).toBeVisible();
  });
});
```

**Playwright 配置：**
```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
});
```

---

## Phase 4: Bug 记录与报告生成

> ⚠️ **执行前必须读取 `references/bug-report-template.md` 获取 Bug 记录模板**
> ⚠️ **执行前必须读取 `references/test-report-template.md` 获取测试报告模板**

### 4.1 Bug 记录规范

**Bug 记录必须包含：**

| 字段 | 说明 | 必填 |
|------|------|------|
| Bug ID | 唯一标识 BUG_[编号] | ✅ |
| 标题 | 简洁描述问题 | ✅ |
| 严重程度 | Critical/Major/Minor/Trivial | ✅ |
| 优先级 | P0/P1/P2/P3 | ✅ |
| 所属模块 | 功能模块 | ✅ |
| 复现步骤 | 详细操作步骤 | ✅ |
| 预期结果 | 期望的正确行为 | ✅ |
| 实际结果 | 实际观察到的行为 | ✅ |
| 截图/录屏 | 问题截图或录屏 | ✅ |
| 复现环境 | 浏览器、OS、账号等 | ✅ |
| 测试数据 | 复现时使用的数据 | ✅ |
| 关联用例 | 关联的测试用例ID | 可选 |

**Bug 记录示例：**
```markdown
## BUG_001: 登录页面密码输入框未做长度限制

### 基本信息
- 严重程度：Minor
- 优先级：P2
- 所属模块：用户认证
- 发现日期：2024-01-15
- 发现人：测试专家

### 复现步骤
1. 打开登录页面 http://localhost:3000/login
2. 在用户名输入框输入：test@example.com
3. 在密码输入框输入超过100个字符的密码
4. 点击登录按钮

### 预期结果
- 密码输入框应限制最大长度（如32位）
- 超出长度时应有提示

### 实际结果
- 密码输入框无长度限制
- 可输入任意长度字符串

### 截图
![bug_001_screenshot](./screenshots/bug_001.png)

### 复现环境
- 浏览器：Chrome 120.0.6099.109
- 操作系统：macOS 14.2
- 测试账号：test@example.com
- 测试数据：密码 "a" * 200
```

### 4.2 测试报告生成

**测试报告结构：**

```markdown
# 测试报告: [项目名称]

## 1. 报告概述
- 项目名称：[名称]
- 测试版本：[版本号]
- 测试周期：[开始日期] - [结束日期]
- 测试负责人：测试专家

## 2. 测试范围
| 测试类型 | 用例数 | 通过 | 失败 | 阻塞 | 通过率 |
|----------|--------|------|------|------|--------|
| 单元测试 | [n] | [n] | [n] | [n] | [%] |
| 集成测试 | [n] | [n] | [n] | [n] | [%] |
| 黑盒测试 | [n] | [n] | [n] | [n] | [%] |
| UI自动化 | [n] | [n] | [n] | [n] | [%] |
| **总计** | [n] | [n] | [n] | [n] | [%] |

## 3. Bug 统计
| 严重程度 | 数量 | 已修复 | 待修复 |
|----------|------|--------|--------|
| Critical | [n] | [n] | [n] |
| Major | [n] | [n] | [n] |
| Minor | [n] | [n] | [n] |
| Trivial | [n] | [n] | [n] |

## 4. Bug 详情列表
[详细 Bug 记录]

## 5. 测试用例执行详情
[测试用例表格]

## 6. PRD 问题与建议
[PRD 分析中发现的问题]

## 7. 行业对标分析
[与同类产品对比分析]

## 8. 测试结论
- 测试通过率：[%]
- 遗留问题：[数量]
- 发布建议：[建议]

## 9. 附件
- 测试用例表格
- Bug 截图
- 测试日志
```

---

## Phase 5: 产品评审与行业对标

### 5.1 产品完整性评审

**评审维度：**

| 维度 | 检查项 |
|------|--------|
| 功能完整性 | 核心功能是否完整 |
| 用户体验 | 交互是否流畅 |
| 异常处理 | 错误提示是否友好 |
| 安全性 | 基本安全措施是否到位 |
| 性能 | 响应速度是否可接受 |

### 5.2 行业对标分析

**对标内容：**
- 同类型产品功能对比
- 行业标准功能清单
- 用户体验最佳实践
- 缺失功能建议

**输出格式：**
```markdown
# 行业对标分析报告

## 1. 对标产品
| 产品名称 | 类型 | 特点 |
|----------|------|------|
| [产品A] | [类型] | [特点] |
| [产品B] | [类型] | [特点] |

## 2. 功能对比
| 功能点 | 本产品 | 产品A | 产品B | 行业标准 |
|--------|--------|-------|-------|----------|
| [功能1] | ✅/❌ | ✅/❌ | ✅/❌ | 必备/可选 |

## 3. 缺失功能建议
| 功能 | 重要性 | 建议 |
|------|--------|------|
| [功能] | 高/中/低 | [建议] |

## 4. 改进建议
[综合改进建议]
```

---

## Test Case Summary Table

> ⚠️ **所有测试用例必须汇总到测试用例表格中**

**测试用例汇总表格式：**

| 用例ID | 用例名称 | 类型 | 优先级 | 前置条件 | 测试步骤 | 预期结果 | 实际结果 | 状态 |
|--------|----------|------|--------|----------|----------|----------|----------|------|
| TC_UNIT_001 | [名称] | 单元 | P0 | [条件] | [步骤] | [预期] | [实际] | Pass/Fail |
| TC_API_001 | [名称] | 集成 | P0 | [条件] | [步骤] | [预期] | [实际] | Pass/Fail |
| TC_FUNC_001 | [名称] | 黑盒 | P1 | [条件] | [步骤] | [预期] | [实际] | Pass/Fail |
| TC_UI_001 | [名称] | UI自动化 | P0 | [条件] | [步骤] | [预期] | [实际] | Pass/Fail |

---

## Output Files

| 文件 | 路径 | 说明 |
|------|------|------|
| 测试方案 | `docs/test/test-plan.md` | 测试策略和方案 |
| 测试用例 | `docs/test/test-cases.md` | 测试用例汇总表 |
| Bug 记录 | `docs/test/bug-list.md` | Bug 详情列表 |
| 测试报告 | `docs/test/test-report.md` | 完整测试报告 |
| 行业对标 | `docs/test/benchmark-analysis.md` | 行业对标分析 |
| 截图目录 | `docs/test/screenshots/` | Bug 截图 |

---

## References

| 文档 | 用途 |
|------|------|
| `references/test-plan-template.md` | 测试方案模板 |
| `references/test-case-template.md` | 测试用例模板 |
| `references/test-data-design.md` | 测试数据设计规范 |
| `references/bug-report-template.md` | Bug 记录模板 |
| `references/test-report-template.md` | 测试报告模板 |
| `references/playwright-guide.md` | Playwright 使用指南 |
| `references/benchmark-checklist.md` | 行业对标检查清单 |

## Related Skills

- `prd-review` - PRD 评审
- `development-workflow` - 开发工作流
- `bug-fix-task-split` - Bug 修复任务拆分
