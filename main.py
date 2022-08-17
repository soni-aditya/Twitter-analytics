import tweepy
import configparser

# read configs
config = configparser.ConfigParser()
config.read('config.ini')

API_KEY = config['twitter']['API_KEY']
API_KEY_SECRET = config['twitter']['API_KEY_SECRET']
ACCESS_TOKEN = config['twitter']['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = config['twitter']['ACCESS_TOKEN_SECRET']

# authentication
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

public_tweets = api.home_timeline()
print(public_tweets[0])