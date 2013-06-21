import datetime as dt
import sqlite3
import csv

con = sqlite3.connect('vzv.db')
con.text_factory = str
cursor = con.cursor()


with open("test.csv", 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for row in reader:
        allocation = row[0]
        txdateraw = row[1]
        initials = row[2]
    
        txdate = dt.datetime.strptime(txdateraw, "%m/%d/%Y")
        days = [30, 60, 90, 118, 180, 455]
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
        calldays_complete = zip(calldays_projected, calldays_projected_sql, calltype)

        cursor.execute("""DELETE FROM calls where allocation = ?""",
                [allocation])
        for cp, cps, ct in calldays_complete:
            cursor.execute("""INSERT INTO calls (initials, expected_calldate,
                    expected_calldate_sql, calltype, allocation) 
                    values (?,?,?,?,?)""", [initials, cp, cps, ct, allocation])
con.commit()
