#!/usr/bin/env python3
"""
Gmail Management System for Spencer
Built by Kim ⚡ | 2026-02-18
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import json
import base64
import re
from datetime import datetime
import os

class GmailManager:
    def __init__(self, token_path='token.json'):
        """Initialize Gmail API connection"""
        self.service = None
        self.token_path = token_path
        self.connect()
    
    def connect(self):
        """Connect to Gmail API using stored token"""
        try:
            creds = Credentials.from_authorized_user_file(self.token_path)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            
            self.service = build('gmail', 'v1', credentials=creds)
            print("✅ Connected to Gmail successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def get_inbox_summary(self, max_results=20):
        """Get recent inbox emails with priority analysis"""
        try:
            # Get recent emails
            results = self.service.users().messages().list(
                userId='me', 
                labelIds=['INBOX'],
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_summaries = []
            
            for msg in messages:
                # Get detailed message info
                message = self.service.users().messages().get(
                    userId='me', 
                    id=msg['id']
                ).execute()
                
                # Extract email details
                headers = message['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
                
                # Get email body
                body = self.extract_body(message['payload'])
                
                # Priority analysis
                priority = self.analyze_priority(subject, sender, body)
                
                email_summaries.append({
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body_preview': body[:200] + "..." if len(body) > 200 else body,
                    'priority': priority,
                    'labels': message.get('labelIds', [])
                })
            
            return email_summaries
            
        except Exception as e:
            print(f"❌ Error getting inbox: {e}")
            return []
    
    def extract_body(self, payload):
        """Extract email body from message payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        data = part['body']['data']
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
        else:
            if payload['mimeType'] == 'text/plain':
                if 'data' in payload['body']:
                    data = payload['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def analyze_priority(self, subject, sender, body):
        """Analyze email priority based on content"""
        priority_keywords = {
            'URGENT': ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'deadline'],
            'HIGH': ['important', 'priority', 'follow up', 'meeting', 'call', 'proposal'],
            'BUSINESS': ['client', 'customer', 'policy', 'insurance', 'quote', 'application'],
            'REVENUE': ['commission', 'sale', 'premium', 'contract', 'closing', 'signed']
        }
        
        text = (subject + " " + sender + " " + body).lower()
        
        # Check for business-specific high priority
        if any(keyword in text for keyword in ['pinnacle', 'allstate', 'dcbg', 'simerp']):
            return 'URGENT'
        
        # Revenue-related always high priority
        if any(keyword in text for keyword in priority_keywords['REVENUE']):
            return 'HIGH'
        
        # Check other priority levels
        if any(keyword in text for keyword in priority_keywords['URGENT']):
            return 'URGENT'
        elif any(keyword in text for keyword in priority_keywords['HIGH']):
            return 'HIGH'
        elif any(keyword in text for keyword in priority_keywords['BUSINESS']):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def create_daily_report(self):
        """Create Spencer's daily email triage report"""
        emails = self.get_inbox_summary()
        
        # Sort by priority
        priority_order = {'URGENT': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        emails.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        report = f"""
# 📧 DAILY EMAIL TRIAGE REPORT
*Generated by Kim ⚡ | {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## 🚨 CRITICAL ITEMS ({len([e for e in emails if e['priority'] == 'URGENT'])})
"""
        
        for email in emails:
            if email['priority'] == 'URGENT':
                report += f"""
**Subject:** {email['subject']}  
**From:** {email['sender']}  
**Preview:** {email['body_preview']}  
**Action:** IMMEDIATE RESPONSE NEEDED

---
"""
        
        report += f"\n## 🔶 HIGH PRIORITY ({len([e for e in emails if e['priority'] == 'HIGH'])})\n"
        
        for email in emails:
            if email['priority'] == 'HIGH':
                report += f"- **{email['subject']}** from {email['sender']}\n"
        
        report += f"\n## 📋 BUSINESS/MEDIUM ({len([e for e in emails if e['priority'] == 'MEDIUM'])})\n"
        
        for email in emails:
            if email['priority'] == 'MEDIUM':
                report += f"- {email['subject']} from {email['sender']}\n"
        
        report += f"\n## 📝 LOW PRIORITY/FYI ({len([e for e in emails if e['priority'] == 'LOW'])})\n"
        
        low_count = len([e for e in emails if e['priority'] == 'LOW'])
        report += f"*{low_count} emails - can be batch processed later*\n"
        
        return report

if __name__ == "__main__":
    # Initialize Gmail manager
    gm = GmailManager('/Users/kimbot/.openclaw/gmail-config/token.json')
    
    # Generate and display report
    report = gm.create_daily_report()
    print(report)
    
    # Save report to workspace
    with open('/Users/kimbot/.openclaw/workspace/daily-email-report.md', 'w') as f:
        f.write(report)
    
    print("\n✅ Daily email report saved to workspace/daily-email-report.md")