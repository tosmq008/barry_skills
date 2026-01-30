---
name: dev-task-split
description: This skill splits development requirements into structured task lists. It should be used when a new feature or requirement needs to be broken down into backend tasks, database changes, API changes, frontend UI tasks, and integration tasks. The skill follows a systematic approach to ensure all aspects of development are covered including testing and documentation.
license: MIT
compatibility: Requires access to project documentation (PRD, tech plan). Works with any development workflow.
metadata:
  category: planning
  phase: development-planning
  version: "1.0.0"
---

# Development Task Split Skill

This skill helps split development requirements into actionable task lists following a structured methodology.

## When to Use

Use this skill when:
- A new feature requirement needs to be broken down into development tasks
- You need to create a comprehensive task list from a PRD or tech plan
- You want to ensure all aspects of development are covered (backend, frontend, database, API, testing)

## Task Split Rules

Follow these rules when splitting development tasks:

### 1. Backend Business Logic Tasks
- Evaluate business rule changes
- Design backend modifications
- Create backend business change tasks

### 2. Database Change Tasks
- Evaluate database schema changes based on business rules
- Create database migration tasks
- Consider data integrity and rollback strategies

### 3. API Change Tasks
- Evaluate API design changes
- Update or create API documentation
- Create backend API implementation tasks
- Create frontend API integration tasks

### 4. Frontend UI Tasks
- Design and evaluate frontend interface changes
- Create UI component tasks
- Create interaction logic tasks

### 5. Integration Tasks
- Create frontend-backend integration tasks
- Define integration test scenarios

### 6. Testing Tasks
- Create test case checklist
- Execute smoke tests
- Iterate until all tests pass

## Output Format

Generate a task list in the following format:

```markdown
# Task List: [Feature Name]

## Backend Tasks
- [ ] 1.1 [Task description]
- [ ] 1.2 [Task description]

## Database Tasks
- [ ] 2.1 [Task description]

## API Tasks
- [ ] 3.1 [Task description]
- [ ] 3.2 Update API documentation

## Frontend Tasks
- [ ] 4.1 [Task description]

## Integration Tasks
- [ ] 5.1 Frontend-backend integration

## Testing Tasks
- [ ] 6.1 Create test cases
- [ ] 6.2 Execute smoke tests
```

## Post-Execution Hooks

After task completion, trigger:
1. Code quality check
2. Unit tests (must pass)
3. Integration tests (must pass)
4. Generate test report
5. Update API documentation
6. Update README.md
