from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload

import SSSTest
import json
import sys

SCOPES = ['https://www.googleapis.com/auth/drive']
DOCUMENT_ID = '17fI0PQODwmZpWjGv2f1SGYCVfI7_Wykhtui3YwMDEkk'

def getCreds(creds):
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
    
    return creds


def main():
    # Gets Credentials
    creds = None
    creds = getCreds(creds)

    # Gets the Google Drive and Google Docs API services
    service = build('drive', 'v3', credentials=creds)
    doc_service = build('docs', 'v1', credentials = creds)

    # Content of the Original file
    file = doc_service.documents().get(documentId=DOCUMENT_ID).execute()

    # Creates copies for the shares
    shareDocs = []
    fileID = file.get('documentId')
    id_list = []

    # Makes copies of the original document
    for copies in range(3):
        copied_file = {'title': 'Share ' + str(copies + 1)}
        ShareDoc = service.files().copy(fileId=fileID, body=copied_file).execute()
        shareID = ShareDoc.get('id')
        id_list.append(shareID)
        shareDoc = doc_service.documents().get(documentId=shareID).execute()
        shareDocs.append(shareDoc)

    # Get the content of the original document
    doc_content = file.get('body').get('content')

    hasOrigContent = 1
    for i in range(len(doc_content)):
        if 'paragraph' in doc_content[i]:
            text = doc_content[i].get('paragraph').get('elements')[0].get('textRun').get('content')
            SSShares = SSSTest.SSSText(text)

            # Gets the sss shares from each letter
            # j = 0 to length of the share content - 1
            for j in range(len(SSShares)):

                # Split the share between the three doc shares
                # k = 0 to 2
                for k in range(len(SSShares[j])):
                    # Get current element in content position i from each copy
                    shareDocContent = shareDocs[k].get('body').get('content')[i]
                    # If the element in content is a paragraph
                    if 'paragraph' in shareDocContent:
                        doc = shareDocContent.get('paragraph').get('elements')[0].get('textRun')

                        # Remove Original Content from textrun.content
                        if(hasOrigContent == 1):
                            for content in range(3):
                                contentClear = shareDocs[content].get('body').get('content')[i].get('paragraph').get('elements')[0].get('textRun')
                                contentClear['content'] = ""
                                hasOrigContent = 0

                        # Add share to the current copy
                        doc['content'] += str(SSShares[j][k]) + " "

            # Set it back for the next content
            hasOrigContent = 1

#    for copies in range(len(shareDocs)):
#        update_file = service.files().update(fileId = id_list[copies], media_body = str(shareDocs[copies])).execute()


    with open('FirstDocx.txt', 'w') as f:
        sys.stdout = f
        print(json.dumps(file, indent=4, sort_keys=True))

    # Output json
    for index in range(3):
        with open('jsonDocx' + str(index) +'.txt', 'w') as f:
            sys.stdout = f
            print(json.dumps(shareDocs[index], indent=4, sort_keys=True))

if __name__ == '__main__':
    main()

