from app.game_scraper import GameScraper
from app.csv_reader import CsvReader
from app.sendgrid_mailer import SendGridMailer
from app.google_calendar import GoogleCalendar
import requests
import copy
import datetime
import urllib.parse
import csv
import io
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import sys
import argparse

parser = argparse.ArgumentParser(description='Referee Scraper.')

parser.add_argument("-l", "--league", help="Either mv or ohiosouth.", default="mv")
parser.add_argument("-f", "--format", help="Either scraper or csv.", default="scraper")

args = parser.parse_args()

headers = { 'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }

league = args.league or 'mv'
parsing_format = args.format or 'scraper'

#For Setting Cookies
URL = "http://www.thegameschedule.com/{}/index.php".format(league)

session = requests.Session()
r = session.get(URL, headers = headers)

LOGIN_URL = "http://www.thegameschedule.com/{}/ref1.php".format(league)
data = {
    'requiredref_num': '19172',
    'requiredpassword':  'VR9vn2',
    'Submit1': 'Go'
}

post_headers = copy.copy(headers)
post_headers["Accept-Language"] = 'en-US,en;q=0.9'
post_response = session.post(LOGIN_URL, data=data, headers=post_headers)

now = datetime.datetime.now()
end = now + datetime.timedelta(days=30)

sendgrid_mailer = SendGridMailer()

ALLOWED_LEVELS = ['G09', 'G11', 'G10', 'G12', 'G13', 'G14', 'B09', 'B10', 'B11', 'B12']
MY_NAME = 'C. Utter'

google_calendar = GoogleCalendar()

def create_event(summary, location, date_time):
    event_end = date_time + datetime.timedelta(minutes=90)
    return {
        'summary': summary,
        'location': location,
        'description': '',
        'start': {
            'dateTime': date_time.isoformat() + '-04:00'
        },
        'end': {
            'dateTime': event_end.isoformat() + '-04:00'
        },
        'reminders': {
            'useDefault': True,
        },
    }

def parse_event_line(line):
    age_level = line['Level'][0: 3]
    is_my_game = False
    summary = age_level
    if age_level not in ALLOWED_LEVELS:
        return False, None, None, None
    position = None
    location = line['Field']
    if MY_NAME == line['Ref']:
        position = 'Ref'
    elif MY_NAME == line['AR1']:
        position = 'AR1'
    elif MY_NAME == line['AR2']:
        position = 'AR2'
    
    if position:
        is_my_game = True
        summary += " {}".format(position)
        print('existing game for me')

    date_time = datetime.datetime.strptime("{} {}".format(line['Date'], line['Time']), '%Y-%m-%d %I:%M %p')

    return is_my_game, summary, date_time, location

games = []
if parsing_format == 'scraper':
    scraper = GameScraper(league, post_headers, session)
    games = scraper.get_all_games()
else:
    stream = CsvReader.get_stream(post_headers, session, sendgrid_mailer)
    games = csv.DictReader(stream)

# for line in reader:
for line in games:
    is_my_game, summary, date_time, location = parse_event_line(line)
    if is_my_game:
        event = create_event(summary, location, date_time)
        print(event)
        if not google_calendar.already_exists(event):
            print('creating event')
            google_calendar.create_event(event)
            sendgrid_mailer.send_new_calendar_event(summary, date_time)