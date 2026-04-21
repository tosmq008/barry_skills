# 多 Agent 调度指南

## 概述

`tech-manager` 的职责不是直接写代码，而是在 **PRD + 架构方案** 的约束下组织实施。标准链路如下：

```text
product-expert -> system-architect -> tech-manager -> experts -> test-expert
```

如果架构边界不清晰，`tech-manager` 必须先暂停实施并回流 `system-architect`，而不是带着不确定性硬拆任务。

## 角色分工

| 角色 | 主要职责 | 输入 | 输出 |
|------|----------|------|------|
| `product-expert` | 输出产品需求与结构化 PRD | 业务需求 | `docs/prd/...` |
| `system-architect` | 架构评审、架构设计、架构调整 | PRD、现有系统 | `docs/architecture/...` |
| `tech-manager` | 实施前检查、任务拆分、调度、联调、交付 | PRD + 架构文档 | `docs/dev/...` |
| `client-expert` | iOS、Android、Flutter、小程序、混合壳实现 | 客户端任务单 | 代码与自测结果 |
| `frontend-expert` | Web Client、Admin、Operation、H5 实现 | 前端任务单 | 代码与自测结果 |
| `python-expert` | API、服务、数据模型、业务逻辑实现 | 后端任务单 | 代码、测试、接口更新 |
| `test-expert` | 功能、集成、回归与多端一致性验收 | 测试任务单 | 测试报告、Bug 列表 |

## 调度前硬性检查

在发出任何任务单前，`tech-manager` 必须先回答以下问题：

1. 当前需求是否已经过架构关卡？
2. API 契约是否已有唯一可信来源？
3. 数据模型是否已经明确？
4. 技术栈、认证、部署、数据库是否属于稳定约束？
5. 是否存在需要先回流 `system-architect` 的结构性问题？

任一问题答案不明确，都不应直接进入实现调度。

## 架构回流规则

出现以下情况时，停止专家开发并回流 `system-architect`：

- 新增或重构核心服务边界
- 现有 API 契约无法覆盖需求
- 数据模型、索引、关系设计明显不足
- 认证或权限方案需要变化
- 部署方式或基础设施假设发生变化
- 前后端、客户端与后端对同一能力的系统边界理解不一致

## 平台路由规则

| 输入场景 | 调度对象 | 备注 |
|----------|----------|------|
| Client 端为 Web（Vue/React） | `frontend-expert` | Web Client 视为前端端 |
| Admin / Operation | `frontend-expert` | 后台和运营端统一归前端 |
| iOS / Android 原生 | `client-expert` | 原生端交给客户端专家 |
| Flutter / 小程序 | `client-expert` | 跨平台和小程序交给客户端专家 |
| 混合方案（原生壳 + WebView/H5） | `client-expert` + `frontend-expert` | 壳、桥接、H5 拆分协作 |
| API / 数据库 / 业务逻辑 | `python-expert` | 后端统一归后端专家 |

## 调度批次建议

### 批次 A：可并行的无依赖任务

- 静态页面与基础组件
- 后端基础工程与数据模型骨架
- 本地 Mock 与测试桩
- 不依赖真实联调的页面布局与交互壳

### 批次 B：受契约约束的实现任务

- API 真实对接
- 认证与权限联通
- 数据写入与查询逻辑
- 混合方案的 JSBridge 与容器能力

### 批次 C：联调与收尾

- 多端一致性校验
- 错误处理与边界场景
- 回归修复
- 提交测试验收

## 任务单最小字段

发给任意专家的任务单，至少包含以下字段：

- 任务 ID
- 项目路径与分支
- 来源 PRD
- 来源架构文档
- 当前范围与优先级
- 不可变更架构约束
- 功能清单 / 接口清单 / 数据模型
- 依赖关系
- 验收标准
- 输出要求

## 输出结果约定

建议各专家回传统一结构的信息，便于 `tech-manager` 汇总：

```json
{
  "task_id": "TASK_FE_001",
  "agent_type": "frontend",
  "status": "completed",
  "blocked_by": [],
  "changed_files": ["src/pages/Login.vue"],
  "verified_items": ["AC-001", "AC-002"],
  "open_risks": []
}
```

如果未完成，必须明确：
- 阻塞点是什么
- 属于实现问题还是架构问题
- 需要谁来继续处理

## 调度后的职责

`tech-manager` 在调度后继续负责：
- 维护任务依赖顺序
- 识别阻塞属于实现还是架构
- 推动接口、数据、认证等跨角色对齐
- 组织联调和测试
- 汇总完成报告
