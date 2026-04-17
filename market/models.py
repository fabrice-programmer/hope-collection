from market import db

class user(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.column(db.string(length=50),nullable=False,unique=True)
    password_hash = db.column(db.string(length=68),nullable=False)
    budget = db.column(db.Integer(),nullable=False,)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    barcode = db.Column(db.String(12), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(1024), nullable=False)

    def __repr__(self):
        return f"Item('{self.name}')"

    