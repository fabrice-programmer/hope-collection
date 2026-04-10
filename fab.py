from flask import Flask,render_template
app = Flask(__name__)
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')
@app.route('/market')
def market_page():
     items= [
        {"id": 1, "name": "phone", "barcode": "8673458", "price": 300},
        {"id": 2, "name": "laptop", "barcode": "23455", "price": 800},
        {"id": 3, "name": "keyboard", "barcode": "445544", "price": 50}
    ]
     return render_template('market.html', items=items)
    
