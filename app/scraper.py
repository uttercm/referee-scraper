import collections
import copy
import datetime

import requests
from pytz import timezone

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
        self.year = datetime.datetime.now().strftime("%Y")

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

    def parse_event_line(self, line):
        age_level = line["Level"][0:3]
        is_my_game = False
        summary = age_level or ""
        position = None
        description = ""
        location = line["Field"]
        if self.my_name == line["Ref"]:
            position = "Ref"
        elif self.my_name == line["AR1"]:
            position = "AR1"
        elif self.my_name == line["AR2"]:
            position = "AR2"

        is_cancelled = line["hm_team"] == "Canceled"

        if position:
            is_my_game = True
            summary += " {}".format(position)
            print("existing game for me")

        date_time = datetime.datetime.strptime(
            "{} {}".format(line["Date"], line["Time"]), "%Y-%m-%d %I:%M %p"
        )
        date_time = date_time.astimezone(timezone("US/Eastern"))
        description = "{} vs {}".format(line["hm_team"], line["aw_team"])
        return GameEvent(
            is_my_game, summary, date_time, location, description, is_cancelled
        )
