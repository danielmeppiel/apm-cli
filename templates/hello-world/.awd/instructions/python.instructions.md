---
applyTo: "**/*.py"
description: "Python development guidelines"
---

## Python Development Standards

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Implement proper docstrings with examples
- Use dataclasses or Pydantic models for structured data

### Code Structure
- Organize code into logical modules and packages
- Use dependency injection for better testability
- Implement proper exception handling
- Follow the principle of least surprise

### Testing Requirements
- Write unit tests with pytest
- Use fixtures for test data setup
- Mock external dependencies appropriately
- Aim for comprehensive test coverage

### Performance
- Use appropriate data structures for the task
- Profile code when performance is critical
- Consider async/await for I/O bound operations
- Use generators for memory efficiency when processing large datasets