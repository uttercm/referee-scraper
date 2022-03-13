from bs4 import BeautifulSoup
import datetime
from pytz import timezone
import collections
import requests
import copy

GameEvent = collections.namedtuple('Event', ['is_my_game', 'summary', 'date_time', 'location', 'description', 'is_cancelled'])

class Scraper:

    def __init__(self):
        self.headers = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}
        self.url = None
        self.login_url = None
        self.session = None
        self.post_headers = None
        self.my_name = None

    def login(self):
                #For Setting Cookies
        self.session = requests.Session()
        r = self.session.get(self.url, headers = self.headers)
        
        data = self.get_login_data()

        post_headers = copy.copy(self.headers)
        post_headers["Accept-Language"] = 'en-US,en;q=0.9'
        self.post_headers = post_headers
        post_response = self.session.post(self.login_url, data=data, headers=post_headers)

    def get_login_data(self):
        raise NotImplementedError

    def navigate_parsing_page(self):
        raise NotImplementedError

    def get_current_games(self):
        raise NotImplementedError
    
    def get_all_games(self):
        raise NotImplementedError

    def parse_event_line(self, line):
        raise NotImplementedError
