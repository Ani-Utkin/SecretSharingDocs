import docx

# Gets all the paragraphs in a document
def getParagraphs(document):
    docParagraphs = document.paragraphs

# Gets all the tables in a document
def getTables(document):
    docTables = document.tables


doc = docx.Document("testDocuments/TestDocument.docx")

getParagraphs(doc)
getTables(doc)