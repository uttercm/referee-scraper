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
        for game in games[1:2]:
            game_data = game.find_all("td")

            game_num, level = (
                game_data[0].get_text(strip=True, separator="\n").splitlines()
            )
            game_date, game_time = (
                game_data[1].get_text(strip=True, separator="\n").splitlines()
            )
            field = game_data[2].get_text(strip=True, separator="\n").replace("\n", " ")
            home, away = game_data[3].get_text(strip=True, separator="\n").splitlines()
            ref, ar1, ar2 = (
                game_data[5].get_text(strip=True, separator="\n").splitlines()
            )
            game_date = (
                self.year
                + "-"
                + datetime.strptime(game_date, "%a, %b %d").strftime("%m-%d")
            )
            new_game = {
                "game_num": game_num,
                "Level": level,
                "Date": game_date,
                "Time": game_time,
                "Field": field,
                "hm_team": home,
                "aw_team": away,
                "Ref": ref,
                "AR1": ar1,
                "AR2": ar2,
            }
            print(new_game)
            # all_games.append(new_game)
        return all_games
