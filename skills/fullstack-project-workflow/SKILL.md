---
name: fullstack-project-workflow
description: "This skill manages full-stack software projects with client-side frontend/backend and admin-side frontend/backend. It should be used when initializing multi-tier OOP project structures, or executing any task (feature, bug fix, iteration) following the standard workflow - goal understanding, system analysis, technical design, implementation, testing, and release planning. The skill enforces layered architecture and language-specific project conventions."
license: MIT
compatibility: "Supports Java, Python, TypeScript/JavaScript, Go. Requires project initialization capability."
metadata:
  category: project-management
  phase: full-lifecycle
  version: "1.0.0"
allowed-tools: bash cat read_file write_file
---

# Full-Stack Project Workflow Skill

This skill manages multi-tier full-stack projects with standardized OOP architecture and development workflow.

## When to Use

Use this skill when:
- Initializing a new full-stack project (client + admin, frontend + backend)
- Starting any development task (feature, bug fix, iteration)
- Ensuring consistent layered architecture across all modules
- Following standardized development workflow

## Project Architecture

### Four-Module Structure

```
project-root/
├── client-frontend/     # 使用侧前端 (User-facing Frontend)
├── client-backend/      # 使用侧后端 (User-facing Backend)
├── admin-frontend/      # 管理侧前端 (Admin Frontend)
├── admin-backend/       # 管理侧后端 (Admin Backend)
├── shared/              # 共享模块 (Shared Libraries)
└── docs/                # 项目文档
```

### OOP Layered Architecture Principles

All modules follow these principles:
1. **Abstraction** - Define interfaces/abstract classes for core behaviors
2. **Encapsulation** - Hide implementation details, expose clean APIs
3. **Layering** - Strict separation of concerns between layers
4. **Dependency Inversion** - Depend on abstractions, not concretions

## Project Initialization

### Step 1: Choose Language Stack

Determine the technology stack for each module:

| Module | Common Choices |
|--------|----------------|
| client-frontend | React, Vue, Angular |
| client-backend | Java/Spring, Python/FastAPI, Node/Express, Go/Gin |
| admin-frontend | React, Vue, Angular |
| admin-backend | Java/Spring, Python/FastAPI, Node/Express, Go/Gin |

### Step 2: Initialize Project Structure

See `references/project-structures.md` for language-specific templates.

## Standard Development Workflow

**Every task (feature, bug fix, iteration) MUST follow these 7 phases:**

### Phase 1: Goal Understanding (目标理解)

- [ ] Clarify task objectives and scope
- [ ] Identify affected modules (client/admin, frontend/backend)
- [ ] Define success criteria
- [ ] List stakeholders and dependencies

**Output:** Task understanding document

### Phase 2: System Analysis (系统分析)

#### 2.1 Call Chain Analysis (链路分析)
- [ ] Map user interaction flow
- [ ] Trace frontend → backend → database call chain
- [ ] Identify cross-module dependencies
- [ ] Document existing code paths affected

#### 2.2 Impact Analysis
- [ ] List affected components per module
- [ ] Identify shared code impacts
- [ ] Assess backward compatibility requirements

**Output:** System analysis document with call chain diagrams

### Phase 3: Technical Design (技术方案设计)

#### 3.1 Design Points (设计/改动点)
- [ ] Define new components/classes needed
- [ ] List modifications to existing code
- [ ] Design class hierarchies (OOP)
- [ ] Define interfaces and abstractions

#### 3.2 Database Changes (数据库变更)
- [ ] Schema changes (new tables, columns)
- [ ] Migration scripts
- [ ] Data backfill requirements
- [ ] Index optimization

#### 3.3 API Contract (前后端接口约定)
- [ ] Define API endpoints
- [ ] Request/Response schemas
- [ ] Error codes and handling
- [ ] Authentication/Authorization requirements

#### 3.4 Cross-Module Coordination
- [ ] Shared library changes
- [ ] Client-Admin data synchronization
- [ ] Event/Message contracts

**Output:** Technical design document

### Phase 4: Implementation (实现技术方案)

#### 4.1 Implementation Order
1. Database migrations
2. Shared libraries
3. Backend services (client → admin)
4. Frontend components (client → admin)
5. Integration points

#### 4.2 Code Standards
- Follow layered architecture
- Apply OOP principles
- Write unit tests alongside code
- Document public APIs

**Output:** Implemented code with unit tests

### Phase 5: Test Design (测试方案设计)

#### 5.1 Test Strategy
- [ ] Unit test scope and coverage target
- [ ] Integration test scenarios
- [ ] E2E test cases
- [ ] Performance test requirements

#### 5.2 Test Cases
- [ ] Happy path scenarios
- [ ] Edge cases
- [ ] Error handling scenarios
- [ ] Cross-module integration scenarios

**Output:** Test plan and test cases

### Phase 6: Test Execution & Acceptance (执行测试验收)

#### 6.1 Test Execution
- [ ] Run unit tests (coverage ≥ 80%)
- [ ] Run integration tests
- [ ] Run E2E tests
- [ ] Performance validation

#### 6.2 Acceptance Criteria
- [ ] All tests pass
- [ ] Code review approved
- [ ] Documentation updated
- [ ] No critical/high severity bugs

**Output:** Test report and acceptance sign-off

### Phase 7: Release Planning (发布方案设计)

#### 7.1 Release Strategy
- [ ] Deployment sequence (DB → Backend → Frontend)
- [ ] Feature flags configuration
- [ ] Rollout percentage plan
- [ ] Rollback procedures

#### 7.2 Release Checklist
- [ ] Database migrations ready
- [ ] Configuration changes documented
- [ ] Monitoring/Alerts configured
- [ ] Runbook updated

**Output:** Release plan document

## Task Tracking Template

```markdown
# Task: [Task Name]

## Phase 1: Goal Understanding
- Objective: 
- Affected Modules: [ ] client-fe [ ] client-be [ ] admin-fe [ ] admin-be
- Success Criteria:

## Phase 2: System Analysis
- Call Chain: [diagram/description]
- Impact Analysis:

## Phase 3: Technical Design
- Design Points:
- Database Changes:
- API Contract:

## Phase 4: Implementation
- [ ] Database migrations
- [ ] Backend implementation
- [ ] Frontend implementation
- [ ] Unit tests

## Phase 5: Test Design
- Test Strategy:
- Test Cases:

## Phase 6: Test Execution
- [ ] Unit tests passed
- [ ] Integration tests passed
- [ ] Acceptance criteria met

## Phase 7: Release Planning
- Deployment Sequence:
- Rollback Plan:
```

## References

- `references/project-structures.md` - Language-specific project templates
- `references/layer-patterns.md` - OOP layered architecture patterns
- `references/api-conventions.md` - API design conventions
