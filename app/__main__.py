import argparse
import datetime

from app.google_calendar import GoogleCalendar
from app.scrapers.mvysa_scraper import MVYSAScraper
from app.scrapers.ohio_south_scraper import OhioSouthScraper
from app.sendgrid_mailer import SendGridMailer


def parse_args():
    parser = argparse.ArgumentParser(description="Referee Scraper.")
    parser.add_argument(
        "-s", "--site", help="Defaults to ohiosouth.", default="ohiosouth"
    )
    return parser.parse_args()


def create_event(summary, location, date_time, description):
    event_end = date_time + datetime.timedelta(minutes=90)
    return {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {"dateTime": date_time.isoformat()},
        "end": {"dateTime": event_end.isoformat()},
        "reminders": {
            "useDefault": True,
        },
    }


HEADERS = {
    "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}


def main():
    args = parse_args()
    site = args.site

    sendgrid_mailer = SendGridMailer()
    google_calendar = GoogleCalendar()

    if site == "ohiosouth":
        scraper = OhioSouthScraper()
    elif site == "mvysa":
        scraper = MVYSAScraper()

    scraper.login()
    scraper.navigate_parsing_page()
    games = scraper.get_all_games()

    # for line in reader:
    for game_event in games:
        if game_event.is_my_game and not game_event.is_cancelled:
            google_event = create_event(
                game_event.summary,
                game_event.location,
                game_event.date_time,
                game_event.description,
            )
            print(google_event)
            if not google_calendar.already_exists(google_event):
                print("creating event")
                google_calendar.create_event(google_event)
                sendgrid_mailer.send_new_calendar_event(
                    game_event.summary, game_event.date_time
                )


if __name__ == "__main__":
    main()
