#!/usr/bin/env python3
"""Test script to verify all imports and app configuration."""

try:
    from market import app, db
    from market.models import User, Item, TopUpRequest, Order, OrderItem, Transaction, SiteSettings
    from market.forms import (
        RegisterForm,
        LoginForm,
        TopUpForm,
        CheckoutForm,
        RequestResetForm,
        ResetPasswordForm,
        TestEmailForm,
    )

    print('OK: All imports successful')
    print('OK: App initialized')
    print('OK: All models loaded')
    print('OK: All forms loaded')
    print()
    print('Flask App Configuration:')
    print(f'  - Database: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    print(f'  - Debug Mode: {app.debug}')
    print(f'  - Session Type: {app.config["SESSION_TYPE"]}')
    print(f'  - Mail Server: {app.config["MAIL_SERVER"]}')
    print(f'  - Mail Username Loaded: {bool(app.config["MAIL_USERNAME"])}')
    print(f'  - Mail Password Loaded: {bool(app.config["MAIL_PASSWORD"])}')
    print()
    print('Routes available:')
    for rule in app.url_map.iter_rules():
        print(f'  - {rule.endpoint}: {rule.rule}')

except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
