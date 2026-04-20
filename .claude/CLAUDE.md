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

## Architecture Patterns
- Redux-style state management in LangGraph subgraphs: states, actions, per-(state, action) reducer functions.
- Reducer signature: always `(state, action, logger)` — prefix unused params with `_`.
- Use `get_tasks_substate(state, expected_type)` for typed state access in nodes.
- Tool node return dicts use `tasks_substate` key (not `router_state`).
- Parse tool args with typed Pydantic input models (public, not prefixed with `_`).
- Pass `tool_input=args.model_dump()` to `arun` (dict, not Pydantic model).
