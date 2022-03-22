import datetime

from bs4 import BeautifulSoup

from app.models.game_event import GameEvent
from app.models.referee_crew import RefereeCrew
from app.scrapers.scraper import Scraper


class OhioSouthScraper(Scraper):
    name = "ohio_south"

    def __init__(self):
        super().__init__()
        base_url = "http://www.thegameschedule.com/ohiosouth"
        self.login_url = base_url + "/index.php"
        self.home_url = base_url + "/ref1.php"
        self.games_url = base_url + "/ref2.php"
        self.my_name = None
        self.ref_num = None

    def get_login_data(self):
        self.ref_num = self.login_info["ref_num"]
        self.my_name = self.login_info["my_name"]
        return {
            "requiredref_num": self.ref_num,
            "requiredpassword": self.login_info["password"],
            "Submit1": "Go",
        }

    def navigate_parsing_page(self):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=7)
        # to convert dates to string use .strftime('%Y-%m-%d')
        game_data = {
            "ref_radio": "add_open",
            "ref_num": [self.ref_num, self.ref_num],
            "complexes": "all",
            "v_start_day": now.strftime("%Y-%m-%d"),
            "v_end_day": end.strftime("%Y-%m-%d"),
            "submit3": "Show+Games",
            "quick_pick": "6",
        }

        get_response = self.session.post(
            self.games_url, data=game_data, headers=self.post_headers
        )
        self.soup = BeautifulSoup(get_response.content, "html.parser")

    def get_current_games(self):
        game_list = []
        main_table = self.soup.find("body").find_all("table")[1].find_all("tr")
        games = main_table[2].find("table").find_all("tr")
        for game in games[1:]:
            game_data = game.find_all("td")
            level = game_data[1].text.strip()
            game_date = game_data[2].text.strip()
            game_time = game_data[3].text.strip()
            date_time = datetime.datetime.strptime(
                "{} {}".format(game_date, game_time), "%m/%d %I:%M %p"
            ).replace(year=self.year)

            location = game_data[4].text.strip()

            home_team = game_data[5].text.strip()
            away_team = game_data[6].text.strip()
            ref_crew = RefereeCrew(
                self.my_name,
                game_data[7].text.strip(),
                game_data[8].text.strip(),
                game_data[9].text.strip(),
            )
            new_game = GameEvent(
                self.name,
                level,
                date_time,
                location,
                home_team,
                away_team,
                ref_crew,
                is_cancelled=home_team == "Canceled",
            )
            game_list.append(new_game)
        return game_list

    def get_all_games(self):
        all_games = []
        pages = self.soup.find("body").find_all("table")[1].find_all("option")
        if len(pages) > 0:
            original_soup = self.soup
            for page in pages:
                url = self.games_url + page["value"]
                get_response = self.session.get(url, headers=self.post_headers)
                self.soup = BeautifulSoup(get_response.content, "html.parser")
                all_games += self.get_current_games()
            self.soup = original_soup
        else:
            all_games = self.get_current_games()
        return all_games
