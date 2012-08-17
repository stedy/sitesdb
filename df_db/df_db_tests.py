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

	def test_add(self):
		self.login('admin', 'default')
		rv = self.app.post('/add_form', data=dict(
			id= '20000', 
			visit = 'F1', 
			stddx = '0', 
			dxnotes = '', 
			cvexam = '1', 
			visitdt = '15-Apr-11', 
			cvnotes = 'normal'), follow_redirects = True)
		assert '20000' in rv.data
		assert 'blog_titles' not in rv.data



if __name__ == '__main__':
    unittest.main()
