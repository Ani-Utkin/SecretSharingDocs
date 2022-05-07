import json
from flask import Flask, request

import googleDocUpload
import googleSheetUpload

app = Flask(__name__)


# Receive data for encryption
@app.route('/post/encode', methods=['POST'])
def get_encode():

    # Get the info received from the frontend
    body = request.get_json()['docs'][0]
    id = body['id']
    name = body['name']
    mt = body['mimeType']

    if "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in mt:
        googleSheetUpload.SheetsAPI(id)
    elif "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in mt:
        googleDocUpload.DocsAPI(id)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# Receive data for decryption
@app.route('/post/decode', methods=['POST'])
def get_decode():

    id_list = []
    mt = request.get_json()['docs'][0].get('mimeType')

    for doc in request.get_json()['docs']:

        # If the mime type of the files don't match each other
        if doc.get('mimeType') != mt:
            return json.dumps({'success': False }), 404, {'ContentType':'application/json'}

        id_list.append(doc['id'])
    
    if "application/vnd.google-apps.spreadsheet" in mt:
        googleSheetUpload.ReconstructSheets(id_list)
    elif "application/vnd.google-apps.document" in mt:
        googleDocUpload.SSSReconstruct(id_list)

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

# runs the app on the backend
if __name__ == '__main__':
    app.run(debug=True)
