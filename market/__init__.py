from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = '6bbfe0ca18dacabb4c4f3b66'

db = SQLAlchemy(app)

# import routes ONLY after app + db are created
from market import routes
