import zipfile
import datetime as dt
import sqlite3
import csv
import os
from glob import glob
from contextlib import closing

def main():
    with sqlite3.connect('irb_site.db') as connection:
        tables = []
        c = connection.cursor()
        c.execute("""SELECT name FROM sqlite_master WHERE type = 'table';""")
        for x in c.fetchall():
            tables.append(x[0])
        tables.remove('user')
        tables.remove('sqlite_sequence')
        for table in tables:
            fn = "archives/" + table + ".csv"
            with open(fn, "w") as outfile:
                csvWriter = csv.writer(outfile)
                c = connection.cursor()
                cmd = "SELECT * FROM " + table
                code = c.execute(cmd)
                rows = code.fetchall()
                headers_demo = []
                for colinfo in c.description:
                    headers_demo.append(colinfo[0])
                csvWriter.writerow(headers_demo)
                csvWriter.writerows(rows)

    now = dt.datetime.now().strftime('%Y-%m-%d')
    with closing(zipfile.ZipFile(os.path.join('archives', now + "_database.zip"), 'w')) as zf:
        for fn in glob("archives/*.csv"):
            zf.write(fn)

    os.chmod(os.path.join('archives', now + "_database.zip"), 0777)

if __name__ == "__main__":
    main()
