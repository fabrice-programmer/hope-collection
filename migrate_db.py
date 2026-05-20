import os
import sqlite3

from market import app, db

REQUIRED_ORDER_COLUMNS = [
    ('sector', 'TEXT'),
    ('district', 'TEXT'),
    ('street', 'TEXT'),
    ('location_note', 'TEXT')
]


def get_sqlite_path(database_uri: str) -> str:
    if database_uri.startswith('sqlite:///'):
        return database_uri.replace('sqlite:///', '')
    raise ValueError(f'Unsupported database URI: {database_uri}')


with app.app_context():
    db.create_all()

    database_path = get_sqlite_path(app.config['SQLALCHEMY_DATABASE_URI'])
    if not os.path.exists(database_path):
        raise FileNotFoundError(f'Database file not found: {database_path}')

    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info('order')")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type in REQUIRED_ORDER_COLUMNS:
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE 'order' ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added missing order column: {column_name}")

    connection.commit()
    cursor.close()
    connection.close()

    print(f"Database created/updated successfully at: {database_path}")
