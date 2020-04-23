from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request 
dir_path = os.path.dirname(os.path.realpath(__file__))

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID and range of a sample spreadsheet.
spreadsheet_id = "1ztRUmGchJLMTBrDrpPEF8yh8XWmrzOH1ouWOvJrwCME"
def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                dir_path + '/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    range_sh = "Engineering!A1:10000"
    result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id, range=range_sh).execute()
    rows = result.get('values', [])
    print('{0} rows retrieved.'.format(len(rows)))
    print (rows)

if __name__ == '__main__':
    main()