import sqlite3
import csv

with sqlite3.connect("vzv.db") as connection:
    csvWriter = csv.writer(open("dumpedcalls.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from calls")
    rows = code.fetchall()
    csvWriter.writerows(rows)

    csvWriter2 = csv.writer(open("dumpeddemo.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from demo")
    rows = code.fetchall()
    csvWriter2.writerows(rows)
