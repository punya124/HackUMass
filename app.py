import random
from flask import Flask, redirect, render_template, request, url_for
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from google.cloud.firestore_v1.base_query import FieldFilter

API_KEY = 'HlrEa2UcmnNgX6vYkKzU65JDfRnBVWmXbRdxtxuqwI9ih8TbEXPFPSWV'
SEARCH_TERM = 'party'
SEARCH_TERM2 = 'statue'
URL = f'https://api.pexels.com/v1/search?query={SEARCH_TERM}&per_page=80'
URL2 = f'https://api.pexels.com/v1/search?query={SEARCH_TERM2}&per_page=80&orientation=square'

headers = {
    'Authorization': API_KEY
}


cred = credentials.Certificate("usocial-70895-firebase-adminsdk-3nfqt-d7ff690e5b.json")
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
# storage = firebase_p.storage()

app = Flask(__name__)

@app.route("/")
def home():
    eventList = db.collection('Events').order_by('Date', direction=firestore.Query.ASCENDING).limit(6).get()
    events = [{"id": event.id, **event.to_dict()} for event in eventList]
    request_list = db.collection('Requests').order_by('Date', direction=firestore.Query.ASCENDING).limit(6).get()
    requests = [{"id": request.id, **request.to_dict()} for request in request_list]
    return render_template('index.html', user=auth.current_user, user_icon=getUserPhoto(), events=events, requests=requests)

@app.route("/account")
def account():
    if auth.current_user:
        CurrentUser = db.collection('Users').document(auth.current_user.get('localId')).get().to_dict()

        rsvpdEvents = db.collection('Events').where('attendees', 'array_contains', auth.current_user.get('localId')).limit(2).get()
        events = [event.to_dict() for event in rsvpdEvents]

        joinedrqsts = db.collection('Requests').where('attendees', 'array_contains', auth.current_user.get('localId')).limit(2).get()
        requests = [event.to_dict() for event in joinedrqsts]
    else:
        return redirect(url_for('login'))
    return render_template('accounts.html', user=CurrentUser, user_icon=getUserPhoto(), events=events, requests=requests)

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

        
        URLNEW = f'https://api.pexels.com/v1/search?query={event_type}&per_page=80'
        response = requests.get(URLNEW, headers=headers)

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

    if (request.args):
        eventList = filterResults(request.args, 'Events')
    else:
        eventList = db.collection('Events').order_by('Date', direction=firestore.Query.ASCENDING).get()
    
    events = [{"id": event.id, **event.to_dict()} for event in eventList]

    return render_template('events.html', user=auth.current_user, events = events, user_icon=getUserPhoto())

@app.route("/signUp", methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cnfpassword = request.form['cnfpassword']
        password = request.form['password']

        response = requests.get(URL2, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Extracting image URLs
            image_urls = [photo['src']['original'] for photo in data['photos']]
            
            imgUrl = random.choice(image_urls)
        else:
            print("Error:", response.status_code)

        if cnfpassword == password:
            try:
                auth.create_user_with_email_and_password(email=email, password=password)
                print('Signed up!')
                auth.sign_in_with_email_and_password(email=email, password=password)
                print('Signed in!')
                db.collection('Users').document(auth.current_user.get('localId')).set({
                    'email': email,
                    'name': name,
                    'photoURL': imgUrl,
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
        description = request.form.get('description')
        image_url = currentUser.get('photoURL')

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
            'Description': description,
            'ImageURL': image_url  # Include the image URL if available
        })

    # Retrieve events from Firestore ordered by date
    if (request.args):
        request_list = filterResults(request.args, 'Requests')
    else:
        request_list = db.collection('Requests').order_by('Date', direction=firestore.Query.ASCENDING).get()
    
    requests = [{"id": request.id, **request.to_dict()} for request in request_list]

    return render_template('people.html', requests=requests, user=auth.current_user, user_icon=getUserPhoto())

def getUserPhoto():
    if(auth.current_user):
        # Directly access the 'photoURL' field in a single line
        photo_url = db.collection('Users').document(auth.current_user.get('localId')).get(field_paths=['photoURL']).to_dict().get('photoURL')
        return photo_url
    else:
        return ''


def filterResults(args, path):
    # Initialize the Firestore collection reference
    query = db.collection(path)
    
    # Filter by event type (if multiple, handle as an array for Firestore 'in' query)
    event_types = args.getlist('event_type')
    if event_types:
        if path=='Events':
            query = query.where('Type', 'in', event_types)
        elif path=='Requests':
            print('using rqsts')
            query = query.where('RequestType', 'in', event_types)
    
    # Filter by start date (if provided)
    start_date = args.get('start_date')
    if start_date != '' and start_date:
        query = query.where('Date', '>=', start_date)
    else:
        print('no start date')

    # Filter by end date (if provided)
    end_date = args.get('end_date')
    if end_date != '' and end_date:
        query = query.where('Date', '<=', end_date)
    else:
        print('no end date')

    # Execute and return the filtered query
    results = query.get()
    if not results:
        print('no results found')
    return results


@app.route('/rsvp', methods=['GET'])
def rsvp():
    # Get the event ID from the URL
    event_id = request.args.get('eventId')
    
    if not event_id:
        print("Event ID is required!", "danger")
        return redirect(url_for('home'))  # Adjust the redirect based on your app structure

    # Get the current user ID from Firebase Authentication
    user = auth.current_user

    if not user:
        print("User is not authenticated!", "danger")
        return redirect(url_for('login'))  # Adjust redirect based on your app structure
    
    user_id = user.get('localId')

    # Get a reference to the event document
    event_ref = db.collection('Events').document(event_id)

    # Fetch the event document
    event_doc = event_ref.get()

    if event_doc.exists:
        event_data = event_doc.to_dict()

        # Check if 'attendees' field exists and update it
        attendees = event_data.get('attendees', [])

        # If the user is not already in the attendees list, add them
        if user_id not in attendees:
            attendees.append(user_id)

            # Update the event document with the new attendees array
            event_ref.update({'attendees': attendees})

            print("RSVP successful!", "success")
        else:
            print("You have already RSVP'd to this event.", "warning")
    else:
        print("Event not found.", "danger")

    return redirect(url_for('events')) 

@app.route('/cancel_rsvp', methods=['GET'])
def cancel_rsvp():
    event_id = request.args.get('eventId')
    user = auth.current_user

    if not event_id or not user:
        print("Event ID or user ID missing", "danger")
        return redirect(url_for('home'))
    
    user_id = user.get('localId')

    event_ref = db.collection('Events').document(event_id)
    event_doc = event_ref.get()

    if event_doc.exists:
        event_data = event_doc.to_dict()
        attendees = event_data.get('attendees', [])

        if user_id in attendees:
            attendees.remove(user_id)
            event_ref.update({'attendees': attendees})
            print("RSVP canceled.", "success")
        else:
            print("You were not RSVP'd for this event.", "warning")
    else:
        print("Event not found.", "danger")

    return redirect(url_for('events'))

@app.route('/join', methods=['GET'])
def join():
    # Get the event ID from the URL
    event_id = request.args.get('eventId')
    
    if not event_id:
        print("Event ID is required!", "danger")
        return redirect(url_for('home'))  # Adjust the redirect based on your app structure

    # Get the current user ID from Firebase Authentication
    user = auth.current_user

    if not user:
        print("User is not authenticated!", "danger")
        return redirect(url_for('login'))  # Adjust redirect based on your app structure
    
    user_id = user.get('localId')

    # Get a reference to the event document
    event_ref = db.collection('Requests').document(event_id)

    # Fetch the event document
    event_doc = event_ref.get()

    if event_doc.exists:
        event_data = event_doc.to_dict()

        # Check if 'attendees' field exists and update it
        attendees = event_data.get('attendees', [])

        # If the user is not already in the attendees list, add them
        if user_id not in attendees:
            attendees.append(user_id)

            # Update the event document with the new attendees array
            event_ref.update({'attendees': attendees})

            print("RSVP successful!", "success")
        else:
            print("You have already RSVP'd to this event.", "warning")
    else:
        print("Event not found.", "danger")

    return redirect(url_for('people')) 

@app.route('/cancel_join', methods=['GET'])
def cancel_join():
    event_id = request.args.get('eventId')
    user = auth.current_user

    if not event_id or not user:
        print("Event ID or user ID missing", "danger")
        return redirect(url_for('home'))
    
    user_id = user.get('localId')

    event_ref = db.collection('Requests').document(event_id)
    event_doc = event_ref.get()

    if event_doc.exists:
        event_data = event_doc.to_dict()
        attendees = event_data.get('attendees', [])

        if user_id in attendees:
            attendees.remove(user_id)
            event_ref.update({'attendees': attendees})
            print("RSVP canceled.", "success")
        else:
            print("You were not RSVP'd for this event.", "warning")
    else:
        print("Event not found.", "danger")

    return redirect(url_for('people'))


if __name__ == '__main__':
   app.run(debug=True)