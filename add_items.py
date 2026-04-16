from market import app, db
from market.models import Item

with app.app_context():
    item1 = Item(name="Laptop", barcode="111111111111", price=800, description="Good laptop")
    item2 = Item(name="Phone", barcode="222222222222", price=500, description="Smartphone")

    db.session.add(item1)
    db.session.add(item2)
    db.session.commit()

    print("Items added!")