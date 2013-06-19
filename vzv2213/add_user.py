from werkzeug import generate_password_hash
import sqlite3

con =  sqlite3.connect('vzv.db')
con.text_factory = str
cursor = con.cursor()

cursor.execute("""INSERT INTO user (username, password) values (?,?)""",
                ['vzv2472', generate_password_hash('FHCRC_1600')])
con.commit()
