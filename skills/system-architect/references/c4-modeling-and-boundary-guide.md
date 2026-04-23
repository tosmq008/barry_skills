# C4 Modeling and Boundary Guide

## 目标

用最小且足够的 C4 抽象把系统讲清楚，而不是把图画得很大。

---

## 1. 先画哪一层

### 必须有
- Context
- Container

### 按需补
- Component：当容器内部职责复杂、边界不清、多人并行开发时
- Dynamic：当主路径或故障路径仅靠静态图解释不清时
- Deployment：当运行时拓扑、网络边界、环境差异会影响架构决策时

---

## 2. Context 层怎么画

回答 4 个问题：

1. System of Interest 是谁
2. 它服务谁
3. 它依赖谁
4. 哪些边界是高风险或高信任要求

### Context 图最少元素
- User / Actor
- External System
- System of Interest
- 关系箭头
- Trust boundary 注释

### 不要做的事
- 不要在 Context 图里塞 HTTP 路径、topic 名称、数据库表
- 不要用 Context 图代替容器图

---

## 3. Container 层怎么画

Container 不是 k8s container，而是**可独立部署或独立运行的执行边界**。

### 每个 Container 至少写清楚
- 它的主要责任
- 它拥有/缓存什么状态
- 它和谁通信
- 它怎么认证/鉴权
- 它怎么发布/扩容/回滚

### 常见 Container
- Web / BFF
- API service
- Worker / batch
- Message broker
- Database / cache / search
- Identity / policy engine

### 常见误区
- 把“模块”当 Container
- 把“数据库”漏掉
- 把第三方关键服务画成注脚而不是边界对象

---

## 4. Component 层什么时候值得画

满足任一条件就该画：
- 单个 Container 职责较重
- 关键路径跨多个内部模块
- 安全/审计/权限逻辑复杂
- 需要多人并行开发
- 测试与故障定位依赖内部边界

### Component 图关注
- 业务 orchestration
- policy / authorization
- domain service
- integration adapter
- persistence / event publisher

---

## 5. Dynamic View 什么时候需要

当以下任一问题出现时，必须补 dynamic/sequence 视图：
- 同步/异步混合
- 补偿、重试、降级逻辑复杂
- 读写分离、一致性策略关键
- 关键失败路径必须解释
- 发布/回滚/迁移依赖时序

### Dynamic View 最少要写
- Trigger
- Main path
- Error path
- Retry / timeout / fallback
- Observability hooks

---

## 6. Trust Boundary 画法

每个 boundary 至少说明：
- 边界两侧主体
- 认证方式
- 授权方式
- 审计要求
- 数据分类
- 可疑流量/滥用面

### 常见 boundary
- Internet -> Edge
- User tenant -> Platform
- Internal service -> privileged service
- Platform -> third-party
- Prod -> support / operations tooling

---

## 7. 命名与图示规范

### 推荐命名
- Container: `billing-api`, `risk-worker`, `identity-service`
- Component: `OrderPolicyEvaluator`, `SettlementPublisher`
- Flow: `CreateOrder`, `ApprovePayout`, `RotateKey`

### 图示规范
- 一张图只表达一个层次
- 图上的元素要能在 `docs/architecture/*.md` 中找到对应解释
- 图例与缩写要统一
- 高风险边界要显式标红/加注释

---

## 8. 自检清单

- Context 是否覆盖关键 actor 和外部系统
- Container 是否覆盖所有 deployable/runtime unit
- 是否标出 trust boundary
- 关键路径是否至少有 1 个 dynamic view 或 flow 文字说明
- 图中的所有元素是否都能映射到文档正文
