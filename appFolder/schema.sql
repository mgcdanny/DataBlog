DROP TABLE IF EXISTS csvFiles;
CREATE TABLE csvFiles (
	name text, 
	row int, 
	col text, 
	value text, 
	PRIMARY KEY(name,row,col)
);

