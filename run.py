import os
from market import app, db
from market.models import *

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    # Use PORT environment variable provided by Render
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)