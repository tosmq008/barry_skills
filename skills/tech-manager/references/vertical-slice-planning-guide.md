# Vertical Slice Planning Guide

## 目标

按用户价值和可发布边界切交付，而不是按“前端/后端/数据库”拆成只能汇报、不能验收的伪任务。

---

## 1. 一个好切片的标准

一个切片至少要满足：

- 有清晰用户/运营/系统目标
- 能映射到一个或多个 UseCase / Story
- 能单独验证
- 能单独集成
- 最好能单独灰度或由开关控制
- 失败时回滚边界清楚

---

## 2. 先切什么

推荐顺序：

1. 风险最高的切片
2. 依赖最重但必须先打通的切片
3. 能形成端到端价值闭环的切片
4. 观察性 / 回滚 / 审计等支撑切片
5. Nice-to-have 切片

---

## 3. 切片类型

### 用户闭环切片
直接形成用户价值，例如：
- 注册并首次完成核心动作
- 提交订单并可查询状态
- 审核通过并触发通知

### 架构使能切片
为后续切片创造条件，例如：
- 身份与权限主链路
- 审计日志
- 事件总线 / outbox
- 监控 / 告警 / 灰度开关

### 发布安全切片
保障上线安全，例如：
- 回滚脚本
- 数据迁移验证
- hypercare dashboard
- feature flag skeleton

---

## 4. Cut Line

Cut line 用来处理“本来想做、但本次不纳入”的边界。

每次必须明确：
- Above cut line: 本次必须交付
- Below cut line: 可延后但已识别
- Frozen: 冻结后不接受新增需求
- Exception path: 谁能批准插队，条件是什么

---

## 5. Slice Detail 最少字段

- Slice ID
- Name
- Objective
- Included features / stories
- Dependency
- Validation method
- Release strategy
- Rollback scope
- Owner
- Exit criteria

---

## 6. 常见误区

- 按技术层硬拆，导致没有任何一个切片能单独验收
- 把“回滚 / 监控 / 开关”留到最后补
- 把依赖都写成“协作项”而不是阻塞项
- 每个切片都塞太多故事，变成 mini-release
