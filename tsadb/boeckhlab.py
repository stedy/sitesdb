import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, jsonify
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing

DATABASE = 'tsadb.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'test'


app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('IRB_DB_SETTINGS', silent = True)

def connect_db():
    """Returns a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_user_id(username):
    rv = g.db.execute('select user_id from user where username = ?',
                        [username]).fetchone()
    return rv[0] if rv else None

def query_db(query, args=(), one = False):
	"""Queries the database and returns a list of dictionaries"""
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value)
		for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv

#then add om decorators

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = ?',
                            [session['user_id']], one = True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('query'))
    return render_template('login.html', error = error)

 
@app.route('/results', methods = ['GET', 'POST'])
def results():
	error = None
	if request.form['urid']:
		entries = query_db("""select urid, ptdon, resclin, sample_type,
                        sourcecoll, accession_number, coll_date 
						from main where urid = ?""",
						[request.form['urid']], one = False ) 
		return render_template('get_results.html', id = request.form['urid'], entries
							= entries)
	else:
		error = "Must have either ID number to search"
		return render_template('subj_query.html', error=error)

@app.route('/query')
def query():
    return render_template('subj_query.html')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))	


if __name__ == '__main__':
    app.run()
