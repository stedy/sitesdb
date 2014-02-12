import sqlite3
import datetime as dt
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash
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
    """Initializes database at start of each session"""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_user_id(username):
    rv = g.db.execute('SELECT user_id FROM user WHERE username = ?',
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
        g.user = query_db('SELECT * FROM user WHERE user_id = ?',
                            [session['user_id']], one = True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods = ['GET', 'POST'])
def login():
    """Main login feature"""
    error = None
    if request.method == 'POST':
        user = query_db( """SELECT * FROM user WHERE username = ?""",
                [request.form['username']], one = True)
        if user is None:
            error = "Invalid Username"
        elif not check_password_hash(user['pw_hash'],
                request.form['password']):
            error = "Invalid Password"
        else:
            flash('You were logged in')
            session['user_id'] = user['user_id']
            entries = query_db("""SELECT Protocol, Title FROM
                base WHERE Protocol != ''""")
            return redirect(url_for('main'))
    return render_template('login.html', error = error)

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    """For for adding new study"""
    if request.form['Protocol']:
        error = None
        radsafetyreview, fhibc, src, uwehs, cim, pim = None, None, \
            None, None, None, None
        full, coop, minimal, irbauth, exempt, iacucauth, \
            nothumansubjects = None, None, None, None, None, None, None
        hctallo, hctauto, heme, solidorgan, autoimmune, bv = None, None, \
            None, None, None, None
        consentwaiver, hipaawaiver, hipaaauth, repository, nihcert, \
            substudies, mta = None, None, None, None, None, None, None
        if request.form.getlist('full'):
            full = 'Y'
        if request.form.getlist('coop'):
            coop = 'Y'
        if request.form.getlist('minimal'):
            minimal = 'Y'
        if request.form.getlist('irbauth'):
            irbauth = 'Y'
        if request.form.getlist('exempt'):
            exempt = 'Y'
        if request.form.getlist('iacucauth'):
            iacucauth = 'Y'
        if request.form.getlist('nothumansubjects'):
            nothumansubjects = 'Y'
        g.db.execute("""INSERT INTO commreviews (Protocol, full, coop, minimal,
            irbauth, exempt, iacucauth, iacuc_number, nothumansubjects) VALUES
            (?,?,?,?,?,?,?,?,?)""",
            [request.form['Protocol'], full, coop, minimal,
                irbauth, exempt, iacucauth, request.form['iacuc_number'],
                nothumansubjects])
        g.db.commit()
        if request.form.getlist('hctallo'):
            hctallo = 'Y'
        if request.form.getlist('hctauto'):
            hctauto = 'Y'
        if request.form.getlist('heme'):
            heme = 'Y'
        if request.form.getlist('solidorgan'):
            solidorgan = 'Y'
        if request.form.getlist('autoimmune'):
            autoimmune = 'Y'
        if request.form.getlist('bv'):
            bv = 'Y'
        g.db.execute("""INSERT INTO dontype (Protocol, hctallo, hctauto, heme,
            solidorgan, autoimmune, bv) VALUES (?,?,?,?,?,?,?)""",
            [request.form['Protocol'], hctallo, hctauto, heme, solidorgan,
            autoimmune, bv])
        g.db.commit()

        if request.form.getlist('radsafetyreview'):
            radsafetyreview = "Y"
        if request.form.getlist('fhibc'):
            fhibc = "Y"
        if request.form.getlist('src'):
            src = "Y"
        if request.form.getlist('uwehs'):
            uwehs = "Y"
        if request.form.getlist('cim'):
            cim = 'Y'
        if request.form.getlist('pim'):
            pim = 'Y'
        g.db.execute("""INSERT INTO reviewtype (Protocol, radsafetyreview,
                        fhibc, src, uwehs, cim, pim, radsafetyreview_date)
                        VALUES (?,?,?,?,?,?,?,?)""",
            [request.form['Protocol'],
            radsafetyreview, fhibc, src, uwehs, cim, pim,
            request.form['radsafetyreview_date']])
        g.db.commit()

        if request.form.getlist('consentwaiver'):
            consentwaiver = 'Y'
        if request.form.getlist('hipaawaiver'):
            hipaawaiver = 'Y'
        if request.form.getlist('hipaaauth'):
            hipaaauth = 'Y'
        if request.form.getlist('repository'):
            repository = 'Y'
        if request.form.getlist('nihcert'):
            nihcert = 'Y'
        if request.form.getlist('substudies'):
            substudies = 'Y'
        if request.form.getlist('mta'):
            mta = 'Y'
        g.db.execute("""INSERT INTO supplemental (Protocol, consentwaiver,
                consentwaiver_type, hipaawaiver, hipaawaiver_type,
                hipaaauth, repository, nihcert, substudies, mta) VALUES
                (?,?,?,?,?,?,?,?,?,?)""", [request.form['Protocol'],
                consentwaiver, request.form['consentwaiver_text'],
                hipaawaiver, request.form['hipaawaiver_text'],
                hipaaauth, repository, nihcert, substudies, mta])
        g.db.execute("""INSERT INTO base (Protocol, Title, PI, IR_file,
                    CTE, Funding_source, RN_coord, IRB_approved, Primary_IRB,
                    FHCRC_renewal, UW_renewal, IRB_expires, IND, Min_age,
                    Pt_total, Type, FH_coord) VALUES
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                   [request.form['Protocol'], request.form['Title'],
                   request.form['PI'], request.form['IR_file'],
                   request.form['CTE'],
                   request.form['Funding_source'], request.form['RN_coord'],
                   request.form['IRB_approved'], request.form['Primary_IRB'],
                   request.form['FHCRC_renewal'],
                   request.form['UW_renewal'], request.form['IRB_expires'],
                   request.form['IND'], request.form['Min_age'],
                   request.form['Pt_total'], request.form['Type'],
                   request.form['FH_coord']])
        g.db.execute("""INSERT INTO createdby (Protocol, user_id, pub_date)
                    values (?,?,?)""", [request.form['Protocol'],
                    g.user['username'], dt.datetime.now().strftime("%m/%d/%Y")])
        g.db.commit()

        flash('Study %s was successfully added by %s' %
                (request.form['Protocol'], g.user['username']))
        return render_template('main.html')
    else:
        error = "You must enter a Protocol Number to proceed"
        return render_template('main.html', error = error)

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
                Award_type, PI, Institution, Source, start,
                end, NCE, FVAF, notes) values (?,?,?,?,?,?,?,?,?,?,?)""",
                [request.form['Protocol'], request.form['Funding_Title'],
                request.form['Award_type'], request.form['PI'],
                request.form['Institution'],
                request.form['Source'], request.form['start'],
                request.form['end'], request.form['NCE'], request.form['FVAF'],
                request.form['notes']])
        g.db.commit()
        flash('New funding was successfully added')
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        funding.PI, funding.Funding_Title,
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes
                        FROM base, funding WHERE
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [request.form['Protocol']])
    return render_template('study_funding.html', entries = entries)

@app.route('/add_mod', methods=['GET', 'POST'])
def add_mod():
    """Add new study modification to exisiting study"""
    g.db.execute("""INSERT into mods (Protocol, exp_review_date, date_back,
                    date_received, date_due, Date_to_IRB, Description, 
                    submitted, aprvd_date, Comments)
                    values (?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['Protocol'], request.form['exp_review_date'],
                        request.form['date_back'],
                        request.form['date_received'],
                        request.form['date_due'],
                        request.form['Date_to_IRB'],
                        request.form['Description'],
                        request.form['submitted'],
                        request.form['aprvd_date'], request.form['Comments']])
    g.db.commit()
    flash('New modification for %s was successfully added' \
            % request.form['Protocol'])
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received, mods.aprvd_date
                        FROM base, mods WHERE
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
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report FROM base,
                        ae WHERE
                        ae.Protocol = base.Protocol and base.Protocol
                        = ? order by ae.Date_report ASC""",
                        [request.form['Protocol']])
    return render_template('ae.html', entries = entries)

@app.route('/main')
def main():
    entries = query_db("""SELECT Protocol, Title FROM
        base WHERE Protocol != ''""")
    return render_template('main.html', entries=entries)

@app.route('/pre_safety', methods = ['GET', 'POST'])
def pre_safety():
    return render_template('pre_safety.html')

@app.route('/add_safety', methods = ['GET', 'POST'])
def add_safety():
    error = None
    check = query_db("""SELECT Protocol from safety WHERE Protocol = ?""",
            [request.form['Protocol']])
    if check:
        entries = query_db("""SELECT Title, safety.Protocol, min(submit_date),
            investigator, IR_file FROM base,
            safety WHERE
            base.Protocol = safety.Protocol AND safety.Protocol = ?""",
            [request.form['Protocol']])
        return render_template('add_safety.html', entries=entries)
    else:
        entries = query_db("""SELECT Title, Protocol FROM base WHERE Protocol
        =?""", [request.form['Protocol']])
        if entries:
            return render_template('new_safety.html', entries = entries)
        else:
            error = "Study %s does not currently exist" % \
            request.form['Protocol']
            return render_template('main.html' , error = error)

#search based on ID number

@app.route('/<id_number>')
def id_results(id_number):
    """Display all results and info for a given IR number """
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        docs.aprvd_date, docs.doc_name, docs.Version,
                        docs.Type, base.PI,
                        docs.doc_date, docs.id FROM base, docs WHERE
                        docs.Protocol = base.Protocol
                        and base.Protocol = ? order by docs.doc_date ASC""",
                        [id_number])
    personnel = query_db("""SELECT name, role, added_date FROM personnel WHERE
                        Protocol = ?""", [id_number])
    if entries:
        return render_template('study.html', entries = entries,
                personnel=personnel)
    else:
        entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title
            FROM base WHERE base.Protocol = ?""", [id_number])
        return render_template('study_none.html', entries = entries)

@app.route('/add_docs', methods = ['GET', 'POST'])
def add_docs():
    """Add new documents"""
    g.db.execute("""INSERT INTO docs (Protocol, doc_name, Version, doc_date,
            aprvd_date, Type) values (?,?,?,?,?,?)""",
            [request.form['Protocol'], request.form['doc_name'],
                request.form['Version'], request.form['doc_date'],
                request.form['aprvd_date'], request.form['Type']])
    g.db.commit()
    flash('New doc was successfully added')
    return render_template('main.html')

@app.route('/add_study')
def add_study():
    """create new entries"""
    return render_template('add_study.html')

@app.route('/<id_number>/ae')
def id_results_ae(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report FROM base,
                        ae WHERE
                        ae.Protocol = base.Protocol and base.Protocol
                        = ? order by ae.Date_report ASC""", [ids])
    if entries:
        return render_template('ae.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title FROM base
                            WHERE Protocol = ?""", [ids])
        return render_template('ae_none.html', entries = entries)

@app.route('/<ae_id>/ae_edit', methods = ['GET', 'POST'])
def ae_edit(ae_id):
    entries = query_db("""SELECT PI, Protocol, id, Report_ID, Reported_RXN,
                            Date_report FROM ae WHERE id = ?""", [ae_id])
    return render_template('ae_edit.html', entries = entries)

@app.route('/<ae_id>/submit_ae_edits', methods = ['GET', 'POST'])
def submit_ae_edits(ae_id):
    #if request.method == "POST":
    g.db.execute("""DELETE FROM ae WHERE id = ?""", [ae_id])
    g.db.execute("""INSERT INTO ae (Protocol, Report_ID, Reported_RXN,
                        Date_report) values (?,?,?,?)""",
                            [request.form['Protocol'],
                            request.form['Report_ID'],
                            request.form['Reported_RXN'],
                            request.form['Date_report']])
    g.db.commit()
    flash('AE for %s successfully edited' % request.form['Protocol'])
    return render_template('main.html')


@app.route('/<funding_id>/funding_edit', methods = ['GET', 'POST'])
def funding_edit(funding_id):
    """Line item editing functionality for funding"""
    entries = query_db("""SELECT Protocol, PI, id, Source, Source_ID, start,
                            end, notes FROM funding WHERE id = ?""",
                            [funding_id])
    return render_template('funding_edit.html', entries = entries)

@app.route('/<funding_id>/submit_funding_edits', methods = ['GET', 'POST'])
def submit_funding_edits(funding_id):
    study_id = request.form['Protocol']
    g.db.execute("""DELETE FROM funding WHERE id = ?""", [funding_id])
    g.db.execute("""INSERT INTO funding (Protocol, Funding_Title, Award_type,
                        PI, Institution, Source, start, end,
                        NCE, FVAF, notes) values (?,?,?,?,?,?,?,?,?,?,?)""",
                            [request.form['Protocol'],
                            request.form['Funding_Title'],
                            request.form['Award_type'],
                            request.form['PI'], request.form['Institution'],
                            request.form['Source'], request.form['start'],
                            request.form['end'], request.form['NCE'],
                            request.form['FVAF'],
                            request.form['notes']])
    g.db.commit()
    flash('funding for %s successfully edited' % request.form['Protocol'])
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        funding.PI, funding.Funding_Title, 
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes 
                        FROM base, funding WHERE
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [study_id])
    return render_template('study_funding.html', entries = entries)

@app.route('/<id_number>/mods')
def id_results_mods(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received,
                        mods.aprvd_date FROM base, mods WHERE
                        mods.Protocol = base.Protocol and base.Protocol
                        = ? order by mods.Date_to_IRB ASC""", [ids])
    if entries:
        return render_template('mods.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title FROM base
                            WHERE Protocol = ?""", [ids])
        return render_template('mods_none.html', entries = entries)

@app.route('/<mods_id>/mods_edit', methods = ['GET', 'POST'])
def mods_edit(mods_id):
    """Line item edit functionality for mods"""
    entries = query_db("""SELECT Protocol, date_received, date_due,
                        exp_review_date, id, date_back, aprvd_date,
                        Description, submitted, Date_to_IRB, Comments
                         FROM mods WHERE id = ?""", [mods_id])
    return render_template('mods_edit.html', entries = entries)

@app.route('/<mods_id>/submit_mods_edits', methods = ['GET', 'POST'])
def submit_mods_edits(mods_id):
    g.db.execute("""DELETE FROM mods WHERE id = ?""", [mods_id])
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
                            request.form['date_back'],
                            request.form['aprvd_date'],
                            request.form['Description'],
                            request.form['submitted'],
                            request.form['Comments']])
    g.db.commit()
    flash('Mod for %s successfully edited' % request.form['Protocol'])
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received,
                        mods.aprvd_date FROM base, mods WHERE
                        mods.Protocol = base.Protocol and base.Protocol
                        = ? order by mods.Date_to_IRB ASC""",
                        [request.form['Protocol']])
    return render_template('mods.html', entries = entries)

@app.route('/<docs_id>/edit_docs', methods = ['GET', 'POST'])
def docs_edit(docs_id):
    """Edit functionality for study docs"""
    entries = query_db("""SELECT Protocol, doc_name, substudy,
                        Version, doc_date, aprvd_date, id
                         FROM docs WHERE id = ?""", [docs_id])
    return render_template('docs_edit.html', entries = entries)

@app.route('/<docs_id>/submit_docs_edits', methods = ['GET', 'POST'])
def submit_docs_edits(docs_id):
    g.db.execute("""DELETE FROM docs WHERE id = ?""", [docs_id])
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
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
            docs.aprvd_date, docs.doc_name, docs.Version, docs.Type, base.PI,
            docs.doc_date, docs.id FROM base, docs
            WHERE docs.Protocol = base.Protocol
            and base.Protocol = ? order by docs.doc_date ASC""",
            [request.form['Protocol']])
    return render_template('study.html', entries=entries)

@app.route('/new_safety', methods = ['GET', 'POST'])
def new_safety():
    """Add new safety report form to db"""
    submit = str(request.form['submit_date'])
    g.db.execute("""INSERT INTO safety (Protocol, submit_date, Submission_type,
        Report_ID, Report_type, FU_report_no, reportdate,
        investigator_det_date, date_IRB_review, date_back_IRB, comments) values
        (?,?,?,?,?,?,?,?,?,?,?)""", [request.form['Protocol'],
        dt.datetime.strptime(submit, "%m/%d/%Y").strftime("%Y-%m-%d"),
        request.form['Submission_type'],
        request.form['Report_ID'], request.form['Report_type'],
        request.form['FU_report_no'], request.form['reportdate'],
        request.form['investigator_det_date'],
        request.form['date_IRB_review'], request.form['date_back_IRB'],
        request.form['comments']])
    g.db.commit()
    flash('New safety form for %s successfully entered' % \
    str(request.form['Protocol']))
    return render_template('main.html')

@app.route('/new_personnel', methods = ['GET', 'POST'])
def new_personnel():
    """Add new personnel to study"""
    g.db.execute("""INSERT INTO personnel (Protocol, added_date, name, role)
    values (?,?,?,?)""", [request.form['Protocol'], request.form['date_added'],
        request.form['name'], request.form['role']])
    g.db.commit()
    flash('%s added to Protocol %s' % (request.form['name'], \
        request.form['Protocol']))
    return render_template('main.html')

@app.route('/add_personnel')
def add_personnel():
    """Add new personnel to existing study"""
    return render_template('add_personnel.html')

@app.route('/<id_number>/study_funding')
def id_results_sn(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        funding.PI, funding.Funding_Title,
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end,
                        funding.notes FROM base,funding WHERE
                        funding.Protocol = base.Protocol and base.Protocol
                        = ?""", [ids])
    if entries:
        return render_template('study_funding.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_file, Title FROM base WHERE
                        Protocol = ?""", [ids])
        return render_template('study_funding_none.html', entries = entries)

@app.route('/<id_number>/binder_template')
def binder_template(id_number):
    ids = str(id_number)
    bnum = query_db("""SELECT Protocol FROM base WHERE
                        Protocol = ? """, [ids], one = True)
    if bnum is None:
        abort(404)
    entries = query_db("""SELECT base.Protocol, base.IR_file, base.Title,
                        base.PI, base.CTE FROM base
                        WHERE base.Protocol = ?""", [ids])
    return render_template('binder_template.html', entries=entries)


@app.route('/query')
def query():
    """Main search query based on ID numbers """
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
        entries = query_db("""SELECT base.Title, base.PI, base.Comments,
                        base.IR_file, base.rn_coord, base.IRB_expires,
                        base.IRB_approved, base.Funding_source, base.Type,
                        base.CTE, base.Accrual_status, createdby.user_id
                        FROM base, createdby WHERE base.Protocol =
                        createdby.Protocol and base.Protocol = ?""",
                        [request.form['id']], one = False )
        return render_template('get_results.html', id = request.form['id'],
                entries = entries)
    if request.form['ir']:
        entries = query_db("""SELECT Title, PI, IR_file, Comments, rn_coord,
                        IRB_expires, IRB_approved, Funding_source, Type,
                        CTE, Accrual_status FROM base WHERE IR_file = ?""",
                        [request.form['ir']], one = False )
        return render_template('get_results.html', id = request.form['id'],
                entries = entries)
    else:
        error = "Must have either ID number to search"
        return render_template('main.html', error=error)

#results views

@app.route('/safety_results', methods = ['GET', 'POST'])
def safety_results():
    entries = query_db("""SELECT Protocol, submit_date, Submission_type,
    Report_ID, Report_type, FU_report_no, reportdate, investigator,
    investigator_det_date, date_IRB_review, date_back_IRB, comments FROM
    safety;""")
    return render_template('safety_summary.html', entries=entries)

@app.route('/pi_results', methods = ['GET', 'POST'])
def pi_results():
    error = None
    if request.form['PI']:
        entries = query_db("""SELECT Title, Protocol, UW, Comments, IR_file,
                        rn_coord, IRB_expires,
                        IRB_approved, Funding_source, Type, CTE, Accrual_status
                         FROM base WHERE PI = ?""",
                        [request.form['PI']], one = False )
        return render_template('pi_results.html', PI = request.form['PI'],
                entries = entries)
    else:
        error = "Must have PI name to search"
        return render_template('pi_query.html', error=error)

@app.route('/title_results', methods = ['GET', 'POST'])
def title_results():
    if request.form['title']:
        titlestr = "%" + request.form['title'] + "%"
        entries = query_db("""SELECT PI, Protocol, RN_coord, IRB_expires,
                        IRB_approved, Funding_source, Type, CTE, Accrual_status,
                        Title, IR_file, Comments FROM base WHERE Title
                        LIKE ?""", [titlestr], one = False)
    return render_template('title_results.html',
                Title = request.form['title'],
                entries = entries)

@app.route('/funding_results', methods = ['GET', 'POST'])
def funding_results():
    error = None
    if request.form['funding']:
        fundingstr = "%" + request.form['funding'] + "%"
        entries = query_db("""SELECT Title, Protocol, Comments, IR_file,
                        RN_coord, IRB_expires,
                        IRB_approved, Funding_source, Type, CTE,
                        Accrual_status FROM base WHERE
                        Funding_source LIKE ?""",
                        [fundingstr], one = False )
        return render_template('funding_results.html',
                Funding = request.form['funding'],
                entries = entries)
    else:
        error = "Must enter funding info to search"
        return render_template('funding_query.html', error=error)


#utility functions

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
            g.db.execute('''INSERT INTO user (
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
    """Logs the user out"""
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run()
