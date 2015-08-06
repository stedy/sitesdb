import os
import unittest
import tempfile
import requests

from irbsite import app

class TestIRBDB(unittest.TestCase):
    def setUp(self):
        app.config['SECRET_KEY'] = 'development key'
        app.testing = True
        self.username = 'ZJS'
        self.password = 'pwd_2012'
        self.app = app.test_client()

    def test_login(self):
        r = requests.get("http://127.0.0.1:5000/main", \
                auth=(self.username, self.password))
        self.assertTrue(r.ok)

    def test_logout(self):
        return self.app.get('/logout', follow_redirects = True)

if __name__ == '__main__':
	unittest.main()
