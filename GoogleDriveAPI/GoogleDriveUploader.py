import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pprint import  pprint
import io
import os
import json


SCOPES = ['https://www.googleapis.com/auth/drive']
APP_TOKEN_FILE = os.path.join(os.getcwd(), 'GoogleDriveAPI/credentials.json')
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
        # log 'Received correct token'
        self.service = build('drive', 'v3', credentials=creds)
        print('Received correct token')

    def create_dir(self, folder_name):
        results = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=False", pageSize=500, fields="nextPageToken, files(id, name)").execute()
        nextPageToken = results.get('nextPageToken')
        while nextPageToken: 
            nextPage = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=False", pageSize=500, fields="nextPageToken, files(id, name)", pageToken=nextPageToken).execute()
            nextPageToken = nextPage.get('nextPageToken')
            results['files'] = results['files'] + nextPage['files']
        for result in results['files']:
            if folder_name == result['name']:
                # log "Dir already exist"
                print("Dir already exist")
                return result['id']    
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        result = self.service.files().create(body=file_metadata, fields='id').execute()
        # log f"Dir ID {result.get('id')}"
        print(f"Dir ID {result.get('id')}")
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
                print(f"{result['id']}")
                # fileid = "'{}'".format(result['id'])
                self.service.files().delete(fileId=f"{result['id']}").execute()
                  # log файл существует в папке и удаление файла
        file_metadata = {'name': name, 'parents': [folder_id]}
        body_b = requests.get(url)
        with open(f"tmp/{name}", 'wb') as body:
            body.write(body_b.content)
        media = MediaFileUpload(f"tmp/{name}", mimetype='image/jpeg', resumable=True)
        file = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        # lod файл записан
        print (f"File ID: {file.get('id')}")
        print(file)
        os.remove(f"tmp/{name}")
         # log  файл удален с сервера
        return file.get('id')

if __name__ == '__main__':
    GDriveUploader = GDriveUp()
    folder_id = GDriveUploader.create_dir('New_new_folder')

    url_file = 'https://sun6-20.userapi.com/s/v1/if1/NqpcH7sWt_0QGbLXO-NfxOohtrCWNn6uqDif3Aw_U7kDnFekyRYREJpSN6cXMrYrAaWOiCJB.jpg?size=968x1080&quality=96&type=album'
    file_name = 'test.jpg'
    file_id = GDriveUploader.upload_file(folder_id, url_file, file_name)








