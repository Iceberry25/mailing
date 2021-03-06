from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/drive']

spreadsheet_id = "1KvhduDzY-7gwAchCBjgW6w6GgiAxEZdp_VlhT8wlB5Q"
message_text = ""
with open("email.txt", "r") as f:
    message_text = f.read()

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service_gmail = build('gmail', 'v1', credentials=creds)
    service_sheets =  build('sheets', 'v4', credentials=creds)

    # send_matching_mails(service)  
    data = get_sheet_data(service_sheets) [1:]

    data_list = format_data(data)
    send_matching_mails(service_gmail, service_sheets, data_list)

def format_data(data):
    data_list = []
    for counter, row in enumerate(data):
        if (len(row)) < 20:
            continue
        if len(row)>=21:
            if row[20] == 'Yes': 
                continue

        email = row[19]
        if email == '':
            continue
        row_no = counter+2
        message = message_text.format(mentorname=row[18], name=row[2], email=row[1], mode=row[8], phoneno=row[9], extra=row[13], subjects=row[12], group=row[17], reason=row[7], extradetails=row[14])
        if len(row) >= 21:
            row[20] = 'Yes'
        else:
            row.append('Yes')
        obj = {"email":email, "message": message, "row": row_no, "raw": row}
        data_list.append(obj)

    return data_list

def get_sheet_data(service):
    range_sh = "Form Responses 2!A1:10000"
    result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id, range=range_sh).execute()
    rows = result.get('values', [])
    return rows

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  raw_message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
  return {
    'raw': raw_message.decode("utf-8")
  }


def create_draft(service, user_id, message_body):
  try:
    message = {'message': message_body}
    draft = service.users().drafts().create(userId=user_id, body=message).execute()

    print("Draft id: %s\nDraft message: %s" % (draft['id'], draft['message']))

    return draft
  except Exception as e:
    print('An error occurred: %s' % e)
    return None 

def send_message(service, user_id, message):
  try:
    message = service.users().messages().send(userId=user_id, body=message).execute()
    return message
  except Exception as e:
    print('An error occurred: %s' % e)
    return None

def send_matching_mails(service_gmail, service_sheets, data_list):
    counter = 0
    for entry in data_list:
        message = create_message("covedindia@gmail.com", entry["email"], "Coved India: Mentee has been assigned", (entry["message"]))
        result = send_message(service_gmail, 'me', message)
        if result is None:
            print ("Entry {0}: Email could not be sent. Skipping".format(entry["row"]))
            continue
        sheet_result = update_status(service_sheets, entry)
        if sheet_result is None:
            print ("Entry {0}: Sheet could not be updated. Skipping".format(entry["row"]))
            continue
        print ("Entry in Row {0} updated and mentor informed".format(entry["row"]))
        counter+=1
    print ("Total {0} out of {1} matches have been informed".format(counter, len(data_list)))

def update_status(service_sheets, entry):
    range_up = "A{0}:W{0}".format(entry["row"])
    values = [entry["raw"]]
    body = {'values': values}

    try:
        result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_up,valueInputOption="RAW", body=body).execute()
        return result
    except Exception as e:
        print('An error occurred: %s' % e)
        return None

if __name__ == '__main__':
    main()