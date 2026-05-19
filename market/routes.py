from datetime import datetime, timezone
import json

from market import app, db
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from market.models import Item, User, TopUpRequest, Order, Transaction
from market.forms import RegisterForm, LoginForm, TopUpForm, CheckoutForm


# -------------------------
# Helper
# -------------------------
def is_site_owner():
    return current_user.is_authenticated and current_user.id == 1


# -------------------------
# HOME
# -------------------------
@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)


# -------------------------
# AUTH
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()

    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data
        )

        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Welcome {user_to_create.username}', category='success')
        return redirect(url_for('market_page'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password_correction(form.password.data):
            login_user(user)
            flash('Login successful!', category='success')
            return redirect(url_for('market_page'))

        flash('Invalid username or password', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('Logged out successfully', category='info')
    return redirect(url_for('home_page'))


# -------------------------
# CART SYSTEM
# -------------------------
@app.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item = db.session.get(Item, item_id)

    if not item:
        flash('Item not found', category='danger')
        return redirect(url_for('market_page'))

    if 'cart' not in session:
        session['cart'] = []

    for cart_item in session['cart']:
        if cart_item['id'] == item_id:
            cart_item['quantity'] += 1
            break
    else:
        session['cart'].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'quantity': 1
        })

    session.modified = True
    flash('Item added to cart', category='success')
    return redirect(url_for('market_page'))


@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(i['price'] * i['quantity'] for i in cart)
    form = CheckoutForm()
    return render_template('cart.html', cart=cart, total_price=total_price, form=form)


@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [i for i in session['cart'] if i['id'] != item_id]
        session.modified = True

    flash('Item removed', category='info')
    return redirect(url_for('view_cart'))


@app.route('/clear-cart')
@login_required
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Cart cleared', category='info')
    return redirect(url_for('view_cart'))


# -------------------------
# UPDATE CART QUANTITY
# -------------------------
@app.route('/update-cart/<int:item_id>/<int:quantity>')
@login_required
def update_cart(item_id, quantity):

    if 'cart' not in session:
        flash('Cart is empty', category='warning')
        return redirect(url_for('view_cart'))

    for cart_item in session['cart']:
        if cart_item['id'] == item_id:
            if quantity <= 0:
                session['cart'] = [i for i in session['cart'] if i['id'] != item_id]
                flash('Item removed from cart', category='info')
            else:
                cart_item['quantity'] = quantity
                flash('Cart updated successfully', category='success')

            session.modified = True
            break

    return redirect(url_for('view_cart'))


# -------------------------
# CHECKOUT (FIXED - NO DUPLICATES, NO ERRORS)
# -------------------------
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    form = CheckoutForm()
    cart = session.get('cart', [])

    if not cart:
        flash('Cart is empty', category='warning')
        return redirect(url_for('market_page'))

    if not form.validate_on_submit():
        flash('Please select a payment method before checking out.', category='warning')
        return redirect(url_for('view_cart'))

    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    order = Order(
        user_id=current_user.id,
        items=json.dumps(cart),
        total_price=total_amount,
        payment_method=form.payment_method.data,
        status='pending'
    )

    db.session.add(order)

    new_transaction = Transaction(
        user_id=current_user.id,
        amount=total_amount,
        transaction_type='Order',
        status='pending'
    )

    db.session.add(new_transaction)
    db.session.commit()

    session['cart'] = []
    session.modified = True

    flash('Order placed successfully!', 'success')
    return redirect(url_for('transaction_history'))


# -------------------------
# TOP UPS (UNCHANGED)
# -------------------------
@app.route('/top-up', methods=['GET', 'POST'])
@login_required
def top_up():
    form = TopUpForm()

    if form.validate_on_submit():
        req = TopUpRequest(
            user_id=current_user.id,
            amount=form.amount.data,
            method=form.payment_method.data,
            status='pending'
        )

        db.session.add(req)
        db.session.commit()

        return redirect(url_for('top_up_confirmation', request_id=req.id))

    return render_template('top_up.html', form=form)


@app.route('/top-up-confirmation/<int:request_id>')
@login_required
def top_up_confirmation(request_id):
    topup_request = db.session.get(TopUpRequest, request_id)

    if topup_request is None:
        flash('Request not found', category='danger')
        return redirect(url_for('market_page'))

    if topup_request.user_id != current_user.id:
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    return render_template('top_up_confirmation.html', topup_request=topup_request)


@app.route('/my-top-ups')
@login_required
def my_top_ups():
    requests = TopUpRequest.query.filter_by(user_id=current_user.id).order_by(TopUpRequest.id.desc()).all()
    return render_template('my_top_ups.html', requests=requests)


@app.route('/transaction-history')
@login_required
def transaction_history():
    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).all()

    return render_template('transaction_history.html', transactions=transactions)