import os
from market import app, db

# -----------------------------
# Fix DATABASE URL (Render fix)
# -----------------------------
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Render gives postgres:// but SQLAlchemy needs postgresql+psycopg2://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url


# Optional safety config

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# -----------------------------
# Create tables on startup
# -----------------------------
with app.app_context():
    db.create_all()
    print("✅ Database tables checked/created successfully")


# -----------------------------
# Run app locally only
# (Render uses gunicorn, NOT this)
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)