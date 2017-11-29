from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
from HTMLParser import HTMLParser

consumer_token = 'vwMzLzLxKmRwygyCarHEBTdgd'
consumer_secret = 'e4wjTf5K20nBXDoJPtMFNoSuGfn79dcqoKd8QVZsmPOe450b4S'
access_token = '1177565569-gvXPi5G3uzIYF2GaBMTZOsYA8lj5ZQKf9j0jdtg'
access_token_secret = 'MMNmTd1HvsuiqPqezL13OOE87CelrSc2JLjNL1yyxQRDt'



class StdOutListener(StreamListener):

    def on_status(self, status):
        location = False
        if status.user.location:
            print(status.user.location)
            location = True
        if status.coordinates:
            print 'coordinates: ', status.coordinates
            location = True
        if status.place:
            print 'place: ', status.place.full_name
            location = True


if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_token, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    myStream = Stream(auth, l)
    myStream.filter(track=['the', 'The'])
