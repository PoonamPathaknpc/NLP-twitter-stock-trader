import logging
from subprocess import Popen, PIPE
import signal
import os
import sys
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from datetime import datetime

# Grabs non-application specific helper modules
import helper

"""
Engine that'll
batch together input stream while
the backend processing is working
"""

#Variables that contains the user credentials to access Twitter API
consumer_key = "WFRQZJIdXhlB820QrErwUKsmY"
consumer_secret = "s6Rgx84N6W7lJb3jfcko5QUpAfVUxLTdeMR6jaXhuFPYhrHoXy"
access_token = "795845870344404993-SVtvORUUBoIhYX1hzZBH84JpCBIQi3h"
access_token_secret = "b8dnhXFfeWIG5Rawms8nsn3xCYYe1JBrtda7k2x8HS6vE"


#consumer_key = "ogNxlePtssKDxdIGVX1dKUHry"
#consumer_secret = "gSAdFrmtiOYkL1lTa4clNHpzgG2Amy2ksvA6tAPU4YEckcALYM"
#access_token = "795845870344404993-uuSmDHmYvOKNg96G4nZhGRovTrZK4BU"
#access_token_secret = "OISMaNqiJfeh1M0qClqSttQMCdOpqFU0C2adosMjAymHN"


INPUT_FILE = 'CollectedTweets.txt'
POLLING_TIMEOUT = 10

USERS = [
    "1364930179",   # Warren Buffett
    "14886375",    # Stock Tweets
    "15897179",     # breakoutstocks
    "28571999",       # bespokeinvest
    "2837841",      # CNNMoneyInvest
    "16228398",     # Mark Cuban
    "1754641",     # nytimesbusiness
    "21323268",     # NYSE
    "184020744",    # Mike Flache
    "19546277",     # YahooFinance
    "778670441405775872", # MarketsInsider
    "15085627"   #Alcoa Corporation
    "22536055"     #American Airlines Group Inc
    "380749300"      #Apple Inc
    "1155522630 "   #J P Morgan Chase & Co
    "253167239"   #Goldman Sachs Group Inc (The)
    ]

TRACK = [
    "15085627"   #Alcoa Corporation
    "22536055"     #American Airlines Group Inc
    "380749300"      #Apple Inc
    "1155522630 "   #J P Morgan Chase & Co
    "253167239"   #Goldman Sachs Group Inc (The)
]

KEYWORDS = [
        "NYSE",
        "IPO",
        "NASDAQ",
]

NEXT_TWEET_BATCH = []


class Tweet:
    def __init__(self, text, retweets, favorites, time):
        self.tweet_text = text
        self.retweet_count = retweets
        self.favorite_count = favorites
        self.timestamp = time

    def __str__(self):
        # tweet text|retweets+fav|timestamp
        return self.tweet_text + "|" + str(self.retweet_count + self.favorite_count) + "|" \
               + str(datetime.strptime(str(self.timestamp), '%Y-%m-%d %H:%M:%S'))


class SListener(StreamListener):

    def on_status(self, status):
        if (len(NEXT_TWEET_BATCH) < 10):
            # if status.user.id_str in USERS:
            # if not status.retweeted and ('RT @' not in status.text):
            print(status.favorite_count)
            print(status.retweet_count)
            print(status.user.screen_name)
            print(status.text)
            print(status.created_at)
            print(len(NEXT_TWEET_BATCH))
            status.text = status.text.replace('\n', '')
            status.text = status.text.replace('|', '').encode('utf-8')
            print status.text
            new_tweet = Tweet(status.text, status.retweet_count, status.favorite_count, status.created_at)
            NEXT_TWEET_BATCH.append(new_tweet)
            return True
        else:
            return False


    def on_error(self, status_code):
        if status_code == 420:
            # Disconnect the stream
            return False


def generate_input_file():
    global NEXT_TWEET_BATCH
    print("generate the files ")
    logging.info("Writing tweets to input file")
    with open(INPUT_FILE, "w") as input_file:
        for tweet in NEXT_TWEET_BATCH:
            input_file.write(str(tweet) + "\n")
    logging.info("Input file successfully generated")
    NEXT_TWEET_BATCH = []


def handler(signum, frame):
    print("\nChecking if processing engine is done with the last batch")
    raise ValueError()



# Initial setup
print ('test')
args = helper.parse_args()
helper.setup_logging(args.verbose)
logging.info("Polling is set to: " + str(int(POLLING_TIMEOUT)) + " seconds")

# Make call to twitter's streaming API to gather tweets
while True:
        print('Gathering tweets from twitter\n')
        try:

            try:
                auth = OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_token_secret)
                print('done')
                twitter_stream = tweepy.Stream(auth, SListener())


                twitter_stream.filter(follow=TRACK)
            except:
                print("Authentication error")
                twitter_stream.disconnect()

            #Writes the processing input file
            generate_input_file()


            # Starts the background process
            background_process = Popen(["python2.7", "process.py", INPUT_FILE], stdout=PIPE)

            while background_process.poll() is None:
                print("[SA engine]\t\tStatus: Currently processing a batch.")

                # Signal handling
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(POLLING_TIMEOUT)

                try:
                    auth = OAuthHandler(consumer_key, consumer_secret)
                    auth.set_access_token(access_token, access_token_secret)
                    twitter_stream = tweepy.Stream(auth, SListener())

                    twitter_stream.filter(follow=TRACK)
                except ValueError:
                    print("Checking if backend if free for the next batch")
                except KeyboardInterrupt:
                    print("\nCleaning up and exiting the ingestion engine")
                    if os.path.isfile(INPUT_FILE):
                        os.remove(INPUT_FILE)
                    sys.exit(0)

                except:
                    print("Authentication error")
                    twitter_stream.disconnect()


            # At this point, the last batch is complete
            print("The last batch is now complete, processing next batch.")
            print("--------------------")
            break
        except KeyboardInterrupt:
            print("\nCleaning up and exiting the ingestion engine")
            #if os.path.isfile(INPUT_FILE):
             #   os.remove(INPUT_FILE)
            sys.exit(0)
