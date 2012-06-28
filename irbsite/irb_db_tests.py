import os
import irb_db
import unittest
import tempfile

class IRBDBTestCase(unittest.TestCase):
	def setUp(self):
		self.db_fd, irb_db.app.config['DATABASE'] = tempfile.mkstemp()
		irb_db.app.config['TESTING'] = True
		self.app = irb_db.app.test_client()
		irb_db.init_db()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(irb_db.app.config['DATABASE'])

	def login(self, username, password):
		return self.app.post('/', data = dict(
			username = username,
			password = password), follow_redirects = True)

	def logout(self):
		return self.app.get('/logout', follow_redirects = True)

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
