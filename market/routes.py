from datetime import datetime, timedelta, timezone
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
        sector=form.sector.data,
        district=form.district.data,
        street=form.street.data,
        location_note=form.location_note.data,
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
# LEGACY TOP-UP ROUTES
# -------------------------
@app.route('/top-up', methods=['GET', 'POST'])
@login_required
def top_up():
    flash('Use the order summary on the cart page to proceed with payment and review your order details.', category='info')
    return redirect(url_for('view_cart'))


@app.route('/top-up-confirmation/<int:request_id>')
@login_required
def top_up_confirmation(request_id):
    flash('Payment confirmation has moved to the order summary flow. Review your cart to proceed.', category='info')
    return redirect(url_for('view_cart'))


@app.route('/my-top-ups')
@login_required
def my_top_ups():
    flash('Payment request tracking is now handled through your transaction history.', category='info')
    return redirect(url_for('transaction_history'))


@app.route('/transaction-history')
@login_required
def transaction_history():
    orders = Order.query.filter_by(user_id=current_user.id)\
        .order_by(Order.created_at.desc()).all()

    transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.created_at.desc()).all()

    return render_template(
        'transaction_history.html',
        orders=orders,
        transactions=transactions
    )

# -------------------------
# ADMIN
# -------------------------
@app.route('/admin')
@login_required
def admin_dashboard():
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))

    users = User.query.order_by(User.username).all()
    items = Item.query.order_by(Item.name).all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    requests = Order.query.filter_by(status='pending').order_by(Order.created_at.desc()).all()

    pending_orders = Order.query.filter_by(status='pending').count()
    pending_requests = pending_orders
    total_customers = User.query.count()
    total_items = Item.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.coalesce(db.func.sum(Order.total_price), 0)).scalar() or 0

    now = datetime.now(timezone.utc)
    monthly_labels = []
    monthly_sales = []
    for months_back in range(5, -1, -1):
        month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        target_month = month_start - timedelta(days=months_back * 30)
        label = target_month.strftime('%b %Y')
        month_end = datetime(target_month.year, target_month.month, 1, tzinfo=timezone.utc) + timedelta(days=32)
        month_end = month_end.replace(day=1)
        sales = db.session.query(db.func.coalesce(db.func.sum(Order.total_price), 0)).filter(
            Order.created_at >= target_month,
            Order.created_at < month_end
        ).scalar() or 0
        monthly_labels.append(label)
        monthly_sales.append(int(sales))

    product_counts = {}
    for order in Order.query.all():
        try:
            items_data = json.loads(order.items)
        except (TypeError, ValueError):
            continue
        for item in items_data:
            product_counts[item.get('name', 'Unknown')] = product_counts.get(item.get('name', 'Unknown'), 0) + item.get('quantity', 0)

    top_products = sorted(product_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]
    top_product_labels = [label for label, _ in top_products]
    top_product_values = [value for _, value in top_products]

    conversion_rate = round((total_orders / max(total_customers, 1)) * 100, 1) if total_customers else 0
    revenue_change_text = 'Steady performance' if total_revenue else 'No revenue yet'

    return render_template(
        'admin_dashboard.html',
        users=users,
        items=items,
        requests=requests,
        orders=orders,
        recent_orders=recent_orders,
        pending_orders=pending_orders,
        pending_requests=pending_requests,
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_customers=total_customers,
        total_items=total_items,
        conversion_rate=conversion_rate,
        revenue_change_text=revenue_change_text,
        monthly_labels=monthly_labels,
        monthly_sales=monthly_sales,
        top_product_labels=top_product_labels,
        top_product_values=top_product_values
    )


@app.route('/admin/top-up-requests')
@login_required
def top_up_requests():
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))

    orders = Order.query.filter_by(status='pending').order_by(Order.created_at.desc()).all()
    return render_template('top_up_requests.html', orders=orders)


@app.route('/admin/top-up-requests/<int:order_id>/<action>')
@login_required
def manage_top_up_request(order_id, action):
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))

    order = db.session.get(Order, order_id)
    if order is None:
        flash('Payment request not found', category='danger')
        return redirect(url_for('top_up_requests'))

    if order.status != 'pending':
        flash('This request has already been processed.', category='info')
        return redirect(url_for('top_up_requests'))

    if action == 'approve':
        order.status = 'approved'
        order.approved_at = datetime.now(timezone.utc)
        order.approver_id = current_user.id
        transaction = Transaction.query.filter_by(
            user_id=order.user_id,
            amount=order.total_price,
            transaction_type='Order'
        ).order_by(Transaction.id.desc()).first()
        if transaction:
            transaction.status = 'approved'
        flash(f'Payment request for Order #{order.id} approved.', category='success')
    elif action == 'decline':
        order.status = 'cancelled'
        order.approved_at = datetime.now(timezone.utc)
        order.approver_id = current_user.id
        flash(f'Payment request for Order #{order.id} declined.', category='warning')
    else:
        flash('Invalid action.', category='danger')
        return redirect(url_for('top_up_requests'))

    db.session.commit()
    return redirect(url_for('top_up_requests'))


@app.route('/admin/orders/<int:order_id>/<action>')
@login_required
def manage_order(order_id, action):
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))

    order = db.session.get(Order, order_id)
    if order is None:
        flash('Order not found.', category='danger')
        return redirect(url_for('admin_dashboard'))

    if action == 'approve' and order.status == 'pending':
        order.status = 'approved'
        order.approved_at = datetime.now(timezone.utc)
        order.approver_id = current_user.id
        transaction = Transaction.query.filter_by(
            user_id=order.user_id,
            amount=order.total_price,
            transaction_type='Order'
        ).order_by(Transaction.id.desc()).first()
        if transaction:
            transaction.status = 'approved'
        flash(f'Order #{order.id} approved.', category='success')
    elif action == 'decline' and order.status == 'pending':
        order.status = 'cancelled'
        order.approved_at = datetime.now(timezone.utc)
        order.approver_id = current_user.id
        flash(f'Order #{order.id} declined.', category='warning')
    elif action == 'complete' and order.status == 'approved':
        order.status = 'completed'
        transaction = Transaction.query.filter_by(
            user_id=order.user_id,
            amount=order.total_price,
            transaction_type='Order'
        ).order_by(Transaction.id.desc()).first()
        if transaction:
            transaction.status = 'completed'
        flash(f'Order #{order.id} marked completed.', category='success')
    else:
        flash('Invalid order action or order state.', category='danger')
        return redirect(url_for('admin_dashboard'))

    db.session.commit()
    return redirect(url_for('admin_dashboard'))
