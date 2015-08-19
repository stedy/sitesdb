import zipfile
import datetime as dt
import sqlite3
import csv
import os
from glob import glob

def main():
    with sqlite3.connect('irb_site.db') as connection:
        with open("archives/protocols.csv", "w") as cw:
            csvWriter = csv.writer(cw)
            c = connection.cursor()
            code = c.execute("SELECT * from protocols")
            rows = code.fetchall()
            headers_demo = []
            for colinfo in c.description:
                headers_demo.append(colinfo[0])
            csvWriter.writerow(headers_demo)
            csvWriter.writerows(rows)

        with open("archives/reviewcomm.csv", "w") as rc:
            csvWriter = csv.writer(rc)
            c = connection.cursor()
            code = c.execute("SELECT * from reviewcomm")
            rows = code.fetchall()
            headers_demo = []
            for colinfo in c.description:
                headers_demo.append(colinfo[0])
            csvWriter.writerow(headers_demo)
            csvWriter.writerows(rows)

    now = dt.datetime.now().strftime('%Y-%m-%d')
    with zipfile.ZipFile(os.path.join('archives', now + "_database.zip"), 'w') as zf:
        for fn in glob("archives/*.csv"):
            zf.write(fn)

    os.chmod(os.path.join('archives', now + "_database.zip"), 0777)

if __name__ == "__main__":
    main()
