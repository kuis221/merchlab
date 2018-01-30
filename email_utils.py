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


def create_mailing_list(list_name, description, domain_name=DOMAIN_NAME):
    """
    Create mailgun mailing list

    :param list_name: new list's name
    :param description: new list's description
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance
    """
    return requests.post(
        "{0}lists".format(API_URL),
        auth=('api', PRIVATE_API_KEY),
        data={'address': '{0}@{1}'.format(list_name, domain_name),
              'description': description})


def get_mailing_lists():
    """
    Get mailgun mailing lists
    :return: requests' library Request class instance

    Example response:
    response.text == {
      "items": [
        {
          "access_level": "everyone",
          "address": "dev@samples.mailgun.org",
          "created_at": "Tue, 06 Mar 2012 05:44:45 GMT",
          "description": "Mailgun developers list",
          "members_count": 1,
          "name": ""
        },
        {
          "access_level": "readonly",
          "address": "bar@example.com",
          "created_at": "Wed, 06 Mar 2013 11:39:51 GMT",
          "description": "",
          "members_count": 2,
          "name": ""
        }
      ],
      "paging": {
        "first": "https://url_to_next_page",
        "last": "https://url_to_last_page",
        "next": "https://url_to_next_page",
        "previous": "https://url_to_previous_page"
      }
    }
    """
    return requests.get(
        "{0}lists/pages".format(API_URL),
        auth=('api', PRIVATE_API_KEY))


def send_bulk_emails():
    pass
