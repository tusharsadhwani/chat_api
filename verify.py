"""Functions for email verification"""
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
    'https://www.googleapis.com/auth/gmail.send'
]

def generate_creds():
    """Generates the user's access token to the Gmail API"""
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


def send_verification_email(recepient, link):
    """Sends a verification email"""
    if not os.path.exists('token.pickle'):
        raise FileNotFoundError("File 'token.pickle' does not exist")

    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

    if not creds.valid:
        raise ValueError(
            "Credentials are not valid, run generate_token() manually")

    service = build('gmail', 'v1', credentials=creds)

    message_body = f'''
        Click this link to verify your email:
        <br><br>
        <a href="{link}">{link}</a>'''

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verify your Email"
    msg['From'] = open('./.email').read()
    msg['To'] = recepient
    # msg['Cc'] = ','.join(recepients_list)
    msg.attach(MIMEText(message_body, 'html'))
    # msg.attach(MIMEText(MSG_BODY_PLAIN, 'plain'))
    raw_message_no_attachment = base64.urlsafe_b64encode(msg.as_bytes())
    raw_message_no_attachment = raw_message_no_attachment.decode()
    encoded_msg = {'raw': raw_message_no_attachment}

    # Call the Gmail API
    try:
        service.users().messages().send(userId='me', body=encoded_msg).execute()
    except Exception as ex:
        print("Error:", ex)
