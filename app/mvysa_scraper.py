import json
from datetime import datetime

from bs4 import BeautifulSoup

from app.scraper import Scraper


class MVYSAScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.url = "https://www.mvysa.com/cgi-bin/login.cgi"
        self.login_url = "https://www.mvysa.com/cgi-bin/menu.cgi"
        self.naviation_url = ""
        self.games_url = "https://www.mvysa.com/cgi-bin/referee.cgi"
        self.my_name = None
        self.ref_num = None

    def get_login_data(self):
        f = open("application_info.json", "r")
        login_info = json.load(f)

        username = login_info["mvysa"]["username"]
        self.my_name = login_info["mvysa"]["my_name"]
        return {
            "fnc": "login",
            "mo": "",
            "user_id": username,
            "pass": login_info["mvysa"]["password"],
            "cmd": "Log+In",
        }

    def navigate_parsing_page(self):
        game_data = {
            "fnc": "showgames",
            "my_games": "Y",
            "open_games": "Y",
            "cmd": "See+Games",
        }

        self.game_data = game_data
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
            game_data = game.find_all("td")

            columns = {}

            for i, column in enumerate(game_data):
                columns[i] = column.renderContents().decode("utf-8").split("<br/>")

            special_date = BeautifulSoup(columns[1][0], "html.parser")
            game_date = (
                self.year
                + "-"
                + datetime.strptime(
                    special_date.get_text(strip=True), "%a, %b %d"
                ).strftime("%m-%d")
            )
            new_game = {
                "game_num": columns[0][0].strip(),
                "Level": columns[0][1].strip(),
                "Date": game_date,
                "Time": BeautifulSoup(columns[1][1], "html.parser").get_text(
                    strip=True
                ),
                "Field": game_data[2].get_text(strip=True, separator=" "),
                "hm_team": columns[3][0].strip(),
                "aw_team": columns[3][1].strip(),
                "Ref": self.__remove_links(columns[5][0]),
                "AR1": self.__remove_links(columns[5][1]),
                "AR2": self.__remove_links(columns[5][2]),
            }
            all_games.append(new_game)
        return all_games

    def __remove_links(self, position):
        if "Open" in position:
            return "Open"
        if self.my_name in position:
            return self.my_name
        return position.strip()
