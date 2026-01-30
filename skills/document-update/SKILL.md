---
name: document-update
description: This skill manages document linkage and synchronization rules for PRD and prototype documents. It should be used when documents need coordinated updates to maintain consistency. The skill ensures proper version management and change propagation across related documents.
license: MIT
compatibility: Works with any documentation workflow. Requires document access.
metadata:
  category: maintenance
  phase: documentation
  version: "1.0.0"
---

# Document Update Skill

This skill manages document linkage and synchronization.

## When to Use

Use this skill when:
- PRD document is modified
- Prototype document is modified
- New feature iteration is added
- Document consistency needs verification

## Core Rules

### Rule 1: PRD as Master Document
- `PRD方案.md` serves as the master product design document
- All content must be based on this document
- Any product feature or design changes MUST be updated here first

### Rule 2: Prototype Document Linkage
- `PRD产品原型设计文档.md` is based on `PRD方案.md`
- Every modification to `PRD方案.md` MUST trigger update to prototype document
- Prototype changes MUST be reflected back to this document

### Rule 3: New Feature Iterations
- New features require creating `PRD方案_${version}.md`
- Version number follows iteration cycle

## Update Order

```
PRD方案.md (Master)
    │
    ▼
产品原型设计文档.md (Prototype)
```

**Critical:** Always follow this order for document updates.

## Version Management

### New Feature Pattern
```
PRD方案_v1.0.md
PRD方案_v1.1.md
PRD方案_v2.0.md
```

### Change Log Format
```markdown
## Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2024-01-15 | v1.1 | [Name] | Added feature X |
| 2024-01-10 | v1.0 | [Name] | Initial version |
```

## Synchronization Checklist

When updating documents:

- [ ] Identify source document change
- [ ] Update master PRD document
- [ ] Propagate changes to prototype document
- [ ] Update version numbers
- [ ] Add change log entries
- [ ] Verify cross-references
- [ ] Notify stakeholders

## Output

After synchronization:
- List of updated documents
- Change log entries
- Verification status
