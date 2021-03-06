import argparse
import datetime

from app.models.google_calendar import GoogleCalendar
from app.models.sendgrid_mailer import SendGridMailer
from app.scrapers import Scraper


def parse_args():
    parser = argparse.ArgumentParser(description="Referee Scraper.")
    parser.add_argument(
        "-s", "--site", help="Defaults to ohio_south.", default="ohio_south"
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

    scraper_classes = Scraper.__subclasses__()

    for scraper_cls in scraper_classes:
        if site == scraper_cls.name:
            scraper = scraper_cls()
            break
    else:
        print(f"Did not find a scraper called {site}")

    scraper.login()
    scraper.navigate_parsing_page()
    games = scraper.get_all_games()

    for game_event in games:
        if game_event.is_my_game() and not game_event.is_cancelled:
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
