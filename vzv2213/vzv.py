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
    injection1_raw = request.form['injection1']
    injection1 = dt.datetime.strptime(injection1_raw, "%m/%d/%y")
    days = [30, 60, 90, 180, 450, 810]
    fu_days = [(injection1 + dt.timedelta(weeks=day)).strftime("%m/%d/%y") for day in days]
    print fu_days
    print fu_days[2]
    g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, hispanic, 
                    gender, ethnicity, pt_userid, txtype,
                    pre_screening_date, arrival_date, consent, consent_reason,
                    consent_comments, randomize, baseline, allocation, txdate,
                    injection1, injection2p,
                    injection3p, injection4p,
                    injection5p, injection6p,
                    injection7p) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
                    fu_days[0], fu_days[1], fu_days[2], fu_days[3], fu_days[4], 
                    fu_days[5]])
    g.db.commit()
    flash('New patient successfully added')
    return render_template('main.html', error = error)

@app.route('/edit', methods = ['GET', 'POST'])
def results():
    ids = str(request.form['upn'])
    entries = query_db("""SELECT upn, uw_id, initials, dob, hispanic,
                    gender, ethnicity, pt_userid, txtype,
                    pre_screening_date, arrival_date, consent, consent_reason,
                    consent_comments, randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a from demo WHERE upn = ?""",
                    [ids])
    return render_template('edit_patient.html', entries=entries)

@app.route('/query')
def query():
    return render_template('pt_lookup.html')


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
