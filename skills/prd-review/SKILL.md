---
name: prd-review
description: This skill reviews PRD documents against a comprehensive checklist covering completeness, scope, materials, reusability, workflows, data, performance, analytics, release planning, and technical feasibility. It should be used before PRD approval to ensure quality and completeness.
license: MIT
compatibility: Requires PRD document as input. Works with any product development workflow.
metadata:
  category: review
  phase: quality-assurance
  version: "1.0.0"
---

# PRD Review Skill

This skill performs comprehensive PRD quality reviews using a standardized checklist.

## When to Use

Use this skill when:
- A PRD needs quality review before approval
- You want to ensure PRD completeness
- Validating PRD against organizational standards

## Review Checklist

### 1. Completeness (Mandatory)
- [ ] Clear background, goals, user scenarios, interactions, functional logic, business metrics
- [ ] All user roles and operation scenarios considered
- [ ] Interaction flows and state changes clearly marked

### 2. Applicable Scope (Mandatory)
- [ ] Target countries/regions clearly defined
- [ ] Target platforms clearly defined

### 3. Material Completeness
- [ ] All attachments complete (PDF, Word, external files)
- [ ] Message channels complete (SMS, Push, Email)
- [ ] Interaction copy and multi-language text complete
- [ ] Data dictionary for interaction fields defined
- [ ] BI metrics clearly defined

**Important Notes:**
- Message channels: All user touchpoints including SMS, email, popups, app push
- Email attachments: Avoid attachments, use download links in email body
- Download link expiry: Max 1 year validity
- If attachments required: Max 3MB size

### 4. Feature Reusability (Mandatory)
- [ ] Single-country limitation justified
- [ ] Cross-country applicability analyzed
- [ ] All product types supported or customization justified
- [ ] All terminals supported or customization justified

**Terminals:** Fuse Pro, Fina (WhatsApp, Zalo, Line), PC Web, H5 Web

### 5. Workflows & Rules (Mandatory)
- [ ] Business entry conditions defined
- [ ] Data sources clearly identified
- [ ] Forward operation flows complete (CRUD, workflows)
- [ ] Permission descriptions complete
- [ ] Exception flows complete
- [ ] Exception guidance clear and actionable
- [ ] Reverse flows complete
- [ ] Backward compatibility considered
- [ ] Boundary conditions and exceptions detailed
- [ ] Risk control rules defined
- [ ] Required test types specified

**Critical Rules:**
- Money-related manual operations MUST have multi-level review
- Automated processes MUST have sampling for manual audit
- Paid services (SMS, Email) MUST have traffic monitoring

### 6. Data (Mandatory)
- [ ] All display fields have clear data sources and processing logic
- [ ] Amount calculations have clear formulas and data lineage

### 7. Performance & Business Metrics (Mandatory)
- [ ] Throughput evaluated, data retention period defined
- [ ] SLA requirements: min concurrency, response time, maintenance windows
- [ ] 3-year business scale projection
- [ ] Data archival cycle defined

### 8. Analytics (Mandatory)
- [ ] Backend analytics requirements identified
- [ ] Redundant data fields identified

### 9. Release Description (Mandatory)
- [ ] Release plan complete (feature flags, config checks, deployment order)
- [ ] Feature flag enable/disable conditions and impact scope defined
- [ ] Pre-release verification and rollback plan included
- [ ] Deployment order considers system dependencies and risk control

### 10. Technical Feasibility (Mandatory)
- [ ] Data availability confirmed
- [ ] System framework compatibility confirmed
- [ ] Third-party integration feasibility confirmed (network, security)

## Output Format

```markdown
# PRD Review Report

## Summary
- Document: [PRD Name]
- Review Date: [Date]
- Overall Status: [PASS/FAIL]

## Checklist Results
| Category | Status | Issues |
|----------|--------|--------|
| Completeness | ✅/❌ | [details] |
| Scope | ✅/❌ | [details] |
...

## Critical Issues
1. [Issue description and recommendation]

## Recommendations
1. [Improvement suggestion]
```
