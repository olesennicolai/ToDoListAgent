# Claude Code Configuration

## Todo List Management
- Todo list file: `ToDoList.csv`
- Use the `todo-list-manager` agent when user asks to:
  - Read/check their todo list
  - Add new tasks
  - Mark tasks as completed
  - Get task recommendations
  - Manage task priorities

## Google Calendar & Gmail Integration
- MCP server configured for Google Calendar and Gmail access
- Use the `calendar-todo-sync` agent for:
  - Syncing calendar events to todo list
  - Creating calendar events from todos with due dates
  - Bidirectional calendar-todo synchronization
- Use the `task-orchestrator` agent for comprehensive task and calendar management
- Available MCP tools:
  - Calendar: `mcp__google-calendar__list_events`, `mcp__google-calendar__create_event`, `mcp__google-calendar__update_event`, `mcp__google-calendar__delete_event`, `mcp__google-calendar__list_calendars`
  - Gmail: `mcp__google-calendar__list_messages`, `mcp__google-calendar__get_message`, `mcp__google-calendar__send_message`, `mcp__google-calendar__search_messages`
  - Alternative Gmail tools: `mcp__gmail__*` (same functionality)

## Python Environment
- Python version: 3.12.3
- All Python commands must use virtual environment: `./venv/bin/python`
- Virtual environment location: `/mnt/c/Users/olese/Desktop/ToDoList/venv/`
- Dependencies: Google API client, OAuth libraries, MCP, python-dateutil

## MCP Server Configuration
- Main server file: `server.py` (Google Calendar and Gmail MCP Server)
- Calendar-Todo sync script: `calendar_todo_sync.py`
- MCP configuration: `config.json`
- Google OAuth credentials: `credentials.json`
- Authentication token: `token.json` (auto-generated)
- Setup script: `./setup.sh`
- Authentication test: `./venv/bin/python test_auth.py`
- Launcher script: `./run_with_venv.sh`

## Project Files
- Main todo list: `ToDoList.csv` (private, not tracked)
- Project documentation: `README.md`, `PROJECT_STATUS.md`
- Dependencies: `requirements.txt`
- Logs: `auth_output.log`
- Commands reference: `commands.txt`