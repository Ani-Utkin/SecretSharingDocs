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

# Access Credentials from APIs
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

# Extract text from paragraph element
def GetParagraph(elem):
    text_run = elem.get('textRun')
    if not text_run:
        return ''

    return (elem.get('startIndex'), text_run.get('content'))

# Extract the text from the document
def DocumentText(doc_content):
    text_list = dict()
    for value in doc_content:

        # Extract text from paragraphs
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                content = GetParagraph(elem)
                text_list[content[0]] = content[1]

        # Extracts text from tables
        elif 'table' in value:
            table = value.get('table')
            text_list[value.get('startIndex')] = None
            for row in table.get('tableRows'):
                text_list[row.get('startIndex')] = None
                cells = row.get('tableCells')
                for cell in cells:
                    text_list[cell.get('startIndex')] = None
                    content = DocumentText(cell.get('content'))
                    text_list.update(content)
        
        # Checks for any indexes that dont contain text
        # Useful for when getting the offset of share documents.
        if value.get("endIndex") not in text_list:
            text_list[value.get("endIndex")] = None

    # Return dictionary of text and indexes
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

    # dictionary to store text extracted from document and its starting index
    text_store = DocumentText(doc_content)

    # Index increments for the share documents
    startIndex1 = 1
    startIndex2 = 1
    startIndex3 = 1

    print(text_store)

    # Loop through every index in the dictionary
    for index in text_store:
        text = text_store.get(index)

        # For indices without any text content, skip and increment the index
        if text == "\n" or text == None or len(text) == 0:
            startIndex1 += 1
            startIndex2 += 1
            startIndex3 += 1
            continue

        # Get the paragraph from the dictionary
        text = text_store.get(index)[:-1]

        # Implement SSS on document content
        firstSSS = SSSTest.SSSText(text)

        # Separate shares between the share documents
        # by each character in the paragraph
        SSShare1Text = ""
        SSShare2Text = ""
        SSShare3Text = ""

        for share in firstSSS:
            SSShare1Text += str(share[0])
            SSShare2Text += str(share[1])
            SSShare3Text += str(share[2])
        
        # Requests to delete the original text and insert encryptions
        # to each share document
        request1 = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': startIndex1,
                    'endIndex': startIndex1 + len(text),
                }
            },
        },

        {
            'insertText': {
                'location': {
                    'index': startIndex1,
                },
                'text': SSShare1Text
            }
        }]

        request2 = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': startIndex2,
                    'endIndex': startIndex2 + len(text),
                }
            },
        },

        {
            'insertText': {
                'location': {
                    'index': startIndex2,
                },
                'text': SSShare2Text
            }
        }]

        request3 = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': startIndex3,
                    'endIndex': startIndex3 + len(text),
                }
            },
        },

        {
            'insertText': {
                'location': {
                    'index': startIndex3,
                },
                'text': SSShare3Text
            }
        }]

        # Updates the copies
        result1 = doc_service.documents().batchUpdate(documentId=id_list[0], body={'requests': request1}).execute()
        result2 = doc_service.documents().batchUpdate(documentId=id_list[1], body={'requests': request2}).execute()
        result3 = doc_service.documents().batchUpdate(documentId=id_list[2], body={'requests': request3}).execute()

        # Increment index to update with the share documents
        startIndex1 = startIndex1 + len(SSShare1Text) + 1
        startIndex2 = startIndex2 + len(SSShare2Text) + 1
        startIndex3 = startIndex3 + len(SSShare3Text) + 1

if __name__ == '__main__':
    main()

