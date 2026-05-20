import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
from flask_login import LoginManager
from flask_session import Session

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, '..', 'instance', 'database.db')
os.makedirs(os.path.dirname(database_path), exist_ok=True)
database_uri = f"sqlite:///{os.path.normpath(database_path).replace(os.path.sep, '/')}"
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '6bbfe0ca18dacabb4c4f3b66'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message = 'Please log in first to access this page.'
login_manager.login_message_category = 'info'

Session(app)

# Register routes when the package is imported so app routes are available
from market import routes

