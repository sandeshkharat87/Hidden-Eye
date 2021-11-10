import base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import mimetypes
import pickle
import os
import sys
from apiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import cv2
from datetime import datetime
import requests
import json


SCOPES = ['https://mail.google.com/']
os.makedirs("IPICS", exist_ok=True)
os.makedirs("secrets", exist_ok=True)
cred_path = 'secrets/credentials.json'
token_path = 'secrets/token.pickle'
geo_api_path = "secrets/geoAPI.txt"
bot_logs_path = 'secrets/BOT_LOGS.txt'


def login_service():
    creds = None

    # if os.path.exists('token.pickle'):
    if os.path.exists(token_path):
        with open(f'{token_path}', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{cred_path}', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'{token_path}', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service


SERVICE = login_service()


class Botmail:
    def __init__(self, bot, master):
        self.CODES = ("7777", "0000", "1111")
        self.bot = bot
        self.master = master
        self.BOT_PID = bot_logs_path
        open(self.BOT_PID, "a").close()

    def not_executed(self, CHID):
        with open(f"{self.BOT_PID}", "r+") as file:
            allIDs = file.read().splitlines()
            if CHID not in allIDs:
                file.write(f"{CHID}\n")
                return True
            else:
                return False

    # Read mail For Uniqcode
    def get_code(self):
        results = SERVICE.users().messages().list(
            # userId='me', q="from:pycoder87@gmail.com", labelIds=["INBOX"]).execute()
            userId='me', q=f"from:{self.master}", labelIds=["INBOX"]).execute()
        messages = results.get('messages', [])
        # print(messages)
        if not messages:
            print('No msgs found.')
        else:
            # print(messages)
            k = messages[0]
            dmsg = SERVICE.users().messages().get(
                userId='me', id=k['id']).execute()
            print(dmsg['snippet'])
            EM_ID = dmsg['id']
            ACTION_CODE = dmsg['snippet']
            if self.not_executed(EM_ID):
                return {
                    "EM_ID": EM_ID,
                    "ACTION_CODE": ACTION_CODE}

            else:
                print(EM_ID)
                print(ACTION_CODE)
                print("ID Already Executed... Please Send Another One...\n")
                sys.exit()

    def send_mail(self, file_name):
        try:
            message = SERVICE.users().messages().send(userId='me',
                                                      body=self.email_attachment(file_name)).execute()
            print('Message Id: {}'.format(message['id']))

            return message

        except Exception as e:
            print('An error occurred: {}'.format(e))
            return None

    def mylocation(self):
        #Paste your api key here
        api_key = "XXXXXXXXXXXXXXX"
        send_url = f"http://api.ipstack.com/check?access_key={api_key}"
        geo_req = requests.get(send_url)
        geo_json = json.loads(geo_req.text)
        latitude = geo_json['latitude']
        longitude = geo_json['longitude']
        region_name = geo_json['region_name']
        city = geo_json['city']

        return str((region_name, city, longitude, latitude))

    def email_attachment(self, file):

        message = MIMEMultipart()
        # message['to'] = 'sandeshkharat040@gmail.com'
        message['to'] = self.master
        message['from'] = 'sandesh_kharat BOT'
        message['subject'] = 'Intruder Alert'
        # Send current location
        message_text = self.mylocation()

        msg = MIMEText(message_text)
        message.attach(msg)

        (content_type, encoding) = mimetypes.guess_type(file)

        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'

        (main_type, sub_type) = content_type.split('/', 1)

        if main_type == 'text':
            with open(file, 'rb') as f:
                msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)

        elif main_type == 'image':
            with open(file, 'rb') as f:
                msg = MIMEImage(f.read(), _subtype=sub_type)

        elif main_type == 'audio':
            with open(file, 'rb') as f:
                msg = MIMEAudio(f.read(), _subtype=sub_type)

        else:
            with open(file, 'rb') as f:
                msg = MIMEBase(main_type, sub_type)
                msg.set_payload(f.read())

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment',
                       filename=filename)
        message.attach(msg)

        raw_message = base64.urlsafe_b64encode(
            message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}
