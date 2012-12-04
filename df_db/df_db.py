import sqlite3
import subprocess as sp
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash

from contextlib import closing

#DATABASE = '/tmp/zflask.db'
DATABASE = 'version1.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'test'
PASSWORD = 'pw-2012'

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

@app.route('/isolate_query') 
def isolate_query():
			return render_template('isolate_query.html') 

@app.route('/bv_query') 
def bv_query():
			return render_template('bv_query.html') 

@app.route('/image_results')
def image_results():
			return render_template('image_results.html')

@app.route('/gramstain_results')
def gramstain_results():
			return render_template('gramstain_results.html')

@app.route('/colonymorph_results')
def colonymorph_results():
			return render_template('colonymorph_results.html')

@app.route('/results', methods = ['GET', 'POST'])
def results():
	error = None
	if request.form['visit']:
         entries = query_db("""SELECT visit, stddx, visitdt, ectopy, cvamt, dxnotes, cvexam, cvnotes from exam
						    where id = ? and visit = ?""",
						    [request.form['id'], request.form['visit']], one = False )
	else:
		entries = query_db('SELECT visit, visitdt, stddx, ectopy, cvamt, dxnotes, cvexam, cvnotes from exam where id = ?',
							[request.form['id']], one = False )
        return render_template('get_results.html', id = request.form['id'], entries = entries)
#	else:
#		return render_template('/results', error = error)

@app.route('/isolate_results', methods = ['GET', 'POST'])
def isolate_results():
	error = None
	if request.form['Isolate']:
		entries = query_db("""SELECT DISTINCT Subject_ID, Visit, Site, Amsels, Isolate, Colony_Morphology,
							Medium_Isolated, PCR_primers,
							isolate.Accession_number, Gram_stain, Extraction_date,
							Extraction_notes, PCR, PCR_Notes, PCR_Clean_up_date,
							PCR_Clean_up_Kit, Sequence_length_bp,
							GenBank_BLAST_bm, BLAST_bm, BLAST_date, 
							Sequencing_notes, Phyla, Gaps, FredricksDB_BLAST,
							Sequence, taxorder, taxfamily, taxgenus
                            FROM isolate, linker, lineage WHERE
                            isolate.Accession_number = linker.Accession_number
                            AND lineage.tax_id = linker.tax_id and
                            isolate.Isolate = ?""",
							[request.form['Isolate']], one = False)
        if len(entries) == 0:
            error = "No isolates in database for that ID"
            return render_template('isolate_query.html', entries = entries, error = error) 
        else:
            #add function for getting results
		    isolate = str(request.form['Isolate'])
		    call = sp.call(["./isolatesql.sh", isolate])	
		    return render_template('isolate_results.html', entries = entries)
#		error = "Must enter isolate name to search"
#		return render_template('isolate_query.html', entries = entries, error = error)
		

@app.route('/<id_number>')
def id_results(id_number):
	ids = str(id_number)
	idnum = query_db("""SELECT visit, visitdt, stddx, dxnotes, 
						cvexam, cvnotes, visitdt, id from exam where id =?""", [ids])
	if idnum is None:
		abort(404)
	entries = idnum
	return render_template('indiv.html', entries = entries)

@app.route('/<isolate_number>/tracefile')
def isolate_results_tf(isolate_number):
    error = None
    iid = str(isolate_number)
    entries = query_db("""SELECT Isolate, path from tracefile where Isolate = ?""",
            [iid], one = True)
    if entries == None:
        error = "No tracefile for this isolate"
        return render_template('image_results.html', entries = entries, error =
                error)
    else:
        return render_template('image_results.html', entries = entries, error =
                error)

@app.route('/bv_results', methods = ['GET', 'POST'])
def bv_results():
	error = None
	if request.form['option']:
		entries = query_db("""SELECT ID, bv, visit, visitdt
							from exam where bv = ?""",
							[request.form['option']], one = False)
		return render_template('bv_results.html', entries = entries) 
	else:
		error = "Must enter valid BV status to query"
		return render_template('bv_query.html', error = error)

@app.route('/order/<taxorder>', methods = ['GET', 'POST'])
def order_query(taxorder):
    #taxorder = str(taxorder)
    entries = query_db("""SELECT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and lineage.taxorder = ?""",
                        [taxorder], one = False)
    return render_template('tax_results.html', entries = entries)

@app.route('/family/<taxfamily>', methods = ['GET', 'POST'])
def family_query(taxfamily):
    entries = query_db("""SELECT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and
                        lineage.taxfamily = ?""",
                        [taxfamily], one = False)
    return render_template('tax_results.html', entries = entries)

@app.route('/genus/<taxgenus>', methods = ['GET', 'POST'])
def genus_query(taxgenus):
    entries = query_db("""SELECT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and lineage.taxgenus = ?""",
                        [taxgenus], one = False)
    return render_template('tax_results.html', entries = entries)

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
