
PRAGMA foreign_keys = ON;
DROP TABLE IF EXISTS csvMeta;
CREATE TABLE csvMeta (
	name text,
	title text,
	description text,
	PRIMARY KEY(name)
);
CREATE INDEX csvMeta_name ON csvMeta(name);

DROP TABLE IF EXISTS csvFiles;
CREATE TABLE csvFiles (
	name text, 
	row int, 
	col text, 
	value text,
	PRIMARY KEY(name,row,col), 
	FOREIGN KEY(name) REFERENCES csvMeta(name) ON DELETE CASCADE
);
CREATE INDEX csvFiles_index_name_col ON csvFiles (name, col);	

DROP TABLE IF EXISTS commentTable;
CREATE TABLE commentTable (
	id INTEGER PRIMARY KEY,
	thePage text, 
	theUser text, 
	theComment text 
);
CREATE INDEX commentTable_index_name_col ON commentTable(thePage, theUser);	


