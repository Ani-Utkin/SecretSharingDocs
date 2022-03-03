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

SCOPES = ['https://www.googleapis.com/auth/drive']
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



def main():
    """Uses the Docs API to print out the text of a document."""
    credentials = get_credentials()
    http = credentials.authorize(Http())

    # docs_service = discovery.build('docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)

    drive_service = discovery.build('drive', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)

    # Flag variable used to remove original content
    hasOrigContent = 1

    # The Original document to be encrypted
    originalDoc = drive_service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_content = originalDoc.get('body').get('content')

    # The id of the original document
    originalID = originalDoc['documentId']

    # Stores copies of the original document
    shareDocs = []

    # Creates copies for the shares
    copied_file = {'title': 'Share 1'}
    ShareDoc1 = drive_service.list()#.copy(fileId=originalID, body=copied_file).execute()

    for copies in range(3):
        shareDocs.append(originalDoc)
        
        # document_copy_id = drive_response.get('id')

    
    for i in range(len(doc_content)):
        if 'paragraph' in doc_content[i]:
            text = doc_content[i].get('paragraph').get('elements')[0].get('textRun').get('content')
            SSShares = SSSTest.SSSText(text)

            # Gets the sss shares from each letter
            # j = 0 to length of the share content - 1
            for j in range(len(SSShares)):
                # Gets the individual share
                # x = SSShares[j]


                # Split the share between the three doc shares
                # k = 0 to 2
                for k in range(len(SSShares[j])):

                    shareDocContent = shareDocs[k].get('body').get('content')[i]

                    if 'paragraph' in shareDocContent:
                        doc = shareDocContent.get('paragraph').get('elements')[0].get('textRun')

                        # Remove Original Text from copies
                        if(hasOrigContent == 1):
                            doc['content'] = ""
                            hasOrigContent = 0

                        print("Doc "+ str(k) + " Content: " + doc.get('content') + "Share: " + str(SSShares[j][k]))


                        doc['content'] += str(SSShares[j][k]) + " "

            # Set it back for the next content
            hasOrigContent = 1



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
    with open('ShareDoc1.txt', 'w') as f:
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
