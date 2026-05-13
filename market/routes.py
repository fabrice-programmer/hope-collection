from datetime import datetime
from sqlalchemy.sql import func
import json

from market import app, db
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user

from market.models import Item, User, TopUpRequest, Order
from market.forms import RegisterForm, LoginForm, TopUpForm, CheckoutForm


def is_site_owner():
    return current_user.is_authenticated and current_user.id == 1


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

    if form.errors:
        for err_msg in form.errors.values():
            flash(f'There was an error creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()

    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()

        if attempted_user and attempted_user.check_password_correction(
            attempted_password=form.password.data
        ):
            login_user(attempted_user)
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


@app.route('/update-cart/<int:item_id>/<int:quantity>')
@login_required
def update_cart(item_id, quantity):
    if 'cart' in session:
        for cart_item in session['cart']:
            if cart_item['id'] == item_id:
                if quantity <= 0:
                    session['cart'] = [i for i in session['cart'] if i['id'] != item_id]
                else:
                    cart_item['quantity'] = quantity
                break
        session.modified = True

    return redirect(url_for('view_cart'))


@app.route('/clear-cart')
@login_required
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Cart cleared', category='info')
    return redirect(url_for('view_cart'))


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
    user = current_user

    # Create order record
    order = Order(
        user_id=user.id,
        items=json.dumps(cart),
        total_price=total_price,
        payment_method=method,
        status='pending'
    )
    db.session.add(order)
    db.session.commit()

    if method == 'wallet':
        if user.budget >= total_price:
            user.budget -= total_price
            order.status = 'completed'
            db.session.commit()
            session['cart'] = []
            session.modified = True
            flash(f'Payment successful: RWF {total_price}', category='success')
        else:
            flash('Insufficient balance', category='danger')
            return redirect(url_for('view_cart'))
    else:
        session['cart'] = []
        session.modified = True
        destination = ('MTN Mobile Money 0789174857' if method == 'mtn' else 'Equity Bank 4002100815300')
        flash(f'Order placed. Pay RWF {total_price} via {destination}', category='success')

    return redirect(url_for('market_page'))


@app.route('/top-up', methods=['GET', 'POST'])
@login_required
def top_up():
    form = TopUpForm()

    if form.validate_on_submit():
        top_up_request = TopUpRequest(
            user_id=current_user.id,
            amount=form.amount.data,
            method=form.payment_method.data,
            status='pending'
        )

        db.session.add(top_up_request)
        db.session.commit()

        return redirect(url_for('top_up_confirmation', request_id=top_up_request.id))

    return render_template('top_up.html', form=form)


@app.route('/top-up-confirmation/<int:request_id>')
@login_required
def top_up_confirmation(request_id):
    req = TopUpRequest.query.get_or_404(request_id)

    if req.user_id != current_user.id:
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    return render_template('top_up_confirmation.html', request=req)


@app.route('/top-up-requests')
@login_required
def top_up_requests():
    if not is_site_owner():
        flash('Admin only', category='danger')
        return redirect(url_for('market_page'))

    requests = TopUpRequest.query.order_by(TopUpRequest.id.desc()).all()
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


@app.route('/manage_order/<int:order_id>/<action>')
@login_required
def manage_order(order_id, action):
    if not is_site_owner():
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    order = Order.query.get_or_404(order_id)

    if action == 'approve':
        order.status = 'approved'
        order.approved_at = datetime.utcnow()
        order.approver_id = current_user.id
        db.session.commit()
        flash('Order approved successfully', category='success')
    elif action == 'decline':
        order.status = 'cancelled'
        order.approved_at = datetime.utcnow()
        order.approver_id = current_user.id
        db.session.commit()
        flash('Order declined', category='warning')
    elif action == 'complete':
        order.status = 'completed'
        db.session.commit()
        flash('Order marked as completed', category='success')

    return redirect(url_for('admin_dashboard'))

@app.route('/my-top-ups')
@login_required
def my_top_ups():
    requests = TopUpRequest.query.filter_by(user_id=current_user.id).order_by(TopUpRequest.id.desc()).all()
    return render_template('my_top_ups.html', requests=requests)

@app.route('/admin')
@login_required
def admin_dashboard():

    if not is_site_owner():
        flash('Access denied', category='danger')
        return redirect(url_for('market_page'))

    users = User.query.all()
    items = Item.query.all()
    requests = TopUpRequest.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    pending_requests = TopUpRequest.query.filter_by(status='pending').count()
    pending_orders = Order.query.filter_by(status='pending').count()

    # Parse order items from JSON
    for order in orders:
        try:
            order.parsed_items = json.loads(order.items)
        except:
            order.parsed_items = []

    return render_template(
        'admin.html',
        users=users,
        items=items,
        requests=requests,
        orders=orders,
        pending_requests=pending_requests,
        pending_orders=pending_orders
    )