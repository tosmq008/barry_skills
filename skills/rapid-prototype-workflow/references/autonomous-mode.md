# 自动化持续开发模式

## 核心机制

Skill 内部通过 **状态文件** 实现持续开发：

```
.dev-state/
├── current-phase.txt      # 当前阶段 (1-4)
├── current-task.txt       # 当前任务
├── completed-tasks.txt    # 已完成任务列表
├── blocked-tasks.txt      # 阻塞任务及原因
└── dev-log.txt            # 开发日志
```

---

## 启动持续开发

### 用户指令

```
使用 rapid-prototype-workflow skill 进行持续开发：

项目名称: [项目名]
项目需求: [一句话描述]

启动自动化开发模式，持续工作直到完成。
```

### AI 执行流程

```
┌─────────────────────────────────────────────────────────────┐
│                    持续开发执行流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 检查状态文件                                             │
│     ├── 存在 → 读取状态，从断点继续                          │
│     └── 不存在 → 初始化状态，从 Phase 1 开始                 │
│                                                             │
│  2. 执行当前任务                                             │
│     ├── 任务粒度控制（单任务 < 10分钟）                      │
│     ├── 完成后更新状态文件                                   │
│     └── 自动进入下一个任务                                   │
│                                                             │
│  3. 阶段完成检查                                             │
│     ├── 当前阶段所有任务完成 → 进入下一阶段                  │
│     └── 所有阶段完成 → 输出完成报告                          │
│                                                             │
│  4. 异常处理                                                 │
│     ├── 任务阻塞 → 记录到 blocked-tasks.txt，跳过            │
│     └── 上下文过长风险 → 保存状态，提示用户开新会话          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## AI 必须遵守的持续开发规则

### 规则 1: 每次对话开始时检查状态

```markdown
【持续开发检查】
1. 检查 .dev-state/ 目录是否存在
2. 如果存在，读取 current-phase.txt 和 current-task.txt
3. 从断点继续执行
4. 如果不存在，初始化状态文件
```

### 规则 2: 任务粒度控制

```markdown
【任务粒度】
- 单个任务执行时间 < 10 分钟
- 每完成一个任务立即更新状态文件
- 避免在一次对话中执行过多任务

【任务拆分示例】
❌ 错误: "实现整个 Client 端"
✅ 正确: 
  - "实现 Client Backend 用户模型"
  - "实现 Client Backend 登录 API"
  - "实现 Client Frontend 登录页面"
```

### 规则 3: 状态文件必须实时更新

```markdown
【状态更新时机】
- 开始任务前: 更新 current-task.txt
- 完成任务后: 追加到 completed-tasks.txt
- 遇到阻塞: 记录到 blocked-tasks.txt
- 每个操作: 追加到 dev-log.txt
```

### 规则 4: 上下文长度自我监控

```markdown
【上下文监控】
当感知到以下情况时，主动保存状态并提示用户：
- 已执行超过 5 个任务
- 对话轮次超过 20 轮
- 生成的代码量超过 500 行

提示格式:
"⚠️ 建议开启新会话继续开发。当前进度已保存到 .dev-state/，
请发送 '继续开发' 指令恢复。"
```

---

## 状态文件格式

### .dev-state/current-phase.txt

```
3
```

### .dev-state/current-task.txt

```
3.5 实现 Client Frontend 核心页面
```

### .dev-state/completed-tasks.txt

```
[2024-01-31 10:00] 1.1 创建项目简介
[2024-01-31 10:15] 1.2 创建功能架构图
[2024-01-31 10:30] 1.3 创建系统角色定义
...
[2024-01-31 14:00] 3.4 实现 Client Frontend 页面框架
```

### .dev-state/blocked-tasks.txt

```
[2024-01-31 12:00] 2.3 创建 Website UI 设计稿
原因: MCP Pencil 连接失败
建议: 检查 MCP 配置后重试
```

### .dev-state/dev-log.txt

```
[2024-01-31 10:00] 开始 Phase 1: PRD 文档
[2024-01-31 10:00] 执行任务 1.1 创建项目简介
[2024-01-31 10:05] 完成任务 1.1，输出: docs/prd/01-project-brief.md
[2024-01-31 10:05] 执行任务 1.2 创建功能架构图
...
```

---

## 任务清单模板

### Phase 1: PRD 文档 (8 个任务)

```
1.1 创建项目简介 → docs/prd/01-project-brief.md
1.2 创建功能架构图 → docs/prd/02-feature-architecture.md
1.3 创建系统角色定义 → docs/prd/03-role-definition.md
1.4 创建功能模块划分 → docs/prd/04-module-design.md
1.5 创建交互页面清单 → docs/prd/05-page-list.md
1.6 创建页面跳转关系 → docs/prd/06-page-navigation.md
1.7 创建页面交互操作 → docs/prd/07-page-interaction.md
1.8 创建视觉风格规范 → docs/prd/08-visual-style.md
```

### Phase 2: UI 设计 (8 个任务)

```
2.1 创建 Client 端 UI 设计稿
2.2 创建 Admin 端 UI 设计稿
2.3 创建 Website 官网 UI 设计稿
2.4 执行 UI Review Round 1 (商业分析师)
2.5 执行 UI Review Round 2 (领域产品经理)
2.6 执行 UI Review Round 3 (资深产品经理)
2.7 执行 UI Review Round 4 (UED设计专家)
2.8 执行 UI Review Round 5 (小白用户)
```

### Phase 3: 代码实现 (10 个任务)

```
3.1 初始化项目结构和目录
3.2 实现 Client Backend 数据模型
3.3 实现 Client Backend API 接口
3.4 实现 Client Frontend 页面框架
3.5 实现 Client Frontend 核心页面
3.6 实现 Admin Backend 数据模型和 API
3.7 实现 Admin Frontend 页面
3.8 实现 Website 静态页面
3.9 使用 frontend-design skill 优化 Website
3.10 创建启动脚本 start.sh/stop.sh
```

### Phase 4: 测试发布 (6 个任务)

```
4.1 编写 Client Backend 单元测试
4.2 编写 Admin Backend 单元测试
4.3 执行集成测试
4.4 执行功能测试
4.5 修复所有发现的 Bug
4.6 最终验收检查
```

---

## 继续开发指令

当用户发送以下指令时，AI 应从断点继续：

```
继续开发
```

或

```
恢复开发
```

或

```
继续 rapid-prototype-workflow
```

### AI 响应流程

```markdown
1. 读取 .dev-state/current-phase.txt 和 current-task.txt
2. 读取 .dev-state/completed-tasks.txt 了解已完成内容
3. 输出当前状态摘要
4. 继续执行当前任务
```

### 状态摘要输出格式

```markdown
📊 **开发状态恢复**

当前阶段: Phase 3 - 代码实现
当前任务: 3.5 实现 Client Frontend 核心页面
已完成: 20/32 任务 (62.5%)
阻塞任务: 1 个

继续执行任务 3.5...
```

---

## 完成报告

当所有任务完成时，输出完成报告：

```markdown
# 🎉 快速原型开发完成报告

## 项目信息
- 项目名称: [项目名]
- 开发时间: [开始时间] - [结束时间]
- 总任务数: 32
- 完成任务: 31
- 阻塞任务: 1

## 交付物清单

### 文档
- [x] docs/prd/ (8 个 PRD 文档)
- [x] docs/ui/[project].pen (UI 设计稿)
- [x] docs/api/api-spec.md (API 文档)

### 代码
- [x] client/frontend/ (用户前端)
- [x] client/backend/ (用户后端)
- [x] admin/frontend/ (管理前端)
- [x] admin/backend/ (管理后端)
- [x] website/ (官网静态页面)

### 脚本
- [x] start.sh / stop.sh

## 启动方式
\`\`\`bash
./start.sh
\`\`\`

## 访问地址
- Client: http://localhost:3000
- Admin: http://localhost:3001
- Website: http://localhost:4000
- API Docs: http://localhost:8000/docs

## 阻塞任务（需手动处理）
- 2.3 创建 Website UI 设计稿 - MCP Pencil 连接失败
```

---

## 异常处理

### 上下文过长预警

当 AI 感知到上下文可能过长时：

```markdown
⚠️ **上下文长度预警**

当前已执行 6 个任务，建议开启新会话继续开发。

**当前进度已保存:**
- 阶段: Phase 3
- 任务: 3.6 实现 Admin Backend
- 完成: 22/32 (68.75%)

**恢复方式:**
请在新会话中发送: `继续开发`
```

### 任务阻塞处理

```markdown
⚠️ **任务阻塞**

任务 2.3 创建 Website UI 设计稿 执行失败。
原因: MCP Pencil 工具不可用

**处理方式:**
1. 已记录到 .dev-state/blocked-tasks.txt
2. 跳过此任务，继续执行后续任务
3. 请稍后手动处理阻塞任务

继续执行任务 2.4...
```

---

## 最佳实践

| 实践 | 说明 |
|------|------|
| 状态优先 | 每次对话开始先检查 .dev-state/ |
| 小步快跑 | 单任务 < 10 分钟，频繁保存状态 |
| 主动预警 | 感知上下文过长时主动提示 |
| 跳过阻塞 | 遇到阻塞记录并跳过，不要卡住 |
| 完整日志 | 所有操作记录到 dev-log.txt |
