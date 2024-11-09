from flask import Flask, flash, redirect, render_template, request
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)


firebaseConfig = {
    'apiKey': "AIzaSyAqympu8EbHfPZgydl5oOmBKZdKL53TlPc",
  'authDomain': "usocial-70895.firebaseapp.com",
  'projectId': "usocial-70895",
  'storageBucket': "usocial-70895.firebasestorage.app",
  'messagingSenderId': "1012188298507",
  'appId': "1:1012188298507:web:7741d6d389c828b042760e",
  'measurementId': "G-EB4MP6TKEK",
  'databaseURL': 'https://xxxxx.firebaseio.com'
}

firebase_p = pyrebase.initialize_app(firebaseConfig)
db = firestore.client()
auth = firebase_p.auth()
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

@app.route("/events", methods =['GET', 'POST'])
def events():
    if request.method == 'POST':
        # Retrieve form values using request.form
        event_name = request.form.get('eventName')
        event_type = request.form.get('eventType')
        event_date = request.form.get('eventDate')
        event_location = request.form.get('eventLocation')
        event_cost = request.form.get('eventCost')
        event_description = request.form.get('eventDescription')
        
        db.collection('Events').add({
            'Name': event_name,
            'Type': event_type,
            'Date': event_date,
            'Location': event_location,
            'Cost': event_cost,
            'Description': event_description
        })

    eventList = db.collection('Events').order_by('Date', direction=firestore.Query.ASCENDING).get()
    events = [event.to_dict() for event in eventList]

    return render_template('events.html', user=auth.current_user, events = events)

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
                auth.sign_in_with_email_and_password(email=email, password=password)
                print('Signed in!')
                return redirect('/', code=302)
            except:
                print('Email Already exists!')
        else:
            print("Passwords don't match")
    return render_template('signUp.html')

@app.route("/people")
def people():
    return render_template('people.html', user=auth.current_user)

if __name__ == '__main__':
   app.run(debug=True)