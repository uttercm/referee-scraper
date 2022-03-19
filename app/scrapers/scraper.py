import collections
import copy
import datetime
import json

import requests

GameEvent = collections.namedtuple(
    "Event",
    [
        "is_my_game",
        "summary",
        "date_time",
        "location",
        "description",
        "is_cancelled",
    ],
)


class Scraper:
    def __init__(self):
        self.headers = {
            "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
        }
        self.url = None
        self.login_url = None
        self.session = None
        self.post_headers = None
        self.my_name = None
        self.year = datetime.datetime.now().year
        with open("application_info.json", "r") as f:
            self.login_info = json.load(f)

    def login(self):
        # For Setting Cookies
        self.session = requests.Session()
        self.session.get(self.url, headers=self.headers)

        data = self.get_login_data()

        post_headers = copy.copy(self.headers)
        post_headers["Accept-Language"] = "en-US,en;q=0.9"
        self.post_headers = post_headers
        self.session.post(self.login_url, data=data, headers=post_headers)

    def get_login_data(self):
        raise NotImplementedError

    def navigate_parsing_page(self):
        raise NotImplementedError

    def get_current_games(self):
        raise NotImplementedError

    def get_all_games(self):
        raise NotImplementedError

    def get_my_position(self, ref, ar1, ar2):
        position = None
        if self.my_name == ref:
            position = "Ref"
        elif self.my_name == ar1:
            position = "AR1"
        elif self.my_name == ar2:
            position = "AR2"
        return position
