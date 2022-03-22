import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGridMailer:
    from_email = "refereescraper@uttercm.com"

    def __init__(self):
        f = open("application_info.json", "r")
        login_info = json.load(f)

        self.to_email = login_info["sendgrid"]["to_email"]
        self.sg = SendGridAPIClient(login_info["sendgrid"]["api_key"])

    def send_new_calendar_event(self, summary, date_time):
        message = Mail(
            self.from_email,
            self.to_email,
            subject="New Referee Calendar Event",
            html_content="<strong>New Event Added</strong><br/>{} on {}".format(
                summary, date_time
            ),
        )
        try:
            self.sg.send(message)
        except Exception as e:
            print(e.message)
