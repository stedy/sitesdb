import os 
import df_db
import unittest
import tempfile

class df_dbTestCase(unittest.TestCase):
    def setUp(self):    
		self.db_fd, df_db.app.config['DATABASE'] = tempfile.mkstemp()
		df_db.app.config['TESTING'] = True
		self.app = df_db.app.test_client()
		df_db.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(df_db.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post("/", data = dict(
            username="test",
            password="pw-2012"
            ), follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Invalid username' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Invalid password' in rv.data


if __name__ == '__main__':
    unittest.main()
