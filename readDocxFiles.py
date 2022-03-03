# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function

import SSSTest
import json
import sys

import googleapiclient.discovery as discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'
DOCUMENT_ID = '17fI0PQODwmZpWjGv2f1SGYCVfI7_Wykhtui3YwMDEkk'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('token.json')
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    return credentials

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """

    text_run = element.get('textRun')
    if not text_run:
        return ''

    txt = text_run.get('content')

    text_run['content'] = " "

    return text_run.get('content')


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_strucutural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_strucutural_elements(toc.get('content'))
    return text


def main():
    """Uses the Docs API to print out the text of a document."""
    credentials = get_credentials()
    http = credentials.authorize(Http())
    docs_service = discovery.build(
        'docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)

    # The Original document to be encrypted
    originalDoc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_content = originalDoc.get('body').get('content')

    # The id of the original document
    originalID = originalDoc['documentId']

    # Stores copies of the original document
    shareDocs = []

    # Creates copies for the shares
    for copies in range(3):
        shareDocs.append(originalDoc)
        
        # document_copy_id = drive_response.get('id')

    
    for i in range(len(doc_content)):
        if 'paragraph' in doc_content[i]:
            text = doc_content[i].get('paragraph').get('elements')[0].get('textRun').get('content')
            SSShares = SSSTest.SSSText(text)

            # Gets the sss shares from each letter
            for j in range(len(SSShares)):
                # Gets the individual share
                x = SSShares[j]

                # Split the share between the three doc shares
                for k in range(len(SSShares[j])):
                    shareDocContent = shareDocs[k].get('body').get('content')[i]
                    if 'paragraph' in shareDocContent:
                        doc = shareDocContent.get('paragraph').get('elements')[0].get('textRun')

                        doc['content'] += str(x[k]) + " "

    #for content in doc_content:
    #   if 'paragraph':
    #       text = content.get('paragraph').get('elements')[0].get('textRun').get('content')
    #       SSStext = execute SSS on text
    #
    #       Second For Loop to separate the generated shares
    #       
    #       for loop to set the share docs' content to the generated shares.
    #       for share in ShareDocs:
    #           share.get('body').get('content')[content].get('paragraph').get('elements')[0].get('textRun').           get('content')
    #
    with open('FirstDocx.txt', 'w') as f:
        sys.stdout = f
        print(json.dumps(originalDoc, indent=4, sort_keys=True))

    # Output json
    for index in range(3):
        with open('jsonDocx' + str(index) +'.txt', 'w') as f:
            sys.stdout = f
            print(json.dumps(shareDocs[index], indent=4, sort_keys=True))

    """The following program will:
        X    1. Get the document to be encrypted
        X    2. For each number of shares, create a copy
        X    3. Extract text from the original
        X    4. For each character in the text, execute SSS
            5. store each character share into the copies.
    """


if __name__ == '__main__':
    main()
