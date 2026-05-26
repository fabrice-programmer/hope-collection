import os
import sqlite3
from market import app, db

REQUIRED_ORDER_COLUMNS = [
    ('payment_method', "VARCHAR(20) NOT NULL DEFAULT ''"), # Added NOT NULL DEFAULT for existing rows
    ('sector', 'TEXT'),
    ('district', 'TEXT'),
    ('street', 'TEXT'),
    ('location_note', 'TEXT'),
    ('status', "VARCHAR(20) DEFAULT 'pending'"),
    ('approved_at', 'DATETIME'),
    ('approver_id', 'INTEGER')
]

REQUIRED_ITEM_COLUMNS = [
    ('image_file', "VARCHAR(20) NOT NULL DEFAULT 'default.jpg'"),
    ('video_file', "VARCHAR(20)")
]


def get_sqlite_path(database_uri: str) -> str:
    if database_uri.startswith('sqlite:///'):
        return database_uri.replace('sqlite:///', '')
    raise ValueError(f'Unsupported database URI: {database_uri}')


def migrate_table_columns(cursor, table_name, required_columns):
    """Add missing columns safely."""
    cursor.execute(f'PRAGMA table_info("{table_name}")')
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type in required_columns:
        if column_name not in existing_columns:
            try:
                cursor.execute(
                    f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_type}'
                )
                print(f"Added missing {table_name} column: {column_name}")
            except Exception as e:
                print(f"Failed adding {column_name} to {table_name}: {e}")


def run_migrations():
    """Execute the database migration logic."""
    with app.app_context():
        database_path = get_sqlite_path(app.config['SQLALCHEMY_DATABASE_URI'])
        print(database_path)

        os.makedirs(os.path.dirname(database_path), exist_ok=True)

        db.create_all()

        if not os.path.exists(database_path):
            raise FileNotFoundError(f'Database file not found: {database_path}')

        connection = None
        cursor = None

        try:
            connection = sqlite3.connect(database_path)
            cursor = connection.cursor()

            # Match table names defined in models.py (__tablename__)
            migrate_table_columns(cursor, "orders", REQUIRED_ORDER_COLUMNS) # For Order model
            migrate_table_columns(cursor, "item", REQUIRED_ITEM_COLUMNS)

            connection.commit()

        except Exception as e:
            print(f"Migration failed: {e}")
            try:
                if connection: connection.rollback()
            except: pass

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        print(f"Database creation/update finished: {database_path}")

if __name__ == "__main__":
    run_migrations()