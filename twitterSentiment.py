"""Demonstrates how to make a simple call to the Natural Language API."""

import argparse

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

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

def getTweets():
    ####input your credentials here
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    #####United Airlines
    # Open/Create a file to append data
    csvFile = open('tweets.csv', 'w')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)
    for tweet in tweepy.Cursor(api.search,q="#WorldWideWendy",count=100,
    lang="en",
    since="2017-04-03").items():
        print(tweet)
        print (tweet.created_at, tweet.text)
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8'), tweet.user])


def threshold(score):
    if (score > .8):
        #Overwhelming Positive
        print("+positive", score)

    elif (score > .4):
        #Pretty Positve
        print("positive", score)

    elif (score > .1):
        #Average
        print("average", score)

    elif (score < -.2 and score >-.4):
        #Unhappy
        print("negative", score)

    elif (score < -.4):
        #Very Unhappy
        print("+negative", score)


def print_result(annotations):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))
        threshold(sentence_sentiment)

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
            print_result(annotations)

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