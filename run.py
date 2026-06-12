from market import db, app
from market.models import *

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
