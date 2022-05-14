import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pprint import  pprint
from progress.bar import ShadyBar
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fileHandler = logging.FileHandler('logs/logs.log')
fileHandler.setFormatter(logging.Formatter(fmt='[%(asctime)s: %(name)s %(levelname)s] %(message)s'))
logger.addHandler(fileHandler)



SCOPES = ['https://www.googleapis.com/auth/drive']
APP_TOKEN_FILE = os.path.join(os.getcwd(), 'credentials.json')
USER_TOKEN_FILE = "user_token.json"



class GDriveUp:
    def __init__(self):
        # https://developers.google.com/docs/api/quickstart/python
        creds = None
        if os.path.exists(USER_TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(USER_TOKEN_FILE, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(APP_TOKEN_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(USER_TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        logger.info('Received correct token')
        self.service = build('drive', 'v3', credentials=creds)

    def create_dir(self, folder_name):
        results = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=False", pageSize=500, fields="nextPageToken, files(id, name)").execute()
        nextPageToken = results.get('nextPageToken')
        while nextPageToken: 
            nextPage = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=False", pageSize=500, fields="nextPageToken, files(id, name)", pageToken=nextPageToken).execute()
            nextPageToken = nextPage.get('nextPageToken')
            results['files'] = results['files'] + nextPage['files']
        for result in results['files']:
            if folder_name == result['name']:
                logger.info("Dir already exist")
                return result['id']    
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        result = self.service.files().create(body=file_metadata, fields='id').execute()
        logger.info(f"Dir ID {result.get('id')} was recorded")
        return result.get('id')

    def upload_file(self, folder_id: str, url: str, name: str):
        results = self.service.files().list(q=f"trashed=False and '{folder_id}' in parents", pageSize=100, fields="nextPageToken, files(id, name)").execute()
        nextPageToken = results.get('nextPageToken')
        while nextPageToken:
            nextPage = self.service.files().list(q=f"trashed=False and '{folder_id}' in parents", pageSize=100, fields="nextPageToken, files(id, name)", pageToken=nextPageToken).execute()
            nextPageToken = nextPage.get('nextPageToken')
            results['files'] = results['files'] + nextPage['files']
        for result in results.get('files'):
            if name == result['name']:
                # pprint(result)
                self.service.files().delete(fileId=f"{result['id']}").execute()
                logger.info('File exist and will be deleted')
        file_metadata = {'name': name, 'parents': [folder_id]}
        body_b = requests.get(url)
        with open(f"tmp/{name}", 'wb') as body:
            body.write(body_b.content)
        media = MediaFileUpload(f"tmp/{name}", mimetype='image/jpeg', resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"New file {file.get('id')} was recorded")
        # print(file)
        os.remove(f"tmp/{name}")
        logger.info('File deleted from /tmp')
        return file.get('id')

def upload_to_googleDrive(folder_name: str, json_photos: list):
    if os.path.exists(APP_TOKEN_FILE):
        GDriveUploader = GDriveUp()
        folder_id = GDriveUploader.create_dir(folder_name)
        bar = ShadyBar('Loading to GDRiVE', max=len(json_photos))
        for photos in json_photos:
            bar.next()
            file_id = GDriveUploader.upload_file(folder_id, photos['url'], photos['file_name'])
            # print(file_id)
        bar.finish()
    else:
        print(f"No such file or directory:{APP_TOKEN_FILE}")
        logger.error(f"No such file or directory:{APP_TOKEN_FILE}") 
    









