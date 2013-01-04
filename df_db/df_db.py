import sqlite3
import subprocess as sp
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, send_from_directory

from contextlib import closing
from werkzeug import check_password_hash, generate_password_hash
import generate_fasta as gf
import datetime as dt

#DATABASE = '/tmp/zflask.db'
DATABASE = 'version1.db'
DEBUG = True
SECRET_KEY = 'development key'
DOWNLOAD_FOLDER = 'downloads'
#USERNAME = 'test'
#PASSWORD = 'pw-2012'

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
        name = request.form['username']
        user = query_db('''SELECT * from user where username = ?''',
                [name], one = True)
        if user is None:
            error = "Invalid Username"
        elif not check_password_hash(user['password'],
            request.form['password']):
            error = "Invalid Password"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('main'))
            gf.main()
    return render_template('login.html', error = error)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You must enter username'
        elif not request.form['email'] or \
                '@' not in request.form['email']:
                    error = 'Please enter valid email'
        elif not request.form['password']:
            error = 'You must enter a password'
        else:
            db = connect_db()
            db.execute('''INSERT INTO user (username, fullname, email, password)
                        values (?,?,?,?)''', [request.form['username'],
                            request.form['fullname'], request.form['email'],
                            generate_password_hash(request.form['password'])])
            db.commit()
            flash('User added')
            return redirect(url_for('login'))
    return render_template('add_user.html', error = error)

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

@app.route('/main')
def main():
			return render_template('index.html') 

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
            error = "No isolates in database for %s" % request.form['Isolate']
            return render_template('isolate_query.html', entries = entries, error = error) 
        else:
            #add function for getting results
		    isolate = str(request.form['Isolate'])
		    call = sp.call(["./isolatesql.sh", isolate])	
		    return render_template('isolate_results.html', entries = entries)


@app.route('/exam/<id_number>')
def id_results(id_number):
	ids = str(id_number)
	entries = query_db("""SELECT visit, visitdt, stddx, dxnotes, 
						cvexam, cvnotes, visitdt, id from exam where id =?""", [ids])
	if entries is None:
		abort(404)
	#entries = idnum
	return render_template('indiv.html', entries = entries)

@app.route('/<isolate_number>')
def individual_isolate(isolate_number):
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
							[isolate_number], one = False)
	return render_template('isolate_results.html', entries = entries)

@app.route('/tracefile/<isolate_number>')
def isolate_results_tf(isolate_number):
    error = None
    iid = str(isolate_number)
    entries = query_db("""SELECT Isolate, path from tracefile where Isolate = ?""",
            [iid], one = True)
    if entries == None:
        error = "No tracefile for isolate %s" % iid
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
    entries = query_db("""SELECT DISTINCT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and lineage.taxorder
                        = ? order by Isolate ASC""",
                        [taxorder], one = False)
    return render_template('tax_results.html', entries = entries)

@app.route('/family/<taxfamily>', methods = ['GET', 'POST'])
def family_query(taxfamily):
    entries = query_db("""SELECT DISTINCT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and
                        lineage.taxfamily = ? ORDER BY Isolate ASC""",
                        [taxfamily], one = False)
    return render_template('tax_results.html', entries = entries)

@app.route('/genus/<taxgenus>', methods = ['GET', 'POST'])
def genus_query(taxgenus):
    entries = query_db("""SELECT DISTINCT Isolate, GenBank_BLAST_bm,
                        isolate.Accession_number, taxorder, taxgenus, taxfamily FROM isolate,
                        linker, lineage where isolate.Accession_number = linker.Accession_number
                        and linker.tax_id = lineage.tax_id and lineage.taxgenus
                        = ? ORDER BY Isolate ASC""",
                        [taxgenus], one = False)
    return render_template('tax_results.html', entries = entries)

#Downloads

@app.route('/download_fasta', methods = ['GET', 'POST'])
def download_fasta():
    error = None
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
    "current_seqs.fasta", as_attachment = True)

#TODO figure of if timestamp desired?
@app.route('/download_isolates', methods = ['GET', 'POST'])
def download_isolates():
    error = None
    #timestamp = dt.datetime.now().strftime('%m%d%y_%H%M')
    #isofname = 'isolate_results
    return send_from_directory(app.config['DOWNLOAD_FOLDER'],
            "isolateresults.csv", as_attachment = True)

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
