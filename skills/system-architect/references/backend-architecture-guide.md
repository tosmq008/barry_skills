# 后端架构设计指南

## 1. 服务架构设计

### 1.1 服务拆分策略

**拆分维度：**

| 维度 | 说明 | 示例 |
|------|------|------|
| 业务域 | 按业务领域拆分 | 用户服务、订单服务 |
| 数据域 | 按数据归属拆分 | 商品数据、交易数据 |
| 变更频率 | 按变更频率拆分 | 核心稳定服务、快速迭代服务 |
| 扩展需求 | 按扩展需求拆分 | 计算密集型、IO密集型 |

### 1.2 服务间通信

**同步通信：**
- REST API - 简单CRUD操作
- gRPC - 高性能服务间调用
- GraphQL - 灵活数据查询（BFF层）

**异步通信：**
- 消息队列 - 解耦/削峰/异步处理
- 事件总线 - 领域事件传播
- 定时任务 - 批量/定时处理

### 1.3 服务治理

| 治理能力 | 实现方式 | 说明 |
|----------|----------|------|
| 服务注册发现 | Nacos/Consul | 动态服务寻址 |
| 负载均衡 | 客户端/服务端 | 流量分发 |
| 熔断降级 | Sentinel/Resilience4j | 故障隔离 |
| 限流 | 令牌桶/滑动窗口 | 流量控制 |
| 重试 | 指数退避 | 瞬时故障恢复 |
| 超时控制 | 级联超时 | 避免资源耗尽 |

## 2. API 设计规范

### 2.1 RESTful 设计规范

**URL 设计：**
```
GET    /api/v1/users          # 列表查询
GET    /api/v1/users/:id      # 详情查询
POST   /api/v1/users          # 创建
PUT    /api/v1/users/:id      # 全量更新
PATCH  /api/v1/users/:id      # 部分更新
DELETE /api/v1/users/:id      # 删除
```

**查询参数规范：**
```
分页: ?page=1&page_size=20
排序: ?sort=-created_at,name
筛选: ?status=active&role=admin
搜索: ?q=keyword
字段选择: ?fields=id,name,email
```

### 2.2 接口版本管理

| 策略 | 方式 | 优劣 |
|------|------|------|
| URL版本 | /api/v1/, /api/v2/ | 简单直观，URL冗余 |
| Header版本 | Accept: application/vnd.api.v1+json | URL干净，不直观 |
| 参数版本 | ?version=1 | 简单，不够规范 |

## 3. 数据库设计规范

### 3.1 表设计规范

**必备字段：**
```sql
id          BIGINT PRIMARY KEY AUTO_INCREMENT,
created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
deleted_at  TIMESTAMP NULL DEFAULT NULL
```

**命名规范：**
- 表名：小写下划线，复数形式（users, order_items）
- 字段名：小写下划线（user_name, created_at）
- 索引名：idx_表名_字段名（idx_users_email）
- 唯一索引：uk_表名_字段名（uk_users_phone）

### 3.2 索引设计原则

1. 查询条件字段必须建索引
2. 联合索引遵循最左前缀原则
3. 避免在低基数字段上建索引
4. 覆盖索引优化高频查询
5. 避免过多索引影响写入性能

### 3.3 分库分表策略

| 策略 | 适用场景 | 分片键选择 | 注意事项 |
|------|----------|------------|----------|
| 垂直分库 | 业务域独立 | 按业务域 | 跨库事务 |
| 水平分表 | 单表数据量大 | 用户ID/时间 | 数据迁移 |
| 读写分离 | 读多写少 | - | 主从延迟 |

## 4. 缓存设计规范

### 4.1 缓存策略

| 策略 | 读流程 | 写流程 | 适用场景 |
|------|--------|--------|----------|
| Cache Aside | 先读缓存，Miss读DB回填 | 先写DB，再删缓存 | 通用场景 |
| Read Through | 缓存层自动加载 | 缓存层自动写入 | 读多写少 |
| Write Behind | 同Cache Aside | 先写缓存，异步写DB | 写多场景 |

### 4.2 缓存问题应对

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| 缓存穿透 | 查询不存在的数据 | 布隆过滤器/空值缓存 |
| 缓存击穿 | 热点Key过期 | 互斥锁/永不过期 |
| 缓存雪崩 | 大量Key同时过期 | 随机过期时间/多级缓存 |

## 5. 输出物清单

- 服务清单与职责定义
- API接口设计文档
- 数据库设计文档（DDL + 数据字典）
- 缓存设计方案
- 消息队列设计方案
- 服务治理方案
