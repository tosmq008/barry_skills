# 树状测试用例模板

## 一、命名规则

### 1. 树节点 ID

| 节点层级 | 前缀 | 示例 |
|----------|------|------|
| 需求节点 | `REQ_` | `REQ_AUTH` |
| 能力节点 | `CAP_` | `CAP_LOGIN` |
| 场景节点 | `SCN_` | `SCN_LOGIN_SUCCESS` |

### 2. 叶子用例 ID

| 执行路径 | 前缀 | 示例 |
|----------|------|------|
| 单元测试 | `TC_UNIT_` | `TC_UNIT_AUTH_001` |
| 服务/API 集成测试 | `TC_INT_API_` | `TC_INT_API_AUTH_001` |
| 浏览器集成测试 | `TC_INT_UI_` | `TC_INT_UI_AUTH_001` |

> 禁止再使用 `TC_FUNC_*`。功能黑盒用例必须落在 `TC_INT_API_*` 或 `TC_INT_UI_*`。

### 3. 优先级定义

| 优先级 | 说明 | 执行要求 |
|--------|------|----------|
| P0 | 核心功能、发布阻塞 | 必须执行，必须通过 |
| P1 | 重要功能、主路径关键分支 | 必须执行 |
| P2 | 一般功能 | 建议执行 |
| P3 | 边缘功能、优化项 | 时间允许时执行 |

---

## 二、树状用例总表模板

```markdown
# 测试用例树: [项目名称]

## 文档信息
- 版本: 1.0
- 更新日期: [日期]
- 设计人: 测试专家
- 设计叶子总数: [n]

---

## 1. 需求树

### REQ_AUTH 用户认证

#### CAP_LOGIN 登录能力

##### SCN_LOGIN_SUCCESS 正常登录

| case_id | execution_route | black_box | priority | preconditions | expected_observable |
|---------|-----------------|-----------|----------|---------------|---------------------|
| TC_INT_API_AUTH_001 | INT_API | Yes | P0 | 用户已注册 | 返回 200、token、生效的会话 |
| TC_INT_UI_AUTH_001 | INT_UI | Yes | P0 | 浏览器可访问登录页 | 登录成功并跳转首页 |

##### SCN_LOGIN_INVALID_PASSWORD 密码错误

| case_id | execution_route | black_box | priority | preconditions | expected_observable |
|---------|-----------------|-----------|----------|---------------|---------------------|
| TC_INT_API_AUTH_002 | INT_API | Yes | P0 | 用户已注册 | 返回 401 与错误消息 |
| TC_INT_UI_AUTH_002 | INT_UI | Yes | P0 | 浏览器可访问登录页 | 页面展示错误提示且不跳转 |

#### CAP_PASSWORD_RULE 密码规则

##### SCN_PASSWORD_TOO_SHORT 密码长度不足

| case_id | execution_route | black_box | priority | preconditions | expected_observable |
|---------|-----------------|-----------|----------|---------------|---------------------|
| TC_UNIT_AUTH_001 | UNIT | No | P1 | 密码校验函数可调用 | 返回长度不足错误 |
| TC_INT_API_AUTH_003 | INT_API | Yes | P1 | 注册接口可访问 | 返回 400 与字段错误 |
```

---

## 三、单个叶子用例模板

```markdown
# 叶子用例: TC_[ROUTE]_[MODULE]_[编号]

## 基本信息
| 字段 | 值 |
|------|-----|
| case_id | TC_[ROUTE]_[MODULE]_[编号] |
| case_path | REQ_[...] > CAP_[...] > SCN_[...] > TC_[...] |
| execution_route | UNIT / INT_API / INT_UI |
| black_box | Yes / No |
| persona_mode | Standard / Novice |
| ecosystem_mode | None / Parallel |
| priority | P0 / P1 / P2 / P3 |
| owner_node | SCN_[...] |
| module | [模块名] |

## 前置条件
- [条件 1]
- [条件 2]

## 输入 / 测试数据
| 项目 | 值 | 说明 |
|------|----|------|
| [字段] | [值] | [说明] |

## 执行步骤
| 步骤 | 操作 | 输入 |
|------|------|------|
| 1 | [操作] | [输入] |
| 2 | [操作] | [输入] |
| 3 | [操作] | [输入] |

## 预期外部可观察结果
- [可观察结果 1]
- [可观察结果 2]

## 执行记录
| 字段 | 值 |
|------|-----|
| executed_at | [日期时间] |
| executor | [执行人 / Agent] |
| actual_result | [实际观察结果] |
| status | Pass / Fail / Blocked / Not Executed / Skipped |
| evidence | [日志 / 截图 / trace 路径] |
| linked_bug | [Bug ID，如有] |
```

---

## 四、浏览器集成用例补充模板

> `INT_UI` 叶子必须记录关键操作步骤，并能映射到 Playwright。

~~~~markdown
# 浏览器集成叶子用例: TC_INT_UI_[MODULE]_[编号]

## 基本信息
| 字段 | 值 |
|------|-----|
| case_id | TC_INT_UI_[MODULE]_[编号] |
| case_path | REQ_[...] > CAP_[...] > SCN_[...] > TC_INT_UI_[...] |
| execution_route | INT_UI |
| black_box | Yes |
| page | [页面或入口 URL] |

## 操作步骤

### Step 1: [步骤标题]
- 操作: [操作描述]
- 元素定位: `[data-testid="xxx"]`
- 输入: [输入值]
- 预期: [步骤级可观察结果]

### Step 2: [步骤标题]
- 操作: [操作描述]
- 元素定位: `[data-testid="xxx"]`
- 输入: [输入值]
- 预期: [步骤级可观察结果]

## 最终预期结果
- [最终结果 1]
- [最终结果 2]

## Playwright 对应代码
```typescript
test('TC_INT_UI_[MODULE]_[编号]: [用例名称]', async ({ page }) => {
  await page.goto('[URL]');
  await page.fill('[data-testid="xxx"]', '[输入]');
  await page.click('[data-testid="submit"]');
  await expect(page.locator('[data-testid="result"]')).toBeVisible();
});
```
~~~~

---

## 五、小白用户使用测试模板

> `小白用户使用测试` 是特殊黑盒验收场景，默认走 `INT_UI`。

~~~~markdown
# 小白用户使用测试: TC_INT_UI_[MODULE]_[编号]

## 基本信息
| 字段 | 值 |
|------|-----|
| case_id | TC_INT_UI_[MODULE]_[编号] |
| case_path | REQ_[...] > CAP_[...] > SCN_NOVICE_[...] > TC_INT_UI_[...] |
| execution_route | INT_UI |
| black_box | Yes |
| persona_mode | Novice |
| user_profile | 第一次接触产品、不了解术语、不熟悉流程 |

## 起始约束
- 从真实零上下文入口开始
- 不允许跳过引导信息
- 不允许预先知道隐藏路径
- 不允许使用开发者说明补充理解

## 用户任务
- 任务目标: [例如：首次登录并创建第一个项目]
- 成功标准: [例如：无需他人解释即可完成]

## 观察点
| 观察项 | 记录要求 |
|--------|----------|
| 是否知道从哪里开始 | 记录是否能找到首个入口 |
| 是否理解页面文案 | 记录是否出现术语理解障碍 |
| 是否知道下一步做什么 | 记录是否发生停顿或误操作 |
| 是否理解结果反馈 | 记录成功/失败提示是否清晰 |

## 执行步骤
| 步骤 | 用户动作 | 预期 |
|------|----------|------|
| 1 | 从首页开始浏览 | 能找到主要入口 |
| 2 | 尝试完成首个操作 | 无需额外解释也能继续 |
| 3 | 完成任务并确认结果 | 能理解结果状态 |

## 验收记录
| 字段 | 值 |
|------|-----|
| can_finish_independently | Yes / No |
| blockers | [主要阻塞点] |
| acceptance_result | 可被小白用户独立完成 / 需引导后可完成 / 当前不可验收 |
| evidence | [截图 / trace / 录像 / 日志] |
~~~~

---

## 六、多用户生态动态串联黑盒测试模板

> `多个用户并行使用，生态动态串联的黑盒测试` 是特殊黑盒验收场景，默认以 `INT_UI` 为主，必要时补 `INT_API`。

~~~~markdown
# 多用户生态动态串联黑盒测试: TC_INT_UI_[MODULE]_[编号]

## 基本信息
| 字段 | 值 |
|------|-----|
| case_id | TC_INT_UI_[MODULE]_[编号] |
| case_path | REQ_[...] > CAP_[...] > SCN_ECO_[...] > TC_INT_UI_[...] |
| execution_route | INT_UI / INT_API |
| black_box | Yes |
| ecosystem_mode | Parallel |
| participant_roles | [角色A] / [角色B] / [角色C] |

## 生态起点
- 角色 A 初始状态: [状态]
- 角色 B 初始状态: [状态]
- 平台 / 系统初始状态: [状态]

## 链路目标
- 目标闭环: [例如：买家下单 -> 卖家接单 -> 平台通知 -> 买家看到更新]
- 成功标准: [例如：多角色无需人工修正即可完成闭环]

## 并行 / 交错动作
| 阶段 | 参与角色 | 动作 | 预期联动结果 |
|------|----------|------|--------------|
| 1 | 角色A | [动作] | 角色B / 平台可观察到变化 |
| 2 | 角色B | [动作] | 角色A / 平台可观察到变化 |
| 3 | 平台 | [状态同步 / 推送] | 全链路闭环 |

## 观察点
| 观察项 | 记录要求 |
|--------|----------|
| 状态同步 | 不同角色看到的状态是否一致 |
| 时序联动 | 上游动作是否驱动下游变化 |
| 权限隔离 | 角色是否只看到应见信息 |
| 反馈闭环 | 每个角色是否收到正确反馈 |

## 验收记录
| 字段 | 值 |
|------|-----|
| participant_roles | [角色列表] |
| key_linkage | [关键联动链路] |
| blockers | [主要阻塞点] |
| acceptance_result | 生态链路可稳定闭环 / 需约束条件后可闭环 / 当前不可验收 |
| evidence | [多窗口录像 / 截图 / trace / 日志] |
~~~~

---

## 七、统计与回写模板

```markdown
## 场景树回写
| case_path | execution_route | status | linked_bug | evidence |
|-----------|-----------------|--------|------------|----------|
| REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS > TC_INT_API_AUTH_001 | INT_API | Pass | - | logs/int-api-auth-001.txt |
| REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS > TC_INT_UI_AUTH_001 | INT_UI | Fail | BUG_001 | playwright-report/... |

## 父节点汇总
| node_path | leaf_total | executed | passed | failed | blocked |
|-----------|------------|----------|--------|--------|---------|
| REQ_AUTH > CAP_LOGIN > SCN_LOGIN_SUCCESS | 2 | 2 | 1 | 1 | 0 |

## 小白用户验收结论
| node_path | can_finish_independently | blockers | acceptance_result |
|-----------|--------------------------|----------|-------------------|
| REQ_ONBOARDING > CAP_FIRST_USE > SCN_NOVICE_FIRST_LOGIN_AND_CREATE | No | 找不到创建入口 | 需引导后可完成 |

## 多用户生态验收结论
| node_path | participant_roles | key_linkage | blockers | acceptance_result |
|-----------|-------------------|-------------|----------|-------------------|
| REQ_MARKETPLACE > CAP_ORDER_MATCH > SCN_ECO_MULTI_USER_ORDER_FLOW | 买家 / 卖家 / 平台 | 买家下单 -> 卖家接单 -> 平台通知 | 状态刷新延迟 | 需约束条件后可闭环 |
```

---

## 八、检查清单

- [ ] 用例是树状结构，不是平铺列表
- [ ] 需求节点、能力节点、场景节点语义清晰
- [ ] 所有叶子都有唯一 `case_path`
- [ ] 功能黑盒叶子全部映射到 `INT_API` 或 `INT_UI`
- [ ] 没有 `TC_FUNC_*`
- [ ] 叶子都有可观察结果
- [ ] 执行结果只写在叶子节点
- [ ] 父节点只做汇总，不直接标记 Pass / Fail
- [ ] `SCN_NOVICE_*` 场景从零上下文入口开始
- [ ] `SCN_NOVICE_*` 叶子包含验收结论
- [ ] `SCN_ECO_*` 场景包含至少 2 个参与角色
- [ ] `SCN_ECO_*` 叶子包含并行 / 交错动作与生态验收结论
