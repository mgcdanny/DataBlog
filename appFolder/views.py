from flask import render_template, jsonify, make_response, _app_ctx_stack, Response, request, redirect
from werkzeug import secure_filename
from appFolder import app
#from appFolder.models import MainData
import sqlite3
import glob
import csv
import json
import os
import re
import sys

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context"""
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request"""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def init_db():
    """Creates the database tables"""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def strip_non_ascii(string):
    """Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def update_csvFiles(csvFile, table_name):
    """updates the csvFiles table"""
    with app.app_context():
        reader = csv.DictReader(open(csvFile, 'rb'))
        reader.fieldnames = map(lambda x: re.sub("\W","",x), reader.fieldnames)
        container = []
        row_id = 0
        for row in reader:
        	row_id += 1
        	for key in row.keys():
        		container.append((table_name, row_id, json.dumps(key), json.dumps(strip_non_ascii(row[key]))))
        db = get_db()
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        try:
            cur.executemany('INSERT INTO csvFiles VALUES (?,?,?,?)', container)
            db.commit()
        except:
            e = sys.exc_info()[0]
            print(e)
            pass

def update_csvMeta(list_Name_Title_Desc):
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        try:
            cur.execute('INSERT INTO csvMeta VALUES (?,?,?)', list_Name_Title_Desc)
            db.commit()
        except:
            e = sys.exc_info()[0]
            print(e)
            pass

def init_data(csvfile="appFolder/data/*.csv"):
	for f in glob.glob(csvfile):
	    print(f)
	    update_csvFiles(f)

def query_db(query, args=()):
	with app.app_context():
	    cur = get_db().cursor().execute(query, args)
	    rez = cur.fetchall()
	    return rez

def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['csv'])
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    print("I am the file upload API")
    theFile = request.files['upFile']
    csv_save_name = secure_filename(theFile.filename)
    print(csv_save_name)
    if theFile and allowed_file(theFile.filename):
        csv_save_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_save_name)
        theFile.save(csv_save_path)
        container = [csv_save_name,request.form['upFileTitle'],request.form['upFileDesc']]
        update_csvMeta(container)
        update_csvFiles(csv_save_path, csv_save_name)
        return "file upload response: success"
    else: 
        print("Bad file to upload")
        return "file upload response: fail"

@app.route("/api/<thePageUri>", methods = ['GET', 'DELETE', 'PUT'])
def api(thePageUri):
    print("i am the server side PAGE API")
    if request.method == 'GET':
        rez = query_db(jsonQuery, [thePageUri])
        return jsonify(theData=[json.loads(row[0]) for row in rez])
    if request.method == 'DELETE':
        db = get_db()
        cur = db.cursor()
        cur.execute('PRAGMA foreign_keys = ON')
        cur.execute('delete from csvMeta where name= ?', [thePageUri])
        db.commit()
        return "this is the DELETE response"
    if request.method == 'PUT':
        print("this is the PUT API call")
        db = get_db()
        req = request.json
        #if coming from a form instead of inline nggrid
        #req = request.json[0] 
        row = req['row']
        for col in req:
            if col not in ['row','name']:
                updateQuery = "UPDATE csvFiles SET value=? WHERE col=? AND row=? AND name=?"
                db.execute(updateQuery, [json.dumps(req[col]), json.dumps(col), row, thePageUri])
        db.commit()
        return "this is the PUT response"

@app.route("/api/allTables", methods = ['GET'])
def apiAllTables():
    print("i am the server side allTables API")
    rez = query_db("SELECT DISTINCT name FROM csvMeta")
    print(rez)
    return jsonify(theData=[row[0] for row in rez])

@app.route("/api/meta/<thePageUri>", methods = ['GET', 'PUT'])
def apiMeta(thePageUri):
    if request.method == 'GET':
        print("i am the server side GET META API")
        rez = query_db("SELECT * FROM csvMeta WHERE name = ?", [thePageUri])
        rezDict = dict(zip(rez[0].keys(),rez[0]))
        return jsonify(rezDict)
    if request.method == 'PUT':
        print("i am the server side PUT META API")
        updateQuery = "UPDATE csvMeta SET title=?, description=? WHERE name=?"
        db = get_db()
        req = request.json
        print(req)
        db.execute(updateQuery, [req['title'],req['description'],req['name']])
        db.commit()
        return "this is the PUT META API response"




