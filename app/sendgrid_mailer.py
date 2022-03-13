import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, to_email

class SendGridMailer:
    from_email = 'refereescraper@uttercm.com'
    to_email = 'mikeutter19@gmail.com'

    def __init__(self):
        self.sg = SendGridAPIClient('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')

    def send_new_calendar_event(self, summary, date_time):
        message = Mail(
            self.from_email,
            self.to_email, 
            subject='New Referee Calendar Event',
            html_content="<strong>New Event Added</strong><br/>{} on {}".format(summary, date_time))
        try:
            response = self.sg.send(message)
        except Exception as e:
            print(e.message)