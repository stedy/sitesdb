import zipfile
import glob
import datetime as dt
import sqlite3
import csv

with sqlite3.connect('mb.db') as connection:
    csvWriter = csv.writer(open("demo.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from demo")
    rows = code.fetchall()
    headers = []
    for colinfo in c.description:
        headers.append(colinfo[0])
    csvWriter.writerow(headers)
    csvWriter.writerows(rows)

files = glob.glob('*.csv')
now = dt.datetime.now().strftime('%Y-%m-%d')
z = zipfile.ZipFile(now + "_database.zip", 'w')

for x in files:
    z.write(x)
z.close()
