from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload

import SSSTest

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

def GetParagraph(elem):
    text_run = elem.get('textRun')
    if not text_run:
        return ''

    return text_run.get('content')

def DocumentText(doc_content):
    text_list = []
    for value in doc_content:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                content = GetParagraph(elem)
                text_list.append(content)
        elif 'table' in value:
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    content = DocumentText(cell.get('content'))
                    text_list.append(content[0])

    return text_list


def main():
    # Gets Credentials
    creds = None
    creds = getCreds(creds)

    # Gets the Google Drive and Google Docs API services
    drive_service = build('drive', 'v2', credentials=creds)
    doc_service = build('docs', 'v1', credentials = creds)

    # Content of the Original file
    file = doc_service.documents().get(documentId=DOCUMENT_ID).execute()

    # Getting ids from the copies
    fileID = file.get('documentId')
    id_list = []

    # Makes copies of the original document
    for copies in range(3):
        copied_file = {'title': 'Share' + str(copies + 1)}
        ShareDoc = drive_service.files().copy(fileId=fileID, body=copied_file).execute()
        shareID = ShareDoc.get('id')
        id_list.append(shareID)

    # Get the content of the original document
    doc_content = file.get('body').get('content')

    # Store text extracted from document
    text_store = DocumentText(doc_content)

    # For each section of text in the document
    for text in text_store:

        if text == "\n":
            continue
        else:
            text = text.strip()

            # Calculate SSS
            ssshares = SSSTest.SSSText(text)

            #Store SSS content from each content section of document
            share1Text = ""
            share2Text = ""
            share3Text = ""

            # each character in share
            for share in ssshares:
                share1Text += str(share[0]) + " "
                share2Text += str(share[1]) + " "
                share3Text += str(share[2]) + " "

            # For the batchUpdate method to replace the text with shares
            request1 = [{
                'replaceAllText': {
                    'containsText': {
                        'text': text,
                        'matchCase':  'true'
                    },
                    'replaceText': share1Text,
                }}]

            request2 = [{
                'replaceAllText': {
                    'containsText': {
                        'text': text,
                        'matchCase':  'true'
                    },
                    'replaceText': share2Text,
                }}]
            
            request3 = [{
                'replaceAllText': {
                    'containsText': {
                        'text': text,
                        'matchCase':  'true'
                    },
                    'replaceText': share3Text,
                }}]

            # Updates the copies
            result1 = doc_service.documents().batchUpdate(documentId=id_list[0], body={'requests': request1}).execute()
            result2 = doc_service.documents().batchUpdate(documentId=id_list[1], body={'requests': request2}).execute()
            result3 = doc_service.documents().batchUpdate(documentId=id_list[2], body={'requests': request3}).execute()


if __name__ == '__main__':
    main()

