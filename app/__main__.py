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

#sys.path.append(".")
from .google_calendar import GoogleCalendar

headers = { 'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }

#For Setting Cookies
URL = 'http://www.thegameschedule.com/mv/index.php'

session = requests.Session()
r = session.get(URL, headers = headers)

LOGIN_URL = 'http://www.thegameschedule.com/mv/ref1.php'
data = {
    'requiredref_num': '19172',
    'requiredpassword':  'VR9vn2',
    'Submit1': 'Go'
}

post_headers = copy.copy(headers)
post_headers["Accept-Language"] = 'en-US,en;q=0.9'
post_response = session.post(LOGIN_URL, data=data, headers=post_headers)

now = datetime.datetime.now()
end = now + datetime.timedelta(days=7)

# to convert dates to string use .strftime('%Y-%m-%d')
select_statement = "SELECT * FROM schedule_mv WHERE ((game_id = 760 OR game_id = 834 OR game_id = 769 OR game_id = 736) OR (ref1 = '19172' || ref2 = '19172' || ref3 = '19172')  OR (ref1 = '-' || ref2 = '-' || ref3 = '-') ) AND (game_ts between '{}' AND '{}') AND (game_status != '4') ORDER BY game_date, field_name, game_ts LIMIT 0,100".format(now.timestamp(), end.timestamp())



GAMES_URL = 'http://www.thegameschedule.com/mv/ref2.php'

game_data = {
    'create_spreadsheet': 'Create Spreadsheet',
    'pull_query': select_statement,
    'ref_radio': 'add_open',
    'ref_num': '19172',
    'v_start_day': now.strftime('%Y-%m-%d'),
    'v_end_day': end.strftime('%Y-%m-%d'),
    'Submit2': 'yes'
}

print(game_data)


get_response = session.post(GAMES_URL, data=game_data, headers=post_headers)

get_csv = session.get('http://www.thegameschedule.com/mv/download.php?file=excel/games_spreadsheet.csv', headers=post_headers)

#stream = io.BytesIO(get_csv.content)

stream = io.StringIO(get_csv.content.decode('utf-8'))
reader = csv.DictReader(stream)

allowed_levels = ['G11', 'G10', 'G12', 'B12', 'G13', 'G14', 'B09', 'B10', 'B11', 'B12']
my_name = 'C. Utter'

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

google_calendar = GoogleCalendar()

# Call the Calendar API
print('Getting the upcoming 10 events')
events = google_calendar.get_events()
print(events)

for line in reader:
    age_level = line['Level'][0: 3]
    print(age_level)
    if age_level in allowed_levels:
        print(line)
        if my_name in [line['Ref'], line['AR1'], line['AR2']]:
            print('existing game for me')

    break