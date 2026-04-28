from market import app
from flask import render_template
from market.models import Item
from market.forms import RegisterForm

@app.route('/')
def home_page():
    return render_template("home.html")

from models import Market   # or your model name

@app.route('/market')
def market_page():
    items = Market.query.all()   # fetch data from DB
    return render_template("market.html", items=items)

@app.route('/login')
def login_page():
    return "Login Page"

@app.route('/register')
def register_page():
    return "Register Page"