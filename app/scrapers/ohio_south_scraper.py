import datetime
import json

from bs4 import BeautifulSoup
from pytz import timezone

from app.scrapers.scraper import GameEvent, Scraper


class OhioSouthScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.url = "http://www.thegameschedule.com/ohiosouth/index.php"
        self.login_url = "http://www.thegameschedule.com/ohiosouth/ref1.php"
        self.games_url = "http://www.thegameschedule.com/ohiosouth/ref2.php"
        self.my_name = None
        self.ref_num = None

    def get_login_data(self):
        f = open("application_info.json", "r")
        login_info = json.load(f)

        self.ref_num = login_info["ohio_south"]["ref_num"]
        self.my_name = login_info["ohio_south"]["my_name"]
        return {
            "requiredref_num": self.ref_num,
            "requiredpassword": login_info["ohio_south"]["password"],
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

        self.game_data = game_data
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
            summary = game_data[1].text.strip()

            game_date = self.year + "-" + game_data[2].text.strip().replace("/", "-")
            game_time = game_data[3].text.strip()
            date_time = datetime.datetime.strptime(
                "{} {}".format(game_date, game_time), "%Y-%m-%d %I:%M %p"
            ).astimezone(timezone("US/Eastern"))

            location = game_data[4].text.strip()

            home_team = game_data[5].text.strip()
            is_cancelled = home_team == "Canceled"
            description = "{} vs {}".format(home_team, game_data[6].text.strip())
            my_position = self.get_my_position(
                self.__remove_links(game_data[7].text.strip()),
                self.__remove_links(game_data[8].text.strip()),
                self.__remove_links(game_data[9].text.strip()),
            )
            if my_position:
                is_my_game = True
                summary += " {}".format(my_position)
                print("existing game for me")
            new_game = GameEvent(
                is_my_game, summary, date_time, location, description, is_cancelled
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
