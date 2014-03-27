import zipfile
import glob
import datetime as dt
import sqlite3
import csv
import os

def main():
    with sqlite3.connect('mb.db') as connection:
        csvWriter = csv.writer(open("archives/demo.csv", "w"))
        c = connection.cursor()
        code = c.execute("SELECT * from demo")
        rows = code.fetchall()
        headers_demo = []
        for colinfo in c.description:
            headers_demo.append(colinfo[0])
        csvWriter.writerow(headers_demo)
        csvWriter.writerows(rows)

        csvWriter2 = csv.writer(open("archives/events.csv", "w"))
        c = connection.cursor()
        code = c.execute("SELECT * from events")
        rows = code.fetchall()
        headers_rb = []
        for colinfo in c.description:
            headers_rb.append(colinfo[0])
        csvWriter2.writerow(headers_rb)
        csvWriter2.writerows(rows)


    files = glob.glob('*.csv')
    now = dt.datetime.now().strftime('%Y-%m-%d')
    z = zipfile.ZipFile(os.path.join('archives', now + "_database.zip"), 'w')

    for x in files:
        z.write(os.path.join('archives', x))
    z.close()

if __name__ == "__main__":
    main()
