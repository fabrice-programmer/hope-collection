from market import app
from flask import render_template
from market.models import Item, User
from market.forms import RegisterForm


@app.route('/')
def home_page():
    return render_template("home.html")


@app.route('/market')
def market_page():
    items = Item.query.all()
    return render_template("market.html", items=items)


@app.route('/login')
def login_page():
    return "Login Page"


@app.route('/register')
def register_page():
    return "Register Page"