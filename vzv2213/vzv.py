import sqlite3
import subprocess as sp
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, send_from_directory

from contextlib import closing
from werkzeug import check_password_hash, generate_password_hash
import generate_fasta as gf
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

@app.route('/')
def main():
    if request_form['UPN']:
        g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, txtype,
                    pre_screening_date, arrival_date, consent, consent_reason,
                    consent_comments, randomize, baseline, allocation, txdate,
                    injection1) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['upn'], request.form['uw_id'],
                    request.form['initials'], request.form['dob'],
                    request.form['txtype'], request.form['pre_screening_date'],
                    request.form['arrival_date'], request.form['consent'],
                    request.form['consent_reason'],
                    request.form['consent_comments'],
                    request.form['randomize'],
                    request.form['baseline'], request.form['allocation'],
                    request.form['txdate'], request.form['injection1']])
        g.db.commit()
        flash('New patient successfully added')
    else:
        error = "Must have UPN to add patient"
    return render_template('add_indiv.html', error = error)

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
