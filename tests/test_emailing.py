import json
import os
import tempfile
import unittest

from app import app


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_sending_mail_requires_3_args_and_responds_with_400(self):
        response = self.app.post('/mailing/send_email/', data={})
        self.assertEqual(400, response.status_code)
        response = self.app.post('/mailing/send_email/', data={"to": "some@email.com",
                                                               "subject": "Test"})
        self.assertEqual(400, response.status_code)
        response = self.app.post('/mailing/send_email/', data={"to": "some@email.com",
                                                               "text": "Test"})
        self.assertEqual(400, response.status_code)
        response = self.app.post('/mailing/send_email/', data={"subject": "Test",
                                                               "text": "Test"})
        self.assertEqual(400, response.status_code)

    def test_sending_mail_responds_with_200_on_OK(self):
        response = self.app.post('/mailing/send_email/', data={"to": "some@email.com",
                                                               "subject": "Test",
                                                               "text": "Test"})
        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['Status'], "Email sent")

    def test_sending_email_renders_html_template(self):
        response = self.app.post('/mailing/send_email/', data={"to": "some@email.com",
                                                               "subject": "Test",
                                                               "text": "Test",
                                                               "template_name": "faq.html"})
        self.assertEqual(200, response.status_code)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['Status'], "Email sent")
        self.assertEqual(response_data['HTML'], "Rendered faq.html")


if __name__ == '__main__':
    unittest.main()
