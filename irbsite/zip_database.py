import zipfile
import glob
import datetime as dt
import sqlite3
import csv
import os

def main():
    with sqlite3.connect('irb_db.db') as connection:
        csvWriter = csv.writer(open("archives/safety_reports.csv", "w"))
        c = connection.cursor()
        code = c.execute("SELECT * from safety")
        rows = code.fetchall()
        headers_demo = []
        for colinfo in c.description:
            headers_demo.append(colinfo[0])
        csvWriter.writerow(headers_demo)
        csvWriter.writerows(rows)

    files = glob.glob('*.csv')
    now = dt.datetime.now().strftime('%Y-%m-%d')
    z = zipfile.ZipFile(os.path.join('archives', now + "_database.zip"), 'w')

    for x in files:
        z.write(os.path.join('archives', x))
    z.close()

if __name__ == "__main__":
    main()
