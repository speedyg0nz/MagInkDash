#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is where we retrieve events from the Google Calendar. Before doing so, make sure you have both the
credentials.json and token.pickle in the same folder as this file. If not, run quickstart.py first.
"""

from __future__ import print_function
import datetime as dt
import pickle
import os.path
import pathlib
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import logging


class GcalHelper:

    def __init__(self):
        self.logger = logging.getLogger('maginkdash')
        # Initialise the Google Calendar using the provided credentials and token
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        self.currPath = str(pathlib.Path(__file__).parent.absolute())

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(self.currPath + '/token.pickle'):
            with open(self.currPath + '/token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.currPath + '/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.currPath + '/token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds, cache_discovery=False)

    def list_calendars(self):
        # helps to retrieve ID for calendars within the account
        # calendar IDs added to config.json will then be queried for retrieval of events
        self.logger.info('Getting list of calendars')
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        if not calendars:
            self.logger.info('No calendars found.')
        for calendar in calendars:
            summary = calendar['summary']
            cal_id = calendar['id']
            self.logger.info("%s\t%s" % (summary, cal_id))

    def to_datetime(self, isoDatetime, localTZ):
        # replace Z with +00:00 is a workaround until datetime library decides what to do with the Z notation
        to_datetime = dt.datetime.fromisoformat(isoDatetime.replace('Z', '+00:00'))
        return to_datetime.astimezone(localTZ)

    def adjust_end_time(self, endTime, localTZ):
        # check if end time is at 00:00 of next day, if so set to max time for day before
        if endTime.hour == 0 and endTime.minute == 0 and endTime.second == 0:
            newEndtime = localTZ.localize(
                dt.datetime.combine(endTime.date() - dt.timedelta(days=1), dt.datetime.max.time()))
            return newEndtime
        else:
            return endTime

    def is_multiday(self, start, end):
        # check if event stretches across multiple days
        return start.date() != end.date()

    def retrieve_events(self, calendars, startDatetime, endDatetime, localTZ):
        # Call the Google Calendar API and return a list of events that fall within the specified dates
        event_list = []

        min_time_str = startDatetime.isoformat()
        max_time_str = endDatetime.isoformat()
        if False:
            return event_list

        self.logger.info('Retrieving events between ' + min_time_str + ' and ' + max_time_str + '...')
        events_result = []
        for cal in calendars:
            events_result.append(
                self.service.events().list(calendarId=cal, timeMin=min_time_str,
                                           timeMax=max_time_str, singleEvents=True,
                                           orderBy='startTime').execute()
            )

        events = []
        for eve in events_result:
            events += eve.get('items', [])
            # events = events_result.get('items', [])

        if not events:
            self.logger.info('No upcoming events found.')
        for event in events:
            # extracting and converting events data into a new list
            new_event = {'summary': event['summary']}

            if event['start'].get('dateTime') is None:
                new_event['allday'] = True
                new_event['startDatetime'] = self.to_datetime(event['start'].get('date'), localTZ)
            else:
                new_event['allday'] = False
                new_event['startDatetime'] = self.to_datetime(event['start'].get('dateTime'), localTZ)

            if event['end'].get('dateTime') is None:
                new_event['endDatetime'] = self.adjust_end_time(self.to_datetime(event['end'].get('date'), localTZ),
                                                               localTZ)
            else:
                new_event['endDatetime'] = self.adjust_end_time(self.to_datetime(event['end'].get('dateTime'), localTZ),
                                                               localTZ)

            new_event['updatedDatetime'] = self.to_datetime(event['updated'], localTZ)
            new_event['isMultiday'] = self.is_multiday(new_event['startDatetime'], new_event['endDatetime'])
            event_list.append(new_event)

        # We need to sort eventList because the event will be sorted in "calendar order" instead of hours order
        # TODO: improve because of double cycle for now is not much cost
        event_list = sorted(event_list, key=lambda k: k['startDatetime'])
        return event_list
