---
applyTo: "**/*.{ts,tsx}"
description: "TypeScript development guidelines"
---

## TypeScript Development Standards

### Type Safety
- Use strict TypeScript configuration
- Prefer interfaces over types for object shapes
- Implement proper generic constraints
- Avoid `any` type - use `unknown` for dynamic content

### Code Structure
- Use barrel exports for clean imports
- Implement proper error boundaries in React components
- Follow functional programming principles where appropriate
- Use composition over inheritance

### Testing Requirements
- Write unit tests for all utility functions
- Test React components with React Testing Library
- Implement integration tests for API interactions
- Achieve minimum 80% code coverage

See the project architecture context for detailed patterns.