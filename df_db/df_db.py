import sqlite3
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash

from contextlib import closing

#DATABASE = '/tmp/zflask.db'
DATABASE = 'version1.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('DF_DB_SETTINGS', silent = True)

def connect_db():
    """Returns a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

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

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid Username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid Password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('query'))
    return render_template('login.html', error = error)


@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
	error = None
#    if not session.get('logged in'):
#        abort(401)
	if request.form['id']:
		g.db.execute('insert into exam (id, visit, stddx, dxnotes, cvexam, visitdt, cvnotes)' \
				'values (?, ?, ?, ?, ?, ?, ?)',
				[request.form['id'], request.form['visit'],
				request.form['stddx'], request.form['dxnotes'],
				request.form['cvexam'], request.form['visitdt'],
				request.form['cvnotes']])
		g.db.commit()
		flash('New entry was successfully posted')
	else:
		error = "Must have valid ID to add new entry"
	return render_template('add_indiv.html', error = error)

@app.route('/add_indiv')
def add_indiv():
			return render_template('add_indiv.html')

@app.route('/query') 
def query():
			return render_template('subj_query.html') 

@app.route('/results', methods = ['GET', 'POST'])
def results():
	if request.form['visit']:
         entries = query_db('select visit, stddx, visitdt, dxnotes, cvexam, cvnotes from exam\
						    where id = ? and visit = ?',
						    [request.form['id'], request.form['visit']], one = False )
	else:
		entries = query_db('select visit, visitdt, stddx, dxnotes, cvexam, cvnotes from exam where id = ?',
							[request.form['id']], one = False )
        return render_template('get_results.html', id = request.form['id'], entries = entries)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))	


if __name__ == '__main__':
    app.run()
