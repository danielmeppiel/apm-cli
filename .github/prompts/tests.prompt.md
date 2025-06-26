---
description: Reviews code diff and identifies missing unit tests, then implements them
---

# Unit Test Gap Analysis & Implementation

Analyze the code changes between the current branch and the default branch to identify missing unit tests and implement them.

## Analysis Process

1. **Diff Review**: Examine the code changes to understand:
   - New functions and methods added
   - Modified logic and behavior
   - New classes and modules
   - Changed error handling paths

2. **Test Coverage Assessment**: Identify gaps in:
   - Happy path testing
   - Edge case coverage
   - Error condition testing
   - Input validation testing
   - Integration points

3. **Test Implementation**: Create basic unit tests for:
   - New public methods and functions
   - Modified business logic
   - Error handling scenarios
   - Input validation cases

## Test Categories to Consider

### Basic Function Tests
- Normal operation with valid inputs
- Return value verification
- State changes verification

### Edge Cases
- Boundary values (empty, null, max/min)
- Invalid input handling
- Resource constraints

### Error Scenarios
- Exception throwing and handling
- Error message accuracy
- Recovery behavior

### Integration Points
- External service interactions
- Database operations
- File system operations

## Output Format

For each missing test:
- **Function/Method**: Name and location
- **Test Type**: Unit/Integration/Edge case
- **Test Description**: What should be tested
- **Implementation**: Basic test code structure

Focus on practical, maintainable tests that provide real value in catching regressions and validating functionality.
