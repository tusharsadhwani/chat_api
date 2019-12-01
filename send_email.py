"""Sends an email to a recepient"""
# pylint: disable=no-member
import base64
import pickle
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send'
]

MSG_BODY = ""
MSG_BODY_PLAIN = ""

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "TEST"
    msg['From'] = "example@gmail.com"
    msg['To'] = "example@gmail.com"
    # msg['Cc'] = ','.join(recepients_list)
    msg.attach(MIMEText(MSG_BODY_PLAIN, 'plain'))
    msg.attach(MIMEText(MSG_BODY, 'html'))
    raw_message_no_attachment = base64.urlsafe_b64encode(msg.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    encoded_msg = {'raw': raw_message_no_attachment}

    # Call the Gmail API
    try:
        service.users().messages().send(userId='me', body=encoded_msg).execute()
    except Exception as ex:
        print("Error:", ex)

if __name__ == '__main__':
    main()
