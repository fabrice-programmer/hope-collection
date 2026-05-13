from market import app, db
from market.models import Item, User, TopUpRequest, Order

with app.app_context():
    db.create_all()
    print(" Tables created successfully!")