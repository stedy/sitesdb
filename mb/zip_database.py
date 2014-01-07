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
    headers_demo = []
    for colinfo in c.description:
        headers_demo.append(colinfo[0])
    csvWriter.writerow(headers_demo)
    csvWriter.writerows(rows)

    csvWriter2 = csv.writer(open("recipient_blood.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from recipient_blood")
    rows = code.fetchall()
    headers_rb = []
    for colinfo in c.description:
        headers_rb.append(colinfo[0])
    csvWriter2.writerow(headers_rb)
    csvWriter2.writerows(rows)

    csvWriter3 = csv.writer(open("recipient_swabs.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from recipient_swabs")
    rows = code.fetchall()
    headers_rs = []
    for colinfo in c.description:
        headers_rs.append(colinfo[0])
    csvWriter3.writerow(headers_rs)
    csvWriter3.writerows(rows)

    csvWriter4 = csv.writer(open("donor_blood.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from donor_blood")
    rows = code.fetchall()
    headers_db = []
    for colinfo in c.description:
        headers_db.append(colinfo[0])
    csvWriter4.writerow(headers_db)
    csvWriter4.writerows(rows)

    csvWriter5 = csv.writer(open("donor_swabs.csv", "w"))
    c = connection.cursor()
    code = c.execute("SELECT * from donor_swabs")
    rows = code.fetchall()
    headers_ds = []
    for colinfo in c.description:
        headers_ds.append(colinfo[0])
    csvWriter5.writerow(headers_ds)
    csvWriter5.writerows(rows)

files = glob.glob('*.csv')
now = dt.datetime.now().strftime('%Y-%m-%d')
z = zipfile.ZipFile(now + "_database.zip", 'w')

for x in files:
    z.write(x)
z.close()
