---
name: orchestrator
description: This skill coordinates all development skills as a central dispatcher for end-to-end delivery. It should be used when managing complete feature development, bug fixes, or iterations. The skill routes tasks to appropriate sub-skills, manages quality gates, tracks state, and ensures delivery standards.
license: MIT
compatibility: Requires access to all sub-skills. Works with any development workflow.
metadata:
  category: coordination
  phase: orchestration
  version: "1.0.0"
allowed-tools: bash cat read_file
---

# Orchestrator Skill

This skill serves as the central coordinator for all development skills, managing end-to-end delivery workflows.

## When to Use

Use this skill when:
- Starting a new feature development (full workflow)
- Managing bug fix processes
- Handling hotfix emergencies
- Coordinating iteration improvements

## Managed Skills

| Skill | Phase | Purpose |
|-------|-------|---------|
| prd-template | Requirements | Generate PRD documents |
| srs-template | Requirements | Generate SRS documents |
| prd-review | Review | Review PRD quality |
| tech-plan-template | Design | Generate technical designs |
| dev-task-split | Planning | Split development tasks |
| bug-fix-task-split | Planning | Split bug fix tasks |
| development-workflow | Execution | Coordinate development |
| document-update | Maintenance | Sync document changes |

## Task Types & Routing

### new_feature
Full development workflow for new features.

```
Requirements → Design → Planning → Execution → Maintenance
    │            │          │           │            │
    ▼            ▼          ▼           ▼            ▼
prd-template  tech-plan  dev-task   development  document-
srs-template  -template  -split     -workflow    update
prd-review
```

### bug_fix
Streamlined workflow for bug fixes.

```
Analysis → Execution → Maintenance
    │          │           │
    ▼          ▼           ▼
bug-fix-   development  document-
task-split -workflow    update
```

### hotfix
Emergency fix with minimal process.

```
Quick Fix (smoke test only)
    │
    ▼
bug-fix-task-split → development-workflow
```

### iteration
Incremental improvement workflow.

```
Update PRD → Update Design → Split Tasks → Execute
```

## Workflow Definitions

### New Feature Workflow

**Phase 1: Requirements**
1. Generate PRD using `prd-template`
2. Generate SRS using `srs-template` (optional)
3. Review PRD using `prd-review`
4. **Gate:** PRD must pass review

**Phase 2: Design**
1. Generate technical plan using `tech-plan-template`

**Phase 3: Planning**
1. Split tasks using `dev-task-split`

**Phase 4: Execution**
1. Execute workflow using `development-workflow`
2. **Gate:** All tests must pass

**Phase 5: Maintenance**
1. Sync documents using `document-update`

### Bug Fix Workflow

**Phase 1: Analysis**
1. Analyze and split tasks using `bug-fix-task-split`

**Phase 2: Execution**
1. Execute fix using `development-workflow`

**Phase 3: Maintenance**
1. Update documents if needed using `document-update`

## Quality Gates

| Gate | Condition | On Failure |
|------|-----------|------------|
| PRD Review | No critical issues | Block & notify |
| Unit Test | Coverage ≥ 80% | Warn & continue |
| Integration Test | All pass | Block & notify |
| Smoke Test | All pass | Block & rollback |

## Priority Handling

| Priority | Max Wait | Skip Optional | Notify |
|----------|----------|---------------|--------|
| P0 | 0 | Yes | Slack+Email+SMS |
| P1 | 4h | No | Slack+Email |
| P2 | 24h | No | Slack |
| P3 | 72h | No | None |

## State Machine

```
PENDING → ANALYZING → DESIGNING → PLANNING → EXECUTING → TESTING → REVIEWING → COMPLETED
    │         │           │          │           │          │          │
    └─────────┴───────────┴──────────┴───────────┴──────────┴──────────┴→ BLOCKED/FAILED
```

## Usage Examples

**New Feature:**
```bash
start_delivery --type new_feature --description "User login feature" --priority P1
```

**Bug Fix:**
```bash
start_delivery --type bug_fix --description "Login page blank screen" --priority P0
```

**Hotfix:**
```bash
start_delivery --type hotfix --description "Payment API timeout" --priority P0
```

## Output

- Execution plan with phases and steps
- Deliverables list
- Execution log with timestamps
- Quality gate results
