import json
from datetime import datetime, timedelta, timezone
from market import db, bcrypt, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # ✅ FIXED: replaced deprecated User.query.get()


# -------------------------
# USER
# -------------------------
class User(db.Model, UserMixin):  # ✅ FIXED: only ONE User class (merged both into this one)
    __tablename__ = 'user'

    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(100), nullable=False, unique=True)
    email_address    = db.Column(db.String(120), nullable=False, unique=True)
    password_hash    = db.Column(db.String(200), nullable=False)
    budget           = db.Column(db.Integer, nullable=False, default=1000)

    # Relationships
    items            = db.relationship('Item', backref='owned_user', lazy=True)
    top_up_requests  = db.relationship(
                            'TopUpRequest',
                            backref='requester',           # ✅ FIXED: renamed backref to avoid clash with Transaction backref 'user'
                            lazy=True,
                            foreign_keys='TopUpRequest.user_id'
                        )
    transactions     = db.relationship('Transaction', backref='user', lazy=True)  # ✅ FIXED: moved here from duplicate class

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute!')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(
            plain_text_password
        ).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(
            self.password_hash, attempted_password
        )

    def __repr__(self):
        return f"User('{self.username}')"


# -------------------------
# ITEM
# -------------------------
class Item(db.Model):
    __tablename__ = 'item'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(30), nullable=False)
    price       = db.Column(db.Integer, nullable=False)
    barcode     = db.Column(db.String(12), nullable=False)
    description = db.Column(db.String(1024), nullable=False, unique=True)
    owner       = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Item('{self.name}')"


# -------------------------
# TOP UP REQUEST
# -------------------------
class TopUpRequest(db.Model):
    __tablename__ = 'top_up_request'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount      = db.Column(db.Integer, nullable=False)
    method      = db.Column(db.String(20), nullable=False)
    status      = db.Column(db.String(20), nullable=False, default='pending')
    created_at  = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))   # ✅ FIXED: utcnow() deprecated
    expires_at  = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(hours=24))
    reviewed_at = db.Column(db.DateTime)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', foreign_keys=[user_id], overlaps='requester,top_up_requests')

    def __repr__(self):
        return f"TopUpRequest(user_id={self.user_id}, amount={self.amount}, status={self.status})"


# -------------------------
# ORDER
# -------------------------
class Order(db.Model):
    __tablename__ = 'order'

    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items          = db.Column(db.Text, nullable=False)       # JSON string of cart items
    total_price    = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    sector         = db.Column(db.String(100), nullable=False)
    district       = db.Column(db.String(100), nullable=False)
    street         = db.Column(db.String(100), nullable=False)
    location_note  = db.Column(db.String(255), nullable=True)
    status         = db.Column(db.String(20), nullable=False, default='pending')  # pending | approved | completed | cancelled
    created_at     = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))  # ✅ FIXED: utcnow() deprecated
    approved_at    = db.Column(db.DateTime)
    approver_id    = db.Column(db.Integer, db.ForeignKey('user.id'))

    user     = db.relationship('User', foreign_keys=[user_id],     backref='orders')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_orders')

    @property
    def parsed_items(self):
        try:
            return json.loads(self.items)
        except (TypeError, ValueError):
            return []

    def __repr__(self):
        return f"Order(user_id={self.user_id}, total={self.total_price}, status={self.status})"


# -------------------------
# TRANSACTION
# -------------------------
class Transaction(db.Model):
    __tablename__ = 'transaction'

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount           = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    status           = db.Column(db.String(20), default='pending')
    created_at       = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # ✅ FIXED: utcnow() deprecated

    def __repr__(self):
        return f'<Transaction {self.id}>'