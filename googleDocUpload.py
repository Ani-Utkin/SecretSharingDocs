from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload





SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Uploading A file
    file_metadata = {
        'name': 'TestDocument.docx',
        'parents': ['1PLROB_V9AIuFBLJr5dqRDIUwka3_cBwu'], # Save to a folder on the Drive
    }

    # Content of the file
    media_content = MediaFileUpload('/testDocuments/TestDocument.docx', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    file = service.files().create(
        body=file_metadata,
        media_body=media_content
    ).execute()

    fileID = file.get('id')

    print(fileID)

if __name__ == '__main__':
    main()

