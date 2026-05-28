from datetime import datetime, timedelta, timezone
import os
import secrets
import json

from market import app, db
from sqlalchemy import select
from flask import render_template, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user

from market.email_utils import send_email
from market.models import Item, User, TopUpRequest, Order, OrderItem, Transaction, SiteSettings
from market.forms import (
    RegisterForm,
    LoginForm,
    TopUpForm,
    CheckoutForm,
    RequestResetForm,
    ResetPasswordForm,
    TestEmailForm,
    ItemForm,
    SettingsForm
)


# -------------------------
# Helper
# -------------------------
def is_site_owner():
    return current_user.is_authenticated and (current_user.is_admin or current_user.email_address == 'niyonsabafabrice03@gmail.com')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/product_pics', picture_fn)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    form_picture.save(picture_path)
    return picture_fn

def save_video(form_video):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_video.filename)
    video_fn = random_hex + f_ext
    video_path = os.path.join(app.root_path, 'static/product_videos', video_fn)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    
    form_video.save(video_path)
    return video_fn

def save_logo(form_logo):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_logo.filename)
    logo_fn = random_hex + f_ext.lower()
    logo_path = os.path.join(app.root_path, 'static/images/logos', logo_fn)

    os.makedirs(os.path.dirname(logo_path), exist_ok=True)

    form_logo.save(logo_path)
    return f'/static/images/logos/{logo_fn}'

def send_invoice_email(user, order):
    try:
        items_summary = "\n".join([
            f"- {oi.item.name} (x{oi.quantity}): RWF {oi.price * oi.quantity:,}" 
            for oi in order.order_items
        ])
        
        subject = f"Invoice for Your Order #{order.id}"
        message = f"Hello {user.username},\n\n" \
                  f"Your payment for Order #{order.id} has been received and approved.\n\n" \
                  f"Order Details:\n{items_summary}\n" \
                  f"Total Amount Paid: RWF {order.total_price:,}\n\n" \
                  f"Thank you for your purchase!\nBest regards,\nThe Market Team"
        
        sent, error = send_email(user.email_address, subject, message)
        if not sent:
            current_app.logger.warning(f"Invoice email failed for Order {order.id}: {error}")
        return sent, error
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error preparing invoice for Order {order.id}: {error_msg}")
        return False, error_msg

# -------------------------
# ADMIN PRODUCT MANAGEMENT
# -------------------------
@app.route('/admin/items/new', methods=['GET', 'POST'])
@login_required
def add_item():
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))
    
    form = ItemForm()
    if form.validate_on_submit():
        # Manual check for barcode uniqueness for new items
        existing = Item.query.filter_by(barcode=form.barcode.data).first()
        if existing:
            flash('Barcode already exists! Please use a unique barcode.', category='danger')
            return render_template('admin_item_form.html', form=form, title="Add New Product")

        picture_file = 'default.jpg'
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            
        video_file = None
        if form.video.data:
            video_file = save_video(form.video.data)

        item_to_create = Item(
            name=form.name.data,
            price=form.price.data,
            barcode=form.barcode.data,
            description=form.description.data,
            image_file=picture_file,
            video_file=video_file
        )
        db.session.add(item_to_create)
        db.session.commit()
        flash(f'Product "{item_to_create.name}" added successfully!', category='success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_item_form.html', form=form, title="Add New Product")


@app.route('/admin/items/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))
    
    item = db.session.get(Item, item_id)
    if not item:
        flash('Item not found', category='danger')
        return redirect(url_for('admin_dashboard'))

    form = ItemForm(obj=item) # Pre-fill form with existing data
    
    if form.validate_on_submit():
        # Manual check for barcode uniqueness if it changed
        if form.barcode.data != item.barcode:
            existing = Item.query.filter_by(barcode=form.barcode.data).first()
            if existing:
                flash('Barcode already exists on another product.', category='danger')
                return render_template('admin_item_form.html', form=form, title="Edit Product")

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            item.image_file = picture_file

        if form.video.data:
            video_file = save_video(form.video.data)
            item.video_file = video_file

        item.name = form.name.data
        item.price = form.price.data
        item.barcode = form.barcode.data
        item.description = form.description.data
        
        db.session.commit()
        flash(f'Product "{item.name}" updated successfully!', category='success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_item_form.html', form=form, title="Edit Product")


@app.route('/admin/items/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))
    
    item = db.session.get(Item, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('Product deleted successfully.', category='info')
    
    return redirect(url_for('admin_dashboard'))


# -------------------------
# HOME
# -------------------------
@app.route('/')
def home_page():
    featured_items = Item.query.order_by(Item.id.desc()).limit(8).all()
    jewelry_items = Item.query.filter(
        (Item.name.contains('Jewelry')) | 
        (Item.name.contains('Ring')) | 
        (Item.name.contains('Bracelet')) |
        (Item.name.contains('Hairband')) |
        (Item.name.contains('Headband')) |
        (Item.name.contains('Fan'))
    ).all()
    return render_template('home.html', 
                         featured_items=featured_items, 
                         jewelry_items=jewelry_items)


@app.route('/market')
@login_required
def market_page():
    items = Item.query.all()
    return render_template('market.html', items=items)


# -------------------------
# ABOUT PAGE
# -------------------------
@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')


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
        welcome_sent, welcome_error = send_email(
            to=user_to_create.email_address,
            subject='Welcome to Market App',
            message=f"""Hello {user_to_create.username},

Welcome to Market App. Your account has been created successfully.

You can now log in, browse items, and place orders.

Best regards,
The Market Team
"""
        )
        if not welcome_sent:
            current_app.logger.warning('Welcome email was not sent: %s', welcome_error)

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


@app.route('/test-email', methods=['GET', 'POST'])
@login_required
def test_email():
    form = TestEmailForm(
        to=current_user.email_address,
        subject='Flask Email Test',
        message='If you received this, your email system is working!'
    )

    if form.validate_on_submit():
        sent, error_message = send_email(
            to=form.to.data,
            subject=form.subject.data,
            message=form.message.data
        )
        if sent:
            flash(f'Test email sent to {form.to.data}. Check the inbox and spam folder.', category='success')
        else:
            flash(error_message, category='danger')
        return redirect(url_for('test_email'))

    return render_template('test_email.html', form=form)


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
        total_price=total_amount,
        payment_method=form.payment_method.data,
        sector=form.sector.data,
        district=form.district.data,
        street=form.street.data,
        location_note=form.location_note.data,
        status='pending'
    )

    db.session.add(order)
    db.session.flush() # Secure the Order ID before committing

    for item_data in cart:
        order_item = OrderItem(
            order_id=order.id,
            item_id=item_data['id'],
            quantity=item_data['quantity'],
            price=item_data['price']
        )
        db.session.add(order_item)

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


def send_reset_email(user):
    token = user.get_reset_token()
    reset_url = url_for('reset_token', token=token, _external=True)
    subject = 'Reset Your Password'
    message = f"""
Hello {user.username},

A password reset has been requested for your account. Click the link below to set a new password:

{reset_url}

If you did not request this password change, ignore this message. This link expires in 30 minutes.

Best regards,
The Market Team
"""

    sent, error_message = send_email(user.email_address, subject, message)
    if sent:
        flash('A password reset email has been sent. Check your inbox.', 'success')
    return sent, error_message, reset_url


@app.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('market_page'))

    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email_address.data).first()
        if user:
            sent, failure_message, reset_url = send_reset_email(user)
            if not sent:
                show_dev_reset_link = current_app.debug or current_app.config.get('SHOW_RESET_LINK_WHEN_EMAIL_FAIL', False)
                return render_template(
                    'reset_sent.html',
                    email_failed=True,
                    failure_message=failure_message,
                    reset_url=reset_url if show_dev_reset_link else None
                )
        flash('If an account exists for that email, a reset link has been sent.', 'info')
        return redirect(url_for('reset_sent'))

    return render_template('reset_request.html', form=form)


@app.route('/reset-password-sent')
def reset_sent():
    return render_template('reset_sent.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('market_page'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That reset link is invalid or has expired.', 'warning')
        return redirect(url_for('reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password1.data
        db.session.commit()
        flash('Your password has been updated! You can now log in.', 'success')
        return redirect(url_for('login_page'))

    return render_template('reset_token.html', form=form)

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
    items_sold = db.session.query(Item.name, db.func.sum(OrderItem.quantity)).join(OrderItem).group_by(Item.name).all()
    for name, count in items_sold:
        product_counts[name] = count
        
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

        # Send Invoice Email to Customer (Consistency with manage_order)
        user = db.session.get(User, order.user_id)
        if user:
            sent, error = send_invoice_email(user, order)
            if sent:
                flash(f'Order #{order.id} approved and invoice sent to {user.email_address}.', category='success')
            else:
                flash(f'Order approved, but invoice email failed: {error}', category='warning')

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

        # Send Invoice Email to Customer
        user = db.session.get(User, order.user_id)
        if user:
            sent, error = send_invoice_email(user, order)
            if sent:
                flash(f'Order #{order.id} approved and invoice sent to {user.email_address}.', category='success')
            else:
                flash(f'Order approved, but invoice email failed: {error}', category='warning')
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

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if not is_site_owner():
        flash('Admin access only', category='danger')
        return redirect(url_for('market_page'))

    settings = db.session.execute(select(SiteSettings)).scalar_one_or_none()
    if not settings:
        settings = SiteSettings(id=1)
        db.session.add(settings)
        db.session.commit()

    form = SettingsForm(obj=settings)
    if form.validate_on_submit():
        settings.business_name = form.business_name.data
        settings.tagline = form.tagline.data
        if form.logo_file.data:
            settings.logo_url = save_logo(form.logo_file.data)
        settings.meta_description = form.meta_description.data
        settings.whatsapp_number = form.whatsapp_number.data
        settings.contact_email = form.contact_email.data
        settings.business_phone = form.business_phone.data
        settings.business_address = form.business_address.data
        settings.facebook_url = form.facebook_url.data
        settings.instagram_url = form.instagram_url.data
        settings.currency_code = form.currency_code.data
        settings.delivery_fee = form.delivery_fee.data
        settings.about_content = form.about_content.data
        db.session.commit()
        flash('Site settings have been updated!', category='success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_settings.html', form=form, settings=settings, title="Business Settings")
