from market import app, db
from market.models import *

with app.app_context():
    db.create_all()