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
FROM_NAME = "Admin"
FROM_ADDRESS = "admin@merchlab.io"


def send_email(to, subject, text, html=None, attachments=None, from_name=FROM_NAME,
               from_address=FROM_ADDRESS, domain_name=DOMAIN_NAME):
    """
    Send email message

    :param to: array of recipients, i.e. ["john@mail.com", "jane@mail.com"] or single email, i.e. "john@mail.com";
    :param subject: email subject text;
    :param text: email body;
    :param html: HTML payload of the message;
    :param attachments: list of attachments;
    :param from_name: name to send mail from. If not specified, defaults to FROM_NAME ("Admin")
    :param from_address: address to send mail from. If not specified, defaults to FROM_ADDRESS ("admin@merchlab.io")
    :param domain_name: sender domain name. If not specified, defaults to DOMAIN_NAME ("domain.mailgun.com")
    :return: requests' library Request class instance

    Example attachments list:

    attachments = [
        {"filename": "test.jpg", "path": "files/test.jpg"},
        {"filename": "test.txt", "path": "files/test.txt"},
    ]
    """
    url = "{0}{1}/messages".format(API_URL, domain_name)

    # Create initial data
    data = {
        "from": "{0} <{1}>".format(from_name, from_address),
        "to": to,
        "subject": subject,
        "text": text,
    }

    # Add HTML payload
    if html:
        data["html"] = html

    # Process attachments files
    files = list()
    for attachment in attachments:
        # Open each one with context manager
        with open(attachment['path'], "rb") as attachment_file:
            # And append its binary data to the list of attachments
            files.append(
                ("attachment", (attachment['filename'], attachment_file.read()))
            )

    return requests.post(url, auth=("api", PRIVATE_API_KEY), files=files, data=data)


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


def add_members_to_mailing_list(list_name, members, domain_name=DOMAIN_NAME):
    """
    Add new members to mailing list
    :param list_name: name of the list to add members to
    :param members: list of dicts with data
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance

    Example members list:
    [
        {"address": "Alice <alice@example.com>", "vars": {"age": 26}},
        {"name": "Bob", "address": "bob@example.com", "vars": {"age": 34}}
    ]
    """

    url = "{0}lists/{1}@{2}/members.json".format(API_URL, list_name, domain_name)

    return requests.post(
        url, auth=('api', PRIVATE_API_KEY), data={
            'upsert': True,
            'members': str(members)
        })


def update_mailing_list_member(list_name, member_email, data, domain_name=DOMAIN_NAME):
    """
    Update data of the member of the mailing list

    :param list_name: list name to update member into
    :param member_email: member's email
    :param data: data to update
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance

    Data example: {'subscribed': False, 'name': 'Foo Bar'}
    """
    url = "{0}lists/{1}@{2}/members/{3}".format(API_URL, list_name, domain_name, member_email)

    return requests.put(url=url, auth=('api', PRIVATE_API_KEY), data=data)


def list_mailing_list_members(list_name, domain_name=DOMAIN_NAME):
    """
    List members of mailing list

    :param list_name: list name to get members info from
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance

    Example response:
    response.text == {
      "items": [
          {
              "vars": {
                  "age": 26
              },
              "name": "Foo Bar",
              "subscribed": false,
              "address": "bar@example.com"
          }
      ],
      "paging": {
        "first": "https://url_to_first_page",
        "last": "https://url_to_last_page",
        "next": "http://url_to_next_page",
        "previous": "http://url_to_previous_page"
      }
    }
    """

    url = "{0}lists/{1}@{2}/members/pages".format(API_URL, list_name, domain_name)
    return requests.get(url, auth=('api', PRIVATE_API_KEY))


def remove_mailing_list_member(list_name, member_email, domain_name=DOMAIN_NAME):
    """
    Remove member from mailing list

    :param list_name: list name to remove member from
    :param member_email: member's email
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance
    """
    url = "{0}lists/{1}@{2}/members/{3}".format(API_URL, list_name, domain_name, member_email)

    return requests.delete(url, auth=('api', API_URL))


def remove_mailing_list(list_name, domain_name=DOMAIN_NAME):
    """
    Remove mailing list

    :param list_name: list name to remove
    :param domain_name: your mailgun domain name
    :return: requests' library Request class instance
    """

    url = "{0}lists/{1}@{2}".format(API_URL, list_name, domain_name)
    return requests.delete(url, auth=('api', 'YOUR_API_KEY'))


def send_bulk_email(mailing_list_address, subject, text, html=None, attachments=None,
                    from_name=FROM_NAME, from_address=FROM_ADDRESS, domain_name=DOMAIN_NAME):
    """
    Send email messages to mailing list. Uses `send_email` function

    :param mailing_list_address: mailing list address you created earlier, i.e. "customers@merchlab.com";
    :param subject: email subject text;
    :param text: email body;
    :param html: HTML payload of the message;
    :param attachments: list of attachments;
    :param from_name: name of sender. If not specified, defaults to FROM_NAME ("Merchlab admin")
    :param from_address: address to send mail from. If not specified, defaults to FROM_ADDRESS ("admin@merchlab.io")
    :param domain_name: sender domain name. If not specified, defaults to DOMAIN_NAME ("domain.mailgun.com")
    :return: requests' library Request class instance

    Example attachments list:

    attachments = [
        {"filename": "test.jpg", "path": "files/test.jpg"},
        {"filename": "test.txt", "path": "files/test.txt"},
    ]
    """
    return send_email(mailing_list_address, subject, text, html, attachments, from_name, from_address, domain_name)
