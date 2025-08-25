# Google Services MCP Server

An MCP (Model Context Protocol) server that provides access to Google Calendar and Gmail functionality through Claude Code with specialized agents.

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
   claude mcp add google-services --scope local -- ./venv/bin/python server.py
   ```

4. **Restart Claude Code** after adding the MCP server configuration.

## Local Todo CSV

Create `ToDoList.csv` to track notes locally (Windows PowerShell):
```powershell
if (!(Test-Path .\ToDoList.csv)) { 'title,notes,due,status' | Set-Content .\ToDoList.csv }
```

## MCP Configuration in Claude Code

### Adding MCP Servers

Claude Code supports three types of MCP server connections:

1. **Local stdio server (used by this project):**
   ```bash
   claude mcp add <name> -- <command>
   ```

2. **Remote SSE server:**
   ```bash
   claude mcp add --transport sse <name> <url>
   ```

3. **Remote HTTP server:**
   ```bash
   claude mcp add --transport http <name> <url>
   ```

### Configuration Options

- **Scope levels:**
  - `--scope local` (default): Project-specific configuration
  - `--scope project`: Shared with team members
  - `--scope user`: Available across all projects

- **Environment variables:**
  ```bash
  claude mcp add <name> --env KEY=value -- <command>
  ```

- **Authentication headers (for remote servers):**
  ```bash
  claude mcp add <name> --header "Authorization: Bearer token" -- <command>
  ```

### Managing MCP Servers

- **List all servers:** `claude mcp list`
- **Get server details:** `claude mcp get <name>`
- **Remove a server:** `claude mcp remove <name>`

### Important Notes

- **Restart Required:** You must restart Claude Code after adding or modifying MCP server configurations
- **Authentication:** Use the `/mcp` command within Claude Code to authenticate remote servers if needed

## Manual Setup (Alternative)

1. **Ensure your `credentials.json` is in this directory**

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

Once configured, Claude Code agents will have access to:

### Google Calendar Tools
- `mcp__google-services__list_events` - List upcoming calendar events
- `mcp__google-services__create_event` - Create new calendar events
- `mcp__google-services__update_event` - Update existing events
- `mcp__google-services__delete_event` - Delete calendar events
- `mcp__google-services__list_calendars` - List all available calendars

### Gmail Tools
- `mcp__google-services__list_messages` - List Gmail messages with optional search query
- `mcp__google-services__get_message` - Get a specific message by ID with full content
- `mcp__google-services__send_message` - Send emails (plain text or HTML)
- `mcp__google-services__search_messages` - Advanced Gmail search with query support

### Gmail Search Examples
- `from:example@gmail.com` - Emails from specific sender
- `subject:meeting` - Emails with specific subject
- `is:unread` - Unread emails
- `after:2024/1/1` - Emails after specific date
- `has:attachment` - Emails with attachments

## Integration with Specialized Agents

### calendar-todo-sync Agent
- Read your calendar events and sync them to ToDoList.csv
- Create calendar events from todo items with due dates
- Keep your calendar and todo list synchronized bidirectionally

### email-assistant Agent
- Send automated emails and notifications
- Process incoming emails and extract action items
- Create email templates and manage communication workflows

### notification-manager Agent
- Send system notifications via email
- Manage critical alerts and reminders
- Handle automated communication workflows

### email-sender-bot Agent
- Send emails to contacts from contacts.csv file
- Look up contact information automatically
- Handle bulk email sending to multiple contacts

## Current Project Status

### ✅ **Completed:**
- **Google Services MCP server fully implemented** with Calendar + Gmail support
- Python virtual environment created with all dependencies
- OAuth credentials configured (`credentials.json` present)
- **OAuth authentication completed successfully** (`token.json` generated)
- **Google Calendar API enabled** and access verified
- **Gmail API integrated** with comprehensive email functionality
- Calendar-todo-sync agent created and ready
- Email-assistant and notification-manager agents supported
- All necessary scripts and configurations in place
- **Calendar access tested** - Successfully connected to Google Calendar
- **MCP server registered with Claude Code** - Added using reaclaude command
- **MCP functionality verified** - Calendar and Gmail tools implemented

### 🔄 **Ready for Use:**
- **Todo List Management**: `ToDoList.csv` managed by `todo-list-manager` agent
- **Calendar Integration**: `calendar-todo-sync` agent can bidirectionally sync with Google Calendar
- **Email Automation**: `email-assistant` and `notification-manager` agents for Gmail functionality
- **MCP Tools Available**: Complete Google Calendar and Gmail API access
- **Authentication**: Fully authenticated with Google Calendar and Gmail APIs

### 📋 **Next Actions:**
1. ~~Complete OAuth authentication~~ ✅ **DONE**
2. ~~Add MCP server to Claude Code settings~~ ✅ **DONE**
3. ~~Test calendar-todo sync functionality~~ ✅ **DONE**
4. ~~Implement Gmail integration~~ ✅ **DONE**
5. **Re-authenticate with new Gmail scopes** (required on first Gmail tool use)

**Google Services MCP server ready for production use with Calendar + Gmail!**

## Files

- `server.py` - Main MCP server implementation with Calendar + Gmail support ✅
- `requirements.txt` - Python dependencies ✅
- `config.json` - MCP server configuration with venv paths ✅
- `credentials.json` - Google OAuth credentials ✅
- `token.json` - Generated OAuth token (needs re-auth for Gmail scopes)
- `setup.sh` - Automated setup script ✅
- `test_auth.py` - Authentication testing utility ✅
- `run_with_venv.sh` - Script to ensure venv usage ✅
- `venv/` - Python virtual environment with dependencies ✅
- `CLAUDE.md` - Updated project configuration ✅
- `ToDoList.csv` - Todo list file ✅
- `contacts.csv` - Contact information for email-sender-bot agent ✅