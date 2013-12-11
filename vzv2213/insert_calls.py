import csv
import sqlite3

connection = sqlite3.connect("vzv.db")
connection.text_factory = str
cursor = connection.cursor()

cursor.execute('DROP TABLE IF EXISTS calls')
cursor.execute("""CREATE TABLE calls (allocation text, expected_calldate date, initials text,
			show_calldate text, expected_calldate_sql date, calltype text, 
			actual_calldate text, actual_calldate_sql date, phonenumber text,
                    call_check_no text, call_check_amt text, email text)""")
connection.commit()

csvre = csv.reader(open("dumpedcalls.csv", 'rb'), delimiter = ",", quotechar='"')

t = (csvre,)
for t in csvre:
	cursor.execute('INSERT into calls VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', t)
connection.commit()

