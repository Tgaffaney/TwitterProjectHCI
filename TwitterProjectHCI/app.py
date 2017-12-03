#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from html.parser import HTMLParser
from multiprocessing import Queue
from textblob import TextBlob
import re

consumer_token = 'vwMzLzLxKmRwygyCarHEBTdgd'
consumer_secret = 'e4wjTf5K20nBXDoJPtMFNoSuGfn79dcqoKd8QVZsmPOe450b4S'
access_token = '1177565569-gvXPi5G3uzIYF2GaBMTZOsYA8lj5ZQKf9j0jdtg'
access_token_secret = 'MMNmTd1HvsuiqPqezL13OOE87CelrSc2JLjNL1yyxQRDt'


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

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


states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

class StdOutListener(StreamListener):

    def on_status(self, status):
       filter(status)



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
l = StdOutListener()
auth = OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
streams = []


def background_thread():
    while True:
        socketio.sleep(10)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


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


    #print(output)
    if isinstance(output, str):
        output.upper()
        # vals = output.split(',')
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
                # else:
                # for var in sp:
                #     if var in us_state_abbrev:
                #         print(var)
                #         socketio.emit('tweet', {'data': 'US-' + var, 'sentiment': text.sentiment.polarity}, namespace='/stream')

    # print(status.text)
    # print(text.sentiment.polarity)


@socketio.on('new_filter', namespace='/stream')
def change_filter(message):
    for stream in streams:
        stream.disconnect()
        del stream
        print('ended stream')


    del streams[:]
    fil = message['data']
    myStream = Stream(auth, l)
    streams.append(myStream)
    myStream.filter(track=[fil], async=True)
    pausedStreamFilter = message['data']

@socketio.on('connect', namespace='/stream')
def connect():
    global thread
    print('connect')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})



@socketio.on('dis', namespace='/stream')
def disconnect():
    for stream in streams:
        stream.disconnect()
        del stream

    del streams[:]
    print('disconnected ', request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True)
