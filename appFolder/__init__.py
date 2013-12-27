from flask import Flask

# configuration
DATABASE = 'test.db'
DEBUG = True
SECRET_KEY = '1234'
UPLOAD_FOLDER = 'appFolder/uploads'
ALLOWED_EXTENSIONS = set(['csv'])

# create our little application :)
app = Flask(__name__)

app.config['DATABASE'] = DATABASE
app.config['DEBUG'] = DEBUG
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


#this import is neccesary even though it doesn't look like it is being used
import appFolder.views


