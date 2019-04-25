"""Demonstrates how to make a simple call to the Natural Language API."""

import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import google
import statistics
import dotenv
import tweepy
import csv
import pandas as pd
from time import gmtime, strftime
import datetime

now = datetime.datetime.now()
previousTime = (now + datetime.timedelta(days=-1)).isoformat()
now = now.isoformat()
print("Now", now)
print("Previous Time", previousTime)
replies = []
sentiment = []
# Move to env file
consumer_key = 'nebmNNRrm1j6G4vrPWSzaKY0P'
consumer_secret = '8m7mOa5xghJTjsImoLuql4bkqAFY9CqILrhDt9fKS9UQ2xIw1s'
access_token = '1039562255967375362-o8m0M9V5x2YhEaMAGEm9DUbzE1uGL2'
access_token_secret = 'Cm5qq1IQNvPk0PyNEhYp0ISU65VqIZvzwH9jc53IPZK95'
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def get_tweets(query, n):
    _max_queries = 2  # arbitrarily chosen value
    tweets = tweet_batch = api.search(q=query, count=n)
    ct = 1
    while len(tweets) < n and ct < _max_queries:
        print(len(tweets))
        tweet_batch = api.search(q=query,
                                 count=n - len(tweets),
                                 locale='en',
                                 lang="en",
                                 max_id=tweet_batch.max_id)
        # for tweet in tweet_batch:
        #     print(any(True for tweet.id in tweet_batch if tweet.id in tweets))
        tweets.extend(tweet_batch)
        ct += 1
    return tweets


def getTweets():
    global replies
    # United Airlines
    # Open/Create a file to write data
    csvFile = open('tweets.csv', 'w', newline='')
    # Use csv Writer
    csvWriter = csv.writer(csvFile)
    # for tweet in api.search(q="#WorldWideWendy", rpp=100,lang="en"):
    # for tweet in tweepy.Cursor(api.search, q="#WorldWideWendy", rpp=100,lang="en",result_type='recent', since_id="1120440913497554944").items(100):
    # for tweet in api.search(q="#Wendys",count=100):
    for tweet in get_tweets("#WorldWideWendy", 100):
        print(tweet.created_at, tweet.text)
        text = ""
        for e in str(tweet.text.encode('utf-8')):
            if(e != ','):
                text = text+e
        for e in text:
            if e == ",":
                break
        text = text[2:-1]
        csvWriter.writerow([tweet.created_at, text, tweet.id])
        replies.append(tweet.id)

def threshold(score, statusID):
    global replies
    if (statusID in replies):
        return
    if (score > .8):
        print("+positive", score)
        try:
            # Overwhelming Positive
            api.update_status(status="We're Glad to hear it! Thanks for your awesome feedback. Be sure to mention this tweet with your next order to get a free drink! While you're at it, check out our indiegogo :)", in_reply_to_status_id=statusID)

        except tweepy.error.TweepError:
            print("Already Replied to Tweet")
    elif (score > .4):
        print("positive", score)
        try:
            # Pretty Positve
            api.update_status(
                status="Thanks for your awesome feedback. We look forward to seeing you soon!", in_reply_to_status_id=statusID)
            
        except tweepy.error.TweepError:
            print("Already Replied to Tweet")
    elif (score > .1):
        print("average", score)
        try:
        # Average
            api.update_status(status="Thanks for your feedback! Be sure to mention this tweet on your next order for a free order of Toasted Corn",
                          in_reply_to_status_id=statusID)
            
        except tweepy.error.TweepError:
            print("Already Replied to Tweet")
    elif (score < -.2 and score > -.7):
        print("negative", score)
        try:
            # Unhappy
            api.update_status(
            status="Sorry to hear it. If you give us another try, we'll sweeten the deal. Be sure to mention this tweet with your next order to get a free drink!", in_reply_to_status_id=statusID)
           
        except tweepy.error.TweepError:
            print("Already Replied to Tweet")

    elif (score < -.7):
        print("+negative", score)
        try:
            # Very Unhappy
            api.update_status(status="Sorry to hear it! We apologize and hope you will give us another chance. Be sure to mention this tweet with your next order to get a free meal, on us!", in_reply_to_status_id=statusID)
            
        except tweepy.error.TweepError:
            print("Already Replied to Tweet")

    if(len(replies) > 99):
        replies = []


def print_result(annotations, tweetID):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))
        threshold(sentence_sentiment, tweetID)
        sentiment.append(score)

    print('Overall Sentiment: score of {} with magnitude of {}'.format(
        score, magnitude))
    return 0


def analyze(movie_review_filename):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()
    getTweets()
    with open("tweets.csv", 'r') as tweets:
        csv_reader = csv.reader(tweets, delimiter=",",)
        for row in csv_reader:
            print(row[1])
            document = types.Document(
                content=row[1],
                type=enums.Document.Type.PLAIN_TEXT)
            try:
                annotations = (client.analyze_sentiment(document=document))
                print_result(annotations, row[2])
            except google.api_core.exceptions.InvalidArgument:
                print("Incorrect Language")
            # Print the results

    print("Overall Sentiment Score", statistics.mean(sentiment))
    # with open(movie_review_filename, 'r') as review_file:
    #     # Instantiates a plain text document.
    #     content = review_file.read()

    # document = types.Document(
    #     content=content,
    #     type=enums.Document.Type.PLAIN_TEXT)
    # annotations = client.analyze_sentiment(document=document)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'movie_review_filename',
        help='The filename of the movie review you\'d like to analyze.')
    args = parser.parse_args()

    analyze(args.movie_review_filename)
