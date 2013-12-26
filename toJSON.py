#http://jaranto.blogspot.com/2012/12/transform-csv-file-to-json-file-with.html
import csv
import json
import sys
from collections import OrderedDict
from appFolder.models import MainData
from appFolder import db

def updateDatabase(data):
	db.session.add(data)
	db.session.commit()

def strip_non_ascii(string):
    """Returns the string without non ASCII characters"""
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def csvToJson(filename):
	"""converts a csv file to json file and maintains the order of the columns"""
	container = []
	print("Opening CSV file: "),filename 
	with open(filename, 'r') as f:
		csv_reader = csv.DictReader(f)	
		for row in csv_reader:
			temp = OrderedDict()
			for name in csv_reader.fieldnames:
				temp[name] = strip_non_ascii(row[name])
			container.append(temp)
	container = json.dumps(container)
	return container

def columnDefs(filename):
	"""this output goes in the angular controler variable $scope.columnDefs"""
	container = []
	with open(filename, 'r') as f:
		csv_reader = csv.DictReader(f)
		for (index, name) in enumerate(csv_reader.fieldnames):
			temp = "{{\"mDataProp\": \"{0}\",\"aTargets\":[{1}]}}".format(name, index)
			container.append(temp)
	container = json.dumps(container)
	return container
  
def trMaker(filename):
	"""this output goes into the HTML file"""
	container = []
	csv_filename = filename[0]
	with open(csv_filename, 'r') as f:
		csv_reader = csv.DictReader(f)
		for name in enumerate(csv_reader.fieldnames):
			temp = "<th style=\"width:150px\"> {} </th>".format(name)
			container.append(temp)
	return container

if __name__ == "__main__":
	theFile = sys.argv[1]
	pageUri = sys.argv[2]
	theData = csvToJson(theFile)
	theColDef = columnDefs(theFile)
	data = MainData(thePageUri=pageUri,theData=theData,theColumnDefs=theColDef)
	#will break poorly if 'thePageUri' already exists (must be unique).  
	#Will just print bunch of crap to the console (DOS, BASH) on error
	#the webapp server needs to be running before this command is run
	updateDatabase(data)

