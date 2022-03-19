from datetime import datetime

from bs4 import BeautifulSoup
from pytz import timezone

from app.scrapers.scraper import GameEvent, Scraper


class MVYSAScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.url = "https://www.mvysa.com/cgi-bin/login.cgi"
        self.login_url = "https://www.mvysa.com/cgi-bin/menu.cgi"
        self.naviation_url = ""
        self.games_url = "https://www.mvysa.com/cgi-bin/referee.cgi"
        self.my_name = None
        self.ref_num = None
        self.login_info = self.login_info["mvysa"]

    def get_login_data(self):

        username = self.login_info["username"]
        self.my_name = self.login_info["my_name"]
        return {
            "fnc": "login",
            "mo": "",
            "user_id": username,
            "pass": self.login_info["password"],
            "cmd": "Log+In",
        }

    def navigate_parsing_page(self):
        game_data = {
            "fnc": "showgames",
            "my_games": "Y",
            "open_games": "Y",
            "cmd": "See+Games",
        }

        get_response = self.session.post(
            self.games_url, data=game_data, headers=self.post_headers
        )

        self.soup = BeautifulSoup(get_response.content, "html.parser")

    # MVYSA shows all games on the first page for this
    def get_current_games(self):
        pass

    def get_all_games(self):
        all_games = []
        main_table = (
            self.soup.find("body")
            .find("center")
            .find_all("table")[1]
            .find_all("table")[1]
        )
        games = main_table.find_all("tr")
        for game in games[1:]:
            is_my_game = False
            game_data = game.find_all("td")

            columns = {}

            for i, column in enumerate(game_data):
                columns[i] = column.renderContents().decode("utf-8").split("<br/>")

            unparsed_date = game_data[1].get_text(strip=True, separator=" ")
            date_time = (
                datetime.strptime(unparsed_date, "%a, %b %d %I:%M %p")
                .replace(year=self.year)
                .astimezone(timezone("US/Eastern"))
            )
            summary = "MVYSA " + columns[0][1].strip()
            my_position = self.get_my_position(
                self.__remove_links(columns[5][0]),
                self.__remove_links(columns[5][1]),
                self.__remove_links(columns[5][2]),
            )
            if my_position:
                is_my_game = True
                summary += " {}".format(my_position)
                print("existing game for me")

            is_cancelled = False
            location = game_data[2].get_text(strip=True, separator=" ")
            description = "{} vs {}".format(
                columns[3][0].strip(), columns[3][1].strip()
            )
            new_game = GameEvent(
                is_my_game, summary, date_time, location, description, is_cancelled
            )
            all_games.append(new_game)
        return all_games

    def __remove_links(self, position):
        if "Open" in position:
            return "Open"
        if self.my_name in position:
            return self.my_name
        return position.strip()
