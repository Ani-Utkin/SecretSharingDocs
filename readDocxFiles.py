import docx

# The program should be able to take a .docx document as input
# Then distinguish between tables and paragraph from the document
# This program should be able to read the contents of the document,
# and write them to another new document.

# When the new document is finished writing, the Google Drive API will upload it to the Google Drive.

# This is to test out how to perserve the structure of the input document.

# From working with this api, the paragraphs (docParagraphs) is an object.
# There should be a way to convert it to a string so that it can be written
# into the new document.

# Gets all the paragraphs in a document
def getParagraphs(document):
    docParagraphs = document.paragraphs

# Gets all the tables in a document
def getTables(document):
    docTables = document.tables


doc = docx.Document("testDocuments/TestDocument.docx")

getParagraphs(doc)
getTables(doc)