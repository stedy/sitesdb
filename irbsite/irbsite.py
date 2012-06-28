import sqlite3
import time
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash

from contextlib import closing

DATABASE = 'irb_db.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

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
    if request.form['Protocol']:
		g.db.execute('insert into base (Protocol, TITLE, PI) values (?, ?, ?)',
			    [request.form['Protocol'], request.form['TITLE'],
				request.form['PI']])
		g.db.commit()
		flash('New entry was successfully posted')
    else:
		error = 'Must have Protocol number to add entry'
    return render_template('add_study.html', error = error)

@app.route('/<id_number>')
def id_results(id_number):
	ids = str(id_number)
	"""Display all results and info for a given IR number """	
	idnum = query_db('select Protocol from docs where Protocol = ?', [ids], one =
		True)
	if idnum is None:
		abort(404)
	entries = query_db('select base.Protocol, base.IR_file, base.Title,\
			docs.aprvd_date, docs.doc_name,\
			docs.doc_date from base, docs where docs.Protocol = base.Protocol \
			and base.Protocol = ?', [ids])
	return render_template('study.html', entries = entries)	

@app.route('/<id_number>/ae')
def id_results_ae(id_number):
	ids = str(id_number)
	idnum = query_db("""select FH_Protocol_1 from thirdparty_pending where
						FH_Protocol_1 = ?""", [ids], one = True)
	if idnum is None:
		abort(404)
	entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
						thirdparty_pending.PI, thirdparty_pending.FH_Protocol_1, 
						thirdparty_pending.Report_ID, thirdparty_pending.Reported_RXN,
						thirdparty_pending.Date_report from base,
						thirdparty_pending where
						thirdparty_pending.FH_Protocol_1 = base.Protocol and base.Protocol
						= ?""", [ids])
	return render_template('ae.html', entries = entries)

@app.route('/add_study')
def add_study():
	        return render_template('add_study.html')

@app.route('/query') 
def query():
			return render_template('subj_query.html') 

@app.route('/title_query') 
def title_query():
			return render_template('title_query.html') 

@app.route('/pi_query') 
def pi_query():
			return render_template('pi_query.html')

@app.route('/funding_query') 
def funding_query():
			return render_template('funding_query.html')

@app.route('/date_query') 
def date_query():
			return render_template('date_query.html')
 
@app.route('/results', methods = ['GET', 'POST'])
def results():
	error = None
	if request.form['id']:
		entries = query_db('select Title, PI, Comments, IR_file, rn_coord, IRB_expires, \
						IRB_approved, Funding_source, Type, CTE, Accrual_status from base where Protocol = ?',
						[request.form['id']], one = False ) 
	if request.form['ir']:
		entries = query_db('select Title, PI, IR_file, Comments, rn_coord, IRB_expires, \
						IRB_approved, Funding_source, Type, CTE, Accrual_status \
						from base where IR_file = ?',
						[request.form['ir']], one = False )
	return render_template('get_results.html', id = request.form['id'], entries
							= entries)


@app.route('/pi_results', methods = ['GET', 'POST'])
def pi_results():
	error = None
	if request.form['PI']:
		entries = query_db('select Title, Protocol, Comments, IR_file, rn_coord, IRB_expires, \
						IRB_approved, Funding_source, Type, CTE, Accrual_status \
 						from base where PI = ?',
						[request.form['PI']], one = False ) 
	return render_template('pi_results.html', PI = request.form['PI'], entries
							= entries)

@app.route('/title_results', methods = ['GET', 'POST'])
def title_results():
	if request.form['title']:
		titlestr = "%" + request.form['title'] + "%"
		entries = query_db('select PI, Protocol, rn_coord, IRB_expires,\
						IRB_approved, Funding_source, Type, CTE, Accrual_status,\
						Title, IR_file, Comments from base where Title\
						LIKE ?', [titlestr], one = False)
	return render_template('title_results.html', entries
							= entries)

@app.route('/date_results', methods = ['GET', 'POST'])
def date_results():
	if request.form['datemin']:
		mind = str(request.form['datemin'])
		maxd = str(request.form['datemax'])
		mind = time.strptime(mind, "%m/%d/%y")
		mindval = "%s-%s-%s" % (mind.tm_year, mind.tm_mon, mind.tm_mday)
		maxd = time.strptime(maxd, "%m/%d/%y")
		maxdval = "%s-%s-%s" % (maxd.tm_year, maxd.tm_mon, maxd.tm_mday)
		entries = query_db('select Title, Protocol, Comments, IR_file, rn_coord, IRB_expires, \
						IRB_approved, Funding_source, Type, CTE, Accrual_status \
 						from base where IRB_expires > ? AND IRB_expires < ?',
						[mindval, maxdval], one = False ) 
	return render_template('date_results.html', entries = entries)
		

@app.route('/funding_results', methods = ['GET', 'POST'])
def funding_results():
	error = None
	if request.form['funding']:
		fundingstr = "%" + request.form['funding'] + "%"
		entries = query_db('select Title, Protocol, Comments, IR_file, rn_coord, IRB_expires, \
						IRB_approved, Funding_source, Type, CTE, Accrual_status \
 						from base where Funding_source LIKE ?',
						[fundingstr], one = False ) 
	return render_template('funding_results.html', Funding = request.form['funding'], entries
							= entries)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))	


if __name__ == '__main__':
    app.run()