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


# Tokens necessary for connection to Twitter API
consumer_token = 'vwMzLzLxKmRwygyCarHEBTdgd'
consumer_secret = 'e4wjTf5K20nBXDoJPtMFNoSuGfn79dcqoKd8QVZsmPOe450b4S'
access_token = '1177565569-gvXPi5G3uzIYF2GaBMTZOsYA8lj5ZQKf9j0jdtg'
access_token_secret = 'MMNmTd1HvsuiqPqezL13OOE87CelrSc2JLjNL1yyxQRDt'

# Assorted Variables
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
l = StdOutListener()
auth = OAuthHandler(consumer_token, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
streams = []

# Class used for listening for incoming tweets and filtering them
class StdOutListener(StreamListener):

    def on_status(self, status):
       filter(status)

# Starts background thread, allows updating of index.html
def background_thread():
    while True:
        socketio.sleep(10)

# Creates html template at base directory
@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

# Connects server websocket to client websocket
@socketio.on('connect', namespace='/stream')
def connect():
    global thread
    print('connect')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

# Disconnects websockets on clients leaving page, ends streams on server
@socketio.on('dis', namespace='/stream')
def disconnect():
    for stream in streams:
        stream.disconnect()
        del stream

    del streams[:]
    print('disconnected ', request.sid)

# Starts socketio
if __name__ == '__main__':
    socketio.run(app, debug=True)

# Filters tweets so that only tweets 
# with location data are passed on to the client, also passes a text sentiment score
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
    
    # print(status.text)
    # print(text.sentiment.polarity)
    socketio.emit('tweet', {'data': output, 'sentiment': text.sentiment.polarity}, namespace='/stream')

# Called when the client changes the filtering text for tweets
# Halts and deletes all of the streams currently running
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
