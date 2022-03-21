from datetime import datetime

from bs4 import BeautifulSoup

from app.models.game_event import GameEvent
from app.models.referee_crew import RefereeCrew
from app.scrapers.scraper import Scraper


class MVYSAScraper(Scraper):
    name = "mvysa"

    def __init__(self):
        super().__init__()
        base_url = "https://www.mvysa.com/cgi-bin/"
        self.login_url = base_url + "/login.cgi"
        self.home_url = base_url + "/menu.cgi"
        self.games_url = base_url + "/referee.cgi"
        self.my_name = None
        self.ref_num = None

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
            game_data = game.find_all("td")

            columns = {}

            for i, column in enumerate(game_data):
                columns[i] = column.renderContents().decode("utf-8").split("<br/>")

            unparsed_date = game_data[1].get_text(strip=True, separator=" ")
            date_time = datetime.strptime(unparsed_date, "%a, %b %d %I:%M %p").replace(
                year=self.year
            )
            level = columns[0][1].strip()
            ref = self.__remove_links(columns[5][0])
            ar1 = self.__remove_links(columns[5][1])
            ar2 = self.__remove_links(columns[5][2])
            ref_crew = RefereeCrew(self.my_name, ref, ar1, ar2)

            location = game_data[2].get_text(strip=True, separator=" ")
            home_team = columns[3][0].strip()
            away_team = columns[3][1].strip()
            new_game = GameEvent(
                self.name, level, date_time, location, home_team, away_team, ref_crew
            )
            all_games.append(new_game)
        return all_games

    def __remove_links(self, position):
        if "Open" in position:
            return ""
        if self.my_name in position:
            return self.my_name
        return position.strip()
