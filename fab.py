from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello_world():
    return '<h1> fab business </h1>'

@app.route('/about/<username>')
def about_page(username):
    return f'<h1>this about of {username}</h1>'