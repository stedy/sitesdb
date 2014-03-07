import sqlite3
from flask import Flask, request, session, g, \
        render_template, flash, send_from_directory

from contextlib import closing
import datetime as dt
import zip_database as zd

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
        g.user = query_db('select * from user where user_id = ?',
                        [session['user_id']], one=True)

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html')

@app.route('/add_form', methods=['GET', 'POST'])
def add_form():
    """Setting up adding new user"""
    error = None
    if request.form['txdate'] and request.form['subject_ID']:
        raw_id = "M-" + request.form['subject_ID'] + "-S001"
        swabs = [7 * x for x in range(14)]
        txdate_raw = request.form['txdate']
        txdate = dt.datetime.strptime(txdate_raw, "%m/%d/%Y")
        fu_days = [(next_weekday(txdate, 0) +
            dt.timedelta(days=day)).strftime("%m/%d/%Y") for day in swabs]
        outvals = [raw_id]
        for x in range(14):
            outvals.append(fu_days[x])
        g.db.execute("""INSERT INTO demo (subject_ID, uwid, pt_init, Name,
                    Status, txdate, Donrep, conditioning_start_date) values
                    (?,?,?,?,?,?,?,?)""",
                    [raw_id, request.form['uwid'],
                    request.form['pt_init'], request.form['Name'],
                    request.form['Status'], request.form['txdate'],
                    request.form['Donrep'],
                    request.form['conditioning_start_date']])
        if request.form['Donrep'] == "Recipient":
            g.db.execute("""INSERT INTO recipient_swabs (subject_ID,
                        Expected_week1, Expected_week2,
                        Expected_week3, Expected_week4,
                        Expected_week5, Expected_week6,
                        Expected_week7, Expected_week8,
                        Expected_week9, Expected_week10,
                        Expected_week11, Expected_week12,
                        Expected_week13,
                        Expected_week14) VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        outvals)
            g.db.execute("""INSERT INTO recipient_blood (Subject_ID) VALUES
                        (?)""", [raw_id])
        if request.form['Donrep'] == "Donor":
            g.db.execute("""INSERT INTO donor_swabs (subject_ID,
                        Expected_pre_tx, Received_pre_tx) VALUES (?,?,?)""",
                        [raw_id, request.form['Expected_pre_tx'],
                        request.form['Received_pre_tx']])
            g.db.execute("""INSERT INTO donor_blood (Subject_ID) VALUES (?)""",
                        [raw_id])
        g.db.commit()
        flash('New patient successfully added')
    else:
        error = "Must have txdate and subject ID to enter new patient"
    return render_template('main.html', error=error)

@app.route('/edit', methods=['GET', 'POST'])
def results():
    """Main functionality to edit and update sample data"""
    ids = str(request.form['subject_ID'])
    entries = query_db("""SELECT demo.subject_ID, pt_init, Name, uwid,
                    Status, txdate, Donrep, Expected_week1, Expected_week2,
                    Expected_week1, Received_week1,
                    Expected_week2, Received_week2,
                    Expected_week3, Received_week3,
                    Expected_week4, Received_week4,
                    Expected_week5, Received_week5,
                    Expected_week6, Received_week6,
                    Expected_week7, Received_week7,
                    Expected_week8, Received_week8,
                    Expected_week9, Received_week9,
                    Expected_week10, Received_week10,
                    Expected_week11, Received_week11,
                    Expected_week12, Received_week12,
                    Expected_week13, Received_week13,
                    Expected_week14, Received_week14,
                    Blood_expected_week1, Blood_received_week1,
                    Week1_time_drawn, Week1_time_processed,
                    Blood_expected_week2, Blood_received_week2,
                    Week2_time_drawn, Week2_time_processed,
                    Blood_expected_week3, Blood_received_week3,
                    Week3_time_drawn, Week3_time_processed,
                    Blood_expected_week4, Blood_received_week4,
                    Week4_time_drawn, Week4_time_processed
                    from demo, recipient_swabs,
                    recipient_blood WHERE demo.subject_ID =
                    recipient_swabs.subject_ID AND demo.subject_ID =
                    recipient_blood.subject_ID AND
                    demo.subject_ID = ?""",
                    [ids])
    return render_template('edit_subject.html', entries=entries)

@app.route('/query')
def query():
    return render_template('subj_lookup.html')

@app.route('/check_query')
def check_query():
    return render_template('check_lookup.html')

@app.route('/add_subject')
def add_subject():
    return render_template('add_subject.html')

@app.route('/update_form', methods=['GET', 'POST'])
def update_form():
    """Submit update form for individual participant"""
    subject_id = request.form['subject_ID']
    g.db.execute("""DELETE FROM demo WHERE subject_ID = ?""", [subject_id])
    g.db.execute("""INSERT INTO demo (subject_ID, pt_init, Name, uwid, Status,
                    txdate, Donrep) values
                    (?,?,?,?,?,?,?)""",
                    [request.form['subject_ID'], request.form['pt_init'],
                    request.form['Name'], request.form['uwid'],
                    request.form['Status'], request.form['txdate'],
                    request.form['Donrep']])
    g.db.execute("""DELETE FROM recipient_swabs WHERE subject_ID = ?""",
            [subject_id])
    g.db.execute("""INSERT INTO recipient_swabs (subject_ID, Expected_pre_tx,
                    Received_pre_tx,
                    Expected_week1, Received_week1,
                    Expected_week2, Received_week2,
                    Expected_week3, Received_week3,
                    Expected_week4, Received_week4,
                    Expected_week5, Received_week5,
                    Expected_week6, Received_week6,
                    Expected_week7, Received_week7,
                    Expected_week8, Received_week8,
                    Expected_week9, Received_week9,
                    Expected_week10, Received_week10,
                    Expected_week11, Received_week11,
                    Expected_week12, Received_week12,
                    Expected_week13, Received_week13,
                    Expected_week14, Received_week14) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['subject_ID'],
                    request.form['Expected_pre_tx'],
                    request.form['Received_pre_tx'],
                    request.form['Expected_week1'],
                    request.form['Received_week1'],
                    request.form['Expected_week2'],
                    request.form['Received_week2'],
                    request.form['Expected_week3'],
                    request.form['Received_week3'],
                    request.form['Expected_week4'],
                    request.form['Received_week4'],
                    request.form['Expected_week5'],
                    request.form['Received_week5'],
                    request.form['Expected_week6'],
                    request.form['Received_week6'],
                    request.form['Expected_week7'],
                    request.form['Received_week7'],
                    request.form['Expected_week8'],
                    request.form['Received_week8'],
                    request.form['Expected_week9'],
                    request.form['Received_week9'],
                    request.form['Expected_week10'],
                    request.form['Received_week10'],
                    request.form['Expected_week11'],
                    request.form['Received_week11'],
                    request.form['Expected_week12'],
                    request.form['Received_week12'],
                    request.form['Expected_week13'],
                    request.form['Received_week13'],
                    request.form['Expected_week14'],
                    request.form['Received_week14']
                    ])
    g.db.execute("""DELETE FROM recipient_blood WHERE
            subject_ID = ?""", [subject_id])
    g.db.execute("""INSERT INTO recipient_blood (subject_ID,
                    Blood_draw_pre_tx, Blood_received_pre_tx,
                    Pre_tx_time_drawn, Pre_tx_time_processed,
                    Blood_expected_week1, Blood_received_week1,
                    Week1_time_drawn, Week1_time_processed,
                    Blood_expected_week2, Blood_received_week2,
                    Week2_time_drawn, Week2_time_processed,
                    Blood_expected_week3, Blood_received_week3,
                    Week3_time_drawn, Week3_time_processed,
                    Blood_expected_week4, Blood_received_week4,
                    Week4_time_drawn, Week4_time_processed) values
                    (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    [request.form['subject_ID'],
                    request.form['Blood_draw_pre_tx'],
                    request.form['Blood_received_pre_tx'],
                    request.form['Pre_tx_time_drawn'],
                    request.form['Pre_tx_time_processed'],
                    request.form['Blood_expected_week1'],
                    request.form['Blood_received_week1'],
                    request.form['Week1_time_drawn'],
                    request.form['Week1_time_processed'],
                    request.form['Blood_expected_week2'],
                    request.form['Blood_received_week2'],
                    request.form['Week2_time_drawn'],
                    request.form['Week2_time_processed'],
                    request.form['Blood_expected_week3'],
                    request.form['Blood_received_week3'],
                    request.form['Week3_time_drawn'],
                    request.form['Week3_time_processed'],
                    request.form['Blood_expected_week4'],
                    request.form['Blood_received_week4'],
                    request.form['Week4_time_drawn'],
                    request.form['Week4_time_processed']])
    g.db.commit()
    flash('Entry for subject ID %s edited' % subject_id)
    return render_template('main.html')

@app.route('/all_subjects')
def all_subjects():
    entries = query_db("""SELECT subject_ID, pt_init, Name, uwid, Status,
                    txdate, Donrep FROM demo""")
    return render_template('all_subjects.html', entries=entries)

@app.route('/<id_number>', methods=['GET', 'POST'])
def id_edit(id_number):
    entries = query_db("""SELECT demo.subject_ID, pt_init, Name, uwid,
                    Status, txdate, Donrep, Expected_week1, Expected_week2,
                    Expected_week1, Received_week1,
                    Expected_week2, Received_week2,
                    Expected_week3, Received_week3,
                    Expected_week4, Received_week4,
                    Expected_week5, Received_week5,
                    Expected_week6, Received_week6,
                    Expected_week7, Received_week7,
                    Expected_week8, Received_week8,
                    Expected_week9, Received_week9,
                    Expected_week10, Received_week10,
                    Expected_week11, Received_week11,
                    Expected_week12, Received_week12,
                    Expected_week13, Received_week13,
                    Expected_week14, Received_week14,
                    Blood_expected_week1, Blood_received_week1,
                    Week1_time_drawn, Week1_time_processed,
                    Blood_expected_week2, Blood_received_week2,
                    Week2_time_drawn, Week2_time_processed,
                    Blood_expected_week3, Blood_received_week3,
                    Week3_time_drawn, Week3_time_processed,
                    Blood_expected_week4, Blood_received_week4,
                    Week4_time_drawn, Week4_time_processed
                    from demo, recipient_swabs,
                    recipient_blood WHERE demo.subject_ID =
                    recipient_swabs.subject_ID AND demo.subject_ID =
                    recipient_blood.subject_ID AND
                    demo.subject_ID = ?""",
                    [id_number])
    return render_template('edit_subject.html', entries=entries)

@app.route('/send_kits_form')
def send_kits_form():
    return render_template('send_kits.html')

@app.route('/send_kits', methods=['GET', 'POST'])
def send_kits():
    now = dt.datetime.now().strftime('%Y-%m-%d')
    number_of_kits = request.form['count']
    for kit in range(int(number_of_kits)):
        g.db.execute("""INSERT INTO kit (subject_ID, eventdate, event) VALUES
                    (?,?,?)""", [request.form['subject_ID'], now, 'shipped'])
        g.db.commit()
    flash('Kits for subject ID %s shipped' % request.form['subject_ID'])
    return render_template('main.html')

@app.route('/receive_kits_form')
def receive_kits_form():
    return render_template('receive_kits.html')

@app.route('/receive_kits', methods=['GET', 'POST'])
def receive_kits():
    now = dt.datetime.now().strftime('%Y-%m-%d')
    g.db.execute("""UPDATE kit SET event = ?, eventdate = ? WHERE subject_ID =
                ? AND eventdate = (SELECT MAX(eventdate) FROM kit)""",
                ['received', now, request.form['subject_ID']])
    g.db.commit()
    flash('Kit for subject ID %s received' % request.form['subject_ID'])
    return render_template('main.html')

@app.route('/summarize_indivs', methods = ['GET', 'POST'])
def summarize_indivs():
    entries = query_db("""SELECT subject_ID, COUNT(value) AS count FROM
    blood_events GROUP BY subject_ID""")
    return render_template('summarize_indivs.html', entries=entries)


@app.route('/get_archives', methods=['GET', 'POST'])
def get_archives():
    """Pull all tables from all db and convert into zip file for
    exporting"""
    zd.main()
    now = dt.datetime.now().strftime('%Y-%m-%d')
    filename = now + "_database.zip"
    return send_from_directory(app.config['FILE_FOLDER'],
            filename, as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
