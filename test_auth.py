#!/usr/bin/env python3
"""
Test Google Calendar authentication
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events']

TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'

def authenticate():
    """Authenticate with Google Calendar API"""
    creds = None
    
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"ERROR: Please place your Google credentials file at {CREDENTIALS_FILE}")
                return None
            
            print("Starting OAuth flow...")
            print("You'll need to copy the URL and complete authentication in your browser")
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=False)
            print("Authentication completed!")
        
        # Save credentials for future use
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"Credentials saved to {TOKEN_FILE}")
    
    return creds

def test_calendar_access(creds):
    """Test calendar access"""
    service = build('calendar', 'v3', credentials=creds)
    
    # List calendars
    print("\n=== Testing Calendar Access ===")
    calendar_list = service.calendarList().list().execute()
    calendars = calendar_list.get('items', [])
    
    print(f"Found {len(calendars)} calendars:")
    for calendar in calendars[:3]:  # Show first 3
        print(f"  - {calendar.get('summary')} (ID: {calendar.get('id')})")
    
    # List recent events
    print(f"\n=== Recent Events ===")
    from datetime import datetime
    time_min = datetime.utcnow().isoformat() + 'Z'
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    if not events:
        print("No upcoming events found.")
    else:
        print(f"Next {len(events)} events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"  - {event.get('summary', 'No title')}: {start}")

if __name__ == "__main__":
    print("Google Calendar Authentication Test")
    print("==================================")
    
    creds = authenticate()
    if creds:
        test_calendar_access(creds)
        print("\n✅ Authentication and calendar access successful!")
        print("The MCP server should now work with Claude Code.")
    else:
        print("\n❌ Authentication failed.")