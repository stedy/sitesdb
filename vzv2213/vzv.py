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
    txdate_raw = request.form['txdate']
    txdate = dt.datetime.strptime(txdate_raw, "%m/%d/%Y")
    days = [21, 42, 63, 91, 365, 730]
    fu_days = [(txdate + dt.timedelta(weeks=day/7)).strftime("%m/%d/%Y") for day in days]
    g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, hispanic, 
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p,
                    injection3p, injection4p,
                    injection5p, injection6p,
                    injection7p) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['upn'], request.form['uw_id'],
                    request.form['initials'], request.form['dob'],
                    request.form['hispanic'], request.form['gender'],
                    request.form['ethnicity'],
                    request.form['pt_userid'],
                    request.form['txtype'], request.form['consent'],
                    request.form['consent_reason'],
                    request.form['randomize'],
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
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt,
                    check1date, check2no, check2amt, check2date,
                    check3no, check3amt, check3date, check4no, check4amt,
                    check4date from demo WHERE upn = ?""",
                    [ids])
    return render_template('edit_patient.html', entries=entries)

@app.route('/checkedit', methods = ['GET', 'POST'])
def check_results():
    checknum = str(request.form['check_no'])
    print checknum
    entries = query_db("""SELECT upn, uw_id, initials, dob, hispanic,
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt,
                    check1date, check2no, check2amt, check2date,
                    check3no, check3amt, check3date, check4no, check4amt,
                    check4date from demo WHERE check1no = ? OR
                    check2no = ? OR check3no = ? or check4no= ?""",
                    [checknum, checknum, checknum, checknum])
    return render_template('edit_patient.html', entries=entries)

@app.route('/query')
def query():
    return render_template('pt_lookup.html')


@app.route('/check_query')
def check_query():
    return render_template('check_lookup.html')

@app.route('/add_patient')
def add_patient():
    return render_template('add_patient.html')

@app.route('/update_form', methods= ['GET', 'POST'])
def update_form():
    upn = request.form['upn']
    g.db.execute("""DELETE FROM demo WHERE upn = ?""", [upn])
    g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, hispanic, 
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt, check1date,
                    check2no, check2amt, check2date, check3no, check3amt,
                    check3date, check4no, check4amt, check4date) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['upn'], request.form['uw_id'],
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
                    request.form['check1date'],
                    request.form['check2no'], request.form['check2amt'],
                    request.form['check2date'],
                    request.form['check3no'], request.form['check3amt'],
                    request.form['check3date'],
                    request.form['check4no'], request.form['check4amt'],
                    request.form['check4date']
                    ])
    g.db.commit()
    flash('Entry for UPN %s edited' % upn)
    return render_template('main.html')


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
