import copy
import datetime
import json

import requests


class Scraper:
    def __init__(self):
        self.headers = {
            "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }
        self.login_url = None
        self.home_url = None
        self.session = None
        self.post_headers = None
        self.my_name = None
        self.year = datetime.datetime.now().year
        with open("application_info.json", "r") as f:
            self.login_info = json.load(f)[self.name]

    def login(self):
        # For Setting Cookies
        self.session = requests.Session()
        self.session.get(self.login_url, headers=self.headers)

        data = self.get_login_data()

        post_headers = copy.copy(self.headers)
        post_headers["Accept-Language"] = "en-US,en;q=0.9"
        self.post_headers = post_headers
        self.session.post(self.home_url, data=data, headers=post_headers)

    def get_login_data(self):
        raise NotImplementedError

    def navigate_parsing_page(self):
        raise NotImplementedError

    def get_current_games(self):
        raise NotImplementedError

    def get_all_games(self):
        raise NotImplementedError
