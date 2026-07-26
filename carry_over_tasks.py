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
from zoneinfo import ZoneInfo


def datetime_to_utc(dt):
    return dt.astimezone(datetime.timezone.utc).isoformat().split('+')[0] + 'Z'


def get_event_template(summary):
    today = datetime.datetime.now(ZoneInfo(settings.TIMEZONE)).date()
    tomorrow = (today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    event_body = {
        'summary': summary,
        'start': {
            'dateTime': f'{tomorrow}T17:00:00-07:00',
            'timeZone': settings.TIMEZONE,
        },
        'end': {
            'dateTime': f'{tomorrow}T23:59:00-07:00',
            'timeZone': settings.TIMEZONE,
        },
    }
    return event_body


def get_events_day(date):
    date_start, date_end = (datetime.datetime.combine(date, x) for x in 
                              (datetime.time(0, 0, 0), datetime.time(23, 59, 59)))
    date_start, date_end = map(datetime_to_utc, (date_start, date_end))
    events_all = service.events().list(calendarId='primary', timeMin=date_start, timeMax=date_end, 
                                   singleEvents=True, orderBy='startTime').execute()['items']
    
    events = set()
    for event in events_all:
        if 'attendees' not in event and 'description' not in event:
            events.add(event['summary'])
    return events


for user in settings.CHROME_PROFILES:
	token_file = settings.TOKEN_FILES[user]
	creds = Credentials.from_authorized_user_file(token_file, settings.SCOPES)
	service = build('calendar', 'v3', credentials=creds)

	today = (datetime.datetime.now(ZoneInfo(settings.TIMEZONE))).date()
	tomorrow = today +  datetime.timedelta(days=1)
	for event_summary in get_events_day(today) - get_events_day(tomorrow):
	    event_body = get_event_template(event_summary)
	    created_event = service.events().insert(
	        calendarId='primary', 
	        body=event_body
	    ).execute()

