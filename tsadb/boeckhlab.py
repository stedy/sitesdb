import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, jsonify
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing

DATABASE = 'tsadb.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'zachs'
PASSWORD = 'pwd2012'


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

#then add some decorators

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

 
@app.route('/all_samples', methods = ['GET', 'POST'])
def results():
	error = None
	entries = query_db("""select irs_ID, proj_ID, proj_tube_NO, 
                        proj_cell, date_out, shipped_to,
                        sent_to, received_date from sample_movement""", one = False ) 
	return render_template('all_samples.html', entries = entries)

@app.route('/all_patients', methods = ['GET', 'POST'])
def pt_demo():
    entries = query_db("""select irs_id, ptdon, sample_res, sample_type,
                            sourcecoll, sample_acc, coldate, pt_name, txdate,
                            donor_names, signed9 from demo""", one = False)
    return render_template('all_patients.html', entries = entries)


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
