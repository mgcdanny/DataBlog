Base Code for the DataBlog web app

Requires:
Python 2.7
Flask

to get Flask:
pip install Flask

After cloning cd into directory where startUp.py is and type:

```
$ python startUp.py
$ python app.py
```

This should start the server.  Open a Chrome or FireFox (zero IE support) and go to 

http://127.0.0.1:8000


Uploading CSV Files:

Variables names must be in the first row (header).

No spaces or punctuation is allowed in either the filename or the variable names (header).

The file name must be unique,,, can not upload the same named file twice

There are sample csv files included in the uploads folder, try uploading those and see what happens.
