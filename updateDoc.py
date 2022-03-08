from apiclient import errors
from apiclient.http import MediaFileUpload
# ...

def update_file(service, file_id, new_title,
                new_filename, new_revision):

    # First retrieve the file from the API.
    file = service.files().get(fileId=file_id).execute()

    # File's new metadata.
    file['title'] = new_title

    # File's new content.
    media_body = MediaFileUpload(
        new_filename, resumable=True)

    # Send the request to the API.
    updated_file = service.files().update(
        fileId=file_id,
        body=file,
        newRevision=new_revision,
        media_body=media_body).execute()


    return updated_file
    