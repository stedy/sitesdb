import sqlite3
import subprocess as sp
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, send_from_directory

from contextlib import closing
from werkzeug import check_password_hash, generate_password_hash
import datetime as dt

DATABASE = 'mb.db'
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

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + dt.timedelta(days_ahead)

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
    if request.form['txdate'] and request.form['subject_ID']:
        swabs = [7 * x for x in range(14)]
        txdate_raw = request.form['txdate']
        txdate = dt.datetime.strptime(txdate_raw, "%m/%d/%Y")
        expected_week1 = next_weekday(txdate,0).strftime("%m/%d/%Y")
        fu_days = [(next_weekday(txdate,0) + dt.timedelta(days=day)).strftime("%m/%d/%Y") for
                day in swabs]
        g.db.execute("""INSERT INTO demo (subject_ID, uwid, pt_init, Name,
                    Status, txdate, Donrep) values
                    (?,?,?,?,?,?,?)""",
                    [request.form['subject_ID'], request.form['uwid'],
                    request.form['pt_init'], request.form['Name'],
                    request.form['Status'], request.form['txdate'],
                    request.form['Donrep']])
#                    fu_days[0], fu_days[1], fu_days[2], fu_days[3], fu_days[4], 
#                    fu_days[5], calldate])
        g.db.commit()
        flash('New patient successfully added')
    else:
        error = "Must have txdate and allocation to enter new patient"
    return render_template('main.html', error = error)

@app.route('/edit', methods = ['GET', 'POST'])
def results():
    ids = str(request.form['allocation'])
    entries = query_db("""SELECT upn, uw_id, initials, dob, hispanic,
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt,
                    check1date, check1comment, check2no, check2amt, check2date,
                    check2comment,
                    check3no, check3amt, check3date, check3comment, check4no,
                    check4amt, check4comment,
                    check4date from demo WHERE allocation = ?""",
                    [ids])
    return render_template('edit_patient.html', entries=entries)

@app.route('/query')
def query():
    return render_template('pt_lookup.html')


@app.route('/check_query')
def check_query():
    return render_template('check_lookup.html')

@app.route('/add_subject')
def add_subject():
    return render_template('add_subject.html')

@app.route('/update_form', methods= ['GET', 'POST'])
def update_form():
    allocation = request.form['allocation']
    g.db.execute("""DELETE FROM demo WHERE allocation = ?""", [allocation])
    g.db.execute("""INSERT INTO demo (allocation, uw_id, initials, dob, hispanic, 
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, upn, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt, check1date,
                    check1comment, check2no, check2amt, check2date,
                    check2comment, check3no, check3amt,
                    check3date, check3comment, check4no, check4amt, check4date,
                    check4comment, offstudy) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['allocation'], request.form['uw_id'],
                    request.form['initials'], request.form['dob'],
                    request.form['hispanic'], request.form['gender'],
                    request.form['ethnicity'],
                    request.form['pt_userid'],
                    request.form['txtype'], request.form['consent'],
                    request.form['consent_reason'], request.form['randomize'],
                    request.form['baseline'], request.form['allocation'],
                    request.form['txdate'], request.form['injection1'],
                    request.form['injection2p'], request.form['injection2a'],
                    request.form['injection3p'], request.form['injection3a'],
                    request.form['injection4p'], request.form['injection4a'],
                    request.form['injection5p'], request.form['injection5a'],
                    request.form['injection6p'], request.form['injection6a'],
                    request.form['injection7p'], request.form['injection7a'],
                    request.form['check1no'], request.form['check1amt'],
                    request.form['check1date'], request.form['check1comment'],
                    request.form['check2no'], request.form['check2amt'],
                    request.form['check2date'], request.form['check2comment'],
                    request.form['check3no'], request.form['check3amt'],
                    request.form['check3date'], request.form['check3comment'],
                    request.form['check4no'], request.form['check4amt'],
                    request.form['check4date'], request.form['check4comment'],
                    request.form['offstudy']
                    ])
    g.db.commit()
    flash('Entry for allocation %s edited' % allocation)
    return render_template('main.html')

@app.route('/all_patients')
def all_patients():
    entries = query_db("""SELECT allocation, dob, pt_userid, uw_id, initials, txdate, injection1 FROM
    demo""")
    return render_template('all_patients.html', entries = entries)


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
