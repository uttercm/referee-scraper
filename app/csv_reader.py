import datetime
import io

class CsvReader:
    def get_stream(post_headers, session, send_grid_mailer):
        now = datetime.datetime.now()
        end = now + datetime.timedelta(days=30)
        # to convert dates to string use .strftime('%Y-%m-%d')
        select_statement = "SELECT * FROM schedule_mv WHERE ((ref1 = '19172' || ref2 = '19172' || ref3 = '19172')  OR (ref1 = '-' || ref2 = '-' || ref3 = '-') ) AND (game_ts between '{}' AND '{}') AND (game_status != '4') ORDER BY game_date, field_name, game_ts LIMIT 0,100".format(now.timestamp(), end.timestamp())

        GAMES_URL = 'http://www.thegameschedule.com/mv/ref2.php'

        game_data = {
            'create_spreadsheet': 'Create Spreadsheet',
            'pull_query': select_statement,
            'ref_radio': 'add_open',
            'ref_num': '19172',
            'v_start_day': now.strftime('%Y-%m-%d'),
            'v_end_day': end.strftime('%Y-%m-%d'),
            'Submit2': 'yes'
        }

        get_response = session.post(GAMES_URL, data=game_data, headers=post_headers)

        get_csv = session.get('http://www.thegameschedule.com/mv/download.php?file=excel/games_spreadsheet.csv', headers=post_headers)

        stream = io.StringIO(get_csv.content.decode('utf-8'))
        return stream