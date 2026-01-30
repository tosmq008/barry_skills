---
name: development-workflow
description: This skill coordinates end-to-end development workflows from requirements to deployment. It should be used when managing the complete development lifecycle including design, coding, testing, and release phases. The skill ensures proper task tracking and quality gates at each phase.
license: MIT
compatibility: Works with any development methodology. Requires task tracking capability.
metadata:
  category: execution
  phase: development
  version: "1.0.0"
---

# Development Workflow Skill

This skill coordinates the complete development lifecycle.

## When to Use

Use this skill when:
- Starting a new development project
- Managing end-to-end development workflow
- Coordinating multiple development phases
- Tracking task completion across phases

## Workflow Phases

### Phase 1: Business & Product Design
**Output:** Product Requirements Document (PRD).md

### Phase 2: Prototype Design
**Input:** PRD.md
**Output:** 
- Prototype Design Document.md
- Frontend interaction prototype (HTML)

### Phase 3: System Analysis & Architecture Design
**Input:** PRD.md, Prototype Design Document.md
**Output:**
- Technical Design Document.md
- Task list

### Phase 4: Coding Implementation

#### Frontend Implementation
1. Static page design based on PRD, Tech Design, Prototype
2. Frontend logic design
3. API integration logic
4. Interaction and rendering logic

#### Backend Implementation
1. Database design and API implementation
2. API documentation
3. Backend logic implementation
4. Database and middleware initialization
5. Unit testing (required)
6. API self-testing

#### Frontend-Backend Integration
- Integration testing
- End-to-end validation

### Phase 5: Testing

1. **Black-box Test Design:** Functional test cases
2. **Black-box Test Execution:** Execute functional tests
3. **Smoke Test Design:** Critical path test cases
4. **Smoke Test Execution:** Execute smoke tests
5. **Bug Recording:** Output Test Report.md

### Phase 6: Bug Fix Iteration
**Input:** Test Report.md
1. Fix frontend/backend code based on test report
2. Repeat testing phase until all bugs fixed

### Phase 7: Regression Verification
- Verify each recorded bug using full regression
- Confirm all test cases pass

## Task Management

### Task File: task.md

All tasks are tracked in a single file with:
- Task and sub-task breakdown
- Individual verification criteria
- Completion status markers

### Task Format
```markdown
# Task List: [Project Name]

## Phase 1: Requirements
- [x] 1.1 Create PRD
- [x] 1.2 PRD Review

## Phase 2: Design
- [ ] 2.1 Create prototype
- [ ] 2.2 Create tech design

## Phase 3: Implementation
- [ ] 3.1 Backend development
- [ ] 3.2 Frontend development
- [ ] 3.3 Integration

## Phase 4: Testing
- [ ] 4.1 Unit tests
- [ ] 4.2 Integration tests
- [ ] 4.3 Smoke tests

## Phase 5: Release
- [ ] 5.1 Deployment
- [ ] 5.2 Verification
```

## Execution Rules

1. Break down all workflow content into tasks and sub-tasks
2. Each task must be independently verifiable
3. Consolidate all tasks into single task.md file
4. Mark completion status for each task
5. Execute until all tasks complete
