# Claude Code Configuration

## Todo List Management
- Todo list file: `ToDoList.csv`
- Use the `todo-list-manager` agent when user asks to:
  - Read/check their todo list
  - Add new tasks
  - Mark tasks as completed
  - Get task recommendations
  - Manage task priorities

## Google Calendar Integration
- MCP server configured for Google Calendar access
- Use the `calendar-todo-sync` agent for:
  - Syncing calendar events to todo list
  - Creating calendar events from todos with due dates
  - Bidirectional calendar-todo synchronization
- Available MCP tools: `mcp__list_events`, `mcp__create_event`, `mcp__update_event`, `mcp__delete_event`, `mcp__list_calendars`

## Python Environment
- All Python commands must use virtual environment: `./venv/bin/python`
- Virtual environment location: `/mnt/c/Users/olese/Desktop/ToDoList/venv/`
- Dependencies installed in venv for Google Calendar API and MCP server
- MCP server runs via: `./venv/bin/python server.py`

## MCP Server Configuration
- Server file: `server.py`
- Configuration: `config.json`
- Credentials: `credentials.json` (Google OAuth)
- Authentication token: `token.json` (auto-generated)
- Setup script: `./setup.sh`
- Test script: `./venv/bin/python test_auth.py`