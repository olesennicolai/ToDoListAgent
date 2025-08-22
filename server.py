#!/usr/bin/env python3
"""
Google Calendar MCP Server
Provides access to Google Calendar API through MCP protocol
"""

import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events']

# Token file to store user's access and refresh tokens
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

app = Server("google-calendar")

class GoogleCalendarService:
    def __init__(self):
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(f"Please place your Google credentials file at {CREDENTIALS_FILE}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def list_events(self, calendar_id: str = 'primary', max_results: int = 10, 
                   time_min: Optional[str] = None, time_max: Optional[str] = None) -> List[Dict[str, Any]]:
        """List events from a calendar"""
        try:
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def create_event(self, calendar_id: str = 'primary', **event_data) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            return event
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def update_event(self, event_id: str, calendar_id: str = 'primary', **event_data) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data
            ).execute()
            return event
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars"""
        try:
            calendar_list = self.service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")

# Initialize Google Calendar service
calendar_service = GoogleCalendarService()

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Google Calendar tools"""
    return [
        Tool(
            name="list_events",
            description="List events from Google Calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (default: primary)",
                        "default": "primary"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return",
                        "default": 10
                    },
                    "time_min": {
                        "type": "string",
                        "description": "Start time for events (ISO format)"
                    },
                    "time_max": {
                        "type": "string",
                        "description": "End time for events (ISO format)"
                    }
                }
            }
        ),
        Tool(
            name="create_event",
            description="Create a new Google Calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (default: primary)",
                        "default": "primary"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Event title/summary"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO format)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (ISO format)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location"
                    }
                },
                "required": ["summary", "start_time", "end_time"]
            }
        ),
        Tool(
            name="update_event",
            description="Update an existing Google Calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to update"
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (default: primary)",
                        "default": "primary"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Event title/summary"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO format)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (ISO format)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="delete_event",
            description="Delete a Google Calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to delete"
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Calendar ID (default: primary)",
                        "default": "primary"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="list_calendars",
            description="List all available Google Calendars",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "list_events":
            events = calendar_service.list_events(**arguments)
            events_text = "📅 **Google Calendar Events**\n\n"
            
            if not events:
                events_text += "No upcoming events found."
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    summary = event.get('summary', 'No title')
                    events_text += f"• **{summary}**\n"
                    events_text += f"  📅 {start}\n"
                    if event.get('description'):
                        events_text += f"  📝 {event['description'][:100]}...\n"
                    events_text += "\n"
            
            return [types.TextContent(type="text", text=events_text)]
        
        elif name == "create_event":
            # Build event object
            event_data = {
                'summary': arguments['summary'],
                'start': {
                    'dateTime': arguments['start_time'],
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': arguments['end_time'],
                    'timeZone': 'UTC',
                }
            }
            
            if arguments.get('description'):
                event_data['description'] = arguments['description']
            if arguments.get('location'):
                event_data['location'] = arguments['location']
            
            calendar_id = arguments.get('calendar_id', 'primary')
            event = calendar_service.create_event(calendar_id, **event_data)
            
            return [types.TextContent(
                type="text", 
                text=f"✅ Event created successfully!\n\n**{event.get('summary')}**\nEvent ID: {event.get('id')}\nLink: {event.get('htmlLink')}"
            )]
        
        elif name == "update_event":
            event_id = arguments.pop('event_id')
            calendar_id = arguments.pop('calendar_id', 'primary')
            
            # Build update data
            event_data = {}
            if arguments.get('summary'):
                event_data['summary'] = arguments['summary']
            if arguments.get('description'):
                event_data['description'] = arguments['description']
            if arguments.get('location'):
                event_data['location'] = arguments['location']
            if arguments.get('start_time'):
                event_data['start'] = {'dateTime': arguments['start_time'], 'timeZone': 'UTC'}
            if arguments.get('end_time'):
                event_data['end'] = {'dateTime': arguments['end_time'], 'timeZone': 'UTC'}
            
            event = calendar_service.update_event(event_id, calendar_id, **event_data)
            
            return [types.TextContent(
                type="text", 
                text=f"✅ Event updated successfully!\n\n**{event.get('summary')}**\nEvent ID: {event.get('id')}"
            )]
        
        elif name == "delete_event":
            event_id = arguments['event_id']
            calendar_id = arguments.get('calendar_id', 'primary')
            
            calendar_service.delete_event(event_id, calendar_id)
            
            return [types.TextContent(
                type="text", 
                text=f"✅ Event deleted successfully!\nEvent ID: {event_id}"
            )]
        
        elif name == "list_calendars":
            calendars = calendar_service.list_calendars()
            calendars_text = "📅 **Available Calendars**\n\n"
            
            for calendar in calendars:
                calendars_text += f"• **{calendar.get('summary')}**\n"
                calendars_text += f"  ID: {calendar.get('id')}\n"
                if calendar.get('description'):
                    calendars_text += f"  📝 {calendar.get('description')}\n"
                calendars_text += "\n"
            
            return [types.TextContent(type="text", text=calendars_text)]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

def main():
    """Run the MCP server"""
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(run())

if __name__ == "__main__":
    main()