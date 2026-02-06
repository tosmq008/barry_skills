# KIRO.md - AWS Kiro 约定

> 适用于 AWS Kiro (Amazon Q Developer Agent) 的项目指导文件
>
> 官方约定: Kiro 使用 `.kiro/` 目录存储 steering 文件，本文件可作为 `.kiro/steering/project.md` 使用

本文档定义了 Kiro 在项目中工作的核心规则和约定。Kiro 使用 Spec-Driven Development 模式。

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

## Kiro Spec Structure

Kiro 使用 `.kiro/` 目录存储规格文件，与本项目的 `.dev-state/` 协同工作。

```
.kiro/
├── specs/                    # Kiro 规格文件
│   ├── requirements.md       # 需求规格 (映射到 docs/prd/)
│   ├── design.md             # 设计规格 (映射到 docs/ui/)
│   └── tasks.md              # 任务规格 (映射到 task-registry.json)
├── steering/                 # 引导规则
│   └── rules.md              # 项目规则
└── hooks/                    # 钩子脚本
    └── post-task.sh          # 任务完成后钩子

.dev-state/                   # 项目状态 (与 Kiro 协同)
├── state.json
├── task-registry.json
└── ...
```

---

## Core Principles

| Principle | Description |
|-----------|-------------|
| UI-First | Design UI mockups before writing code |
| Design-Driven | Implementation must strictly follow design specs |
| Speed > Perfect | Ship fast, iterate fast |
| Client First | Complete user-facing features before admin |
| State-Driven | Use `.dev-state/` for checkpoint recovery |
| Spec-Driven | Follow Kiro specs for structured development |

---

## Development Guidelines

### File Writing Strategy (CRITICAL)

Due to AI context window limitations, follow these rules when writing files:

- **NEVER write large files in one shot** - Content may be truncated or lost
- **Write incrementally** - 100-200 lines per write, build file progressively
- **Skeleton first, content later** - Write file structure first, then fill sections
- **Verify after each write** - Read file to confirm content is complete

---

## Steering Rules (.kiro/steering/rules.md)

```markdown
# Project Rules

## Architecture
- Three-tier architecture: Client + Admin + Website
- Client and Admin share SQLite database
- Website is static HTML (no backend)

## Development Order
1. PRD documents (Phase 1)
2. UI design with .pen files (Phase 2)
3. Code implementation (Phase 3)
4. Testing and release (Phase 4)

## Code Standards
- Frontend: React + TypeScript + Tailwind CSS
- Backend: Python + FastAPI + SQLModel
- Database: SQLite (shared at shared/db/data.db)

## Prohibited
- Skip UI design before coding
- Deviate from design specs
- Over-engineer architecture
- Use default ugly styles
```

---

## Task Registry Integration

Kiro 的任务系统与 `task-registry.json` 集成：

### task-registry.json Format

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
      "subtasks": [
        { "name": "Login page", "status": "completed" },
        { "name": "Home page", "status": "in_progress" },
        { "name": "List page", "status": "pending" }
      ]
    }
  ]
}
```

### Kiro Task Mapping (.kiro/specs/tasks.md)

```markdown
# Task Specifications

## Phase 1: Requirements (30 min)
- [ ] 1.1 Project brief → docs/prd/01-project-brief.md
- [ ] 1.2 Feature architecture → docs/prd/02-feature-architecture.md
- [ ] 1.3 Role definition → docs/prd/03-role-definition.md
- [ ] 1.4 Module design → docs/prd/04-module-design.md
- [ ] 1.5 Page list → docs/prd/05-page-list.md
- [ ] 1.6 Page navigation → docs/prd/06-page-navigation.md
- [ ] 1.7 Page interaction → docs/prd/07-page-interaction.md
- [ ] 1.8 Visual style → docs/prd/08-visual-style.md

## Phase 2: UI Design (2-4 hours)
- [ ] 2.1 Client UI design → docs/ui/client.pen
- [ ] 2.2 Admin UI design → docs/ui/admin.pen
- [ ] 2.3 Website UI design → docs/ui/website.pen
- [ ] 2.4 5-round review iteration

## Phase 3: Implementation (1-2 days)
- [ ] 3.1 Project structure setup
- [ ] 3.2 Client Backend models
- [ ] 3.3 Client Backend APIs
- [ ] 3.4 Client Frontend framework
- [ ] 3.5 Client Frontend pages
- [ ] 3.6 Admin Backend
- [ ] 3.7 Admin Frontend
- [ ] 3.8 Website static pages
- [ ] 3.9 Website optimization
- [ ] 3.10 Startup scripts

## Phase 4: Testing & Release (4-8 hours)
- [ ] 4.1 Client Backend tests
- [ ] 4.2 Admin Backend tests
- [ ] 4.3 Integration tests
- [ ] 4.4 Functional tests
- [ ] 4.5 Bug fixes
- [ ] 4.6 Final acceptance
```

---

## Task State Persistence Rules (CRITICAL)

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

## Kiro Hooks

### Post-Task Hook (.kiro/hooks/post-task.sh)

```bash
#!/bin/bash
# Update task-registry.json after each task completion

TASK_ID=$1
STATUS=$2
OUTPUT=$3

# Update task status in registry
python3 << EOF
import json
from datetime import datetime

with open('.dev-state/task-registry.json', 'r') as f:
    registry = json.load(f)

for task in registry['tasks']:
    if task['id'] == '$TASK_ID':
        task['status'] = '$STATUS'
        if '$STATUS' == 'completed':
            task['completed_at'] = datetime.utcnow().isoformat() + 'Z'
            task['output'] = '$OUTPUT'
        break

# Update summary
registry['summary']['completed'] = len([t for t in registry['tasks'] if t['status'] == 'completed'])
registry['summary']['in_progress'] = len([t for t in registry['tasks'] if t['status'] == 'in_progress'])
registry['summary']['pending'] = len([t for t in registry['tasks'] if t['status'] == 'pending'])
registry['summary']['blocked'] = len([t for t in registry['tasks'] if t['status'] == 'blocked'])
registry['updated_at'] = datetime.utcnow().isoformat() + 'Z'

with open('.dev-state/task-registry.json', 'w') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)
EOF
```

---

## Resume Commands

When user sends these commands, resume from checkpoint:

```
continue
resume
/continue
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
- [AGENTS.md](./AGENTS.md) - OpenAI Codex CLI conventions
- [WORKFLOW.md](./WORKFLOW.md) - Development workflow
- [PROJECT.md](./PROJECT.md) - Project structure
- [CODING.md](./CODING.md) - Coding standards
