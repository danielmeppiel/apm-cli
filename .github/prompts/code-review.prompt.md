---
description: Reviews code for security, quality and accessibility issues
---

# Code Security, Quality & Accessibility Review

Analyze the provided code for security vulnerabilities, quality issues, and accessibility problems. Focus on actionable findings with clear recommendations.

## Security Review
- Input validation and sanitization
- Authentication and authorization flaws
- Sensitive data exposure or logging
- Injection vulnerabilities (SQL, XSS, command)
- Cryptography and key management
- Dependency vulnerabilities
- Information disclosure in error handling

## Quality Review
- Code structure and maintainability
- Performance bottlenecks
- Error handling completeness
- Documentation adequacy
- Code duplication
- Naming conventions
- Test coverage gaps

## Accessibility Review
- ARIA labels and semantic HTML
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Focus management
- Form accessibility
- Responsive design considerations

## Output Format
For each issue found:
- **Category**: Security/Quality/Accessibility
- **Severity**: Critical/High/Medium/Low
- **Location**: File and line reference
- **Issue**: Brief description
- **Fix**: Specific recommendation

Prioritize critical security issues first, then high-impact quality and accessibility problems.
