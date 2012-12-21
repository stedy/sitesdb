import csv
import sqlite3

def main():
    connection = sqlite3.connect('version1.db')
    connection.text_factory = str
    cursor = connection.cursor()

    cursor.execute("""select Isolate, Sequence from isolate;""")

    with open('current_seqs.fasta', 'w') as cs:
        for i in cursor.fetchall():
            if len(i[1]) > 0:
                cs.write(">" + i[0] + "\n" + i[1] + "\n")

if __name__=="__main__":
    main()
