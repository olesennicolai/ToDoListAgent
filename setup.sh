#!/bin/bash

echo "Google Calendar MCP Server Setup"
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Check if credentials exist
if [ ! -f "credentials.json" ]; then
    echo "❌ ERROR: credentials.json not found!"
    echo "Please download your Google OAuth credentials and save as 'credentials.json'"
    exit 1
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Run authentication: ./venv/bin/python test_auth.py"
echo "2. Complete OAuth in browser when prompted"
echo "3. Add this MCP server to Claude Code using config.json"
echo ""
echo "The calendar-todo-sync agent will then have access to these tools:"
echo "  - mcp__list_events"
echo "  - mcp__create_event" 
echo "  - mcp__update_event"
echo "  - mcp__delete_event"
echo "  - mcp__list_calendars"