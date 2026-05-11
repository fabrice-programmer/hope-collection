from market import app, db
from market.models import Item

with app.app_context():
    # Clear existing items
    Item.query.delete()
    
    item1 = Item(name="Gaming Laptop", barcode="111111111111", price=1200, description="Powerful gaming laptop with Intel i9, 32GB RAM, RTX 4070")
    item2 = Item(name="Business Laptop", barcode="222222222222", price=950, description="Sleek business laptop with Intel i7, 16GB RAM, 512GB SSD")
    item3 = Item(name="Ultrabook Laptop", barcode="333333333333", price=1100, description="Lightweight ultrabook with long battery life and fast SSD")
    item4 = Item(name="Samsung Galaxy S24", barcode="444444444444", price=999, description="Samsung flagship phone with 50MP camera and AMOLED display")
    item5 = Item(name="Samsung Galaxy A55", barcode="555555555555", price=450, description="Affordable Samsung phone with solid battery and good screen")
    item6 = Item(name="Standard Tablet", barcode="666666666666", price=420, description="10-inch tablet ideal for browsing, reading, and streaming")
    item7 = Item(name="Pro Tablet", barcode="777777777777", price=650, description="High-end tablet for productivity with stylus support")
    item8 = Item(name="Kids Tablet", barcode="888888888888", price=250, description="Durable tablet with parental controls and educational apps")
    item9 = Item(name="Wireless Headphones", barcode="999999999999", price=180, description="Noise cancelling headphones with bluetooth and long battery life")
    item10 = Item(name="Mechanical Keyboard", barcode="000000000000", price=130, description="RGB mechanical keyboard with customizable keys")

    db.session.add_all([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10])
    db.session.commit()

    print("✓ Items added successfully!")