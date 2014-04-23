import zipfile
import datetime as dt
import sqlite3
import csv
import os
import stat

def main():
    with sqlite3.connect('/var/www/html/irbdb/irb_db.db') as connection:
        csvWriter = csv.writer(open("/var/www/html/irbdb/archives/safety_reports.csv", "w"))
        c = connection.cursor()
        code = c.execute("SELECT * from safety")
        rows = code.fetchall()
        headers_demo = []
        for colinfo in c.description:
            headers_demo.append(colinfo[0])
        csvWriter.writerow(headers_demo)
        csvWriter.writerows(rows)

    now = dt.datetime.now().strftime('%Y-%m-%d')
    z = zipfile.ZipFile(os.path.join('archives', now + "_database.zip"), 'w')


    z.write("/var/www/html/irbdb/archives/safety_reports.csv")
    z.close()
    os.chmod(os.path.join('archives', now + "_database.zip"), 0777)

if __name__ == "__main__":
    main()
