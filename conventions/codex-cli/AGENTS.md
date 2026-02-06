# AGENTS.md - OpenAI Codex CLI 约定

> 适用于 OpenAI Codex CLI 的项目指导文件
>
> 官方约定: Codex CLI 自动读取 `~/.codex/AGENTS.md` (全局) 和项目根目录的 `AGENTS.md` (项目级)

本文档定义了 Codex CLI 在项目中工作的核心规则和约定。

---

## Project Context

```yaml
project_type: rapid-prototype
tech_stack:
  frontend: React + Vite + Tailwind CSS
  backend: Python + FastAPI + SQLModel
  database: SQLite
  package_manager: uv (Python) / npm (Node)
architecture: three-tier (Client + Admin + Website)
```

---

## Core Principles

1. **UI-First** - Design UI mockups before writing code
2. **Design-Driven** - Implementation must strictly follow design specs
3. **Speed > Perfect** - Ship fast, iterate fast
4. **Client First** - Complete user-facing features before admin
5. **State-Driven** - Use `.dev-state/` for checkpoint recovery

---

## Development Guidelines

### File Writing Strategy (CRITICAL)

Due to AI context window limitations, follow these rules when writing files:

- **NEVER write large files in one shot** - Content may be truncated or lost
- **Write incrementally** - 100-200 lines per write, build file progressively
- **Skeleton first, content later** - Write file structure first, then fill sections
- **Verify after each write** - Read file to confirm content is complete

---

## Working Mode

### 1. Session Start Checklist

```bash
# Always check project state first
ls docs/prd/*.md 2>/dev/null    # Check PRD documents
cat .dev-state/state.json       # Check development state
ls -la client/ admin/ website/  # Check code directories
```

**Decision Logic:**
- Has `docs/prd/` → Resume from checkpoint, don't recreate PRD
- Has `PRD.md` / `README.md` → Continue based on existing docs
- Empty project → Start from Phase 1 (create PRD)

### 2. Task Execution Rules

- **Task granularity**: Single task < 10 minutes
- **State updates**: Update state file immediately after each task
- **Context monitoring**: After 5+ tasks, save state and suggest new session

### 3. Blocking Handling

When blocked:
1. Log to `.dev-state/blocked-tasks.txt`
2. Skip current task, continue with next
3. Don't get stuck on single task

---

## State File Protocol

```
.dev-state/
├── state.json           # Main state file (JSON)
├── task-registry.json   # Global task registry (CRITICAL)
├── current-phase.txt    # Current phase (1-4)
├── current-task.txt     # Current task
├── completed-tasks.txt  # Completed task list
├── blocked-tasks.txt    # Blocked tasks with reasons
└── dev-log.txt          # Development log
```

### task-registry.json Format (Global Task Summary)

```json
{
  "project": "project-name",
  "created_at": "2024-01-31T08:00:00Z",
  "updated_at": "2024-01-31T14:30:00Z",
  "summary": {
    "total": 32,
    "completed": 20,
    "in_progress": 1,
    "pending": 10,
    "blocked": 1
  },
  "tasks": [
    {
      "id": "1.1",
      "phase": "1",
      "name": "Write project brief",
      "status": "completed",
      "agent": "product-expert",
      "started_at": "2024-01-31T08:00:00Z",
      "completed_at": "2024-01-31T08:15:00Z",
      "output": "docs/prd/01-project-brief.md"
    },
    {
      "id": "3.5",
      "phase": "3",
      "name": "Implement Client Frontend core pages",
      "status": "in_progress",
      "agent": "frontend-expert",
      "started_at": "2024-01-31T14:00:00Z",
      "completed_at": null,
      "output": null,
      "subtasks": [
        { "name": "Login page", "status": "completed" },
        { "name": "Home page", "status": "in_progress" },
        { "name": "List page", "status": "pending" }
      ]
    }
  ]
}
```

### Task State Persistence Rules (CRITICAL)

1. **On task start**: Update `task-registry.json`, set `status: "in_progress"`
2. **On task complete**: Update `status: "completed"` and `completed_at`
3. **On task blocked**: Set `status: "blocked"` and record `blocked_reason`
4. **Subtask progress**: Use `subtasks` array for fine-grained tracking
5. **Recovery**: On new session, read `task-registry.json` to find `in_progress` task

### Recovery Flow

```bash
# New session startup sequence
1. cat .dev-state/task-registry.json  # Read global task summary
2. Find task with status="in_progress" # Locate interruption point
3. Check subtasks progress             # Determine exact checkpoint
4. Resume from checkpoint              # Don't repeat completed work
```

---

## UI Design Specs

### Design File Storage

```
docs/ui/
├── [project-name].pen      # Main design file (all platforms)
├── client/                 # Client designs (optional split)
│   └── client.pen
├── admin/                  # Admin designs (optional split)
│   └── admin.pen
└── website/                # Website designs (optional split)
    └── website.pen
```

### Design Workflow

```
1. Check current editor state
2. Open or create design file
3. Get design guidelines
4. Get available style tags
5. Select and apply style
6. Execute design operations (≤25 per batch)
7. Verify design with screenshot
8. Repeat 6-7 until complete
```

### Required Design Coverage

**Client:**
- Entry flow: Splash, onboarding, login, register, forgot password
- Home: with data, empty state, loading
- Core pages: list, detail, search, filter
- Action pages: form, confirm, result
- Profile: settings, messages
- Error states: empty, loading, error, 404

**Admin:**
- Login, Dashboard
- Data list (with data/empty/loading)
- Forms (create/edit), detail page
- System config, confirm dialogs

**Website:**
- Landing (Hero + features + CTA)
- Features, pricing, about, contact
- Header, footer, 404

---

## Required Documents

| # | Document | Path |
|---|----------|------|
| 1 | Project Brief | `docs/prd/01-project-brief.md` |
| 2 | Feature Architecture | `docs/prd/02-feature-architecture.md` |
| 3 | Role Definition | `docs/prd/03-role-definition.md` |
| 4 | Module Design | `docs/prd/04-module-design.md` |
| 5 | Page List | `docs/prd/05-page-list.md` |
| 6 | Page Navigation | `docs/prd/06-page-navigation.md` |
| 7 | Page Interaction | `docs/prd/07-page-interaction.md` |
| 8 | Visual Style | `docs/prd/08-visual-style.md` |
| 9 | UI Design | `docs/ui/[project].pen` |
| 10 | API Spec | `docs/api/api-spec.md` |
| 11 | Test Plan | `docs/test/test-plan.md` |
| 12 | Test Cases | `docs/test/test-cases.md` |

---

## Prohibited Actions

- **DO NOT** deviate from design specs for UI styling
- **DO NOT** implement UI without design mockups
- **DO NOT** skip UI design and jump to coding
- **DO NOT** repeat completed work
- **DO NOT** blindly recreate existing documents
- **DO NOT** over-engineer architecture
- **DO NOT** use default ugly styles

---

## Resume Commands

When user sends these commands, resume from checkpoint:

```
continue
resume
continue development
```

### Response Format

```markdown
📊 **Development State Restored**

Current Phase: Phase 3 - Implementation
Current Task: 3.5 Implement Client Frontend core pages
Completed: 20/32 tasks (62.5%)
Blocked: 1 task

Resuming task 3.5...
```

---

## Context Warning

When context is getting long, output:

```markdown
⚠️ Recommend starting new session. Progress saved to .dev-state/,
send 'continue' to resume.
```

---

## Related Documents

- [CLAUDE.md](./CLAUDE.md) - Claude Code conventions
- [KIRO.md](./KIRO.md) - AWS Kiro conventions
- [WORKFLOW.md](./WORKFLOW.md) - Development workflow
- [PROJECT.md](./PROJECT.md) - Project structure
- [CODING.md](./CODING.md) - Coding standards
