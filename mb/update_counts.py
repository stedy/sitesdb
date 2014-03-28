import sqlite3

def main():
    with sqlite3.connect('mb.db') as conn:
        cc = conn.cursor()
        cc.execute("""DROP TABLE IF EXISTS samplecounts""")
        cc.execute("""CREATE TABLE samplecounts (Subject_ID text,
                        bloodevents text, swabevents text)""")
        conn.commit()

        bloodcode = cc.execute("""SELECT Subject_ID, COUNT(event) FROM events
            WHERE event = "Received" AND sample = "Blood" GROUP BY Subject_ID""")
        blood = bloodcode.fetchall()

        swabcode = cc.execute("""SELECT Subject_ID, COUNT(event) FROM events
            WHERE event = "Received" AND sample = "Swab" GROUP BY Subject_ID""")
        swab = swabcode.fetchall()

        for x,y in zip(blood, swab):
            cc.execute("""INSERT INTO samplecounts VALUES (?,?,?)""", (x[0],
                x[1], y[1]))
        conn.commit()


if __name__ == "__main__":
    main()
