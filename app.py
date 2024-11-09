import random
from flask import Flask, flash, redirect, render_template, request
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import requests

API_KEY = 'HlrEa2UcmnNgX6vYkKzU65JDfRnBVWmXbRdxtxuqwI9ih8TbEXPFPSWV'
SEARCH_TERM = 'party'
URL = f'https://api.pexels.com/v1/search?query={SEARCH_TERM}&per_page=80'

headers = {
    'Authorization': API_KEY
}


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
storage = firebase_p.storage()

app = Flask(__name__)

@app.route("/")
def home():
    print(auth.current_user)
    return render_template('index.html', user=auth.current_user)

@app.route("/account")
def account():
    return render_template('accounts.html', user=auth.current_user)

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

        response = requests.get(URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Extracting image URLs
            image_urls = [photo['src']['original'] for photo in data['photos']]
            
            imgUrl = random.choice(image_urls)
        else:
            print("Error:", response.status_code)
        
        db.collection('Events').add({
            'Name': event_name,
            'Type': event_type,
            'Date': event_date,
            'ImageURL': imgUrl,
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
        name = request.form['name']
        email = request.form['email']
        cnfpassword = request.form['cnfpassword']
        password = request.form['password']
        if cnfpassword == password:
            try:
                auth.create_user_with_email_and_password(email=email, password=password)
                print('Signed up!')
                auth.sign_in_with_email_and_password(email=email, password=password)
                print('Signed in!')
                db.collection('Users').document(auth.current_user.get('localId')).set({
                    'email': email,
                    'name': name,
                    'photoURL': '',
                })
                return redirect('/', code=302)
            except:
                print('Email Already exists!')
        else:
            print("Passwords don't match")
    return render_template('signUp.html')

@app.route("/people", methods=['GET', 'POST'])
def people():
    if request.method == 'POST':
        currentUser = db.collection('Users').document(auth.current_user.get('localId')).get().to_dict()
        # Retrieve form values
        request_name = request.form.get('eventName')
        person_name = currentUser.get('name')
        request_type = request.form.get('eventType')
        event_date = request.form.get('eventDate')
        event_time = request.form.get('eventTime')
        location = request.form.get('location')
        cost = request.form.get('cost')
        pay = request.form.get('requestPay')
        description = request.form.get('description')
        
        # Handling file upload (profile image)
        event_image = request.files.get('eventImage')
        image_url = None
        if event_image:
            # Add code here to handle saving or uploading the file
            # e.g., save locally or upload to a cloud storage service and get the URL
            # image_url = 'URL of the uploaded image'
            pass

        # Combine date and time for Firestore (optional)
        datetime = f"{event_date} {event_time}"

        # Add the data to Firestore
        db.collection('Requests').add({
            'RequestName': request_name,
            'PersonName': person_name,
            'RequestType': request_type,
            'Date': event_date,
            'Time': event_time,
            'DateTime': datetime,  # Optional: combined datetime
            'Location': location,
            'Cost': cost,
            'Pay': pay,
            'Description': description,
            'ImageURL': image_url  # Include the image URL if available
        })

    # Retrieve events from Firestore ordered by date
    request_list = db.collection('Requests').order_by('Date', direction=firestore.Query.ASCENDING).get()
    requests = [request.to_dict() for request in request_list]

    return render_template('people.html', requests=requests, user=auth.current_user)

if __name__ == '__main__':
   app.run(debug=True)