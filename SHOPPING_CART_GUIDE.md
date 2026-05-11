# Shopping Cart System - Setup & Usage Guide

## What's New ✨

Your Flask app now has a complete shopping cart system with:
- ✅ 6 items in the database (Laptop, Phone, Tablet, Headphones, Monitor, Keyboard)
- ✅ Add items to cart with one click
- ✅ View full shopping cart
- ✅ Adjust item quantities (increase/decrease)
- ✅ Remove items from cart
- ✅ Calculate total price
- ✅ Checkout with budget validation
- ✅ Real-time cart updates in navbar and sidebar

## Quick Start

### Step 1: Reset Database
Delete the old database and recreate it:
```bash
# Delete old database
rm instance/database.db

# Create new database with items
python create_db.py
python add_items.py
```

### Step 2: Run the Application
```bash
python run.py
```

### Step 3: Access the App
Open your browser and go to: `http://localhost:5000`

## How to Use

### Register/Login
1. Click "Register" and create an account
2. Each new user starts with **$1000 budget**
3. Login with your credentials

### Shopping Flow
1. **View Market**: Navigate to the Market page (requires login)
2. **Add Items**: Click "🛒 Add to Cart" on any item
3. **Quick Summary**: See cart preview in the right sidebar
4. **View Full Cart**: Click the cart icon in navbar to see detailed cart
5. **Adjust Quantities**: Use +/- buttons to change item quantities
6. **Remove Items**: Click the trash icon to remove items
7. **Checkout**: Click "Proceed to Checkout" to finalize purchase

### Checkout Process
- App checks if you have enough budget
- If YES: Purchase completes, budget is deducted, cart clears
- If NO: Shows how much more you need

## Features

### Cart Sidebar (Market Page)
- Shows number of items in cart
- Lists all items with quantities
- Displays running total
- Quick checkout button
- Shows your remaining budget

### Full Cart Page (`/cart`)
- Detailed item table
- Quantity adjustment controls
- Remove individual items
- Budget validation
- Order summary panel

### Real-Time Updates
- Cart count badge in navbar updates instantly
- Sidebar updates when items are added
- Budget display updates after checkout

## Database Items

| Name | Price | Description |
|------|-------|-------------|
| Laptop | $800 | High-performance laptop with Intel i7, 16GB RAM, 512GB SSD |
| Phone | $500 | Latest smartphone with 5G connectivity |
| Tablet | $400 | 10-inch tablet for reading and multimedia |
| Headphones | $150 | Wireless noise-cancelling headphones |
| Monitor | $350 | 27-inch 4K monitor with 144Hz refresh rate |
| Keyboard | $120 | Mechanical gaming keyboard with RGB lighting |

## File Structure

```
market/
├── routes.py                 # Added cart routes
├── __init__.py              # Updated with session config
├── templates/
│   ├── base.html            # Updated with cart navbar
│   ├── market.html          # New card-based layout
│   ├── cart.html            # NEW: Shopping cart page
│   ├── login.html
│   ├── register.html
│   └── ...
├── models.py
└── forms.py

add_items.py                  # Updated with 6 items
```

## Routes

| Route | Method | Auth | Purpose |
|-------|--------|------|---------|
| `/` | GET | No | Home page |
| `/market` | GET | Yes | Market with items |
| `/add-to-cart/<id>` | GET | Yes | Add item to cart |
| `/cart` | GET | Yes | View shopping cart |
| `/remove-from-cart/<id>` | GET | Yes | Remove item |
| `/update-cart/<id>/<qty>` | GET | Yes | Update quantity |
| `/checkout` | GET | Yes | Complete purchase |
| `/clear-cart` | GET | Yes | Empty cart |

## Session Management

- Cart items stored in Flask session (not database)
- Cart persists during login session
- Cart clears on logout
- Cart clears after checkout

## Tips & Tricks

### Add More Items
Edit `add_items.py` and add new Item objects:
```python
item7 = Item(
    name="Mouse", 
    barcode="777777777777", 
    price=50, 
    description="Wireless mouse with precision tracking"
)
db.session.add(item7)
```

### Change Starting Budget
Edit `market/models.py` in User model:
```python
budget = db.Column(db.Integer, nullable=False, default=5000)  # Change 1000 to 5000
```

### Customize Item Card Style
Edit `market/templates/market.html` - modify the card styling with Bootstrap classes

## Troubleshooting

### Cart Not Persisting
- Make sure `SESSION_TYPE` is set in `__init__.py`
- Clear browser cookies and try again

### Checkout Not Working
- Check if you have enough budget
- Verify database connections
- Check browser console for errors

### Items Not Showing
```bash
# Re-run add_items.py
python add_items.py
```

### Database Lock Issues
```bash
# Delete and recreate database
rm instance/database.db
python create_db.py
python add_items.py
```

## Next Steps (Optional Enhancements)

- Add product images
- Implement wishlists
- Add order history
- Email confirmation on purchase
- Discount codes
- Quantity discounts
- Payment gateway integration
- Admin panel for item management
