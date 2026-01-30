---
name: prd-template
description: This skill generates PRD (Product Requirements Document) templates following INVEST user story format and EARS acceptance criteria. It should be used when creating new product requirements, defining user stories, or documenting feature specifications. The template ensures comprehensive coverage of business goals, user roles, functional requirements, and release strategy.
license: MIT
compatibility: Works with any product development workflow. Supports INVEST and EARS methodologies.
metadata:
  category: requirements
  phase: product-design
  version: "1.0.0"
---

# PRD Template Skill

This skill generates structured PRD documents using INVEST user stories and EARS acceptance criteria.

## When to Use

Use this skill when:
- Creating a new product requirement document
- Defining user stories for a feature
- Documenting acceptance criteria
- Planning a product release

## Template Structure

### 0. Metadata
| Field | Value |
|-------|-------|
| Document Title | [Domain][Module] PRD v{version} |
| Author | |
| Created Date | |
| Prototype Link | (Figma/Axure) |
| Change Log | Date, Version, Author, Reason |

### 1. Background & Goals (Why)
- User pain points (quantified)
- Business goals (SMART format)
- Success metrics (North Star & guardrail metrics)

### 2. User Roles (Who)
| Role | Definition | Scale | Key Needs |
|------|------------|-------|-----------|

### 3. User Story Pool (INVEST Format)
Each story must be: Independent, Negotiable, Valuable, Estimable, Small, Testable

| Story ID | User Story | Value | Story Points | Priority |
|----------|------------|-------|--------------|----------|
| US-01 | As a [role], I want [action], so that [value] | | | |

### 4. Acceptance Criteria (EARS Format)
Use syntax: "When <condition/event>, then the system shall <expected behavior>"

| Story ID | Acceptance Criteria | Test Type | Status |
|----------|---------------------|-----------|--------|

### 5. Functional Requirements
| Feature | Story | Prototype | Business Rules | Error Handling |
|---------|-------|-----------|----------------|----------------|

### 6. Non-Functional Requirements
| Category | Requirement | Verification |
|----------|-------------|--------------|
| Performance | P99 ≤ 600ms | Load test |
| Security | OWASP Top10 | Penetration test |
| Compatibility | 2 versions backward | Regression |

### 7. Data & Analytics
| Event | Trigger | Properties | Notes |
|-------|---------|------------|-------|

### 8. Interaction & Localization
- Figma link
- Copy key table (CSV/Smartling)

### 9. Business Rules (Decision Table)
| Rule ID | Condition | Action | Notes |
|---------|-----------|--------|-------|

### 10. Exception & Reverse Flows
| Exception | User Guidance | System Compensation | SLA |
|-----------|---------------|---------------------|-----|

### 11. Risk Control & Compliance
- Manual review threshold
- Traffic monitoring
- Compliance ID

### 12. Assets & Message Channels
| Type | Template ID | Language | Trigger | Notes |
|------|-------------|----------|---------|-------|

### 13. Technical Feasibility
| Dependency | Status | Evidence |
|------------|--------|----------|

### 14. Release Strategy
| Phase | Date | Feature Flag | Rollout % | Rollback Plan |
|-------|------|--------------|-----------|---------------|

### 15. Test Strategy
- Scope: Functional/Performance/Security/Compliance
- Coverage target: ≥90%

### 16. Milestones
| Task | Owner | Start | End | Status |
|------|-------|-------|-----|--------|

## Guidelines

1. Write user stories first → Add EARS acceptance criteria → Break down features/exceptions/analytics
2. Each story ≤ 8 story points, otherwise split further
3. Acceptance criteria must be automatable (Gherkin/Postman/Robot)
