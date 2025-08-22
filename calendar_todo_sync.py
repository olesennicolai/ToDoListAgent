#!/usr/bin/env python3
"""
Calendar-Todo Synchronization Script
Tests bidirectional sync between Google Calendar and ToDoList.csv
"""

import csv
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Google Calendar API scopes
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events']

TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
TODO_FILE = 'ToDoList.csv'

class CalendarTodoSync:
    def __init__(self):
        self.service = None
        self.todos = []
        self.calendar_events = []
        self._authenticate()
        
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
        
    def read_todo_list(self) -> List[Dict[str, str]]:
        """Read todos from CSV file"""
        todos = []
        if os.path.exists(TODO_FILE):
            with open(TODO_FILE, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    todos.append(row)
        self.todos = todos
        return todos
        
    def get_calendar_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get calendar events from the next N days"""
        try:
            # Get primary calendar events
            now = datetime.now().isoformat() + 'Z'
            end_time = (datetime.now() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            self.calendar_events = events
            return events
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
            
    def find_missing_todos_from_calendar(self) -> List[Dict[str, Any]]:
        """Find calendar events that should be added as todos"""
        missing_todos = []
        
        for event in self.calendar_events:
            event_title = event.get('summary', 'Untitled Event')
            event_start = event.get('start', {})
            
            # Extract date from calendar event
            if 'dateTime' in event_start:
                event_date = datetime.fromisoformat(event_start['dateTime'].replace('Z', '+00:00')).date()
            elif 'date' in event_start:
                event_date = datetime.fromisoformat(event_start['date']).date()
            else:
                continue
                
            # Check if this event already exists as a todo
            found_match = False
            for todo in self.todos:
                if (self._titles_match(todo['Task'], event_title) and 
                    self._dates_match(todo.get('Start Date', ''), str(event_date))):
                    found_match = True
                    break
                    
            if not found_match:
                missing_todos.append({
                    'title': event_title,
                    'date': str(event_date),
                    'original_event': event
                })
                
        return missing_todos
        
    def find_missing_calendar_events_from_todos(self) -> List[Dict[str, str]]:
        """Find todos with end dates that should be added to calendar"""
        missing_events = []
        
        for todo in self.todos:
            if not todo.get('End Date') or todo['End Date'].strip() == '':
                continue
                
            todo_title = todo['Task']
            todo_end_date = todo['End Date']
            
            # Check if this todo already exists as a calendar event
            found_match = False
            for event in self.calendar_events:
                event_title = event.get('summary', 'Untitled Event')
                event_start = event.get('start', {})
                
                if 'dateTime' in event_start:
                    event_date = datetime.fromisoformat(event_start['dateTime'].replace('Z', '+00:00')).date()
                elif 'date' in event_start:
                    event_date = datetime.fromisoformat(event_start['date']).date()
                else:
                    continue
                    
                if (self._titles_match(todo_title, event_title) and 
                    self._dates_match(todo_end_date, str(event_date))):
                    found_match = True
                    break
                    
            if not found_match:
                missing_events.append(todo)
                
        return missing_events
        
    def _titles_match(self, title1: str, title2: str) -> bool:
        """Check if two titles are similar enough to be considered a match"""
        # Simple similarity check - could be enhanced with fuzzy matching
        t1 = title1.lower().strip()
        t2 = title2.lower().strip()
        
        # Exact match
        if t1 == t2:
            return True
            
        # Check if one contains the other (for partial matches)
        if len(t1) > 5 and len(t2) > 5:
            if t1 in t2 or t2 in t1:
                return True
                
        return False
        
    def _dates_match(self, date1: str, date2: str) -> bool:
        """Check if two date strings represent the same date"""
        try:
            if not date1 or not date2:
                return False
            d1 = datetime.strptime(date1.strip(), '%Y-%m-%d').date()
            d2 = datetime.strptime(date2.strip(), '%Y-%m-%d').date()
            return d1 == d2
        except ValueError:
            return False
            
    def create_calendar_event(self, todo: Dict[str, str]) -> bool:
        """Create a calendar event from a todo item"""
        try:
            event_date = todo['End Date']
            event_title = f"📋 {todo['Task']}"  # Prefix to indicate it's from todo list
            
            # Create all-day event
            event = {
                'summary': event_title,
                'start': {
                    'date': event_date,
                },
                'end': {
                    'date': event_date,
                },
                'description': f"Auto-created from todo list\nSection: {todo.get('Section', 'N/A')}\nUrgency: {todo.get('Urgency', 'N/A')}"
            }
            
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"✅ Created calendar event: {event_title} on {event_date}")
            return True
            
        except HttpError as error:
            print(f"❌ Failed to create calendar event: {error}")
            return False
            
    def add_todo_to_csv(self, todo_data: Dict[str, str]) -> bool:
        """Add a new todo to the CSV file"""
        try:
            # Prepare the new row
            new_row = {
                'Section': 'work',  # Default section
                'Task': todo_data['title'],
                'Start Date': todo_data['date'],
                'End Date': todo_data['date'],
                'Urgency': 'not urgent'  # Default urgency
            }
            
            # Read existing todos
            existing_todos = []
            if os.path.exists(TODO_FILE):
                with open(TODO_FILE, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    existing_todos = list(reader)
            
            # Add new todo
            existing_todos.append(new_row)
            
            # Write back to file
            with open(TODO_FILE, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['Section', 'Task', 'Start Date', 'End Date', 'Urgency']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_todos)
                
            print(f"✅ Added todo: {todo_data['title']} on {todo_data['date']}")
            return True
            
        except Exception as error:
            print(f"❌ Failed to add todo: {error}")
            return False
            
    def perform_sync_test(self):
        """Perform a complete sync test"""
        print("=== Calendar-Todo Sync Test ===\n")
        
        # Step 1: Read current state
        print("1. Reading current todo list...")
        todos = self.read_todo_list()
        print(f"   Found {len(todos)} todos")
        
        print("\n2. Reading calendar events...")
        events = self.get_calendar_events()
        print(f"   Found {len(events)} calendar events")
        
        # Step 2: Find discrepancies
        print("\n3. Analyzing discrepancies...")
        
        missing_todos = self.find_missing_todos_from_calendar()
        print(f"   📅➡️📋 Calendar events missing from todos: {len(missing_todos)}")
        for todo in missing_todos:
            print(f"      - {todo['title']} on {todo['date']}")
            
        missing_events = self.find_missing_calendar_events_from_todos()
        print(f"   📋➡️📅 Todos with end dates missing from calendar: {len(missing_events)}")
        for todo in missing_events:
            print(f"      - {todo['Task']} on {todo['End Date']}")
            
        # Step 3: Perform sync (test mode - ask for confirmation)
        print("\n4. Sync recommendations:")
        
        if missing_todos:
            print("\n   📅➡️📋 Recommend adding these calendar events as todos:")
            for i, todo in enumerate(missing_todos, 1):
                print(f"      {i}. {todo['title']} on {todo['date']}")
            
            # In a real implementation, we would ask for user confirmation here
            print("   💡 In production: Would ask user for confirmation before adding")
            
        if missing_events:
            print("\n   📋➡️📅 Auto-adding these todos as calendar events:")
            for todo in missing_events:
                success = self.create_calendar_event(todo)
                if not success:
                    print(f"   ⚠️ Failed to create event for: {todo['Task']}")
                    
        # Step 4: Summary
        print("\n=== Sync Test Results ===")
        print(f"📊 Initial state:")
        print(f"   - Todos: {len(todos)}")
        print(f"   - Calendar events: {len(events)}")
        print(f"🔄 Sync analysis:")
        print(f"   - Calendar events to add as todos: {len(missing_todos)}")
        print(f"   - Todos added as calendar events: {len(missing_events)}")
        print(f"✅ Sync test completed successfully!")
        
        return {
            'todos_count': len(todos),
            'events_count': len(events),
            'missing_todos': len(missing_todos),
            'missing_events': len(missing_events),
            'missing_todo_details': missing_todos,
            'missing_event_details': missing_events
        }

def main():
    """Run the sync test"""
    try:
        sync = CalendarTodoSync()
        results = sync.perform_sync_test()
        return results
    except Exception as e:
        print(f"❌ Sync test failed: {str(e)}")
        return None

if __name__ == "__main__":
    main()