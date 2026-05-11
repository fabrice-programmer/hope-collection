from market import app, db
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from market.models import Item, User
from market.forms import RegisterForm, LoginForm


@app.route('/users')
def users_page():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/')
def home_page():
    return render_template("home.html")


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template("market.html", items=items)


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

        flash(
            f'Account created successfully! You are now logged in as {user_to_create.username}',
            category='success'
        )

        return redirect(url_for("market_page"))

    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(
                f'There was an error creating a user: {err_msg}',
                category='danger'
            )

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

            flash(
                f'Success! You are logged in as: {attempted_user.username}',
                category="success"
            )

            return redirect(url_for('market_page'))

        else:
            flash(
                'Username and password do not match! Please try again',
                category='danger'
            )

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash('You have been logged out successfully!', category='info')
    return redirect(url_for('home_page'))


@app.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item = Item.query.get(item_id)
    
    if not item:
        flash('Item not found!', category='danger')
        return redirect(url_for('market_page'))
    
    if 'cart' not in session:
        session['cart'] = []
    
    # Check if item already in cart
    cart_item_index = None
    for i, cart_item in enumerate(session['cart']):
        if cart_item['id'] == item_id:
            cart_item_index = i
            break
    
    if cart_item_index is not None:
        # Increase quantity if item already in cart
        session['cart'][cart_item_index]['quantity'] += 1
    else:
        # Add new item to cart
        session['cart'].append({
            'id': item.id,
            'name': item.name,
            'price': item.price,
            'quantity': 1
        })
    
    session.modified = True
    flash(f'{item.name} added to cart!', category='success')
    return redirect(url_for('market_page'))


@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    
    return render_template('cart.html', cart=cart, total_price=total_price)


@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != item_id]
        session.modified = True
        flash('Item removed from cart!', category='info')
    
    return redirect(url_for('view_cart'))


@app.route('/update-cart/<int:item_id>/<int:quantity>')
@login_required
def update_cart(item_id, quantity):
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == item_id:
                if quantity <= 0:
                    session['cart'] = [i for i in session['cart'] if i['id'] != item_id]
                else:
                    item['quantity'] = quantity
                break
        session.modified = True
    
    return redirect(url_for('view_cart'))


@app.route('/checkout')
@login_required
def checkout():
    cart = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    
    if not cart:
        flash('Your cart is empty!', category='warning')
        return redirect(url_for('market_page'))
    
    # Update user budget
    user = current_user
    if user.budget >= total_price:
        user.budget -= total_price
        db.session.commit()
        session['cart'] = []
        session.modified = True
        flash(f'Purchase successful! Total: ${total_price}. Remaining budget: ${user.budget}', category='success')
    else:
        flash(f'Insufficient budget! You need ${total_price - user.budget} more.', category='danger')
    
    return redirect(url_for('market_page'))


@app.route('/clear-cart')
@login_required
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Cart cleared!', category='info')
    return redirect(url_for('view_cart'))