---
name: srs-template
description: This skill generates Software Requirements Specification (SRS) documents with PRD-integrated thinking. It should be used when detailed functional specifications are needed, including use cases, data dictionaries, interface requirements, and non-functional requirements. The template supports requirement review, iteration, and acceptance workflows.
license: MIT
compatibility: Works with any software development methodology. Integrates with PRD workflows.
metadata:
  category: requirements
  phase: specification
  version: "1.0.0"
---

# SRS Template Skill

This skill generates comprehensive Software Requirements Specification documents.

## When to Use

Use this skill when:
- Detailed functional specifications are required
- You need comprehensive use case documentation
- Data dictionary and interface specs are needed
- Formal requirement documentation is required

## Template Structure

### 1. Requirement Background & Strategy

#### 1.1 Market/Business Pain Points
[One-sentence pain point + key data]

#### 1.2 Business Necessity
[Policy/Strategy/Benefits]

#### 1.3 Business Goals (OKR/KPI)
| Metric | Definition | Baseline | Target | Deadline |
|--------|------------|----------|--------|----------|

### 2. Requirement Scope & Boundaries

#### 2.1 System Coverage
[Business scope, organizational boundaries, user scope]

#### 2.2 Requirement List & Priority
| ID | Requirement | Source | Priority (RICE/MoSCoW) |
|----|-------------|--------|------------------------|

#### 2.3 Out of Scope
[Explicitly state what is NOT included]

### 3. User Personas & Scenarios

#### 3.1 User Classification
| Role | Responsibilities | Skill Level | Usage Scenario |
|------|------------------|-------------|----------------|

#### 3.2 User Story Map
Phase → User Activity → User Task → Corresponding Feature

### 4. Functional Requirements

#### 4.1 Overall Use Cases & Flows
- Use case diagram
- Business flow diagram (swimlane)

#### 4.2 Use Case Table
| UC ID | Name | Primary Actor | Description | Priority |
|-------|------|---------------|-------------|----------|

#### 4.3 Feature Structure
- Feature structure diagram
- Feature module list

#### 4.4 Detailed Feature Requirements
| Field | Description |
|-------|-------------|
| Feature ID | Globally unique |
| Feature Name | Chinese short name |
| User Story | As a... I want... So that... |
| Preconditions | Business/Technical/Permission |
| Main Flow | 1. ... 2. ... |
| Branches/Exceptions | Scenario, Prompt, Fallback |
| Input & Rules | Field, Type, Validation, Example |
| Output & Display | Result, Page/API |
| Permission Matrix | Role × Action |
| UI Prototype | [Link] |
| Acceptance Criteria | Quantifiable, Testable |

### 5. Data Requirements

#### 5.1 Data Collection
| Data Name | Collection Method | Frequency | Precision | Notes |
|-----------|-------------------|-----------|-----------|-------|

#### 5.2 Data Dictionary
| Data Item | Type | Length | Range | Unit | Description |
|-----------|------|--------|-------|------|-------------|

#### 5.3 Data Flow Diagram
[Insert diagram or description]

### 6. Interface Requirements

#### 6.1 Internal Interfaces
Module-to-module, protocol, data format

#### 6.2 External Interfaces
External systems, protocol, data format

#### 6.3 Software Interfaces
OS, DB, middleware, SDK

#### 6.4 Hardware Interfaces
Servers, sensors, IoT

### 7. Non-Functional Requirements
| Dimension | Metric | Target | Test Method | Notes |
|-----------|--------|--------|-------------|-------|
| Performance | Concurrent Users | ≥ ___ | JMeter | |
| Performance | Response Time | ≤ ___ s | Lighthouse | |
| Availability | SLA | ≥ ___ % | Monitoring | |
| Scalability | Growth | ___ % | Architecture Review | |
| Fault Tolerance | RTO | ___ min | DR Drill | |
| Security | Compliance Level | ___ | Penetration Test | |

### 8. Analytics & Acceptance

#### 8.1 Analytics Plan
Event, Trigger, Properties

#### 8.2 Acceptance Criteria
Functional, Data, Performance acceptance

#### 8.3 Launch Plan
Rollout strategy, rollback conditions, GTM

### 9. Appendix
- A. Business Flow Diagrams
- B. Use Case Diagrams
- C. Data Tables / Report Samples
- D. Glossary
- E. Version History
