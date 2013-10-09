import sqlite3
import time
import datetime as dt
from flask import Flask, request, session, g, redirect, url_for \
        , abort, render_template, flash, jsonify
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing


DATABASE = 'irb_db.db'
DEBUG = True
SECRET_KEY = 'development key'

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

#then decorators

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
        user = query_db( '''select * from user where username = ?''',
                [request.form['username']], one = True)
        if user is None:
            error = "Invalid Username"
        elif not check_password_hash(user['pw_hash'],
                request.form['password']):
            error = "Invalid Password"
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            return redirect(url_for('query'))
    return render_template('login.html', error = error)


@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    error = None
#    if request.form['Protocol']:
#        g.db.execute("""INSERT INTO base (Protocol, Title, PI, IR_file, UW,
#        CTE, Funding_source, RN_coord, IRB_approved, Primary_IRB, FHCRC_coop,
#        FHCRC_renewal, UW_renewal, IRB_expires, Accrual_status, IND, Pt_total,
#        Type) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
#                [request.form['Protocol'], request.form['Title'],
#                request.form['PI'], request.form['IR_file'],
#                request.form['UW'], request.form['CTE'],
#                request.form['Funding_source'], request.form['RN_coord'],
#                request.form['IRB_approved'], request.form['Primary_IRB'],
#                request.form['FHCRC_coop'], request.form['FHCRC_renewal'],
#                request.form['UW_renewal'], request.form['IRB_expires'],
#                request.form['Accrual_status'], request.form['IND'],
#                request.form['Pt_total'], request.form['Type']])
#        g.db.execute("""INSERT INTO createdby (Protocol, user_id, pub_date)
#                values (?,?,?)""", [request.form['Protocol'],
#                    g.user['username'], int(time.time())])
#        g.db.commit()
#        flash('New study was successfully added by %s' % g.user['username'])
#    else:
#        error = 'Must have Protocol number to add entry'
    print request.form['heme']
    return render_template('subj_query.html', error = error)

@app.route('/add_funding', methods=['GET', 'POST'])
def add_funding():
    print [request.form['Protocol'], request.form['Funding_Title'],
                request.form['Award_type'], request.form['PI'],
                request.form['Institution'],
                request.form['Source'], request.form['start'],
                request.form['end'], request.form['NCE'], request.form['FVAF'],
                request.form['notes']]
    if request.form['PI']:
        g.db.execute("""INSERT INTO funding (Protocol, Funding_Title,
        Award_type, PI, 
        Institution, 
        Source, start, 
        end, NCE, FVAF, 
        notes) values (?,?,?,?,?,?,?,?,?,?,?)""",
                [request.form['Protocol'], request.form['Funding_Title'],
                request.form['Award_type'], request.form['PI'],
                request.form['Institution'],
                request.form['Source'], request.form['start'],
                request.form['end'], request.form['NCE'], request.form['FVAF'],
                request.form['notes']])
        g.db.commit()
        flash('New funding was successfully added')
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        funding.PI, funding.Funding_Title, 
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes from base,
                        funding where
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [request.form['Protocol']])
    return render_template('study_funding.html', entries = entries)

@app.route('/add_mod', methods=['GET', 'POST'])
def add_mod():
    error = None
    g.db.execute("""insert into mods (Protocol, exp_review_date, date_back, date_received, 
                    date_due, Date_to_IRB, Description, submitted, aprvd_date,
                    Comments) values (?,?,?,?,?,?,?,?,?,?)""",                
                    [request.form['Protocol'], request.form['exp_review_date'],
                        request.form['date_back'], request.form['date_received'],
                        request.form['date_due'], request.form['Date_to_IRB'], 
                        request.form['Description'], request.form['submitted'], 
                        request.form['aprvd_date'], request.form['Comments']])
    g.db.commit()
    flash('New modification for %s was successfully added' % request.form['Protocol'])
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received, mods.aprvd_date from base,
                        mods where
                        mods.Protocol = base.Protocol and base.Protocol
                        = ? order by mods.Date_to_IRB ASC""",
                        [request.form['Protocol']])
    return render_template('mods.html', entries = entries)

@app.route('/add_ae', methods=['GET', 'POST'])
def add_ae():
    g.db.execute("""INSERT INTO ae (Protocol, Report_ID, Reported_RXN,
                Date_report) values (?,?,?,?)""",
                [request.form['Protocol'], request.form['Report_ID'],
                    request.form['Reported_RXN'], request.form['Date_report']])
    g.db.commit()
    flash('New AE for %s was successfully added' % request.form['Protocol'])
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report from base,
                        ae where
                        ae.Protocol = base.Protocol and base.Protocol
                        = ? order by ae.Date_report ASC""",
                        [request.form['Protocol']])
    return render_template('ae.html', entries = entries)

#search based on ID number

@app.route('/<id_number>')
def id_results(id_number):
    ids = str(id_number)
    """Display all results and info for a given IR number """    
    idnum = query_db('select Protocol from docs where Protocol = ?', [ids], one =
        True)
    entries = query_db("""select base.Protocol, base.IR_file, base.Title,
                        docs.aprvd_date, docs.doc_name, docs.Version, docs.Type, base.PI,
                        docs.doc_date, docs.id from base, docs where docs.Protocol = base.Protocol
                        and base.Protocol = ? order by docs.doc_date ASC""",
                        [ids])
    if entries:
        return render_template('study.html', entries = entries)    
    else:
        entries = query_db("""select base.Protocol, base.IR_file, base.Title
            from base where base.Protocol = ?""", [ids])
        return render_template('study_none.html', entries = entries)    
    


#Add new docs
@app.route('/add_docs', methods = ['GET', 'POST'])
def add_docs():
    error = None
    #if request.form['doc_name']:
    g.db.execute("""INSERT INTO docs (Protocol, doc_name, Version, doc_date,
            aprvd_date, Type) values (?,?,?,?,?,?)""",
            [request.form['Protocol'], request.form['doc_name'],
                request.form['Version'], request.form['doc_date'],
                request.form['aprvd_date'], request.form['Type']])
    g.db.commit()
    flash('New doc was successfully added')
    return render_template('subj_query.html')

@app.route('/<id_number>/ae')
def id_results_ae(id_number):
    ids = str(id_number)
    idnum = query_db("""select Protocol from ae where
                        Protocol = ?""", [ids], one = True)
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report from base,
                        ae where
                        ae.Protocol = base.Protocol and base.Protocol
                        = ? order by ae.Date_report ASC""", [ids])
    if entries:
        return render_template('ae.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title from base
                            where Protocol = ?""", [ids])
        return render_template('ae_none.html', entries = entries)

@app.route('/<ae_id>/ae_edit', methods = ['GET', 'POST'])
def ae_edit(ae_id):
    entries = query_db("""select PI, Protocol, id, Report_ID, Reported_RXN,
                            Date_report from ae where id = ?""", [ae_id])
    return render_template('ae_edit.html', entries = entries)

@app.route('/<ae_id>/submit_ae_edits', methods = ['GET', 'POST'])
def submit_ae_edits(ae_id):
    #if request.method == "POST":
    g.db.execute("""DELETE from ae where id = ?""", [ae_id])
    g.db.execute("""INSERT INTO ae (Protocol, Report_ID, Reported_RXN,
                        Date_report) values (?,?,?,?)""",
                            [request.form['Protocol'],
                            request.form['Report_ID'],
                            request.form['Reported_RXN'],
                            request.form['Date_report']])
    g.db.commit()
    flash('AE for %s successfully edited' % request.form['Protocol'])
    return render_template('subj_query.html')

#edit functionality for funding

@app.route('/<funding_id>/funding_edit', methods = ['GET', 'POST'])
def funding_edit(funding_id):
    entries = query_db("""select Protocol, PI, id, Source, Source_ID, start,
                            end, notes from funding where id = ?""", [funding_id])
    return render_template('funding_edit.html', entries = entries)

@app.route('/<funding_id>/submit_funding_edits', methods = ['GET', 'POST'])
def submit_funding_edits(funding_id):
    study_id = request.form['Protocol']
    g.db.execute("""DELETE from funding where id = ?""", [funding_id])
    g.db.execute("""INSERT INTO funding (Protocol, Funding_Title, Award_type,
                        PI, Institution, Source, start, end,
                        NCE, FVAF, notes) values (?,?,?,?,?,?,?,?,?,?,?)""",
                            [request.form['Protocol'], request.form['Funding_Title'],
                            request.form['Award_type'],
                            request.form['PI'], request.form['Institution'],
                            request.form['Source'], request.form['start'],
                            request.form['end'], request.form['NCE'],
                            request.form['FVAF'],
                            request.form['notes']])
    g.db.commit()
    flash('funding for %s successfully edited' % request.form['Protocol'])
#    return render_template('subj_query.html')
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        funding.PI, funding.Funding_Title, 
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes from base,
                        funding where
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [study_id])
    return render_template('study_funding.html', entries = entries)

@app.route('/<id_number>/mods')
def id_results_mods(id_number):
    ids = str(id_number)
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received, mods.aprvd_date from base,
                        mods where
                        mods.Protocol = base.Protocol and base.Protocol
                        = ? order by mods.Date_to_IRB ASC""", [ids])
    if entries:
        return render_template('mods.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title from base
                            where Protocol = ?""", [ids])
        return render_template('mods_none.html', entries = entries)


#edit functionality for mods

@app.route('/<mods_id>/mods_edit', methods = ['GET', 'POST'])
def mods_edit(mods_id):
    entries = query_db("""select Protocol, date_received, date_due,
                        exp_review_date, id, date_back, aprvd_date, Description, submitted,
                        Date_to_IRB, Comments
                         from mods where id = ?""", [mods_id])
    return render_template('mods_edit.html', entries = entries)

@app.route('/<mods_id>/submit_mods_edits', methods = ['GET', 'POST'])
def submit_mods_edits(mods_id):
    g.db.execute("""DELETE from mods where id = ?""", [mods_id])
    g.db.execute("""INSERT INTO mods (Protocol, date_received, 
                                      date_due, Date_to_IRB, exp_review_date,
                                      date_back, aprvd_date, Description,
                                      submitted, Comments) values 
                                      (?,?,?,?,?,?,?,?,?,?)""",
                            [request.form['Protocol'],
                            request.form['date_received'],
                            request.form['date_due'],
                            request.form['Date_to_IRB'],
                            request.form['exp_review_date'],
                            request.form['date_back'], request.form['aprvd_date'],
                            request.form['Description'],
                            request.form['submitted'],
                            request.form['Comments']])
    g.db.commit()
    flash('Mod for %s successfully edited' % request.form['Protocol'])
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received, mods.aprvd_date from base,
                        mods where
                        mods.Protocol = base.Protocol and base.Protocol
                        = ? order by mods.Date_to_IRB ASC""",
                        [request.form['Protocol']])
    return render_template('mods.html', entries = entries)

#edit functionality for study documents

@app.route('/<docs_id>/edit_docs', methods = ['GET', 'POST'])
def docs_edit(docs_id):
    entries = query_db("""select Protocol, doc_name, substudy,
                        Version, doc_date, aprvd_date, id
                         from docs where id = ?""", [docs_id])
    return render_template('docs_edit.html', entries = entries)

@app.route('/<docs_id>/submit_docs_edits', methods = ['GET', 'POST'])
def submit_docs_edits(docs_id):
    g.db.execute("""DELETE from docs where id = ?""", [docs_id])
    g.db.execute("""INSERT INTO docs (Protocol, doc_name, substudy,
                    Version, doc_date, aprvd_date, Type) 
                    values (?,?,?,?,?,?,?)""",
                            [request.form['Protocol'],
                            request.form['doc_name'],
                            request.form['substudy'],
                            request.form['Version'],
                            request.form['doc_date'],
                            request.form['aprvd_date'],
                            request.form['Type']])
    g.db.commit()
    flash('Doc for %s successfully edited' % request.form['Protocol'])
    entries = query_db("""select base.Protocol, base.IR_file, base.Title,
            docs.aprvd_date, docs.doc_name, docs.Version, docs.Type, base.PI,
            docs.doc_date, docs.id from base, docs where docs.Protocol = base.Protocol 
            and base.Protocol = ? order by docs.doc_date ASC""",
            [request.form['Protocol']])
    return render_template('study.html', entries=entries)


#add entries
@app.route('/add_study')
def add_study():
            return render_template('add_study.html')

@app.route('/<id_number>/study_funding')
def id_results_sn(id_number):
    ids = str(id_number)
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        funding.PI, funding.Funding_Title, 
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes from base,
                        funding where
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [ids])
    if entries:
        return render_template('study_funding.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_file, Title FROM base where
                        Protocol = ?""", [ids])
        return render_template('study_funding_none.html', entries = entries)

@app.route('/<id_number>/binder_template')
def binder_template(id_number):
    ids = str(id_number)
    bnum = query_db("""select Protocol from base where
                        Protocol = ? """, [ids], one = True)
    print bnum
    if bnum is None:
        abort(404)
    entries = query_db("""select base.Protocol, base.IR_file, base.Title, 
                        base.PI, base.CTE from base
                        where base.Protocol = ?""", [ids])
    return render_template('binder_template.html', entries=entries)

#Search queries and results

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

@app.route('/results', methods = ['GET', 'POST'])
def results():
    error = None
    if request.form['id']:
        entries = query_db("""select base.Title, base.PI, base.Comments, base.IR_file, base.rn_coord, base.IRB_expires, 
                        base.IRB_approved, base.Funding_source, base.Type,
                        base.CTE, base.Accrual_status, createdby.user_id
                        from base, createdby where base.Protocol =
                        createdby.Protocol and base.Protocol = ?""",
                        [request.form['id']], one = False ) 
        return render_template('get_results.html', id = request.form['id'], entries
                            = entries)
    if request.form['ir']:
        entries = query_db("""select Title, PI, IR_file, Comments, rn_coord, IRB_expires, 
                        IRB_approved, Funding_source, Type, CTE, Accrual_status 
                        from base where IR_file = ?""",
                        [request.form['ir']], one = False )
        return render_template('get_results.html', id = request.form['id'], entries
                            = entries)
    else:
        error = "Must have either ID number to search"
        return render_template('subj_query.html', error=error)

@app.route('/pi_results', methods = ['GET', 'POST'])
def pi_results():
    error = None
    if request.form['PI']:
        entries = query_db("""select Title, Protocol, UW, Comments, IR_file, rn_coord, IRB_expires, 
                        IRB_approved, Funding_source, Type, CTE, Accrual_status 
                         from base where PI = ?""",
                        [request.form['PI']], one = False ) 
        return render_template('pi_results.html', PI = request.form['PI'], entries
                            = entries)
    else:
        error = "Must have PI name to search"
        return render_template('pi_query.html', error=error)

@app.route('/title_results', methods = ['GET', 'POST'])
def title_results():
    if request.form['title']:
        titlestr = "%" + request.form['title'] + "%"
        entries = query_db("""select PI, Protocol, RN_coord, IRB_expires,
                        IRB_approved, Funding_source, Type, CTE, Accrual_status,
                        Title, IR_file, Comments from base where Title
                        LIKE ?""", [titlestr], one = False)
    return render_template('title_results.html', entries
                            = entries)

@app.route('/funding_results', methods = ['GET', 'POST'])
def funding_results():
    error = None
    if request.form['funding']:
        fundingstr = "%" + request.form['funding'] + "%"
        entries = query_db("""select Title, Protocol, Comments, IR_file, RN_coord, IRB_expires, 
                        IRB_approved, Funding_source, Type, CTE, Accrual_status 
                         from base where Funding_source LIKE ?""",
                        [fundingstr], one = False ) 
        return render_template('funding_results.html', Funding = request.form['funding'], entries
                            = entries)
    else:
        error = "Must enter funding info to search"
        return render_template('funding_query.html', error=error)


@app.route('/register', methods = ['GET', 'POST'])
def register():
    """Register the user"""
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'you have to enter a username'
        elif not request.form['email'] or \
                    '@' not in request.form['email']:
                error = 'You have to enter a valid email address'
        elif not request.form['password']:
                error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
                error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
                error = 'The username is already taken'
        else:
                g.db.execute('''insert into user (
                    username, email, pw_hash) values (?, ?, ?)''',
                    [request.form['username'], request.form['email'],
                    generate_password_hash(request.form['password'])])
                g.db.commit()
                flash('You were successfully registered and can login now')
                return redirect(url_for('login'))
    return render_template('register.html', error=error)

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
