#!/usr/bin/env python3
"""
Spencer's Task Management Board
Auto-extracts tasks from Gmail and creates manageable workflow
Built by Kim ⚡ | 2026-02-18
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
import base64
import sqlite3
from datetime import datetime, timedelta
import re
import os
from threading import Timer

app = Flask(__name__)

class TaskManager:
    def __init__(self):
        self.db_path = '/Users/kimbot/.openclaw/workspace/tasks.db'
        self.token_path = '/Users/kimbot/.openclaw/gmail-config/token.json'
        self.init_database()
        self.gmail_service = None
        self.connect_gmail()
    
    def init_database(self):
        """Initialize SQLite database for tasks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'MEDIUM',
                status TEXT DEFAULT 'TODO',
                source TEXT DEFAULT 'manual',
                email_id TEXT,
                assigned_to TEXT DEFAULT 'Spencer',
                due_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                division TEXT,
                client_name TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def connect_gmail(self):
        """Connect to Gmail API"""
        try:
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                
                self.gmail_service = build('gmail', 'v1', credentials=creds)
                print("✅ Gmail connected successfully")
                return True
        except Exception as e:
            print(f"❌ Gmail connection failed: {e}")
            return False
    
    def extract_tasks_from_email(self, subject, sender, body, email_id):
        """Extract actionable tasks from email content"""
        tasks = []
        
        # Common task indicators
        task_patterns = [
            r"(?:please|can you|need to|remember to|don't forget to|action needed|follow up)\s+([^.!?]+)",
            r"(?:schedule|call|email|send|review|complete|finish|update|prepare)\s+([^.!?]+)",
            r"(?:by|due|deadline|before)\s+(\w+day|\d{1,2}\/\d{1,2}|\d{1,2}-\d{1,2})"
        ]
        
        # Priority indicators
        priority = 'MEDIUM'
        if any(word in subject.lower() for word in ['urgent', 'asap', 'critical']):
            priority = 'URGENT'
        elif any(word in subject.lower() for word in ['important', 'priority']):
            priority = 'HIGH'
        
        # Business division classification
        division = 'General'
        if any(word in (subject + body).lower() for word in ['annuity', 'pension', 'infinite banking', 'debt free life']):
            division = 'Advanced Market'
        elif any(word in (subject + body).lower() for word in ['health insurance', 'aca', 'major medical']):
            division = 'Health Insurance'
        elif any(word in (subject + body).lower() for word in ['simerp', 'cafeteria', '105b', 'wellness']):
            division = 'Cafeteria 125'
        
        # Extract specific tasks
        text = subject + " " + body
        
        # Direct task extraction
        if any(phrase in text.lower() for phrase in ['need to', 'please', 'can you', 'follow up']):
            # Create a task from the email
            task_title = subject if len(subject) < 100 else subject[:100] + "..."
            task_description = f"Email from: {sender}\n\nAction needed:\n{body[:500]}..."
            
            tasks.append({
                'title': task_title,
                'description': task_description,
                'priority': priority,
                'division': division,
                'email_id': email_id,
                'source': 'email'
            })
        
        return tasks
    
    def scan_emails_for_tasks(self, days_back=7):
        """Scan recent emails for new tasks"""
        if not self.gmail_service:
            return []
        
        try:
            # Get emails from last week
            query = f'in:inbox newer_than:{days_back}d'
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            new_tasks = []
            
            for msg in messages:
                # Skip if we already processed this email
                if self.email_already_processed(msg['id']):
                    continue
                
                message = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                # Extract email details
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                # Get body
                body = self.extract_email_body(message['payload'])
                
                # Extract tasks
                tasks = self.extract_tasks_from_email(subject, sender, body, msg['id'])
                
                for task in tasks:
                    self.add_task(**task)
                    new_tasks.append(task)
            
            return new_tasks
            
        except Exception as e:
            print(f"Error scanning emails: {e}")
            return []
    
    def extract_email_body(self, payload):
        """Extract email body text"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
        elif payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def email_already_processed(self, email_id):
        """Check if email has already been processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE email_id = ?", (email_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def add_task(self, title, description="", priority="MEDIUM", division="General", 
                 email_id=None, source="manual", assigned_to="Spencer", due_date=None, client_name=""):
        """Add new task to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, division, email_id, 
                             source, assigned_to, due_date, client_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, priority, division, email_id, source, assigned_to, due_date, client_name))
        
        conn.commit()
        conn.close()
    
    def get_tasks_by_status(self):
        """Get tasks organized by status for Kanban board"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, description, priority, status, division, 
                   assigned_to, due_date, created_at, client_name, source
            FROM tasks 
            ORDER BY 
                CASE priority 
                    WHEN 'URGENT' THEN 1
                    WHEN 'HIGH' THEN 2  
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                END,
                created_at DESC
        ''')
        
        tasks = cursor.fetchall()
        conn.close()
        
        # Organize by status
        organized = {
            'TODO': [],
            'IN_PROGRESS': [],
            'REVIEW': [],
            'DONE': []
        }
        
        for task in tasks:
            task_dict = {
                'id': task[0],
                'title': task[1],
                'description': task[2],
                'priority': task[3],
                'status': task[4],
                'division': task[5],
                'assigned_to': task[6],
                'due_date': task[7],
                'created_at': task[8],
                'client_name': task[9],
                'source': task[10]
            }
            
            organized[task[4]].append(task_dict)
        
        return organized
    
    def update_task_status(self, task_id, new_status):
        """Update task status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (new_status, task_id))
        
        conn.commit()
        conn.close()
    
    def get_task_stats(self):
        """Get task statistics for dashboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total tasks by status
        cursor.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
        status_counts = dict(cursor.fetchall())
        
        # Tasks by priority
        cursor.execute("SELECT priority, COUNT(*) FROM tasks WHERE status != 'DONE' GROUP BY priority")
        priority_counts = dict(cursor.fetchall())
        
        # Tasks by division
        cursor.execute("SELECT division, COUNT(*) FROM tasks WHERE status != 'DONE' GROUP BY division")
        division_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'status': status_counts,
            'priority': priority_counts,
            'division': division_counts
        }

# Initialize task manager
task_manager = TaskManager()

# Web Routes
@app.route('/')
def dashboard():
    """Main dashboard"""
    tasks = task_manager.get_tasks_by_status()
    stats = task_manager.get_task_stats()
    return render_template('dashboard.html', tasks=tasks, stats=stats)

@app.route('/scan-emails')
def scan_emails():
    """Manually trigger email scan"""
    new_tasks = task_manager.scan_emails_for_tasks()
    return jsonify({'success': True, 'new_tasks': len(new_tasks), 'tasks': new_tasks})

@app.route('/update-task-status', methods=['POST'])
def update_task_status():
    """Update task status via API"""
    data = request.json
    task_id = data.get('task_id')
    new_status = data.get('status')
    
    task_manager.update_task_status(task_id, new_status)
    return jsonify({'success': True})

@app.route('/add-task', methods=['POST'])
def add_task():
    """Add new manual task"""
    data = request.json
    
    task_manager.add_task(
        title=data.get('title'),
        description=data.get('description', ''),
        priority=data.get('priority', 'MEDIUM'),
        division=data.get('division', 'General'),
        assigned_to=data.get('assigned_to', 'Spencer'),
        due_date=data.get('due_date'),
        client_name=data.get('client_name', '')
    )
    
    return jsonify({'success': True})

# Auto-scan emails every hour
def auto_scan_emails():
    """Background task to automatically scan for new email tasks"""
    print("🔍 Auto-scanning emails for new tasks...")
    new_tasks = task_manager.scan_emails_for_tasks(days_back=1)
    print(f"✅ Found {len(new_tasks)} new tasks from emails")
    
    # Schedule next scan
    Timer(3600.0, auto_scan_emails).start()  # Every hour

if __name__ == '__main__':
    # Start auto-scanning
    auto_scan_emails()
    
    # Run web app
    print("🚀 Spencer's Task Board starting...")
    print("📧 Auto-scanning emails for tasks...")
    print("🌐 Access your dashboard at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)