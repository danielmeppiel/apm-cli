---
applyTo: "**/*{test,spec}*"
description: "Testing guidelines and best practices"
---

## Testing Best Practices

### Test Structure
- Follow the Arrange-Act-Assert pattern
- Use descriptive test names that explain the behavior
- Keep tests focused on a single concern
- Group related tests using nested describe blocks

### Test Quality
- Write tests that are independent and can run in any order
- Use appropriate assertions that provide clear failure messages
- Mock external dependencies appropriately
- Avoid testing implementation details

### Coverage and Performance
- Aim for high test coverage but focus on meaningful tests
- Test edge cases and error conditions
- Write fast-running unit tests
- Use integration tests sparingly for critical paths

### Test Data
- Use factories or builders for creating test data
- Keep test data minimal and relevant
- Use realistic but safe test data
- Clean up test data after each test

See [project architecture](../context/architecture.context.md) for testing patterns.