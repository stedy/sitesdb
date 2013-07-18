from werkzeug import generate_password_hash
import sqlite3

con =  sqlite3.connect('v212.db')
con.text_factory = str
cursor = con.cursor()

cursor.execute("""INSERT INTO user (username, password) values (?,?)""",
                ['vzv2472', generate_password_hash('2472fhcrc')])
con.commit()
