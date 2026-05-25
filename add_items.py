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
    item11 = Item(name="Mini Fan", barcode="123456789012", price=15000, description="Stay cool anywhere with this portable high-speed mini fan. Reach us at 0791641207 or 0722451953.")
    item12 = Item(name="Jewelry Set", barcode="234567890123", price=8000, description="A stunning jewelry set designed to add elegance to any outfit.")
    item13 = Item(name="Ring Collection", barcode="345678901234", price=6000, description="Modern and classic rings in various sizes and styles.")
    item14 = Item(name="Stainless Bracelet", barcode="456789012345", price=5000, description="Minimalist stainless steel bracelet that never fades.")
    item15 = Item(name="Silk Hairband", barcode="567890123456", price=3000, description="Soft silk hairbands in multiple colors, perfect for any hairstyle.")
    item16 = Item(name="Gold Plated Necklace", barcode="678901234567", price=12000, description="Elegant gold-plated necklace with a minimalist pendant.")
    item17 = Item(name="Pearl Headband", barcode="789012345678", price=4500, description="Luxury pearl-encrusted headband for special occasions.")
    item18 = Item(name="Portable Handheld Fan", barcode="890123456789", price=10000, description="Powerful yet quiet handheld fan with 3 speed settings.")

    db.session.add_all([item1, item2, item3, item4, item5, item6, item7, item8, item9, item10, 
                        item11, item12, item13, item14, item15, item16, item17, item18])
    db.session.commit()

    print("✓ Items added successfully!")