from datetime import datetime
from sqlalchemy.sql import func
import json

from market import app, db
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user

from market.models import Item, User, TopUpRequest, Order
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


@app.route('/users')
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)


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
    item = Item.query.get(item_id)

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
# CHECKOUT
# -------------------------
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart = session.get('cart', [])
    form = CheckoutForm()

    if not cart:
        flash('Cart is empty', category='warning')
        return redirect(url_for('market_page'))

    if not form.validate_on_submit():
        flash('Select payment method', category='danger')
        return redirect(url_for('view_cart'))

    total_price = sum(i['price'] * i['quantity'] for i in cart)
    method = form.payment_method.data

    order = Order(
        user_id=current_user.id,
        items=json.dumps(cart),
        total_price=total_price,
        payment_method=method,
        status='pending'
    )

    db.session.add(order)
    db.session.commit()

    session['cart'] = []
    session.modified = True

    flash('Order placed successfully', category='success')
    return redirect(url_for('market_page'))


# -------------------------
# TOP UPS
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
    req = TopUpRequest.query.get_or_404(request_id)

    if req.user_id != current_user.id:
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    return render_template('top_up_confirmation.html', request=req)


@app.route('/my-top-ups')
@login_required
def my_top_ups():
    requests = TopUpRequest.query.filter_by(user_id=current_user.id).order_by(TopUpRequest.id.desc()).all()
    return render_template('my_top_ups.html', requests=requests)


@app.route('/top-up-requests')
@login_required
def top_up_requests():
    if not is_site_owner():
        flash('Admin only', category='danger')
        return redirect(url_for('market_page'))

    requests = TopUpRequest.query.order_by(TopUpRequest.created_at.desc()).all()
    return render_template('top_up_requests.html', requests=requests)


@app.route('/top-up-request/<int:request_id>/<action>')
@login_required
def manage_top_up_request(request_id, action):
    if not is_site_owner():
        flash('Admin only', category='danger')
        return redirect(url_for('market_page'))

    req = TopUpRequest.query.get_or_404(request_id)

    if action == 'approve':
        user = User.query.get(req.user_id)
        user.budget += req.amount
        req.status = 'approved'
        req.reviewed_at = func.now()
        req.reviewer_id = current_user.id
        flash('Approved successfully', category='success')
    elif action == 'decline':
        req.status = 'declined'
        req.reviewed_at = func.now()
        req.reviewer_id = current_user.id
        flash('Declined', category='info')
    else:
        flash('Unknown action', category='danger')

    db.session.commit()
    return redirect(url_for('top_up_requests'))


# -------------------------
# ADMIN DASHBOARD (ONLY ONE)
# -------------------------
@app.route('/admin')
@login_required
def admin_dashboard():

    if not is_site_owner():
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    users = User.query.all()
    items = Item.query.all()
    requests = TopUpRequest.query.all()

    # IMPORTANT: always load user relationship + safe ordering
    orders = Order.query.order_by(Order.id.desc()).all()

    # ensure parsed items exist
    for order in orders:
        try:
            order.parsed_items = json.loads(order.items)
        except:
            order.parsed_items = []

    # stats
    pending_orders = Order.query.filter_by(status='pending').count()
    pending_requests = TopUpRequest.query.filter_by(status='pending').count()

    total_revenue = sum(o.total_price for o in orders)
    total_orders = len(orders)
    total_customers = len(set(o.user_id for o in orders)) if orders else 0

    # charts
    product_sales = {}

    for order in orders:
        for item in order.parsed_items:
            name = item.get("name", "Unknown")
            qty = item.get("quantity", 0)
            product_sales[name] = product_sales.get(name, 0) + qty

    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

    top_product_labels = [x[0] for x in top_products] or ["A", "B", "C"]
    top_product_values = [x[1] for x in top_products] or [10, 20, 30]

    monthly_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    monthly_sales = [0, 0, 0, 0, total_revenue, 0]

    return render_template(
        'admin_dashboard.html',
        users=users,
        items=items,
        requests=requests,
        orders=orders,
        recent_orders=orders[:10],
        pending_orders=pending_orders,
        pending_requests=pending_requests,
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        conversion_rate=4.5,
        revenue_change_text="Revenue updated",
        monthly_labels=monthly_labels,
        monthly_sales=monthly_sales,
        top_product_labels=top_product_labels,
        top_product_values=top_product_values
    )
# ORDER MANAGEMENT
# -------------------------
@app.route('/manage_order/<int:order_id>/<action>')
@login_required
def manage_order(order_id, action):

    if not is_site_owner():
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    order = Order.query.get_or_404(order_id)

    if action == 'approve':
        order.status = 'approved'
    elif action == 'decline':
        order.status = 'cancelled'
    elif action == 'complete':
        order.status = 'completed'

    db.session.commit()
    flash('Order updated', category='success')

    return redirect(url_for('admin_dashboard'))


# -------------------------
# SIMPLE ORDER VIEW
# -------------------------
@app.route('/admin/orders')
@login_required
def admin_orders():

    if not is_site_owner():
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    orders = Order.query.all()

    return render_template('admin_orders.html', orders=orders)


@app.route('/confirm-order/<int:id>')
@login_required
def confirm_order(id):

    order = Order.query.get_or_404(id)
    order.status = 'Confirmed'

    db.session.commit()

    return redirect(url_for('admin_orders'))