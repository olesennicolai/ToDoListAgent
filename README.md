# Google Calendar MCP Server

An MCP (Model Context Protocol) server that provides access to Google Calendar functionality through Claude Code and the calendar-todo-sync agent.

## Quick Setup

1. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

2. **Complete authentication:**
   ```bash
   ./venv/bin/python test_auth.py
   ```
   Follow the URL in the output to complete OAuth authentication in your browser.

3. **Add to Claude Code:**
   ```bash
   reaclaude mcp add google-calendar --scope local -- ./venv/bin/python server.py
   ```

## Manual Setup (Alternative)

1. **Ensure your `credentials.json` is in this directory** ✅ (Already present)

2. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Test authentication:**
   ```bash
   ./venv/bin/python test_auth.py
   ```

## Available MCP Tools

Once configured, the calendar-todo-sync agent will have access to:

- `mcp__list_events` - List upcoming calendar events
- `mcp__create_event` - Create new calendar events
- `mcp__update_event` - Update existing events
- `mcp__delete_event` - Delete calendar events
- `mcp__list_calendars` - List all available calendars

## Integration with calendar-todo-sync Agent

The calendar-todo-sync agent can now:
- Read your calendar events and sync them to ToDoList.csv
- Create calendar events from todo items with due dates
- Keep your calendar and todo list synchronized bidirectionally

## Current Project Status

### ✅ **Completed:**
- Google Calendar MCP server fully implemented
- Python virtual environment created with all dependencies
- OAuth credentials configured (`credentials.json` present)
- **OAuth authentication completed successfully** (`token.json` generated)
- **Google Calendar API enabled** and access verified
- Calendar-todo-sync agent created and ready
- All necessary scripts and configurations in place
- **Calendar access tested** - Successfully connected to Google Calendar with 2 calendars detected
- **MCP server registered with Claude Code** - Added using reaclaude command
- **MCP functionality verified** - Successfully listed events and created new calendar entries

### 🔄 **Ready for Use:**
- **Todo List Management**: `ToDoList.csv` managed by `todo-list-manager` agent
- **Calendar Integration**: `calendar-todo-sync` agent can bidirectionally sync with Google Calendar
- **MCP Tools Available**: List/create/update/delete calendar events
- **Authentication**: Fully authenticated with Google Calendar API

### 📋 **Next Actions Needed:**
1. ~~Complete OAuth authentication~~ ✅ **DONE**
2. ~~Add MCP server to Claude Code settings~~ ✅ **DONE**
3. ~~Test calendar-todo sync functionality with real data~~ ✅ **DONE**

**All setup and testing complete! Ready for production use.**

## Files

- `server.py` - Main MCP server implementation ✅
- `requirements.txt` - Python dependencies ✅
- `config.json` - MCP server configuration with venv paths ✅
- `credentials.json` - Google OAuth credentials ✅
- `token.json` - Generated OAuth token ✅ **CREATED**
- `setup.sh` - Automated setup script ✅
- `test_auth.py` - Authentication testing utility ✅
- `run_with_venv.sh` - Script to ensure venv usage ✅
- `venv/` - Python virtual environment with dependencies ✅
- `CLAUDE.md` - Updated project configuration ✅
- `ToDoList.csv` - Todo list file ✅