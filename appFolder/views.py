import sqlite3
import glob
import csv
import json
from appFolder import app
#from appFolder.models import MainData
from flask import render_template, jsonify, make_response, _app_ctx_stack, Response

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def strip_non_ascii(string):
    """Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def update_db(csvfile, table='csvFiles'):
	with app.app_context():
		reader = csv.DictReader(open(csvfile, 'rb'))
		container = []
		table_id = csvfile.split('\\')[1]
		row_id = 0 	
		for row in reader:
			row_id += 1
			for key in row.keys():
				container.append((table_id, row_id, json.dumps(key), json.dumps(strip_non_ascii(row[key]))))
		db = get_db()
		db.cursor().executemany('INSERT INTO csvFiles VALUES (?,?,?,?)', container)
		db.commit()

def init_data(csvfile="appFolder/data/*.csv"):
	for f in glob.glob(csvfile):
	    print(f)
	    update_db(f)

def query_db(query, args=()):
	with app.app_context():
	    cur = get_db().cursor().execute(query, args)
	    rez = cur.fetchall()
	    return rez

jsonQuery = '''
    SELECT
        '{' || '"name": "' || name || '", "row": ' || row || ', ' || group_Concat(concats) || '}' as data
    FROM (
        SELECT
            name , row,  ' ' || col || ': ' || value AS concats
        FROM
            csvFiles
            )
    GROUP BY
        name, row
    HAVING name IN (?)'''

@app.route('/<path:p>')
@app.route('/')
def ui(p=None):
	return make_response(open('appFolder/templates/index.html').read())

@app.route("/api/<thePageUri>", methods = ['GET'])
def api(thePageUri):
	#TODO pass thePageUri to the query as the limiting parameter
	print("i am the server side API")
	rez = query_db(jsonQuery, ["contracts.csv"])
	return jsonify(theData=[json.loads(row[0]) for row in rez])

@app.route("/api/allTables", methods = ['GET'])
def apiAllTables():
	#TODO create another table with just unique names so this can query it
	print("i am the allTables server side API")
	#rez = db.session.query(MainData.thePageUri.distinct()).all()
	#return jsonify(theData=[row[0] for row in rez])
	return jsonify(theData=['qwer'])

