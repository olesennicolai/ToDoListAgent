#!/usr/bin/env python3
"""
Google Calendar and Gmail MCP Server
Provides access to Google Calendar and Gmail APIs through MCP protocol
"""

import json
import os
import base64
import email
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# Google API scopes (Calendar + Gmail)
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']

# Token file to store user's access and refresh tokens
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

app = Server("google-services")

class GoogleServicesClient:
    def __init__(self):
        self.calendar_service = None
        self.gmail_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs"""
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
        
        self.calendar_service = build('calendar', 'v3', credentials=creds)
        self.gmail_service = build('gmail', 'v1', credentials=creds)
    
    def list_events(self, calendar_id: str = 'primary', max_results: int = 10, 
                   time_min: Optional[str] = None, time_max: Optional[str] = None) -> List[Dict[str, Any]]:
        """List events from a calendar"""
        try:
            if not time_min:
                time_min = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
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
            event = self.calendar_service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            return event
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def update_event(self, event_id: str, calendar_id: str = 'primary', **event_data) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            event = self.calendar_service.events().update(
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
            self.calendar_service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars"""
        try:
            calendar_list = self.calendar_service.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def list_messages(self, query: str = '', max_results: int = 10) -> List[Dict[str, Any]]:
        """List Gmail messages"""
        try:
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = result.get('messages', [])
            
            # Get details for each message
            detailed_messages = []
            for msg in messages:
                msg_detail = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id'], format='full'
                ).execute()
                detailed_messages.append(msg_detail)
            
            return detailed_messages
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get a specific Gmail message"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            return message
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def send_message(self, to: str, subject: str, body: str, body_type: str = 'plain') -> Dict[str, Any]:
        """Send a Gmail message"""
        try:
            if body_type == 'html':
                message = MIMEMultipart('alternative')
                message['to'] = to
                message['subject'] = subject
                html_part = MIMEText(body, 'html')
                message.attach(html_part)
            else:
                message = MIMEText(body, 'plain')
                message['to'] = to
                message['subject'] = subject
            
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.gmail_service.users().messages().send(
                userId='me', body={'raw': raw_message}
            ).execute()
            
            return sent_message
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")
    
    def search_messages(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search Gmail messages with advanced query"""
        try:
            result = self.gmail_service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            messages = result.get('messages', [])
            
            # Get basic details for search results
            detailed_messages = []
            for msg in messages[:10]:  # Limit detailed fetch to first 10
                msg_detail = self.gmail_service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                detailed_messages.append(msg_detail)
            
            return detailed_messages
        except HttpError as error:
            raise Exception(f"An error occurred: {error}")

# Initialize Google Services client
google_client = GoogleServicesClient()

@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Google Calendar and Gmail tools"""
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
        ),
        Tool(
            name="list_messages",
            description="List Gmail messages",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (optional)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to return",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="get_message",
            description="Get a specific Gmail message by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "Gmail message ID"
                    }
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="send_message",
            description="Send a Gmail message",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content"
                    },
                    "body_type": {
                        "type": "string",
                        "description": "Body type: 'plain' or 'html'",
                        "default": "plain"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="search_messages",
            description="Search Gmail messages with advanced query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting', 'is:unread')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of messages to return",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "list_events":
            events = google_client.list_events(**arguments)
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
            event = google_client.create_event(calendar_id, **event_data)
            
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
            
            event = google_client.update_event(event_id, calendar_id, **event_data)
            
            return [types.TextContent(
                type="text", 
                text=f"✅ Event updated successfully!\n\n**{event.get('summary')}**\nEvent ID: {event.get('id')}"
            )]
        
        elif name == "delete_event":
            event_id = arguments['event_id']
            calendar_id = arguments.get('calendar_id', 'primary')
            
            google_client.delete_event(event_id, calendar_id)
            
            return [types.TextContent(
                type="text", 
                text=f"✅ Event deleted successfully!\nEvent ID: {event_id}"
            )]
        
        elif name == "list_calendars":
            calendars = google_client.list_calendars()
            calendars_text = "📅 **Available Calendars**\n\n"
            
            for calendar in calendars:
                calendars_text += f"• **{calendar.get('summary')}**\n"
                calendars_text += f"  ID: {calendar.get('id')}\n"
                if calendar.get('description'):
                    calendars_text += f"  📝 {calendar.get('description')}\n"
                calendars_text += "\n"
            
            return [types.TextContent(type="text", text=calendars_text)]
        
        elif name == "list_messages":
            query = arguments.get('query', '')
            max_results = arguments.get('max_results', 10)
            messages = google_client.list_messages(query=query, max_results=max_results)
            
            messages_text = "📧 **Gmail Messages**\n\n"
            if not messages:
                messages_text += "No messages found."
            else:
                for msg in messages:
                    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                    subject = headers.get('Subject', 'No subject')
                    sender = headers.get('From', 'Unknown sender')
                    date = headers.get('Date', 'Unknown date')
                    
                    messages_text += f"• **{subject}**\n"
                    messages_text += f"  👤 {sender}\n"
                    messages_text += f"  📅 {date}\n"
                    messages_text += f"  🆔 {msg.get('id')}\n\n"
            
            return [types.TextContent(type="text", text=messages_text)]
        
        elif name == "get_message":
            message_id = arguments['message_id']
            message = google_client.get_message(message_id)
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            subject = headers.get('Subject', 'No subject')
            sender = headers.get('From', 'Unknown sender')
            date = headers.get('Date', 'Unknown date')
            
            # Extract message body
            body = ""
            payload = message.get('payload', {})
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            elif payload.get('mimeType') == 'text/plain':
                data = payload.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            message_text = f"📧 **{subject}**\n\n"
            message_text += f"**From:** {sender}\n"
            message_text += f"**Date:** {date}\n"
            message_text += f"**Message ID:** {message_id}\n\n"
            message_text += f"**Body:**\n{body[:500]}..." if len(body) > 500 else f"**Body:**\n{body}"
            
            return [types.TextContent(type="text", text=message_text)]
        
        elif name == "send_message":
            to = arguments['to']
            subject = arguments['subject']
            body = arguments['body']
            body_type = arguments.get('body_type', 'plain')
            
            sent_message = google_client.send_message(to, subject, body, body_type)
            
            return [types.TextContent(
                type="text",
                text=f"✅ Email sent successfully!\n\n**To:** {to}\n**Subject:** {subject}\n**Message ID:** {sent_message.get('id')}"
            )]
        
        elif name == "search_messages":
            query = arguments['query']
            max_results = arguments.get('max_results', 20)
            messages = google_client.search_messages(query, max_results)
            
            search_text = f"🔍 **Search Results for:** {query}\n\n"
            if not messages:
                search_text += "No messages found matching the query."
            else:
                for msg in messages:
                    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                    subject = headers.get('Subject', 'No subject')
                    sender = headers.get('From', 'Unknown sender')
                    date = headers.get('Date', 'Unknown date')
                    
                    search_text += f"• **{subject}**\n"
                    search_text += f"  👤 {sender}\n"
                    search_text += f"  📅 {date}\n"
                    search_text += f"  🆔 {msg.get('id')}\n\n"
            
            return [types.TextContent(type="text", text=search_text)]
        
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