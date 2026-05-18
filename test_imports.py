#!/usr/bin/env python3
"""Test script to verify all imports and app configuration."""

try:
    from market import app, db
    from market.models import User, Item, TopUpRequest, Order
    from market.forms import RegisterForm, LoginForm, TopUpForm, CheckoutForm
    
    print('✓ All imports successful')
    print('✓ App initialized')
    print('✓ All models loaded')
    print('✓ All forms loaded')
    print()
    print('Flask App Configuration:')
    print(f'  - Database: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    print(f'  - Debug Mode: {app.debug}')
    print(f'  - Session Type: {app.config["SESSION_TYPE"]}')
    print()
    print('Routes available:')
    for rule in app.url_map.iter_rules():
        print(f'  - {rule.endpoint}: {rule.rule}')
    
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
