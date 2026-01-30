---
name: tech-plan-template
description: This skill generates comprehensive technical design documents from PRD inputs. It should be used when creating architecture designs, detailed technical specifications, database designs, API designs, and deployment plans. The template covers frontend and backend architecture, reliability design, testing strategy, and release planning.
license: MIT
compatibility: Requires PRD document as input. Works with any tech stack.
metadata:
  category: design
  phase: technical-design
  version: "1.0.0"
---

# Technical Plan Template Skill

This skill generates structured technical design documents.

## When to Use

Use this skill when:
- A PRD is approved and needs technical design
- You need to create architecture documentation
- You want a comprehensive technical specification

## Template Structure

### 1. Requirement Background
Summarize the business background and context.

### 2. Requirement Goals
List objectives in checklist format.

### 3. Project Members
Document team members and roles (optional).

#### 3.1 Project Resources
Reference PRD, UI designs, interaction docs, user stories.

### 4. Requirement Plan

#### 4.1 Requirement Checklist
- Frontend requirements: page interactions, responsive design, animations
- Backend requirements: API functions, data processing logic

### 5. Modification Points

#### 5.1 Business Model Extraction
Document key business flows using swimlane diagrams.

#### 5.2 Architecture Analysis
- Frontend: tech stack, project structure, build process, deployment, caching
- Backend: tech stack, project structure, API chains, data flow, error handling

#### 5.3 Architecture Design
Include: business structure, technical architecture, engineering architecture, data architecture

**Frontend Architecture:**
- Framework selection (Vue 3, React, etc.)
- State management (Redux, Pinia, etc.)
- Routing solution
- UI component library
- Build tools (Vite, Webpack)
- Code standards (ESLint, Prettier)
- API management (Axios)

**Backend Architecture:**
- Language and framework
- Database selection
- Middleware selection
- Deployment strategy

#### 5.4 Detailed Design
- API design: endpoints, parameters, responses, error handling
- Database design: tables, fields, indexes, data dictionary
- Frontend components: hierarchy, props, state management
- Service design: inter-service calls, error handling

#### 5.5 Database Design
Document table changes, field changes, unique key considerations.

### 6. Stability Considerations

#### 6.1 Reliability Design
- Error handling, transactions, disaster recovery, reconciliation
- Frontend: retry mechanisms, error display, degradation

#### 6.2 Concurrency
- Traffic estimation
- Data volume estimation

### 7. Operations & Deployment
- Pressure testing plan
- New dependencies (Redis, ES, etc.)

### 8. Error Monitoring
- Error codes, logging
- Frontend error capture and reporting

### 9. Risk Assessment
- Reconciliation model
- Compensation strategies

### 10. Testing Strategy
- Black-box test cases
- White-box test cases
- Smoke test cases

### 11. Release Strategy
- Frontend: build, deployment, versioning
- Backend: build, deployment, versioning

## Usage

Reference the full template in `references/tech-plan-template.md` for detailed sections.
