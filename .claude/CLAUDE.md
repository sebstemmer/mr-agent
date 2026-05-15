# Project Instructions

## General Rules
- Only write code when explicitly instructed. Do not proactively code, refactor, or fix things that were not asked for.
- Never modify LLM system prompts or tool descriptions without explicit user approval.
- Always use named/keyword arguments in Python code.
- Use leading underscore for internal module-level variables (e.g. `_TOOL_NAME`).
- Give opinionated takes on design decisions — don't just list options.
- Do not rush planning. Stay at the user's pace.
- Do not summarize what you just did at the end of every response.

## Naming Conventions
- Services: verb-first names (e.g. `CreateTasksSubgraph`, `HandleWeatherNode`).
- Repositories: Spring Boot-style method names (e.g. `find_by_status`, `save`, `delete_by_id`).
- Service main method: named after the class verb (e.g. `CreateTasksSubgraph.create()`, `HandleWeatherNode.handle()`).

## Environment Variables
- When adding a new variable to `Settings` in `config.py`, also add it to `.env`, `.env.production`, and `.env.example`.