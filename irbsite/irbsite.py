from sqlite3 import dbapi2 as sqlite3
import datetime as dt
from flask import Flask, request, session, g, redirect, url_for, \
        abort, render_template, flash, send_from_directory
from werkzeug import check_password_hash, generate_password_hash, \
        secure_filename
from contextlib import closing
import os
import zip_database as zd


DATABASE = 'irb_site.db'
DEBUG = True
FILE_FOLDER = 'archives'
SECRET_KEY = 'development key'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['csv', 'txt', 'CSV'])

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('IRB_DB_SETTINGS', silent = True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def connect_db():
    """Returns a new connection to the database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

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

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

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
            entries = query_db("""SELECT Protocol, Title, PI FROM
                protocols WHERE Protocol != ''""")
            return redirect(url_for('main'))
    return render_template('login.html', error = error)

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    """Form for adding new study"""
    if request.form['Protocol']:
        error = None
        hctallo, hctauto, hemeonc, solidorgan, autoimmune, bv = None, None, \
            None, None, None, None
        if request.form.getlist('hctallo'):
            hctallo = 'Y'
        if request.form.getlist('hctauto'):
            hctauto = 'Y'
        if request.form.getlist('hemeonc'):
            heme = 'Y'
        if request.form.getlist('solidorgan'):
            solidorgan = 'Y'
        if request.form.getlist('autoimmune'):
            autoimmune = 'Y'
        if request.form.getlist('bv'):
            bv = 'Y'

        cim, pim, src, ibc, ehs, iacuc, radsafety, other = None, None, None, \
            None, None, None, None, None
        if request.form.getlist('cim'):
            cim = 'Y'
        if request.form.getlist('pim'):
            pim = 'Y'
        if request.form.getlist('src'):
            src = 'Y'
        if request.form.getlist('ibc'):
            ibc = 'Y'
        if request.form.getlist('ehs'):
            ehs = 'Y'
        if request.form.getlist('iacuc'):
            iacuc = 'Y'
        if request.form.getlist('radsafety'):
            radsafety = 'Y'
        if request.form.getlist('other'):
            other = 'Y'
        childrens_supp, multi_supp, mta_dua = None, None, None
        if request.form.getlist('childrens_supp'):
            childrens_supp = 'Y'
        if request.form.getlist('multi_supp'):
            multi_supp = 'Y'
        if request.form.getlist('mta_dua'):
            mta_dua = 'Y'
        CRDGeneral, Studyspecific, UWHIPAA, CRD = None, None, None, None
        if request.form.getlist('CRDGeneral'):
            CRDGeneral = 'Y'
        if request.form.getlist('Studyspecific'):
            Studyspecific = 'Y'
        if request.form.getlist('UWHIPAA'):
            UWHIPAA = 'Y'
        if request.form.getlist('CRD'):
            CRD = 'Y'

        g.db.execute("""INSERT INTO dontype (Protocol, hctallo, hctauto, heme,
            solidorgan, autoimmune, bv) VALUES (?,?,?,?,?,?,?)""",
            [request.form['Protocol'], hctallo, hctauto, hemeonc, solidorgan,
            autoimmune, bv])

        g.db.execute("""INSERT INTO reviewcomm (Protocol, iacuc, cim, pim, src,
            FH_IBC, UW_ehs, rad_safety, other) VALUES
            (?,?,?,?,?,?,?,?,?)""",
            [request.form['Protocol'], request.form['iacuc_date'], cim, pim,
                src, ibc, ehs, radsafety, other])

        g.db.execute("""INSERT INTO supplemental (Protocol,
                consentwaiver_type, hipaawaiver_type,
                childrens_supp, multi_supp, mta_dua, CRDGeneral,
                Studyspecific, UWHIPAA, CRD, uwconf_date)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                [request.form['Protocol'],
                request.form['consentwaiver_type'],
                request.form['hipaawaiver_type'],
                childrens_supp, multi_supp, mta_dua, CRDGeneral, Studyspecific,
                UWHIPAA, CRD, request.form['uwconf_date']])

        g.db.execute("""INSERT INTO protocols (Protocol, Title,
                    IR_file, PI,
                    IRB_approved,
                    IRB_expires,
                    Min_age) VALUES
                    (?,?,?,?,?,?,?)""",
                   [request.form['Protocol'], request.form['Title'],
                   request.form['IR_file'], request.form['PI'],
                   request.form['IRB_approved'],
                   request.form['IRB_expires'],
                   request.form['Min_age']])
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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        funding.PI, funding.Funding_Title,
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes
                        FROM protocols, funding WHERE
                        funding.Protocol = protocols.Protocol and protocols.Protocol
                        = ?""", [request.form['Protocol']])
    return render_template('study_funding.html', entries = entries)

@app.route('/add_mods_front')
def add_mods_front():
    entries = query_db("""SELECT Protocol FROM protocols WHERE Protocol != "" ORDER BY Protocol ASC""")
    return render_template('add_mods_front.html', entries=entries)

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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received, mods.aprvd_date
                        FROM protocols, mods WHERE
                        mods.Protocol = protocols.Protocol and protocols.Protocol
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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report FROM protocols,
                        ae WHERE
                        ae.Protocol = protocols.Protocol and protocols.Protocol
                        = ? order by ae.Date_report ASC""",
                        [request.form['Protocol']])
    return render_template('ae.html', entries = entries)

@app.route('/main')
def main():
    entries = query_db("""SELECT Protocol, Title, PI, IR_file, CTE,
        rn_coord, IRB_coord, AE_coord, IRB_approved, IRB_expires, IRB_status,
        Accrual_status, Patient_goal, Patient_total, Min_age, Comments, Cat,
        Phase, IND, Multi_site, FH_coord, HIPAA, Waiver_of_consent,
        HIPAA_waiver, UW_agree, Childrens_agree FROM
        protocols WHERE Protocol != ''""")
    return render_template('main.html', entries=entries)

@app.route('/pre_safety', methods = ['GET', 'POST'])
def pre_safety():
    entries = query_db("""SELECT Protocol FROM protocols WHERE Protocol != "" ORDER BY Protocol ASC""")
    return render_template('pre_safety.html', entries=entries)

@app.route('/add_safety', methods = ['GET', 'POST'])
def add_safety():
    error = None
    check = query_db("""SELECT Protocol from safety WHERE Protocol = ?""",
            [request.form['Protocol']])
    if check:
        entries = query_db("""SELECT Title, safety.Protocol, min(submit_date),
            investigator, IR_file FROM protocols,
            safety WHERE
            protocols.Protocol = safety.Protocol AND safety.Protocol = ?""",
            [request.form['Protocol']])
        return render_template('add_safety.html', entries=entries)
    else:
        entries = query_db("""SELECT Title, Protocol, PI, IR_file
        FROM protocols WHERE Protocol=?""", [request.form['Protocol']])
        if entries:
            return render_template('new_safety.html', entries = entries)
        else:
            error = "Study %s does not currently exist" % \
            request.form['Protocol']
            return render_template('main.html' , error = error)

@app.route('/add_docs', methods = ['GET', 'POST'])
def add_docs():
    """Add new documents"""
    entries = query_db("""SELECT * from docs where Protocol = ?""",
            [request.form['Protocol']])
    return render_template('add_docs.html', entries=entries)

@app.route('/pre_docs', methods = ['GET', 'POST'])
def pre_docs():
    entries = query_db("""SELECT Protocol FROM protocols WHERE Protocol != "" ORDER BY Protocol ASC""")
    return render_template('pre_docs.html', entries=entries)

@app.route('/<id_number>')
def id_results(id_number):
    """Display all results and info for a given IR number """
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        protocols.CTE, protocols.RN_coord, protocols.PI
                        FROM protocols
                        WHERE protocols.Protocol = ?""",
                        [id_number])
    personnel = query_db("""SELECT name, role, added_date FROM personnel WHERE
                        Protocol = ?""", [id_number])
#    committee = query_db("""SELECT Primary_IRB, Review_Type, Committee FROM
#                        reviewcomm WHERE Protocol = ?""", [id_number])
#    funding = query_db("""SELECT Institution, Funding_Title, PI, start, end
#                        FROM funding WHERE Protocol = ?""", [id_number])
    if entries:
        return render_template('study.html', entries = entries,
                personnel = personnel)
    else:
        entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title
            FROM protocols WHERE protocols.Protocol = ?""", [id_number])
        return render_template('study_none.html', entries = entries)

@app.route('/add_study')
def add_study():
    """create new entries"""
    return render_template('add_study.html')

@app.route('/<id_number>/ae')
def id_results_ae(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        ae.PI, ae.Protocol, ae.id,
                        ae.Report_ID, ae.Reported_RXN,
                        ae.Date_report FROM protocols,
                        ae WHERE
                        ae.Protocol = protocols.Protocol and protocols.Protocol
                        = ? order by ae.Date_report ASC""", [ids])
    if entries:
        return render_template('ae.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title FROM protocols
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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        funding.PI, funding.Funding_Title,
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end, funding.notes
                        FROM protocols, funding WHERE
                        funding.Protocol = protocols.Protocol and protocols.Protocol
                        = ?""", [study_id])
    return render_template('study_funding.html', entries = entries)

@app.route('/<id_number>/mods', methods = ['GET', 'POST'])
def id_results_mods(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received,
                        mods.aprvd_date FROM protocols, mods WHERE
                        mods.Protocol = protocols.Protocol and protocols.Protocol
                        = ? order by mods.Date_to_IRB ASC""", [ids])
    if entries:
        return render_template('mods.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_File, Title FROM protocols
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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        mods.PI, mods.Protocol, mods.id, mods.date_due,
                        mods.exp_review_date, mods.date_back,
                        mods.submitted, mods.Comments, mods.Description,
                        mods.Date_to_IRB, mods.date_received,
                        mods.aprvd_date FROM protocols, mods WHERE
                        mods.Protocol = protocols.Protocol and protocols.Protocol
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
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
            docs.aprvd_date, docs.doc_name, docs.Version, docs.Type, protocols.PI,
            docs.doc_date, docs.id FROM protocols, docs
            WHERE docs.Protocol = protocols.Protocol
            and protocols.Protocol = ? order by docs.doc_date ASC""",
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

@app.route('/new_docs', methods = ['GET', 'POST'])
def new_docs():
    """Single page add new study documents"""
    g.db.execute("""INSERT INTO docs (Protocol, doc_name, substudy, Version,
                doc_date, aprvd_date, Type) values (?,?,?,?,?,?,?)""",
                [request.form['Protocol'], request.form['doc_name'],
                request.form['substudy'],
                request.form['Version'], request.form['doc_date'],
                request.form['aprvd_date'], request.form['Type']])
    g.db.commit()
    flash('New doc was successfully added to %s' % request.form['Protocol'])
    return render_template('main.html')

@app.route('/new_personnel', methods = ['GET', 'POST'])
def new_personnel():
    """Add new personnel to study"""
    g.db.execute("""INSERT INTO personnel (Protocol, added_date, name, role,
                removed_date, responsibility) VALUES (?,?,?,?,?,?)""",
                [request.form['Protocol'], request.form['date_added'],
        request.form['name'], request.form['role'],
        request.form['date_removed'], request.form['responsibility']])
    g.db.commit()
    flash('%s added to Protocol %s' % (request.form['name'], \
        request.form['Protocol']))
    return render_template('main.html')

@app.route('/add_personnel')
def add_personnel():
    """Add new personnel to existing study"""
    return render_template('add_personnel.html')

@app.route('/add_review_committee')
def add_review_committee():
    """Add review committee information"""
    entries = query_db("""SELECT statustype from status_list""")
    return render_template('add_review_committee.html', entries=entries)

@app.route('/new_review_committee', methods = ['GET', 'POST'])
def new_review_committee():
    """Add new review committee info to database"""
    g.db.execute("""INSERT INTO reviewcomm (Title, Protocol, IR, PI,
            Primary_IRB, fhcrc_renewal,
            init_approval_date, Committee, Review_Type,
            rad_safety_renewal, cim, FH_IBC, UW_ehs, uw_renewal, irb_expires,
            pim, src, rad_safety, other)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [request.form['Title'], request.form['Protocol'],
                request.form['IR'], request.form['PI'],
                request.form['Primary_IRB'], request.form['fhcrc_renewal'],
                request.form['init_approval_date'],
                request.form['Committee'], request.form['Review_Type'],
                request.form['rad_safety_renewal'], request.form['cim'],
                request.form['FH_IBC'], request.form['UW_ehs'],
                request.form['uw_renewal'], request.form['irb_expires'],
                request.form['pim'], request.form['src'],
                request.form['rad_safety'], request.form['other']
                ])
    g.db.commit()
    flash('Committee Review added for Protocol %s' % request.form['Protocol'])
    return render_template('main.html')

@app.route('/<id_number>/study_funding')
def id_results_sn(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        funding.PI, funding.Funding_Title,
                        funding.source, funding.Source_ID, funding.Award_type,
                        funding.Institution, funding.NCE, funding.FVAF,
                        funding.start, funding.id, funding.end,
                        funding.notes FROM base,funding WHERE
                        funding.Protocol = protocols.Protocol and protocols.Protocol
                        = ?""", [ids])
    if entries:
        return render_template('study_funding.html', entries = entries)
    else:
        entries = query_db("""SELECT Protocol, IR_file, Title FROM protocols WHERE
                        Protocol = ?""", [ids])
        return render_template('study_funding_none.html', entries = entries)

@app.route('/<id_number>/binder_template')
def binder_template(id_number):
    ids = str(id_number)
    bnum = query_db("""SELECT Protocol FROM protocols WHERE
                        Protocol = ? """, [ids], one = True)
    if bnum is None:
        abort(404)
    entries = query_db("""SELECT protocols.Protocol, protocols.IR_file, protocols.Title,
                        protocols.PI, protocols.CTE FROM protocols
                        WHERE protocols.Protocol = ?""", [ids])
    return render_template('binder_template.html', entries=entries)

@app.route('/add_sponsor')
def add_sponsor():
    """Add new personnel to existing study"""
    return render_template('add_sponsor.html')

@app.route('/add_sponsor_info', methods = ['GET', 'POST'])
def add_sponsor_info():
    """Add new sponsor to study"""
    g.db.execute("""INSERT INTO sponsor (Protocol, added_date, name, telephone,
                removed_date, company, cellphone, fax, email, address, notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                [request.form['Protocol'], request.form['date_added'],
        request.form['name'], request.form['telephone'],
        request.form['date_removed'], request.form['company'],
        request.form['cellphone'], request.form['fax'],
            request.form['email'], request.form['address'],
            request.form['notes']])
    g.db.commit()
    flash('%s added to Protocol %s' % (request.form['name'], \
        request.form['Protocol']))
    return render_template('main.html')

#queries


@app.route('/funding_query')
def funding_query():
    return render_template('funding_query.html')

#results views

@app.route('/safety_results', methods = ['GET', 'POST'])
def safety_results():
    entries = query_db("""SELECT Protocol, submit_date, Submission_type,
    Report_ID, Report_type, FU_report_no, reportdate, investigator,
    investigator_det_date, date_IRB_review, date_back_IRB, comments FROM
    safety;""")
    return render_template('safety_summary.html', entries=entries)


@app.route('/funding_results', methods = ['GET', 'POST'])
def funding_results():
    error = None
    if request.form['funding']:
        fundingstr = "%" + request.form['funding'] + "%"
        entries = query_db("""SELECT Title, Protocol, Comments, IR_file,
                        RN_coord, IRB_expires,
                        IRB_approved, Funding_source, Type, CTE,
                        Accrual_status FROM protocols WHERE
                        Funding_source LIKE ?""",
                        [fundingstr], one = False )
        return render_template('funding_results.html',
                Funding = request.form['funding'],
                entries = entries)
    else:
        error = "Must enter funding info to search"
        return render_template('funding_query.html', error=error)

@app.route('/db_to_excel', methods=['GET'])
def db_to_excel():
    """Pull out all db tables as they currently are read"""
    zd.main()
    now = dt.datetime.now().strftime('%Y-%m-%d')
    filename = now + "_database.zip"
    return send_from_directory(app.config['FILE_FOLDER'],
            filename, as_attachment=True)


@app.route('/batch_upload')
def batch_upload():
    entries = query_db("""SELECT Protocol FROM protocols WHERE Protocol
            != "" ORDER BY Protocol ASC""")
    names = query_db("""SELECT name from personnel WHERE name != "" ORDER by
            name ASC""")
    return render_template('batch_upload.html', entries=entries, names=names)

@app.route('/batch_new_personnel', methods = ['GET', 'POST'])
def batch_new_personnel():
    """Batch new personnel to study"""
    g.db.execute("""INSERT INTO personnel (Protocol, name, role,
                responsibility) VALUES (?,?,?,?)""",
                [request.form['Protocol1'], request.form['name1'],
                request.form['role1'], request.form['responsibility1']])
    if request.form['Protocol2'] != "":
        g.db.execute("""INSERT INTO personnel (Protocol, name, role,
                responsibility) VALUES (?,?,?,?)""",
                [request.form['Protocol2'], request.form['name2'],
                request.form['role2'], request.form['responsibility2']])
    if request.form['Protocol3'] != "":
        g.db.execute("""INSERT INTO personnel (Protocol, name, role,
                responsibility) VALUES (?,?,?,?)""",
                [request.form['Protocol3'], request.form['name3'],
                request.form['role3'], request.form['responsibility3']])
    if request.form['Protocol4'] != "":
        g.db.execute("""INSERT INTO personnel (Protocol, name, role,
                responsibility) VALUES (?,?,?,?)""",
                [request.form['Protocol4'], request.form['name4'],
                request.form['role4'], request.form['responsibility4']])
    if request.form['Protocol5'] != "":
        g.db.execute("""INSERT INTO personnel (Protocol, name, role,
                responsibility) VALUES (?,?,?,?)""",
                [request.form['Protocol5'], request.form['name5'],
                request.form['role5'], request.form['responsibility5']])

    g.db.commit()
    flash('Batch upload sucessfully completed')
    entries = query_db("""SELECT Protocol, Title, PI FROM
        protocols WHERE Protocol != ''""")
    return render_template('main.html', entries=entries)

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
