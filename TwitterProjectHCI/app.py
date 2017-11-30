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

consumer_token = 'vwMzLzLxKmRwygyCarHEBTdgd'
consumer_secret = 'e4wjTf5K20nBXDoJPtMFNoSuGfn79dcqoKd8QVZsmPOe450b4S'
access_token = '1177565569-gvXPi5G3uzIYF2GaBMTZOsYA8lj5ZQKf9j0jdtg'
access_token_secret = 'MMNmTd1HvsuiqPqezL13OOE87CelrSc2JLjNL1yyxQRDt'

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None
tweetQueue = Queue()


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
    
    print(status.text)
    print(text.sentiment.polarity)
    socketio.emit('tweet', {'data': output, 'sentiment': text.sentiment.polarity}, namespace='/test')


@socketio.on('new_filter', namespace='/test')
def change_filter(message):
    for stream in streams:
        stream.disconnect()
    fil = message['data']
    myStream = Stream(auth, l)
    streams.append(myStream)
    myStream.filter(track=[fil], async=True)

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    for stream in streams:
        stream.disconnect()
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
