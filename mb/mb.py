import sqlite3
from flask import Flask, request, session, g, \
        render_template, flash, send_from_directory

from contextlib import closing
import datetime as dt
import zip_database as zd
import update_counts as uc

DATABASE = 'mb.db'
DEBUG = True
SECRET_KEY = 'development key'
FILE_FOLDER = 'archives'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('DF_DB_SETTINGS', silent=True)

def connect_db():
    """Returns a new connection to the database"""
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    """Initializes a new database"""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries"""
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def next_weekday(d, weekday):
    """Calculates the next weekday in case tx on weekend"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return d + dt.timedelta(days_ahead)

#start with some decorators

@app.before_request
def before_request():
    g.db = connect_db()
    g.user = None
    if 'user_id' in session:
        g.user = query_db('SELECT * FROM user WHERE user_id = ?',
                        [session['user_id']], one=True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def main():
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP By Subject_ID""")
    blood = query_db("""SELECT Subject_ID, eventdate FROM events
            WHERE event = "Scheduled" """)
    upcomingkits = query_db("""SELECT Subject_ID, kit_event, kit_eventdate,
            kit_expected FROM kit WHERE kit_expected >
            (SELECT date('NOW', '+7 days')) AND kit_expected <
            (SELECT date('NOW', '+14 days')) AND kit_event = 'shipped'""")
    return render_template('main.html', entries=entries, blood=blood,
            upcomingkits=upcomingkits)

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    """Setting up adding new user"""
    error = None
    if request.form['txdate'] and request.form['Subject_ID']:
        raw_id = "M-" + request.form['Subject_ID'] + "-S001"
        swabs = [7 * x for x in range(14)]
        txdate_raw = request.form['txdate']
        txdate = dt.datetime.strptime(txdate_raw, "%m/%d/%Y")
        fu_days = [(next_weekday(txdate, 0) +
            dt.timedelta(days=day)).strftime("%m/%d/%Y") for day in swabs]
        outvals = []
        for x in range(14):
            outvals.append(fu_days[x])
        g.db.execute("""INSERT INTO demo (Subject_ID, uwid, pt_init, Name,
                    Status, txdate, Donrep, onoff) VALUES
                    (?,?,?,?,?,?,?,?)""",
                    [raw_id, request.form['uwid'],
                    request.form['pt_init'], request.form['Name'],
                    request.form['Status'], request.form['txdate'],
                    request.form['Donrep'], "on"])
        for x in outvals:
            g.db.execute("""INSERT INTO events (Subject_ID, event,
                            eventdate) VALUES (?,?,?)""",
                            [raw_id, "Expected", x])
            g.db.commit()
        flash('New patient successfully added')
    else:
        error = "Must have txdate and subject ID to enter new patient"
    return render_template('main.html', error=error)

@app.route('/query')
def query():
    return render_template('subj_lookup.html')

@app.route('/check_query')
def check_query():
    return render_template('check_lookup.html')

@app.route('/add_subject')
def add_subject():
    return render_template('add_subject.html')

@app.route('/all_subjects')
def all_subjects():
    entries = query_db("""SELECT Subject_ID, pt_init, Name, uwid, Status,
                    txdate, Donrep, onoff FROM demo""")
    return render_template('all_subjects.html', entries=entries)

@app.route('/all_checks')
def all_checks():
    entries = query_db("""SELECT COUNT(*) as checktotal,
        checks.Subject_ID, pt_init FROM checks, demo WHERE
        checks.Subject_ID = demo.Subject_ID GROUP BY checks.Subject_ID""")
    return render_template('all_checks.html', entries=entries)

@app.route('/<id_number>', methods=['GET', 'POST'])
def id_edit(id_number):
    evententries = query_db("""SELECT event, eventdate, week, sample FROM
                    events WHERE
                    Subject_ID = ? AND event = "Received" """,
                    [id_number])
    entries = query_db("""SELECT Subject_ID, pt_init, Name, uwid,
                    Status, txdate, Donrep FROM
                    demo where Subject_ID = ?""", [id_number])
    return render_template('edit_subject.html', evententries=evententries,
                            entries=entries)

@app.route('/send_kits_form')
def send_kits_form():
    entries = query_db("""SELECT Subject_ID FROM demo ORDER BY
            Subject_ID ASC""")
    return render_template('send_kits.html', entries=entries)

@app.route('/send_kits', methods=['GET', 'POST'])
def send_kits():
    now = dt.datetime.now()
    number_of_kits = request.form['count']
    for kit in range(int(number_of_kits)):
        exp_date = (next_weekday(now, 0) + dt.timedelta(days= 7 *
            kit)).strftime("%Y-%m-%d")
        g.db.execute("""INSERT INTO kit (Subject_ID, kit_eventdate,
                    kit_event, kit_expected) VALUES (?,?,?,?)""",
                    [request.form['Subject_ID'], now.strftime('%Y-%m-%d'),
                        'shipped', exp_date])
        g.db.commit()
    flash('Kits for subject ID %s shipped' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP BY Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/receive_kits_form')
def receive_kits_form():
    entries = query_db("""SELECT Subject_ID FROM kit WHERE kit_event =
                        "shipped" GROUP BY Subject_ID""")
    return render_template('receive_kits.html', entries=entries)

@app.route('/receive_kits', methods=['GET', 'POST'])
def receive_kits():
    now = dt.datetime.now().strftime('%Y-%m-%d')
    g.db.execute("""DELETE FROM kit WHERE id = (SELECT MIN(id) FROM kit)
            AND Subject_ID = ? AND kit_event = "shipped" """,
            [request.form['Subject_ID']])
    g.db.execute("""INSERT INTO kit (Subject_ID, kit_eventdate, kit_event)
                VALUES (?,?,?)""",
                [request.form['Subject_ID'], now, 'received'])
    g.db.commit()
    flash('Kit for subject ID %s received' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP BY Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/add_event_form')
def add_event_form():
    entries = query_db("""SELECT Subject_ID FROM demo ORDER BY Subject_ID
                        ASC""")
    return render_template('add_event.html', entries=entries)

@app.route('/add_event', methods = ['GET', 'POST'])
def add_event():
    g.db.execute("""INSERT INTO events (Subject_ID, sample, event, eventdate,
                comments) VALUES (?,?,?,?,?)""", [request.form['Subject_ID'],
                    request.form['sample'], "Received",
                    request.form['eventdate'], request.form['comments']])
    g.db.commit()
    flash('Event added for subject ID %s' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP By Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/summarize_indivs', methods = ['GET', 'POST'])
def summarize_indivs():
    uc.main()
    entries = query_db("""SELECT Subject_ID, bloodevents, swabevents FROM
            samplecounts""")
    return render_template('summarize_indivs.html', entries=entries)

@app.route('/drop_subject_form')
def drop_subject_form():
    entries = query_db("""SELECT Subject_ID FROM demo WHERE onoff = "on"
                        ORDER BY Subject_ID ASC""")
    return render_template('drop_subject.html', entries=entries)

@app.route('/drop_subject', methods = ['GET', 'POST'])
def drop_subject():
    g.db.execute("""UPDATE demo SET onoff = "off" WHERE Subject_ID = ?""",
            [request.form['Subject_ID']])
    g.db.commit()
    flash('Subject ID %s dropped from study' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP By Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/send_check_form')
def send_check_form():
    entries = query_db("""SELECT Subject_ID FROM demo WHERE onoff = "on"
                        ORDER BY Subject_ID ASC""")
    return render_template('write_check.html', entries=entries)

@app.route('/send_check', methods = ['GET', 'POST'])
def send_check():
    g.db.execute("""INSERT into checks (Subject_ID, event, eventdate,
            checknumber, checkdeliver) VALUES (?,?,?,?,?)""",
            [request.form['Subject_ID'],
            request.form['event'], request.form['eventdate'],
            request.form['checknumber'], request.form['checkdeliver']])
    g.db.commit()
    flash('Check written for %s' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP By Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/schedule_blood_form')
def schedule_blood_form():
    entries = query_db("""SELECT Subject_ID FROM demo WHERE onoff = "on" ORDER
                        BY Subject_ID ASC""")
    return render_template('schedule_blood.html', entries=entries)

@app.route('/schedule_blood', methods = ['GET', 'POST'])
def schedule_blood():
    blood = request.form['blooddraw_date']
    sql_date = dt.datetime.strptime(blood, "%m/%d/%Y").strftime("%Y-%m-%d")
    g.db.execute("""INSERT into events (Subject_ID, eventdate, sample, event,
            sql_date) VALUES (?,?,?,?,?)""", [request.form['Subject_ID'],
                blood, "Blood", "Scheduled", sql_date])
    g.db.commit()
    flash('Blood draw scheduled for %s' % request.form['Subject_ID'])
    entries = query_db("""SELECT Subject_ID, COUNT(kit_event) as count FROM kit
            WHERE kit_event = "shipped" GROUP By Subject_ID""")
    return render_template('main.html', entries=entries)

@app.route('/get_archives', methods=['GET', 'POST'])
def get_archives():
    """Pull all tables from all db and convert into zip file for
    exporting"""
    zd.main()
    now = dt.datetime.now().strftime('%Y-%m-%d')
    filename = now + "_database.zip"
    return send_from_directory(app.config['FILE_FOLDER'],
            filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
