import sqlite3
from flask import Flask, request, session, g, \
        redirect, url_for, render_template, flash

from contextlib import closing
from werkzeug import check_password_hash
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

def convertsql(date):
    """Checks id date in %m/%d/%Y then converts to SQL for db insert"""
    try:
        return dt.datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'username' in session:
        g.user = query_db("""SELECT * FROM user where username = ?""",
                        [session['username']], one = True)

@app.teardown_request
def teardown_request(exception):
    """Tears down the database after use"""
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods = ['GET', 'POST'])
def login():
    error = None
    if request.method == "POST":
        name = request.form['username']
        user = query_db("""SELECT * from user where username = ?""", [name],
                one = True)
        if user is None:
            error = "Invalid Username"
        elif not check_password_hash(user['password'],
                request.form['password']):
            error = "Invalid Password"
        else:
            flash('You were logged in')
            session['username'] = user['username']
            return redirect(url_for('main'))
    return render_template('login.html', error = error)


@app.route('/main')
def main():
    entries = query_db("""SELECT * FROM
            (SELECT calls.allocation, calls.expected_calldate_sql,
            expected_calldate as expdate,
            initials, calltype, phonenumber, email
            FROM calls
            JOIN(SELECT allocation,
                MIN(expected_calldate_sql) as expected_calldate_sql
            FROM calls WHERE expected_calldate_sql > date('NOW')
            GROUP BY allocation
            ) as earliest
            ON calls.allocation = earliest.allocation AND
            calls.expected_calldate_sql = earliest.expected_calldate_sql) as
            latest
            INNER JOIN
            (SELECT allocation, max(actual_calldate_sql) as mdate
            FROM calls WHERE actual_calldate IS NOT 'None'
            GROUP BY allocation) as recent
            ON latest.allocation = recent.allocation;""")
    return render_template('main.html', entries=entries)

@app.route('/add_form', methods = ['GET', 'POST'])
def add_form():
    error = None
    if request.form['txdate'] and request.form['allocation']:
        txdate_raw = request.form['txdate']
        txdate = dt.datetime.strptime(txdate_raw, "%m/%d/%Y")
        days = [30, 60, 90, 118, 180, 455]
        fu_days = [(txdate + dt.timedelta(days=day)).strftime("%m/%d/%Y")
                for day in days]
        calldate = (txdate + dt.timedelta(days=30+118)).strftime("%m/%d/%Y")
        calldate_time = dt.datetime.strptime(calldate, "%m/%d/%Y")
        calldays = [x * 30 for x in range(60)]
        calltype = ['monthly', 'monthly', '3 month'] * 20
        calldays_projected = [(calldate_time +
                    dt.timedelta(days=callday)).strftime("%m/%d/%Y")
                    for callday in calldays]
        calldays_projected_sql = [(calldate_time +
                    dt.timedelta(days=callday)).strftime("%Y-%m-%d")
                    for callday in calldays]
        calldays_complete = zip(calldays_projected, calldays_projected_sql,
                calltype)
        g.db.execute("""INSERT INTO demo (upn, uw_id, initials, dob, hispanic,
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p,
                    injection3p, injection4p,
                    injection5p, injection6p,
                    injection7p, phonecall, phonenumber, status) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
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
                    fu_days[5], calldate, request.form['phonenumber'], "on"])
        for cp, cps, ct in calldays_complete:
            g.db.execute("""INSERT INTO calls (allocation, initials,
            expected_calldate,
            expected_calldate_sql, calltype, phonenumber) values
                    (?,?,?,?,?,?)""", [request.form['allocation'],
                    request.form['initials'], cp, cps, ct,
                    request.form['phonenumber']])
        g.db.commit()
        entries = query_db("""SELECT calls.allocation,
            MIN(expected_calldate_sql) as mdate, calls.calltype,
            calls.expected_calldate as expdate,
            demo.initials, demo.phonenumber, demo.email FROM calls, demo
            WHERE calls.allocation = demo.allocation and
            expected_calldate_sql > date('NOW') GROUP BY
            calls.allocation""")
        flash('New patient successfully added')
    else:
        error = "Must have txdate and allocation to enter new patient"
    return render_template('main.html', error = error, entries = entries)

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
                    check4amt, check4date, check4comment, check5no,
                    check5amt, check5comment, check5date,
                    check6amt, check6date, check6comment, check6no,
                    check7amt, check7date, check7comment, check7no,
                    phonecall, phonenumber
                    from demo WHERE allocation = ?""",
                    [ids])
    phonecalls = query_db("""SELECT allocation, expected_calldate,
                    actual_calldate, call_check_no, call_check_amt
                    from calls where allocation = ?""",
                    [ids])
    return render_template('edit_patient.html', entries=entries,
            phonecalls=phonecalls)

@app.route('/checkedit', methods = ['GET', 'POST'])
def check_results():
    error = None
    checknum = str(request.form['check_no'])
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
                    check2no = ? OR check3no = ? OR check4no= ? OR
                    check5no = ?""",
                    [checknum, checknum, checknum, checknum, checknum])
    if entries:
        return render_template('check_info.html', entries=entries)
    else:
        entries = query_db("""SELECT calls.allocation,
            MIN(expected_calldate_sql) as mdate, calls.calltype,
            calls.expected_calldate as expdate,
            demo.initials, demo.phonenumber, demo.email FROM calls, demo
            WHERE calls.allocation = demo.allocation and
            expected_calldate_sql > date('NOW') GROUP BY
            calls.allocation""")
        error = 'Check %s was not found' % checknum
        return render_template('main.html', entries=entries, error = error)

@app.route('/<id_number>')
def id_edit(id_number):
    ids = str(id_number)
    entries = query_db("""SELECT upn, uw_id, initials, dob, hispanic,
                    gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, allocation, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a, check1no, check1amt,
                    check1date, check1comment, check2no, check2amt, 
                    check2date, check2comment,
                    check3no, check3amt, check3date, check3comment, check4no,
                    check4amt, check4date, check4comment, check5no,
                    check5amt, check5comment, check5date,
                    check6amt, check6date, check6comment, check6no,
                    check7amt, check7date, check7comment, check7no,
                    phonecall, phonenumber, hzdate
                    from demo WHERE allocation = ?""",
                    [ids])
    phonecalls = query_db("""SELECT expected_calldate,
                    actual_calldate, call_check_no, call_check_amt, email
                    from calls WHERE allocation = ? AND
                    calltype = 'monthly'""", [ids])
    email = query_db("""SELECT DISTINCT email from calls WHERE allocation =
                    ?""", [ids])
    phonecalls3 = query_db("""SELECT expected_calldate AS ec3,
                    actual_calldate AS ac3, call_check_no AS ccn3,
                    call_check_amt AS cca3
                    from calls WHERE allocation = ? AND calltype =
                    "3 month" """, [ids])
    return render_template('edit_patient.html', entries=entries,
            phonecalls=phonecalls, phonecalls3=phonecalls3, email=email)

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
    allocation = request.form['allocation']
    g.db.execute("""DELETE FROM demo WHERE allocation = ?""", [allocation])
    g.db.execute("""INSERT INTO demo (allocation, uw_id, initials, dob,
                    hispanic, gender, ethnicity, pt_userid, txtype,
                    consent, consent_reason,
                    randomize, baseline, upn, txdate,
                    injection1, injection2p, injection2a,
                    injection3p, injection3a, injection4p, injection4a,
                    injection5p, injection5a, injection6p, injection6a,
                    injection7p, injection7a,
                    check1no, check1amt, check1date,
                    check1comment, check2no, check2amt, check2date,
                    check2comment, check3no, check3amt,
                    check3date, check3comment, check4no, check4amt,
                    check4date, check4comment, offstudy,
                    check5no, check5amt, check5date, check5comment,
                    check6no, check6amt, check6date, check6comment,
                    check7no, check7amt, check7date, check7comment,
                    hzdate) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?)""",
                    [request.form['allocation'], request.form['uw_id'],
                    request.form['initials'], request.form['dob'],
                    request.form['hispanic'], request.form['gender'],
                    request.form['ethnicity'], request.form['pt_userid'],
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
                    request.form['offstudy'],
                    request.form['check5no'], request.form['check5amt'],
                    request.form['check5date'], request.form['check5comment'],
                    request.form['check6no'], request.form['check6amt'],
                    request.form['check6date'], request.form['check6comment'],
                    request.form['check7no'], request.form['check7amt'],
                    request.form['check7date'], request.form['check7comment'],
                    request.form['hzdate']
                    ])
    g.db.commit()
    actual_call_date, expected_call_date, chkno, chkdt = [], [], [], []
    expected_call_date_sql = []
    for x in range(1, 19):
        val = 'calldate%s' % x
        expval = 'expcall%s' % x
        checknoval = 'call_check_no%s' % x
        chkdtval = 'call_check_amt%s' % x
        val3 = 'call3date%s' % x
        expval3 = 'exp3call%s' % x
        checknoval3 = 'call3_check_no%s' % x
        chkdtval3 = 'call3_check_amt%s' % x
        actual_call_date.append(request.form[val])
        expected_call_date.append(request.form[expval])
        expected_call_date_sql.append(convertsql(request.form[expval]))
        chkno.append(request.form[checknoval])
        chkdt.append(request.form[chkdtval])
        actual_call_date.append(request.form[val3])
        expected_call_date.append(request.form[expval3])
        chkno.append(request.form[checknoval3])
        chkdt.append(request.form[chkdtval3])

    calldate_raw = query_db("""SELECT calldate from lastcall where allocation =
        ?""", [request.form['allocation']])
    calldate = calldate_raw[0]['calldate']
    calldate = dt.datetime.strptime(calldate, "%Y-%m-%d")
    for a, b, c, d in zip(actual_call_date, expected_call_date,
            chkno, chkdt):
        try:
            calldate_a = dt.datetime.strptime(str(a), "%m/%d/%Y")
            if calldate_a > calldate:
                g.db.execute("""DELETE FROM lastcall WHERE allocation = ?""",
                        [allocation])
                g.db.execute("""INSERT INTO lastcall (calldate, calldate_text,
                allocation) VALUES (?,?,?)""",
                [str(calldate_a.strftime("%Y-%m-%d")), a,
                    allocation])
                g.db.commit()
        except ValueError:
            pass
        g.db.execute("""UPDATE calls SET actual_calldate = ?,
            call_check_no = ?,
            call_check_amt = ?
            WHERE expected_calldate = ? AND
            allocation = ?""", [a, c, d, b, request.form['allocation']])
        g.db.commit()
    flash('Entry for allocation %s edited' % allocation)
    entries = query_db("""SELECT calls.allocation, MIN(expected_calldate_sql)
            as mdate, calls.calltype, calls.expected_calldate as expdate,
            demo.initials, demo.phonenumber, demo.email FROM calls, demo
            WHERE calls.allocation = demo.allocation and
            expected_calldate_sql > date('NOW') GROUP BY
            calls.allocation""")
    return render_template('main.html', entries=entries)

@app.route('/remove_patient')
def remove_patient():
    return render_template('remove_patient.html')

@app.route('/submit_removal', methods = ['GET', 'POST'])
def submit_removal():
    error = None
    if request.form['allocation']:
        g.db.execute("""INSERT INTO dropped_from_study (allocation,
        pt_offstudy, offstudyreason) values (?,?,?)""",
            [request.form['allocation'],
            request.form['pt_offstudy'], request.form['offstudyreason']])
        g.db.execute("""UPDATE demo SET status = "off" WHERE allocation = ?""",
            [request.form['allocation']])
        g.db.execute("""DELETE FROM calls where allocation = ?""",
            [request.form['allocation']])
        g.db.commit()
        entries = query_db("""SELECT calls.allocation,
            MIN(expected_calldate_sql) as mdate, calls.calltype,
            calls.expected_calldate as expdate,
            demo.initials, demo.phonenumber, demo.email FROM calls, demo
            WHERE calls.allocation = demo.allocation and
            expected_calldate_sql > date('NOW') GROUP BY
            calls.allocation""")
    else:
        error = "Must have allocation to remove patient"
    return render_template('main.html', error = error, entries = entries)

@app.route('/all_patients')
def all_patients():
    entries = query_db("""SELECT allocation, dob, pt_userid, uw_id,
    initials, txdate, injection1, status FROM demo""")
    return render_template('all_patients.html', entries = entries)

@app.route('/summary_stats')
def summary_stats():
    visit1 = query_db("""SELECT COUNT(check1no) FROM demo WHERE check1no !=
                'None'""")
    visit2 = query_db("""SELECT COUNT(check2no) FROM demo WHERE check2no !=
                'None'""")
    visit3 = query_db("""SELECT COUNT(check3no) FROM demo WHERE check3no !=
                'None'""")
    visit4 = query_db("""SELECT COUNT(check4no) FROM demo WHERE check4no !=
                'None'""")
    visit5 = query_db("""SELECT COUNT(check5no) FROM demo WHERE check5no !=
                'None'""")
    visit6 = query_db("""SELECT COUNT(check6no) FROM demo WHERE check6no !=
                'None'""")
    visit7 = query_db("""SELECT COUNT(check7no) FROM demo WHERE check7no !=
                'None'""")
    return render_template('summary_statistics.html', visit1=visit1,
            visit2=visit2, visit3=visit3, visit4=visit4, visit5=visit5,
            visit6=visit6, visit7=visit7)

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

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
