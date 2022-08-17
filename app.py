# from streamlit_autorefresh import st_autorefresh
# # Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# # after it's been refreshed 100 times.
# count = st_autorefresh(interval=2000, limit=100, key="fizzbuzzcounter")
import spacy
from spacy import displacy
import streamlit as st
from config import *
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

# ----- PAGE CONFIG (title bar)------
import tweepy

st.set_page_config(
    page_title="Tweets Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
)
data = []
sentiments = []
df = None
entities = []
NER = spacy.load("en_core_web_sm")

def sentiment_scores(sentence):
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

def doNER(text):
    pred = NER(text)
    result = []
    for word in pred.ents:
        result.append((word.text, word.label_))
    return result

def getData():
    global data
    global filter
    global df
    print("Came here.....")
    auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(auth)
    tweets = api.home_timeline()
    for tweet in tweets:
        data.append(tweet.text)
        sentiments.append(sentiment_scores(tweet.text))
        entities.append(doNER(tweet.text))

    df = pd.DataFrame(list(zip(data, sentiments, entities)),
                      columns=['Tweets', 'Sentiments', 'Entities Keywords'])

getData()
# ---- SIDEBAR ----
st.sidebar.header("Apply Filters:")

filter = st.sidebar.text_input("Enter Filter String")
st.sidebar.button(label="Apply", on_click=getData)

# ----- MAIN -------
if df is not None:
    st.table(df)