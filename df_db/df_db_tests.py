import os 
import df_db
import unittest
import tempfile

class df_dbTestCase(unittest.TestCase):
    def setUp(self):    
		self.db_fd, df_db.app.config['DATABASE'] = tempfile.mkstemp()
		#df_db.app.config['TESTING'] = True
		self.app = df_db.app.test_client()
		df_db.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(df_db.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data = {
            'username': username,
            'password': password
            }, follow_redirects = True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def add_user(self, username, password, password2=None, email=None):
        if password2 is None:
            password2=password
        if email is None:
            email = username + '@example.com'
        return self.app.post('/add_user', data = {
            'username': username,
            'password': password,
            'password2': password2,
            'email': email,
            }, follow_redirects= True)

    def test_register(self):
        rv = self.add_user('user1', 'default1')
        assert 'User added' in rv.data
#    def test_login_logout(self):
#        rv = self.login('zachs', 'pwd2012')
#        assert 'You were logged in' in rv.data
#        rv = self.logout()
#        assert 'You were logged out' in rv.data
#        rv = self.login('adminx', 'default')
#        assert 'Invalid username' in rv.data
#        rv = self.login('admin', 'defaultx')
#        assert 'Invalid password' in rv.data


if __name__ == '__main__':
    unittest.main()
