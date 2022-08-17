import time
import tweepy
from config import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# authentication
# auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
#
# api = tweepy.API(auth)

# public_tweets = api.home_timeline()
# print(public_tweets[0])

# streaming
search_terms = ['biden', 'russia', 'china']

data = []

class InOutStream(tweepy.StreamingClient):
    def on_connect(self):
        print("Connected!")
    # called when stream finds a tweet matching filter criteria
    def on_tweet(self, tweet):
        # checking if tweets are first hand and not replies to the tweets
        if tweet.referenced_tweets == None:
            global data
            print(tweet.text)
            print(tweet.geo)
            print(f"Language: {tweet.lang}")
            print(f"stats: {tweet.public_metrics}")
            print("\n\n\n\n\n\n\n")
            if len(data) > 50:
                data = data[1:]
                data.append(tweet)
            time.sleep(0.5)


stream = InOutStream(bearer_token=BEARER_TOKEN)

for term in search_terms:
    stream.add_rules(tweepy.StreamRule(term))

stream.filter(tweet_fields=['referenced_tweets'])