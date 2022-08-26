import re
import time
import tweepy
from config import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from cleantext import clean

# authentication
# auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
#
# api = tweepy.API(auth)

# public_tweets = api.home_timeline()
# print(public_tweets[0])

# streaming
from db_service import DbService

def cleaner(tweet):
    tweet = re.sub("@[A-Za-z0-9]+","",tweet) #Remove @ sign
    tweet = re.sub(r"(?:\@|http?\://|https?\://|www)\S+", "", tweet) #Remove http links
    tweet = tweet.replace("#", "").replace("_", " ") #Remove hashtag sign but keep the text
    tweet = clean(tweet,
                  no_emoji=True,
                  fix_unicode=True,  # fix various unicode errors
                  to_ascii=True,  # transliterate to closest ASCII representation
                  lower=True,  # lowercase text
                  no_line_breaks=False,  # fully strip line breaks as opposed to only normalizing them
                  no_urls=True,  # replace all URLs with a special token
                  no_emails=True,  # replace all email addresses with a special token
                  no_phone_numbers=True,  # replace all phone numbers with a special token
                  )
    return tweet

def sentiment_scores(sentence):
    sentence = cleaner(sentence)
    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)

    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05:
        return "Positive"

    elif sentiment_dict['compound'] <= - 0.05:
        return "Negative"

    else:
        return "Neutral"

class InOutStream(tweepy.StreamingClient):
    def on_connect(self):
        print("Connected!")

    # called when stream finds a tweet matching filter criteria

    def on_tweet(self, tweet):
        global data
        global dbService
        print(tweet.public_metrics)
        print(tweet.non_public_metrics)
        print(tweet.organic_metrics)
        print(tweet.promoted_metrics)
        print('\n\n\n\n')
        id = int(tweet.id)
        body = tweet.text
        reference = tweet.referenced_tweets[0].type if tweet.referenced_tweets is not None else 'post'
        language = tweet.lang
        public_retweet = tweet.public_metrics['retweet_count']
        public_reply = tweet.public_metrics['reply_count']
        public_like = tweet.public_metrics['reply_count']
        public_quote = tweet.public_metrics['reply_count']
        created_at = tweet.created_at
        source = tweet.source

        NER = tweet.context_annotations
        named_entities = {}
        for item in NER:
            entity = item['domain']['name']
            name = item['entity']['name']
            if entity in named_entities:
                named_entities[entity].append(name)
            else:
                named_entities[entity] = []

        sentiment = sentiment_scores(body)

        data = {
            'id': id,
            'text': body,
            'ref': reference,
            'lang': language,
            'retweet': public_retweet,
            'like': public_like,
            'reply': public_reply,
            'quote': public_quote,
            'year': created_at.strftime("%Y"),
            'month': created_at.strftime('%m'),
            'day': created_at.strftime('%d'),
            'hour': created_at.strftime('%H'),
            'min': created_at.strftime('%M'),
            'sec': created_at.strftime('%S'),
            'source': source,
            'senti': sentiment,
            'ner': named_entities
        }
        dbService.insert(data)
        # print(f"Data in the DB--- {dbService.fetch()}")
        time.sleep(5)


def getTweets(keywords):
    global data
    global stream
    data = []
    for term in keywords:
        stream.add_rules(tweepy.StreamRule(term))

    stream.filter(
        tweet_fields=['id','referenced_tweets', 'geo', 'lang', 'public_metrics', 'context_annotations', 'created_at',
                      'organic_metrics', 'source', 'withheld'], threaded=True)



def addNewRules(keywords):
    global stream
    dbService.removeAll()
    cleanAllRules()
    print(f"Data REMOVED ----- {dbService.fetch()}")
    # stream.disconnect()
    dbService.removeAll()
    for term in keywords:
        stream.add_rules(tweepy.StreamRule(term))
    print(f"New Rules applied -----> {stream.get_rules()}")

def endStream():
    global stream
    stream.disconnect()

def cleanAllRules():
    global stream
    current_rules = stream.get_rules()
    rule_ids = []
    for rule in current_rules.data:
        rule_ids.append(rule.id)
    print(f"Current rules : {current_rules}")
    stream.delete_rules(ids=rule_ids)

if __name__ == '__main__':
    global dbService
    global stream
    dbService = DbService()
    dbService.initConnect()
    # dbService.removeAll()

    stream = InOutStream(bearer_token=BEARER_TOKEN)
    cleanAllRules()
    getTweets(keywords=['India', 'Inflation', 'Recession', 'China', 'Jobs'])
    # time.sleep(20)
    # addNewRules(keywords=['modi', 'india', 'bjp'])