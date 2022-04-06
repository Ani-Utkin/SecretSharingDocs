from __future__ import print_function
from asyncio.windows_events import NULL
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

import SSSTest
import random

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
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


def SSSEncrypt(doc_content):
    # dictionary to store text extracted from document and its starting index
    text_store = DocumentText(doc_content)

    # Index increments for the share documents
    startIndex1 = 1
    startIndex2 = 1
    startIndex3 = 1

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
            SSShare1Text += str(share[0]) + " "
            SSShare2Text += str(share[1]) + " "
            SSShare3Text += str(share[2]) + " "
        
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


def DownloadFile(id, title):

    request = drive_service.files().export_media(fileId=id, mimeType='application/pdf')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request=request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print('Download progress {0}'.format(status.progress() * 100))
    
    fh.seek(0)

    downtitle = title.get('title') + ".pdf"

    with open(downtitle, 'wb') as f:
        f.write(fh.read())
        f.close

def SSSReconstruct(docIDs):
    
    # Create the Reconstructed Document Object
    reconstruct_title = {'title': 'Reconstructed Document'}
    reconDrive = drive_service.files().copy(fileId=id_list[0], body=reconstruct_title).execute()
    reconDoc = doc_service.documents().get(documentId=reconDrive.get('id')).execute()
    reconID = reconDoc.get('documentId')

    reconDocContent = DocumentText(reconDoc.get('body').get('content'))

    # Randomize between which 2 shares will be chosen for reconstruction
    pool = random.sample(docIDs, 2)
    shareDocs = []
    for id in pool:
        shareDoc = doc_service.documents().get(documentId=id).execute()
        shareDocs.append(shareDoc)
    
    # Access the contents of the document and extract the shares
    doc1 = DocumentText(shareDocs[0].get('body').get('content'))
    doc2 = DocumentText(shareDocs[1].get('body').get('content'))

    # With the extracted text, combine the shares and calculate reconstruction
    # Then insert the result to the reconstructed document
    startIndex = 1
    for (key1, value1), (key2, value2), (key3, value3) in zip(doc1.items(), doc2.items(), reconDocContent.items()):

        if value1 == None or value1 == "\n" or len(value1) == 0 or value2 == None or value2 == "\n" or len(value2) == 0:
            startIndex += 1
            continue

        if value3 == None or value3 == "\n" or len(value3) == 0:
            startIndex+=1
            continue

        share1 = value1.split(") ")
        share2 = value2.split(") ")

        reconstruct_list = []
        for i in range(len(share1) - 1):
            share_list = []
            j1 = share1[i] + ")"
            j2 = share2[i] + ")"

            j1int = tuple(int(num) for num in j1.replace('(', '').replace(')', '').replace('...', '').split(', '))
            j2int = tuple(int(num) for num in j2.replace('(', '').replace(')', '').replace('...', '').split(', '))

            share_list.append(j1int) 
            share_list.append(j2int)

            reconstruct_list.append(share_list)
    
        text = SSSTest.SSS_reconstruct(reconstruct_list)

        # Requests to delete the original text and insert reconstructed text
        request1 = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': startIndex,
                    'endIndex': startIndex + len(value3) - 1,
                }
            },
        },

        {
            'insertText': {
                'location': {
                    'index': startIndex,
                },
                'text': text
            }
        }]

        result = doc_service.documents().batchUpdate(documentId=reconID, body={'requests': request1}).execute()
        startIndex = startIndex + len(text) + 1
    
    # Once the reconstruction is done, download the file and remove the file from the drive
    DownloadFile(reconDrive.get('id'), reconstruct_title)


def main():
    global id_list
    global drive_service
    global doc_service

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

    # Makes copies of the original document
    id_list = []
    for copies in range(3):
        copied_file = {'title': 'Share' + str(copies + 1)}
        ShareDoc = drive_service.files().copy(fileId=fileID, body=copied_file).execute()
        shareID = ShareDoc.get('id')
        id_list.append(shareID)

    # Get the content of the original document
    doc_content = file.get('body').get('content')



    # Method which will encrypt the entire document,
    # Creating 3 shares which would all be uploaded to Google Drive
    SSSEncrypt(doc_content)


    # Reconstruction using the three created shares
    # Choose 2 shares and implement SSS_reconstruction on each paragraph
    # Create a copy from one of the shares and update with the reconstructed data
    # Then download the reconstructed document
    SSSReconstruct(id_list)



if __name__ == '__main__':
    main()

