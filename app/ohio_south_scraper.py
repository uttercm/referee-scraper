from bs4 import BeautifulSoup
import datetime
from pytz import timezone
import requests
import copy

from app.scraper import Scraper, GameEvent

class OhioSouthScraper(Scraper):

    HEADERS = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0'}

    def __init__(self):
        super().__init__()
        self.url = "http://www.thegameschedule.com/ohiosouth/index.php"
        self.login_url = "http://www.thegameschedule.com/ohiosouth/ref1.php"
        self.games_url = "http://www.thegameschedule.com/ohiosouth/ref2.php"
        self.my_name = 'C. Utter'

    def get_login_data(self):
        return {
            'requiredref_num': '19172',
            'requiredpassword':  'VR9vn2',
            'Submit1': 'Go'
        }

    def navigate_parsing_page(self):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=7)
        # to convert dates to string use .strftime('%Y-%m-%d')
        game_data = {
            'ref_radio': 'add_open',
            'ref_num': ['19172', '19172'],
            'complexes': 'all',
            'v_start_day': now.strftime('%Y-%m-%d'),
            'v_end_day': end.strftime('%Y-%m-%d'),
            'submit3': 'Show+Games',
            'quick_pick': '6'
        }

        self.game_data = game_data
        get_response = self.session.post(self.games_url, data=game_data, headers=self.post_headers)
        self.soup = BeautifulSoup(get_response.content, "html.parser")

    def get_current_games(self):
        game_list = []
        main_table = self.soup.find('body').find_all('table')[1].find_all('tr')
        games = main_table[2].find('table').find_all('tr')
        for game in games[1:]:
            game_data = game.find_all('td')
            level = game_data[1].text.strip()[3:]
            level = level[-1] + level[-4:-2]
            new_game = { 
                'game_num': game_data[0].text.strip(),
                'Level': level,
                'Date': datetime.datetime.now().strftime("%Y") + '-'+ game_data[2].text.strip().replace('/', '-'),
                'Time': game_data[3].text.strip(),
                'Field': game_data[4].text.strip(),
                'hm_team': game_data[5].text.strip(),
                'aw_team': game_data[6].text.strip(),
                'Ref': game_data[7].text.strip(),
                'AR1': game_data[8].text.strip(),
                'AR2': game_data[9].text.strip()
            }
            game_list.append(new_game)
        return game_list
    
    def get_all_games(self):
        all_games = []
        pages = self.soup.find('body').find_all('table')[1].find_all('option')
        if len(pages) > 0:
            original_soup = self.soup
            for page in pages:
                url = self.games_url + page['value']
                get_response = self.session.get(url, headers=self.post_headers)
                self.soup = BeautifulSoup(get_response.content, "html.parser")
                all_games += self.get_current_games()
            self.soup = original_soup
        else:
            all_games = self.get_current_games()
        return all_games

    def parse_event_line(self, line):
        age_level = line['Level'][0: 3]
        is_my_game = False
        summary = age_level
        position = None
        description = ''
        location = line['Field']
        if self.my_name == line['Ref']:
            position = 'Ref'
        elif self.my_name == line['AR1']:
            position = 'AR1'
        elif self.my_name == line['AR2']:
            position = 'AR2'
        
        is_cancelled = line['hm_team'] == 'Canceled'

        if position:
            is_my_game = True
            summary += " {}".format(position)
            print('existing game for me')

        date_time = datetime.datetime.strptime("{} {}".format(line['Date'], line['Time']), '%Y-%m-%d %I:%M %p')
        date_time = date_time.astimezone(timezone('US/Eastern'))
        description = "{} vs {}".format(line['hm_team'], line['aw_team'])
        return GameEvent(is_my_game, summary, date_time, location, description, is_cancelled)

