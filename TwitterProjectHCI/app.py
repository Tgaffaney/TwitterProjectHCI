# This is the backend of the Twitter Map Application
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from html.parser import HTMLParser
from multiprocessing import Queue
from textblob import TextBlob
import re

# Twitter listener class
class StdOutListener(StreamListener):

    def on_status(self, status):
       filter(status)


# Keys necessary for connection to Twitter
consumer_token = 'vwMzLzLxKmRwygyCarHEBTdgd'
consumer_secret = 'e4wjTf5K20nBXDoJPtMFNoSuGfn79dcqoKd8QVZsmPOe450b4S'
access_token = '1177565569-gvXPi5G3uzIYF2GaBMTZOsYA8lj5ZQKf9j0jdtg'
access_token_secret = 'MMNmTd1HvsuiqPqezL13OOE87CelrSc2JLjNL1yyxQRDt'

# Assorted variables
async_mode = None

# State names for location mapping
us_state_abbrev = {
    'ALABAMA': 'AL',
    'ALASKA': 'AK',
    'ARIZONA': 'AZ',
    'ARKANSAS': 'AR',
    'CALIFORNIA': 'CA',
    'COLORADO': 'CO',
    'CONNECTICUT': 'CT',
    'DELEWARE': 'DE',
    'FLORIDA': 'FL',
    'GEORGIA': 'GA',
    'HAWAII': 'HI',
    'IDAHO': 'ID',
    'ILLINOIS': 'IL',
    'INDIANA': 'IN',
    'IOWA': 'IA',
    'KANSAS': 'KS',
    'KENTUCKY': 'KY',
    'LOUISIANA': 'LA',
    'MAINE': 'ME',
    'MARYLAND': 'MD',
    'MASSACHUSETTS': 'MA',
    'MICHIGAN': 'MI',
    'MINNESOTA': 'MN',
    'MISSISSIPPI': 'MS',
    'MISSOURI': 'MO',
    'MONTANA': 'MT',
    'NEBRASKA': 'NE',
    'NEVADA': 'NV',
    'NEW HAMPSHIRE': 'NH',
    'NEW JERSEY': 'NJ',
    'NEW MEXICO': 'NM',
    'NEW YORK': 'NY',
    'NORTH CAROLINA': 'NC',
    'NORTH DAKOTA': 'ND',
    'OHIO': 'OH',
    'OKLAHOMA': 'OK',
    'OREGON': 'OR',
    'PENNSYLVANIA': 'PA',
    'RHODE ISLAND': 'RI',
    'SOUTH CAROLINA': 'SC',
    'SOUTH DAKOTA': 'SD',
    'TENNESSEE': 'TN',
    'TEXAS': 'TX',
    'UTAH': 'UT',
    'VERMONT': 'VT',
    'VIRGINIA': 'VA',
    'WASHINGTON': 'WA',
    'WEST VIRGINIA': 'WV',
    'WISCONSIN': 'WI',
    'WYOMING': 'WY',
}

# State initializations for location mapping
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


# Assorted variables for websockets and twitter api streaming
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
l = StdOutListener()
auth = OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
streams = []


# The background thread for the websocket process
def background_thread():
    while True:
        socketio.sleep(10)

# Creates the index page
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

# Creates the sentiment page
@app.route('/sentiment')
def sentiment():
    return render_template('sentiment.html',  async_mode=socketio.async_mode)

# The function used for filtering out tweets that contain location information.
# This function uses either the profile location, the gps location, or a location mentioned in the tweet body
# It then determines the state named in the location and sends it to the javascript layer with the sentiment value provided by TextBlob
def filter(status):
    output = ""
    if status.user.location:
        output = (status.user.location)
    elif status.coordinates:
        output = 'coordinates: ', status.coordinates
    elif status.place:
        output = 'place: ', status.place.full_name
    else:
        return
    text = TextBlob(status.text)

    # Proceeds to state selection if the location is a string
    if isinstance(output, str):
        output.upper()
        if "New Hampshire" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NEW HAMPSHIRE"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "New Jersey" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NEW JERSEY"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "New York" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NEW YORK"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "New Mexico" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NEW MEXICO"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "North Carolina" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NORTH CAROLINA"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "North Dakota" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("NORTH DAKOTA"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "Rhode Island" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("RHODE ISLAND"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "South Carolina" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("SOUTH CAROLINA"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "South Dakota" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("SOUTH DAKOTA"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        elif "West Virginia" in output:
            socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get("WEST VIRGINIA"), 'sentiment': text.sentiment.polarity}, namespace='/stream')
        else:
            vals = re.findall(r'\s|,|[^,\s]+', output)
            for val in vals:
                if val in us_state_abbrev:
                    socketio.emit('tweet', {'data': 'US-' + us_state_abbrev.get(val), 'sentiment': text.sentiment.polarity}, namespace='/stream')
                elif val in states:
                    socketio.emit('tweet', {'data': 'US-' + val, 'sentiment': text.sentiment.polarity}, namespace='/stream')


# Function called when a new filter is sent by the JavaScript layer
# Also changes the filter text to upper case lower case and capitalized
@socketio.on('new_filter', namespace='/stream')
def change_filter(message):
    for stream in streams:
        stream.disconnect()
        del stream
        print('ended stream')


    del streams[:]
    fil = message['data']
    upfil = fil
    upfil.upper()
    capfil = fil
    capfil.capitalize()
    downfil = fil
    downfil.lower()
    myStream = Stream(auth, l)
    streams.append(myStream)
    myStream.filter(track=[upfil, downfil, fil], async=True)

# Function called by Flask-Socketio when a connection is established
@socketio.on('connect', namespace='/stream')
def connect():
    global thread
    print('connect')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


# Function called by Flask-Socketio on a disconnect
@socketio.on('dis', namespace='/stream')
def disconnect():
    for stream in streams:
        stream.disconnect()
        del stream

    del streams[:]
    print('disconnected ', request.sid)

# Function used to set the main application
if __name__ == '__main__':
    socketio.run(app, debug=True)
