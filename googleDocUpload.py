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
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                # make content a tuple
                content = GetParagraph(elem)
                #index = elem.get('startIndex')
                text_list[content[0]] = content[1]
                #text_list[index] = content
        elif 'table' in value:
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    content = DocumentText(cell.get('content'))
                    text_list.update(content)

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

    # For every key-value of the dictionary:
    #       get the text
    #       encrypt the text
    #       Store the value of the shares in 3 different texts
    #       Using the keys, delete and insert in the appropriate indices

    # Index at start of row = +3 of end index of previous paragraph

    # Get the start index and text from first item in dictionary
    firstParagraphTuple = list(text_store.items())[0]
    firstStartIndex = firstParagraphTuple[0]
    firstParagraph = (firstParagraphTuple[1])[:-1]

    firstSSS = SSSTest.SSSText(firstParagraph)
    print(text_store)

    SSShare1Text = ""
    SSShare2Text = ""
    SSShare3Text = ""

    for share in firstSSS:
        SSShare1Text += str(share[0])
        SSShare2Text += str(share[1])
        SSShare3Text += str(share[2])
    
    # Would be helpful to get the updated start index of the share documents
    share1length = len(SSShare1Text) + 2
    share2length = len(SSShare2Text) + 2
    share3length = len(SSShare3Text) + 2

    print(share1length, share2length, share3length)

    request1 = [{
        'deleteContentRange': {
            'range': {
                'startIndex': firstStartIndex,
                'endIndex': firstStartIndex + len(firstParagraph),
            }
        },
    },

    {
            'insertText': {
                'location': {
                    'index': firstStartIndex,
                },
                'text': SSShare1Text
            }
    }]

    request2 = [{
        'deleteContentRange': {
            'range': {
                'startIndex': firstStartIndex,
                'endIndex': firstStartIndex + len(firstParagraph),
            }
        },
    },

    {
            'insertText': {
                'location': {
                    'index': firstStartIndex,
                },
                'text': SSShare2Text
            }
    }]

    request3 = [{
        'deleteContentRange': {
            'range': {
                'startIndex': firstStartIndex,
                'endIndex': firstStartIndex + len(firstParagraph),
            }
        },
    },

    {
            'insertText': {
                'location': {
                    'index': firstStartIndex,
                },
                'text': SSShare3Text
            }
    }]

    # Updates the copies
    result1 = doc_service.documents().batchUpdate(documentId=id_list[0], body={'requests': request1}).execute()
    result2 = doc_service.documents().batchUpdate(documentId=id_list[1], body={'requests': request2}).execute()
    result3 = doc_service.documents().batchUpdate(documentId=id_list[2], body={'requests': request3}).execute()

    #text_store.pop(list(text_store.keys())[0])
    print(firstStartIndex + len(SSShare1Text) + 1)
    print(firstStartIndex + len(SSShare2Text) + 1)
    print(firstStartIndex + len(SSShare3Text) + 1)


    copy = doc_service.documents().get(documentId=id_list[0]).execute()

    with open('Odoc.txt', 'w') as f:
        sys.stdout = f
        print(json.dumps(file, indent=4, sort_keys=True))

    with open('doc.txt', 'w') as f:
        sys.stdout = f
        print(json.dumps(copy, indent=4, sort_keys=True))
    

if __name__ == '__main__':
    main()

