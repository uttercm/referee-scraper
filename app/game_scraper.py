from bs4 import BeautifulSoup
import datetime


class GameScraper:
    GAMES_URL = 'http://www.thegameschedule.com/mv/ref2.php'

    def __init__(self, post_headers, session) -> None:
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
        self.post_headers = post_headers
        self.session = session
        get_response = session.post(self.GAMES_URL, data=game_data, headers=post_headers)
        self.soup = BeautifulSoup(get_response.content, "html.parser")
        pass

    def get_current_games(self):
        game_list = []
        main_table = self.soup.find('body').find_all('table')[1].find_all('tr')
        games = main_table[2].find('table').find_all('tr')
        for game in games:
            game_data = game.find_all('td')
            new_game = { 
                'game_num': game_data[0].text.strip(),
                'Level': game_data[1].text.strip()[3:],
                'Date': '2021-'+ game_data[2].text.strip().replace('/', '-'),
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
        original_soup = self.soup
        print(pages)
        for page in pages:
            print(page['value'])
            url = self.GAMES_URL + page['value']
            get_response = self.session.get(url, headers=self.post_headers)
            self.soup = BeautifulSoup(get_response.content, "html.parser")
            all_games += self.get_current_games()
        self.soup = original_soup
        return all_games

