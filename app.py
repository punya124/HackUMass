from flask import Flask, flash, redirect, render_template, request
import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyAqympu8EbHfPZgydl5oOmBKZdKL53TlPc",
  'authDomain': "usocial-70895.firebaseapp.com",
  'projectId': "usocial-70895",
  'storageBucket': "usocial-70895.firebasestorage.app",
  'messagingSenderId': "1012188298507",
  'appId': "1:1012188298507:web:7741d6d389c828b042760e",
  'measurementId': "G-EB4MP6TKEK",
  'databaseURL': ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
# db = firebase.database()
auth = firebase.auth()
# storage = firebase.storage()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html', user=auth.current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email=email, password=password)
            print('Signed in!')
            return redirect('/', code=302)
        except:
            print('Invlaid Username or Password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    auth.current_user = None
    return redirect('/', code=302)

@app.route("/events")
def events():
    return render_template('events.html')

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        email = request.form['email']
        cnfpassword = request.form['cnfpassword']
        password = request.form['password']
        if cnfpassword == password:
            try:
                auth.create_user_with_email_and_password(email=email, password=password)
                print('Signed up!')
                return redirect('/', code=302)
            except:
                print('Email Already exists!')
        else:
            print("Passwords don't match")
    return render_template('signUp.html')

@app.route("/people")
def people():
    return render_template('people.html')

if __name__ == '__main__':
   app.run(debug=True)