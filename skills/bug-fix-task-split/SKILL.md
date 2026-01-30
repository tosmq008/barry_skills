---
name: bug-fix-task-split
description: This skill analyzes bugs and splits fix tasks into structured steps. It should be used when a bug is reported and needs systematic analysis, root cause identification, and fix planning. The skill covers bug reproduction, backend/frontend evaluation, database changes, API updates, and regression testing.
license: MIT
compatibility: Requires access to error logs and bug reports. Works with any debugging workflow.
metadata:
  category: planning
  phase: bug-fixing
  version: "1.0.0"
---

# Bug Fix Task Split Skill

This skill helps analyze bugs and create structured fix task lists.

## When to Use

Use this skill when:
- A bug is reported and needs systematic analysis
- You need to create a fix plan with clear steps
- You want to ensure the fix covers all affected areas

## Bug Fix Workflow

### Step 1: Confirm Bug Details
- Identify the scenario where the bug occurs
- Document reproduction steps
- Gather relevant error logs

### Step 2: Confirm Expected Behavior
- Define what the correct behavior should be
- Verify the bug actually exists
- Analyze frontend and backend error logs to locate root cause

### Step 3: Reproduce Bug
- Follow bug details to confirm reproduction
- Document exact reproduction steps

### Step 4: Evaluate Backend Changes
- Assess if backend modifications are needed
- Create backend business change tasks if required

### Step 5: Evaluate Database Changes
- Check if database schema changes are needed
- Create database migration tasks if required

### Step 6: Evaluate API Changes
- Determine if API updates are needed
- Update API documentation
- Create backend API change tasks
- Create frontend code change tasks

### Step 7: Evaluate Frontend Changes
- Assess frontend UI and logic changes
- Create UI change tasks
- Create logic change tasks

### Step 8: Integration Tasks
- Create frontend-backend integration tasks

### Step 9: Testing
- Create test case checklist
- Execute smoke tests
- Iterate until all tests pass

## Output Format

```markdown
# Bug Fix Task List: [Bug ID/Title]

## Analysis
- Bug scenario: [description]
- Expected behavior: [description]
- Root cause: [description]

## Backend Fix Tasks
- [ ] 1.1 [Task description]

## Database Tasks
- [ ] 2.1 [Task description]

## API Tasks
- [ ] 3.1 [Task description]

## Frontend Fix Tasks
- [ ] 4.1 [Task description]

## Integration Tasks
- [ ] 5.1 [Task description]

## Regression Testing
- [ ] 6.1 Create regression test cases
- [ ] 6.2 Execute smoke tests
```

## Post-Execution Hooks

After fix completion, trigger:
1. Code quality check
2. Unit tests (must pass)
3. Integration tests (must pass)
4. Generate test report
5. Update API documentation
6. Update README.md
