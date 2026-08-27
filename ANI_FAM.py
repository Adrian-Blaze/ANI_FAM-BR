import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
from datetime import date
import pandas as pd
from dotenv import load_dotenv
import json

load_dotenv()
URL = os.getenv('URL').strip()
#t = date.today()
t = date(2024, 4, 18)
df = pd.read_excel(URL)
#print(df)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
def authenticate():
    creds = None

    # token.json stores the user's authorization credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    # If there are no valid credentials, authenticate
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save credentials for future runs
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def send_email(sender, recipient, subject, body):

    creds = authenticate()

    service = build(
        "gmail",
        "v1",
        credentials=creds
    )

    message = EmailMessage()

    message["To"] = recipient
    message["From"] = sender
    message["Subject"] = subject

    message.set_content(body)

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    create_message = {
        "raw": encoded_message
    }

    send_message = service.users().messages().send(
        userId="me",
        body=create_message
    ).execute()

    print("Email sent successfully!")
    print("Message ID:", send_message["id"])


recipient = json.loads(os.getenv("recipient").strip())


for index, row in df.iterrows():
    birthdate = row['BIRTHDATE']
    name = row['NAME']
    
    if birthdate.month == t.month and birthdate.day == t.day:
        print(f"Today is {name}'s birthday!")
        body = f"Today is {name}'s birthday!"
        
        send_email(
        sender= os.getenv('Email_Address'),
        recipient= recipient,
        subject='Birthday Reminder!',
        body= body 
        )