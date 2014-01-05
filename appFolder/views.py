import sqlite3
import glob
import csv
import json
from appFolder import app
#from appFolder.models import MainData
from flask import render_template, jsonify, make_response, _app_ctx_stack, Response, request, redirect
from werkzeug import secure_filename
import os
import re

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
        reader.fieldnames = map(lambda x: re.sub("\W","",x), reader.fieldnames)
        container = []
        table_id = re.match(r'.*(\W+)(\w*)(\.csv)$', csvfile).groups()[1]
        row_id = 0
        for row in reader:
        	row_id += 1
        	for key in row.keys():
        		container.append((table_id, row_id, json.dumps(key), json.dumps(strip_non_ascii(row[key]))))
        db = get_db()
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.executemany('INSERT INTO csvFiles VALUES (?,?,?,?)', container)
        #db.cursor().executemany('INSERT INTO csvFiles VALUES (?,?,?,?)', container)
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


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['csv'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/<path:p>')
@app.route('/')
def ui(p=None):
	return make_response(open('appFolder/templates/index.html').read())

@app.route('/api/upload', methods=['POST'])
def upload_file():
    print("I am the file upload API")
    print(request.files)
    print(request.data)
    print(request.json)
    theFile = request.files['upFile']
    if theFile and allowed_file(theFile.filename):
        filename = secure_filename(theFile.filename)
        theFile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        update_db(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "file upload response: success"
    else: 
        print("Bad file to upload")
        return "file upload response: fail"


@app.route('/api/upload_meta', methods=['POST'])
def upload_meta():
    print(request.json)
    container = [request.json['name'].split('.')[0],request.json['title'],request.json['desc']]
    db = get_db()
    cur = db.cursor()
    cur.execute('PRAGMA foreign_keys = ON')
    cur.execute('INSERT INTO csvMeta VALUES (?,?,?)', container)
    db.commit()
    return 'upload_meta response: success'

@app.route("/api/<thePageUri>", methods = ['GET', 'DELETE', 'PUT'])
def api(thePageUri):
    print("i am the server side API")
    if request.method == 'GET':
        rez = query_db(jsonQuery, [thePageUri])
        return jsonify(theData=[json.loads(row[0]) for row in rez])
    if request.method == 'DELETE':
        db = get_db()
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute('delete from csvMeta where name= ?', [thePageUri])
        db.commit()
        return "this is the DELETE api response"
    if request.method == 'PUT':
        print("this is the PUT API call")
        db = get_db()
        req = request.json[0]
        row = req['row']
        for col in req:
            if col not in ['row','name']:
                updateQuery = "UPDATE csvFiles SET value=? WHERE col=? AND row=? AND name=?"
                db.execute(updateQuery, [json.dumps(req[col]), json.dumps(col), row, thePageUri])
        db.commit()
        return "this is the PUT response"

@app.route("/api/allTables", methods = ['GET'])
def apiAllTables():
    #TODO create another table with just unique names so this can query it
    print("i am the allTables server side API")
    rez = query_db("SELECT DISTINCT name FROM csvFiles")
    print(rez)
    return jsonify(theData=[row[0] for row in rez])


