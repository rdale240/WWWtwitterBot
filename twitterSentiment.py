"""Demonstrates how to make a simple call to the Natural Language API."""

import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

import dotenv
import tweepy
import csv
import pandas as pd
from time import gmtime, strftime
import datetime

now = datetime.datetime.now()
previousTime = (now + datetime.timedelta(days = -1)).isoformat()
now = now.isoformat()
print("Now",now)
print("Previous Time", previousTime)
####input your credentials here
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

def getTweets():
    
    #####United Airlines
    # Open/Create a file to write data
    csvFile = open('tweets.csv', 'w')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)
    for tweet in tweepy.Cursor(api.search,q="#WorldWideWendy",count=100,
    lang="en",
    since="2017-04-03").items():
        print(tweet)
        print (tweet.created_at, tweet.text)
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8'), tweet.user, tweet.id])


def threshold(score, statusID):
    if (score > .8):
        #Overwhelming Positive
        api.update_status(status="We're Glad to hear it! Thanks for your awesome feedback. Be sure to mention this tweet with your next order to get a free drink! While you're at it, check out our indiegogo :)",in_reply_to_status_id=statusID)
        print("+positive", score)

    elif (score > .4):
        #Pretty Positve
        api.update_status(status="Thanks for your awesome feedback. We look forward to seeing you soon!",in_reply_to_status_id=statusID)
        print("positive", score)

    elif (score > .1):
        #Average
        api.update_status(status="Thanks for your feedback!",in_reply_to_status_id=statusID)
        print("average", score)

    elif (score < -.2 and score >-.4):
        #Unhappy
        api.update_status(status="Sorry to hear it. If you give us another try, we'll sweeten the deal. Be sure to mention this tweet with your next order to get a free drink!",in_reply_to_status_id=statusID)
        print("negative", score)

    elif (score < -.4):
        #Very Unhappy
        api.update_status(status="Sorry to hear it! We pologie and hope you will give us another chance. Be sure to mention this tweet with your next order to get a free meal, on us!",in_reply_to_status_id=statusID)
        print("+negative", score)


def print_result(annotations, tweetID):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))
        threshold(sentence_sentiment, tweetID)

    print('Overall Sentiment: score of {} with magnitude of {}'.format(
        score, magnitude))
    return 0


def analyze(movie_review_filename):
    """Run a sentiment analysis request on text within a passed filename."""
    client = language.LanguageServiceClient()
    with open("tweets.csv",'r') as tweets:
        csv_reader=csv.reader(tweets,delimiter=",",)
        for row in csv_reader:
            print(row[1])
            document = types.Document(
            content=row[1],
            type=enums.Document.Type.PLAIN_TEXT)
            annotations=(client.analyze_sentiment(document=document))
            # Print the results
            print_result(annotations,tweetID)

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