# Project Information

## {{project_name}} APM Project

This is a demonstration project showcasing APM (Agentic Primitives Manager) primitives compilation into AGENTS.md format.

### Project Goals
- Demonstrate APM primitive compilation
- Provide working examples of chatmodes, instructions, and context files
- Show integration with existing coding agent CLIs
- Validate the Phase 1 MVP functionality

### Technology Stack
- **Language**: Multi-language support (TypeScript, Python)
- **Runtime**: APM CLI with Codex/LLM integration
- **Testing**: Jest (TypeScript), pytest (Python)
- **Build**: Standard ecosystem tooling

### Development Workflow
1. Modify primitives in `.apm/` directory
2. Run `apm compile` to generate AGENTS.md
3. Use `apm compile --watch` during active development
4. Execute workflows with `apm run [workflow].prompt.md`

### Key Features
- Conditional instruction sections based on file types
- Chatmode selection for different development contexts
- Context file linking for shared knowledge
- Automated project setup detection