from market import app, db
from market.models import User, Item

with app.app_context():
    db.create_all()
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email_address='test@example.com')
        user.password = 'password123'
        db.session.add(user)
        db.session.commit()
        print('created user', user.id)
    else:
        print('existing user', user.id)

    item = Item.query.first()
    if not item:
        item = Item(name='Test Item', price=100, barcode='123456789012', description='Test item desc')
        db.session.add(item)
        db.session.commit()
        print('created item', item.id)
    else:
        print('existing item', item.id)

    client = app.test_client()
    with client.session_transaction() as sess:
        sess['cart'] = [{'id': item.id, 'name': item.name, 'price': item.price, 'quantity': 1}]
        sess['_user_id'] = str(user.id)

    response = client.post('/checkout', data={'payment_method': 'mtn'}, follow_redirects=False)
    print('checkout status', response.status_code)
    print('location', response.headers.get('Location'))
