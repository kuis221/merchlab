import os
import tempfile
from unittest import TestCase

os.environ["APP_SETTINGS"] = "config.DevelopmentConfig"
os.environ["DATABASE_URL"] = "postgresql://postgres:toor@localhost/merch_db"
from app import app
from firebase_api import *


class RecoverPasswordFlowTestSuite(TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_firebase_tokens_flow(self):
        user = find_user_by_email("bokov.danil@gmail.com")
        token = create_password_reset_token(user['email'])
        found_user = get_user_by_password_reset_token(token)
        self.assertEqual(user, found_user)

    def test_flow(self):
        # User visits /forgot_password/ URL and sees form that invites him to enter Email to send password reset token
        response = self.app.get('/forgot_password/')
        self.assertEqual(200, response.status_code)
        self.assertIn("Please, enter your email in the box below", response.data)
        self.assertIn('<input type="text" name="email" id="email" placeholder="Email" title="Please enter you email" '
                      'required="" value="" class="form-control">', response.data)

        # He enters email address and is redirected to page that says that email has been sent
        response = self.app.post('/forgot_password/', data={'email': "somemail@gmail.com"}, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("We've sent an email with instructions to your address", response.data)
