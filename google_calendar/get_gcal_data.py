#!/usr/bin/env python3

import os
import sys
import subprocess as sp
import datetime
import settings
sys.path.append(settings.PYTHON_LIB_LOCATION)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def parse_description(description):
    items = []
    balance = 0
    prev = False
    for ch in description:
        if ch == '<':
            balance += 1
        elif ch == '>':
            balance -= 1
            prev = bool(balance)
        elif balance == 0:
            if not prev:
                items.append(ch)
                prev = True
            else:
                items[-1] += ch

    items_modified = []
    for item in items:
        item = item.strip().split('\n')
        if any(substring in ''.join(item) for substring in settings.ZOOM_SUBSTRINGS):
            for subitem in item:
                if settings.LINK_PREFIX in subitem:
                    subitem = subitem[subitem.index(settings.LINK_PREFIX):]
                    item = [subitem.strip()]
                    break
        if item and item[0].startswith(settings.LINK_PREFIX):
            items_modified += item
    return items_modified


def write_events(events, outfile_path):
    events_str = ''
    for event in events:
        event_info = [event['summary']]
        if event['start'].get('dateTime') is None:
            start = datetime.datetime.strptime(event['start'].get('date')[:16], '%Y-%m-%d') + datetime.timedelta(hours=12)
        else:
            start = datetime.datetime.strptime(event['start'].get('dateTime')[:16], '%Y-%m-%dT%H:%M')
        event_info.append(start.strftime("%m/%d %I:%M%p"))
        if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
            for entry_point in event['conferenceData']['entryPoints']:
                if entry_point['entryPointType'] == 'video':
                    event_info.append(entry_point['uri'])
        if 'description' in event:
            event_info.extend(parse_description(event['description']))
        if 'creator' in event:
            event_info.append(f"Creator: {event['creator']['email']}")
        if 'attendees' in event:
            num = sum([x['responseStatus'] == 'accepted' for x in event['attendees'] if 'responseStatus' in x])
            event_info.append(f"Number of Confirmed Attendees: {num}")
        events_str += '\n\t- '.join(event_info) + '\n\n'
    
    with open(outfile_path, 'r+') as file:
        if file.read() != events_str:
            file.seek(0)
            file.truncate()
            file.write(events_str)


def main(user=0, mandatory_refresh=False):
    creds = None
    token_file = settings.TOKEN_FILES[user]
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, settings.SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid or mandatory_refresh:
        if creds and creds.expired and creds.refresh_token and not mandatory_refresh:
            try:
                creds.refresh(Request())
            except Exception:
                print("EXCEPTED Error")

        if (not (creds and creds.valid) or mandatory_refresh) and (not os.path.exists(settings.QUIET_PATH) or os.stat(settings.QUIET_PATH).st_size == 0):
            sp.run(f"'{settings.CHROME_LOCATION}' --args --profile-directory='{settings.CHROME_PROFILES[user]}' --new_window &> /dev/null", shell=True)
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.CLIENT_SECRET_FILE, settings.SCOPES)
            creds = flow.run_local_server(port=0)

        if creds and creds.valid:
            # Save the credentials for the next run
            with open(token_file, 'w') as token:
                token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.now(datetime.timezone.utc).isoformat().split('+')[0] + 'Z'
        next_week = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks=1)).isoformat().split('+')[0] + 'Z'

        events_result = service.events().list(calendarId='primary', timeMin=now, 
                                            timeMax=next_week, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        write_events(events, outfile_path=settings.OUTFILES[user])
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    same_gcal = []
    os.chdir(os.path.dirname(sys.argv[0]))
    for user in settings.CHROME_PROFILES:
        with open(settings.OUTFILES[user]) as infile:
            same_gcal.append(infile.read())
    same_gcal = same_gcal[0] == same_gcal[1] and same_gcal[0]

    os.environ['MAILTO'] = ""
    for user in settings.CHROME_PROFILES:
        main(user, mandatory_refresh=same_gcal)

