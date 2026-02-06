# AI 编程工具约定 (Conventions)

> 基于 rapid-prototype-workflow 整理的 AI 编程助手工作约定

本目录包含适用于 Claude Code、Codex、Cursor、Trae、Kiro 等 AI 编程工具的标准化约定文档。

---

## 快速使用 (直接复制)

每个工具都有独立目录，文件名已按官方约定命名，可直接复制到项目：

```
conventions/
├── claude-code/          # Claude Code
│   └── CLAUDE.md         → 复制到项目根目录
├── cursor/               # Cursor
│   └── .cursorrules      → 复制到项目根目录
├── codex-cli/            # OpenAI Codex CLI
│   └── AGENTS.md         → 复制到项目根目录
└── kiro/                 # AWS Kiro
    └── .kiro/steering/project.md  → 复制整个 .kiro/ 目录到项目根目录
```

### 一键复制命令

```bash
# Claude Code
cp conventions/claude-code/CLAUDE.md your-project/

# Cursor
cp conventions/cursor/.cursorrules your-project/

# OpenAI Codex CLI
cp conventions/codex-cli/AGENTS.md your-project/

# AWS Kiro
cp -r conventions/kiro/.kiro your-project/
```

---

## 文档索引

### 工具专用约定 (源文件)

| 文档 | 工具 | 官方约定位置 | 说明 |
|------|------|--------------|------|
| [CLAUDE.md](./CLAUDE.md) | Claude Code | 项目根目录 `CLAUDE.md` | Claude Code 核心约定 |
| [AGENTS.md](./AGENTS.md) | OpenAI Codex CLI | 项目根目录 `AGENTS.md` | OpenAI Codex 工具约定 |
| [KIRO.md](./KIRO.md) | AWS Kiro | `.kiro/steering/project.md` | Amazon Q Developer Agent 约定 |

> Cursor 使用与 Claude Code 相同的约定，文件名为 `.cursorrules`

### 通用约定

| 文档 | 说明 | 适用场景 |
|------|------|----------|
| [WORKFLOW.md](./WORKFLOW.md) | 开发工作流约定 | 项目开发全流程 |
| [PROJECT.md](./PROJECT.md) | 项目结构约定 | 项目初始化、结构规划 |
| [CODING.md](./CODING.md) | 编码规范约定 | 代码编写、审查 |

---

## 核心概念

### 4 阶段工作流

```
Phase 1: Idea (30m)  →  Phase 2: UI (2-4h)  →  Phase 3: Code (1-2d)  →  Phase 4: Ship (4-8h)
     ↓                       ↓                       ↓                       ↓
  8个PRD文档              5轮UI审查             三端代码实现             测试+发布
```

### 三端架构

```
Client (用户端)  +  Admin (管理端)  +  Website (官网)
```

### 技术栈

| 层级 | 技术 |
|------|------|
| Frontend | React + Vite + Tailwind CSS |
| Backend | Python + FastAPI + SQLModel |
| Database | SQLite |
| UI Design | MCP Pencil |

---

## 核心原则

| 原则 | 说明 |
|------|------|
| UI-First | 先设计 UI，再写代码 |
| Design-Driven | 界面必须还原设计稿 |
| Speed > Perfect | 快速交付，快速迭代 |
| 状态驱动 | 使用 `.dev-state/` 实现断点续传 |

---

## 适用场景

**适用：**
- MVP 或概念验证项目
- 快速验证商业想法
- 需要快速反馈的实验性功能
- 上市时间紧迫的项目

**不适用：**
- 生产级系统
- 安全/性能是关键要求
- 需要长期可维护性
- 大型团队协作项目

---

## 相关资源

- [rapid-prototype-workflow SKILL.md](../skills/rapid-prototype-workflow/SKILL.md)
- [continuous-dev-loop SKILL.md](../skills/continuous-dev-loop/SKILL.md)
- [快速原型开发规范](../docs/rapid-prototype-dev-guide.md)

---

## 版本

- 版本: 1.0.0
- 基于: rapid-prototype-workflow v2.0.0
- 更新日期: 2024
