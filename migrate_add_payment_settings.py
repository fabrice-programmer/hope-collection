"""
Migration: Add payment_methods JSON field to SiteSettings
"""
import sqlite3
import json
import os

# Find the database
db_path = None
possible_paths = [
    'market/../instance/database.db',
    'instance/database.db',
    'market.db',
    'your_database.db'
]

for p in possible_paths:
    normalized = os.path.normpath(os.path.join(os.path.dirname(__file__), p))
    if os.path.exists(normalized):
        db_path = normalized
        break

if not db_path:
    print("Could not find database!")
    exit(1)

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Check if column already exists
cur.execute("PRAGMA table_info(site_settings)")
columns = [col[1] for col in cur.fetchall()]

if 'payment_methods' not in columns:
    # Add the payment_methods column (without DEFAULT to avoid SQL quoting issues)
    cur.execute("ALTER TABLE site_settings ADD COLUMN payment_methods TEXT")
    # Set default value for existing rows
    default_methods = json.dumps([
        {"id": "wallet", "name": "Wallet Balance", "enabled": True},
        {"id": "mtn", "name": "MTN Mobile Money", "enabled": True},
        {"id": "equity", "name": "Equity Bank Transfer", "enabled": True}
    ])
    cur.execute("UPDATE site_settings SET payment_methods = ? WHERE payment_methods IS NULL", (default_methods,))
    conn.commit()
    print("Added 'payment_methods' column to site_settings table.")
else:
    print("Column 'payment_methods' already exists.")

conn.close()
print("Migration complete!")