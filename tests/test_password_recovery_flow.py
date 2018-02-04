import os
import tempfile
from unittest import TestCase

os.environ["APP_SETTINGS"] = "config.DevelopmentConfig"
os.environ["DATABASE_URL"] = "postgresql://postgres:toor@localhost/merch_db"
from app import app, hash_pass
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

    def test_success_story_flow(self):
        # User visits /forgot_password/ URL and sees form that invites
        # him to enter email address to send password reset token
        response = self.app.get('/forgot_password/')
        self.assertEqual(200, response.status_code)
        self.assertIn("Please, enter your email in the box below", response.data)
        self.assertIn('<input type="text" name="email" id="email" placeholder="Email" title="Please enter you email" '
                      'required="" value="" class="form-control">', response.data)

        # He enters email address and is redirected to page that says that email has been sent
        response = self.app.post('/forgot_password/', data={'email': "bokov.danil@gmail.com"}, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertIn("We've sent an email with instructions to your address", response.data)

        # Then he receives an email with a link and follows it
        token = get_password_reset_token_by_email("bokov.danil@gmail.com")
        response = self.app.get('/reset_password/?token={0}'.format(token))
        self.assertEqual(200, response.status_code)
        self.assertIn("Please enter new password", response.data)

        # He sets new passwords, gets success message. Everything went fine
        response = self.app.post('/reset_password/', data={'token': token,
                                                           'password': 'new_cool_password',
                                                           'password_2': 'new_cool_password'})
        self.assertEqual(200, response.status_code)
        self.assertIn("Password reset successful", response.data)
        user = find_user_by_email("bokov.danil@gmail.com")
        self.assertEqual(hash_pass('new_cool_password'), user['password'])
