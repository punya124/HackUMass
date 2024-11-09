from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/events")
def events():
    return render_template('events.html')

@app.route("/signUp")
def signUp():
    return render_template('signUp.html')

if __name__ == '__main__':
   app.run(debug=True)