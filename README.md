# Personal Agentic AI Assistant Built with LangChain

A personal AI assistant you interact with through Telegram using [python-telegram-bot](https://python-telegram-bot.org/). It helps with everyday tasks like managing to-do lists, searching for jobs, checking the weather and sends a morning briefing each day with an overview of what's ahead.

Built in Python with [LangChain](https://www.langchain.com/), it implements the agentic loop pattern with tool calling and human-in-the-loop confirmation flows. The project is fully async, running on the event loop with [FastAPI](https://fastapi.tiangolo.com/), and uses dependency injection via [dependency-injector](https://python-dependency-injector.ets-labs.org/) with a clean modular structure. It supports scheduled cron jobs via [APScheduler](https://pypi.org/project/APScheduler/), file uploads, versioned database migrations, and a persistence layer with [SQLModel](https://sqlmodel.tiangolo.com/) and [PostgreSQL](https://www.postgresql.org/). Deployed with [Docker](https://www.docker.com/) and [Ansible](https://docs.ansible.com/) via a [GitHub Actions](https://github.com/features/actions) CI/CD pipeline.

## Architecture

### Structure

```
├── agent/
├── channels/
├── files/
├── job_search/
├── microsoft_todo/
├── patches/
├── scheduled_jobs/
├── utils/
├── weather/
```

* `agent/` contains the LangGraph agent with the planner node, tool registry, and all tool nodes (tasks, job search, weather).
* `channels/` contains messaging channel integrations, currently Telegram (bot setup, message handling, sending).
* `files/` contains file upload handling, storage, and parsing.
* `job_search/` contains the job search domain logic including job models, repositories, and LLM-based classification.
* `microsoft_todo/` contains the Microsoft To Do API client for task management.
* `patches/` contains the database migration system with versioned patches.
* `scheduled_jobs/` contains scheduled cron jobs like the daily morning briefing.
* `utils/` contains shared infrastructure like config, database, HTTP client, LLM builder, and the patcher framework.
* `weather/` contains the weather service for fetching forecasts.

### Agentic Loop with Tool Calling

The [agentic loop](https://code.claude.com/docs/en/agent-sdk/agent-loop) is a pattern where an LLM is given a set of tools it can call. When a message comes in, the LLM decides whether to respond with text or call one or more tools. If tools are called, they are executed and their results are fed back to the LLM. The LLM then decides again whether the goal is reached and it can respond with text, or whether further tool calls are needed. This loop continues until the LLM produces a final text response.

The agent is built as a [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) state graph with a planner node at the center. The planner node calls the LLM with all registered tools bound. Based on the LLM's response, it either responds with text or dispatches to tool nodes. Tools can be executed in parallel when the LLM decides to call multiple tools at once. When a tool is called, it produces two separate messages: a readable message that is sent directly to the chat channel so the user can follow along, and a tool message that is fed back to the LLM for further reasoning. After all tool nodes have finished, a merge node collects the readable tool messages and adds them to the conversation history. The planner is then invoked again to decide whether to respond with text or make further tool calls.

This process is managed by a graph state that transitions through typed states driven by actions. A reducer function takes the current state and an incoming action and produces the next state.

For example, when a user asks "What's the weather and what are my tasks for today?":

1. The user sends a message and the graph enters the planner node. A `NewMessageAction` is fired and `BaseState` transitions to `BaseState` with the message added to history.
2. The planner calls the LLM, which decides to call the weather and tasks tools. An `ExecuteToolCallsAction` is fired and `BaseState` transitions to `ExecuteToolCallsState`. A conditional edge routes after the planner: since the state is `ExecuteToolCallsState`, it sends a [Send](https://reference.langchain.com/python/langgraph/types/Send) to each tool node. Before each tool node runs, a message like "Calling the Weather Tool..." is sent to the chat.
3. Both tool nodes execute in parallel. Each produces an `ExecutedToolAction` containing a `ToolMessage` for the LLM and a readable message that is sent to the chat. As the reducer merges the parallel results, `ExecuteToolCallsState` transitions to `ExecutedToolsState`, then stays `ExecutedToolsState` as more results arrive.
4. All tool nodes have a fixed edge to the merge node. The merge node fires a `MergeReadableToolMessagesAction` and `ExecutedToolsState` transitions back to `BaseState` with the readable messages added to history. A fixed edge loops back to the planner node.
5. The planner calls the LLM again, which responds with text. A `RespondWithTextAction` is fired and `BaseState` transitions to `BaseState`. The conditional edge sees `BaseState` and routes to `END`.

Certain tools are marked as non-parallel in the tool registry. The planner is instructed via the system prompt to never call these tools in parallel with others. If the LLM violates this constraint, the agent catches it and asks the user to try again.

Each tool has its own dedicated node in the graph. Rather than using a single generic node to execute all tools, every tool is represented by its own node class.

Some tools require user confirmation before executing. In these cases, the tool node raises a LangGraph [interrupt](https://docs.langchain.com/oss/python/langgraph/interrupts) which pauses the graph and sends the question to the user. Once the user responds, the graph resumes from where it left off.

### Tools

#### Get Weather

Fetches the weather forecast for a given location and day (today, tomorrow, or the day after).

#### Get Tasks

Retrieves tasks from a Microsoft To Do list. Can filter by status and due date range.

#### Create Task

Creates a new task in a Microsoft To Do list. Supports due dates and recurring schedules (daily, weekly, monthly).

#### Update Task

Updates an existing task. Can change the title, due date, or mark it as completed.

#### Delete Task

Permanently deletes a task from a list.

#### Get Jobs

Refreshes and returns job postings for a given date range. Jobs are classified as interesting or not by an LLM.

#### Like Job

Marks a job posting as liked by the user.

#### Job Search Status

Returns the timestamp of the last job search.

#### Create Job Opening

Creates a job opening from an uploaded HTML file. The HTML is parsed by an LLM to extract title, summary, requirements, and company link. The user is asked for confirmation before saving.

### Channels

The communication layer currently supports Telegram as the only channel. Incoming text messages are forwarded to the agent. File uploads are also supported: the file is saved to disk, stored in the database, and the filename, MIME type, and UUID are forwarded to the agent as a text message.

### Scheduled Jobs

The project uses APScheduler to run async cron jobs on the event loop. Currently there is one scheduled job: the morning briefing. It runs every day at 7:00 AM and sends a Telegram message with the weather forecast, today's tasks from Microsoft To Do, and the number of new interesting job postings. The weather, tasks, and jobs are fetched in parallel using `asyncio.gather`.

### Database Patches

The project includes a custom database patching framework. Each patch is a class that extends the abstract `Patch` base class, has a version number, and implements an `apply` method that receives a database session. On startup, the patcher checks the current database version, finds all patches with a higher version number, and applies them in order. The current version is tracked in the database.

## Development

### Adding a New Tool

1. Create a tool class extending `BaseTool` with an input schema, name, description, and `response_format` set to `content_and_artifact`. The `_arun` method returns a tuple of two strings: the tool message for the LLM and the readable message for the user.
2. Create a node class that calls `invoke_tool` with the tool, the call from the state, and an error message.
3. Register the tool in the tool registry in `AgentContainer` with a `ToolRegistryEntry` (node name, display name, and whether it supports parallel execution).
4. Add the tool to the planner's tools list in `AgentContainer`.
5. Add the node and its edges in `CreateAgent`.

### Run Postgres locally

```bash
docker run -d --name mr-agent-pg -e POSTGRES_USER=mr_agent -e POSTGRES_PASSWORD='<password>' -e POSTGRES_DB=mr_agent -p 5432:5432 -v mr-agent-pg-data:/var/lib/postgresql postgres:18
```

### Update dependencies

```bash
./update_deps.sh
```

## Deployment

### 1. Create SSH key for GitHub Actions

```bash
ssh-keygen -t ed25519 -C "github" -f ansible/github
```

### 2. Add secrets to GitHub

Go to repo -> Settings -> Secrets and variables -> Actions:

- `SSH_KEY` - contents of the `github` private key file
- `SERVER_IP` - your server's IP address

Delete the private key after:

```bash
rm ansible/github
```

### 3. Create production environment file

Set the Postgres connection variables:

```
POSTGRES_USER=mr_agent
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=postgres
POSTGRES_DB=mr_agent
```

### 4. Create Ansible inventory

```bash
cp ansible/inventory.yml.example ansible/inventory.yml
```

Fill in your server IP and SSH key path.

### 5. Run Ansible

```bash
ansible-playbook -i ansible/inventory.yml ansible/setup.yml
```