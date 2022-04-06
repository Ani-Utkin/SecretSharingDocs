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
import googleDocUpload
import random


SHEETS_ID = '1aR13nBTPIQvI0-HblCq2HU7G6SlcbZOB4s4eR3KorKM'

def EncryptSheets(values, sheet_range, shareSheetsIDs):

    # Get the text from the excel sheet
    share1content = []
    share2content = []
    share3content = []

    sss_rowcolumn = []
    for row in values:
        share1row = []
        share2row = []
        share3row = []

        for column in row:

            share1word = ""
            share2word = ""
            share3word = ""
        
            sss_rowcolumn = SSSTest.SSSText(column)
            for letter in range(len(column)):
                share1word += str(sss_rowcolumn[letter][0]) + " "
                share2word += str(sss_rowcolumn[letter][1]) + " "
                share3word += str(sss_rowcolumn[letter][2]) + " "

            share1row.append(share1word)
            share2row.append(share2word)
            share3row.append(share3word)

        share1content.append(share1row)
        share2content.append(share2row)
        share3content.append(share3row)

    value_range_body1={
        'values': share1content
    }

    value_range_body2={
        'values': share2content
    }

    value_range_body3={
        'values': share3content
    }

    sheets_service.spreadsheets().values().update(
        spreadsheetId=shareSheetsIDs[0],
        valueInputOption='USER_ENTERED',
        range=sheet_range,
        body=value_range_body1).execute()

    sheets_service.spreadsheets().values().update(
        spreadsheetId=shareSheetsIDs[1],
        valueInputOption='USER_ENTERED',
        range=sheet_range,
        body=value_range_body2).execute()

    sheets_service.spreadsheets().values().update(
        spreadsheetId=shareSheetsIDs[2],
        valueInputOption='USER_ENTERED',
        range=sheet_range,
        body=value_range_body3).execute()

def ReconstructSheets(shareSheetsIDs, sheet_range):

    # Create Spreadsheet for Reconstruction
    recon_spreadsheet = {
        'properties': {
            'title': 'Reconstructed Document'
        }
    }
    recon_spreadsheet = sheets_service.spreadsheets().create(
        body=recon_spreadsheet,
        fields='spreadsheetId').execute()
    
    pool = random.sample(shareSheetsIDs, 2)

    sheetValues = []

    # Get the two random sheets for reconstruction
    for id in pool:
        sheet = sheets_service.spreadsheets().values().get(spreadsheetId=id, range='Sheet1').execute()
        values = sheet.get('values')
        sheetValues.append(values)
    
    contentList = []
    # Merge the shares of the two chosen sheets and calculate the SSS of the share
    for (row1, row2) in zip(sheetValues[0], sheetValues[1]):
        rowList = []
        for (column1, column2) in zip(row1, row2):
            word_list = []
            share1 = column1.split(") ")
            share2 = column2.split(") ")

            for i in range(len(share1) - 1):
                share1[i] = share1[i] + ")"
                share2[i] = share2[i] + ")"
            
            # Convert word to int tuple type
            for letter1, letter2 in zip(share1, share2):
                letter_list = []
                if letter1 == "" or letter2 == "":
                    continue
                
                letterInt1 = tuple(int(num) for num in letter1.replace('(', '').replace(')', '').replace('...', '').split(', '))
                letterInt2 = tuple(int(num) for num in letter2.replace('(', '').replace(')', '').replace('...', '').split(', '))

                letter_list.append(letterInt1)
                letter_list.append(letterInt2)

                word_list.append(letter_list)
            
            # Reconstruct the word
            reconWord = SSSTest.SSS_reconstruct(word_list)
            rowList.append(reconWord)

        # Add row contents to the full content values
        contentList.append(rowList)

    # Update the reconstructed spreadsheet
    body={
        'values': contentList
    }
    sheets_service.spreadsheets().values().update(
        spreadsheetId=recon_spreadsheet.get('spreadsheetId'),
        valueInputOption='USER_ENTERED',
        range=sheet_range,
        body=body).execute()


def SheetsAPI():

    # Gets Credentials
    creds = None
    creds = googleDocUpload.getCreds(creds)

    global sheets_service

    # Call the Google Spreadsheet API Service
    sheets_service = build('sheets', 'v4', credentials=creds)

    # Get the spreadsheet to be encrypted
    sheet = sheets_service.spreadsheets().values().get(spreadsheetId=SHEETS_ID, range='Sheet1').execute()
    # Text of the original spreadsheet
    values = sheet.get('values')

    # The range of the spreadsheet
    sheet_range = sheet.get('range')

    # Create the spreadsheet shares
    shareSheetsIDs = []
    for i in range(3):
        spreadsheet = {
            'properties': {
                'title': 'Share ' + str(i + 1)
            }
        }
        spreadsheet = sheets_service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId').execute()

        shareSheetsIDs.append(spreadsheet.get('spreadsheetId'))
    
    # Method to encrypt the contents of the sheet
    EncryptSheets(values, sheet_range, shareSheetsIDs)
    # Method to decrypt the shares created by the encryption
    ReconstructSheets(shareSheetsIDs, sheet_range)

SheetsAPI()
