import sqlite3
import subprocess as sp
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, send_from_directory

from contextlib import closing
from werkzeug import check_password_hash, generate_password_hash
import datetime as dt

DATABASE = 'vzv.db'
DEBUG = True
SECRET_KEY = 'development key'
DOWNLOAD_FOLDER = 'downloads'

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

#then add some decorators

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('select * from user where user_id = XXX',
                        [session['user_id']], one = True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/', methods = ['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/add_form', methods = ['GET', 'POST'])
def add_form():
    error = None

    g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, hispanic, 
                    gender, ethnicity, pt_userid, txtype,
                    pre_screening_date, arrival_date, consent, consent_reason,
                    consent_comments, randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['upn'], request.form['uw_id'],
                    request.form['initials'], request.form['dob'],
                    request.form['hispanic'], request.form['gender'],
                    request.form['ethnicity'],
                    request.form['pt_userid'],
                    request.form['txtype'], request.form['pre_screening_date'],
                    request.form['arrival_date'], request.form['consent'],
                    request.form['consent_reason'],
                    request.form['consent_comments'], request.form['randomize'],
                    request.form['baseline'], request.form['allocation'],
                    request.form['txdate'], request.form['injection1'],
                    request.form['injection2p'], request.form['injection2a'],
                    request.form['injection3p'], request.form['injection3a'],
                    request.form['injection4p'], request.form['injection4a'],
                    request.form['injection5p'], request.form['injection5a'],
                    request.form['injection6p'], request.form['injection6a'],
                    request.form['injection7p'], request.form['injection7a']])
    g.db.commit()
    flash('New patient successfully added')
    return render_template('temp.html', error = error)

@app.route('/<id_number>')
def id_results(id_number):
    ids = str(upn)
    #TODO start here


@app.route('/add_patient')
def add_patient():
    return render_template('add_patient.html')


@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
