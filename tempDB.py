import csv
from collections import OrderedDict
import sqlite3
import glob
import json

def strip_non_ascii(string):
    """Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def getDb(database_name='temp.db'):
    return sqlite3.connect(database=database_name)

def query_db(query, args=()):
    conn = getDb()
    cur = conn.cursor()
    cur.execute(query, args)
    rez = cur.fetchall()
    conn.close()
    return rez

jsonQuery = '''
    SELECT
        '{' || '"name": "' || name || '", "row": ' || row || ', ' || group_Concat(concats) || '}'
    FROM (
        SELECT
            name , row,  ' ' || col || ': ' || value AS concats
        FROM
            csvFiles
            )
    GROUP BY
        name, row
    HAVING name IN (?)'''


conn = getDb()
c = conn.cursor()
c.execute('''DROP TABLE IF EXISTS csvFiles''')
c.execute('''CREATE TABLE csvFiles
             (name text, row int, col text, value text, PRIMARY KEY(name,row,col))''')

conn.commit()

theFiles = glob.glob("c:/mycode/officeProjects_V2/appFolder/data/*.csv")
for f in theFiles:
    print(f)
    reader = csv.DictReader(open(f, 'rb'))
    container = []
    table_id = f.split('\\')[1]
    row_id = 0 
    for row in reader:
        row_id += 1
        for key in row.keys():
            container.append((table_id, row_id, json.dumps(key), json.dumps(strip_non_ascii(row[key]))))
    c.executemany('INSERT INTO csvFiles VALUES (?,?,?,?)', container)

conn.commit()
conn.close()

#for r in c.execute("SELECT * FROM csvFiles"): print(r)

my_query = query_db("select * from csvFiles limit 10")

#json_output = json.dumps(my_query)


c = getDb().cursor()

asdf = c.execute('''
    SELECT
        '{' || '"name": "' || name || '", "row": ' || row || ', ' || group_Concat(concats) || '}'
    FROM (
        SELECT
            name , row,  ' ' || col || ': ' || value AS concats
        FROM
            csvFiles
            )
    GROUP BY
        name, row
    HAVING name IN (?)''', ["contracts.csv"]).fetchall()



"""
asdf = c.execute('''
    select
        '{' || '"name": "' || name || '", "row": ' || row || ', ' || group_Concat(concats) || '}'
    from (
        select
            name , row,  ' ' || col || ': ' || value AS concats
        from
            csvFiles
            )
    group by
        name, row
    limit 2''').fetchall()
"""


