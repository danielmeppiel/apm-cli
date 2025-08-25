---
description: "Implement a new feature following AWD best practices"
input:
  - feature_name: "Name of the feature to implement"
  - feature_description: "Detailed description of the feature"
---

# Feature Implementation Workflow

## Overview
Implement the feature: **${input:feature_name}**

Description: ${input:feature_description}

## Implementation Steps

### 1. Specification Review
- [ ] Review [feature specification](.awd/specs/hello-feature.md)
- [ ] Understand requirements and acceptance criteria
- [ ] Identify dependencies and potential conflicts

### 2. Design Phase
- [ ] Create component/module design
- [ ] Define interfaces and data structures
- [ ] Plan testing strategy
- [ ] Consider performance implications

### 3. Implementation
- [ ] Write unit tests first (TDD approach)
- [ ] Implement core functionality
- [ ] Add integration tests
- [ ] Update documentation

### 4. Validation
- [ ] Run full test suite
- [ ] Perform code review
- [ ] Test in staging environment
- [ ] Update CHANGELOG.md

## Success Criteria
- All tests pass
- Code coverage above 80%
- Documentation updated
- No breaking changes to existing APIs