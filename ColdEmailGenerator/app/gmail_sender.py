import os
import pickle
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    """Authenticate with Gmail API and return the service instance."""
    creds = None

    # Load token from pickle file if it exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('ColdEmailGenerator/app/resource/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future runs
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_email(to, subject, body, is_html=False):
    """Create an email message that supports both plain text and HTML."""
    msg = MIMEMultipart("alternative")
    msg["to"] = to
    msg["from"] = 'ramanarayanransingh@gmail.com'  # Replace with your Gmail address
    msg["subject"] = subject

    # Attach plain text version
    plain_text = body.replace('<br>', '\n').replace('<strong>', '').replace('</strong>', '')
    msg.attach(MIMEText(plain_text, "plain"))

    # If HTML is provided, attach HTML version as well
    if is_html:
        msg.attach(MIMEText(body, "html"))

    return {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')}

def send_email(service, to, subject, body, is_html=False):
    """Send an email via Gmail API, supporting both plain text and HTML content."""
    try:
        message = create_email(to, subject, body, is_html)
        send_message = service.users().messages().send(userId='me', body=message).execute()
        logging.info(f"Email sent successfully to {to}, message ID: {send_message['id']}")
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")

