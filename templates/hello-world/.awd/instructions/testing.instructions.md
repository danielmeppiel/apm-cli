---
applyTo: "**/*{test,spec}*"
description: "Testing best practices and guidelines"
---

## Testing Best Practices

### Test Structure
- Use descriptive test names that explain the scenario
- Follow the Arrange-Act-Assert pattern
- Keep tests focused on a single behavior
- Use proper test data setup and teardown

### Test Quality
- Write tests that are independent and can run in any order
- Mock external dependencies to ensure test isolation
- Use meaningful assertions with clear error messages
- Test both happy path and edge cases

### Coverage Goals
- Aim for high test coverage but focus on meaningful tests
- Prioritize testing critical business logic
- Include integration tests for important workflows
- Test error handling and boundary conditions

### Test Organization
- Group related tests using describe/context blocks
- Use shared fixtures for common test data
- Keep test files close to the code they test
- Maintain test code with the same quality standards as production code