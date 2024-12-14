import sqlite3
from datetime import date
connection=sqlite3.connect('kurslar.db')
cursor=connection.cursor()
def create_table():
    cursor.execute("""

    CREATE TABLE  IF NOT EXISTS kurslar(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     kurs_nomi VARCHAR(100),
                     kurs_narxi varchar(100),
                     toliq_malumot varchar(100),
                     kurs_oqituvchisi  varchar(100)
                   )
                   """)
    connection.commit()
    return 
def get_kurs_info(kurs_nomi):
    cursor.execute("""
    SELECT kurs_narxi, toliq_malumot, kurs_oqituvchisi 
    FROM kurslar 
    WHERE kurs_nomi = ?
    """, (kurs_nomi,))
    results = cursor.fetchall()  # Fetch all matching rows

    if not results:
        return "Mavjud emas"  # No data found
    elif len(results) == 1:
        return results[0]  # Return a single tuple for one row
    elif len(results) == 2:
        return results[:2]  # Return the first two rows
    else:
        return results  # Return all rows for three or more results



def insert_kurs(kurs_nomi, kurs_narxi, toliq_malumot, kurs_oqituvchisi):
    cursor.execute("""
    INSERT INTO kurslar (kurs_nomi, kurs_narxi, toliq_malumot, kurs_oqituvchisi)
    VALUES (?, ?, ?, ?)
    """, (kurs_nomi, kurs_narxi, toliq_malumot, kurs_oqituvchisi))
    connection.commit()




