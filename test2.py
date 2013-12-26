import json
from appFolder import views

asdf = views.query_db(views.jsonQuery, ["money.csv"])

for row in asdf:
    print(json.loads(row[0]))


"""
import StringIO
import csv
import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

con = sqlite3.connect("test.db")
con.row_factory = dict_factory
cur = con.cursor()
cur.execute('''
    SELECT
        name, row, group_Concat(col) as cols, group_Concat(value) as vals
    FROM
        csvFiles
    GROUP BY
        name, row
    LIMIT 10''')
rez = cur.fetchall()

for dictRow in rez:
    zip(dictRow['vals']

reader = csv.reader(StringIO.StringIO(asdf[0]['vals']), delimiter=",")
for r in reader: print r
"""
