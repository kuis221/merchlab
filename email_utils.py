#  This file contains utils to send email notifications to particular user
#  and sending bulk emails for all users. We use mailgun for this.
#
#  To send simple message, use `send_email` function.
#
#  To send bulk email, you've got 2 options:
#    1. use `send_bulk_emails` function;
#    2. create mailgun "mailing list", add users to it (max. 1000 users per request) and
#       send emails to them using that list with `send_emails_to_list` function;
import requests

API_URL = "https://api.mailgun.net/v3/"
DOMAIN_NAME = "domain.mailgun.com"
PRIVATE_API_KEY = ""
FROM_NAME = "Merchlab admin"
FROM_USERNAME = "mailgun"


def send_email(to, subject, text, from_name=FROM_NAME, from_username=FROM_USERNAME, domain_name=DOMAIN_NAME):
    """
    Send simple email

    :param to: array of recipients, i.e. ["john@mail.com", "jane@mail.com"];
    :param subject: email subject text;
    :param text: email body;
    :param from_name: name of sender. If not specified, defaults to FROM_NAME ("Merchlab admin")
    :param from_username: username of sender. If not specified, defaults to FROM_USERNAME ("mailgun")
    :param domain_name: sender domain name. If not specified, defaults to DOMAIN_NAME ("domain.mailgun.com")
    :return: requests' library Request class instance
    """
    url = "{0}{1}/messages".format(API_URL, domain_name)
    data = {
        "from": "{0} <{1}@{2}>".format(from_name, from_username, domain_name),
        "to": to,
        "subject": subject,
        "text": text
    }

    return requests.post(url, auth=("api", PRIVATE_API_KEY), data=data)


def send_bulk_emails():
    pass
