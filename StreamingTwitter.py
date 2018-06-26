
#This file streams tweets from the Twitter API and saves them into a file
#It will create a file with thousands of positive and negative tweets
#The format is already set up, but you can modify it too.

import sys
import tweepy
import re 
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler


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
    ]


class Emoticons:
    POSITIVE = ["*O", "*-*", "*O*", "*o*", "* *",
                ":P", ":D", ":d", ":p",
                ";P", ";D", ";d", ";p",
                ":-)", ";-)", ":=)", ";=)",
                ":<)", ":>)", ";>)", ";=)",
                "=}", ":)", "(:;)",
                "(;", ":}", "{:", ";}",
                "{;:]",
                "[;", ":')", ";')", ":-3",
                "{;", ":]",
                ";-3", ":-x", ";-x", ":-X",
                ";-X", ":-}", ";-=}", ":-]",
                ";-]", ":-.)",
                "^_^", "^-^"]

    NEGATIVE = [":(", ";(", ":'(",
                "=(", "={", "):", ");",
                ")':", ")';", ")=", "}=",
                ";-{{", ";-{", ":-{{", ":-{",
                ":-(", ";-(",
                ":,)", ":'{",
                "[:", ";]"
                ]

#******Creating a dataset with POSITIVE Tweets*********** 

class CustomStreamListener(tweepy.StreamListener):
    def __init__(self, maxnum, api=None):
        self.n = maxnum
        self.api = api

    def on_status(self, status):
        try:
            tweets = []
            name = status.author.screen_name

            textTwitter = status.text.encode('utf-8')

            #Convert into lowercase
            Tweet = textTwitter.lower()
            
            #Convert www.* or https?://* to URL
            Tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',Tweet)
            
            #Convert @username to User
            Tweet = re.sub('@[^\s]+','TWITTER_USER',Tweet)


            #Remove additional white spaces
            Tweet = re.sub('[\s]+', ' ', Tweet)
            
            #Replace #word with word Handling hashtags
            Tweet = re.sub(r'#([^\s]+)', r'\1', Tweet)
            
            #trim
            Tweet = Tweet.strip('\'"')
            
            #Deleting happy and sad face emoticon from the tweet 
            for e in Emoticons.POSITIVE:
                Tweet = Tweet.replace(e, " ")
            for e in Emoticons.NEGATIVE:
                Tweet = Tweet.replace(e, " ")


            #Deleting the Twitter @username tag and reTweets
            tag = 'TWITTER_USER' 
            rt = 'rt'
            Tweet = Tweet.replace(tag,'')
            Tweet = Tweet.replace(rt,'')
            Tweet = Tweet.replace('|', ' ')
            Tweet = Tweet.replace('\n', ' ')
            
            final_tweet = '|positive|, |%s| ' % (Tweet)

            f = open('TrainedTweets.txt', 'r+')
            old = f.read()
            f.write(final_tweet+'\n')
            f.close()
        
            self.n = self.n+1
            if self.n < 3000:
                return True
            else:
                print ('maxnum = '+str(self.n))
                return False
        
        except Exception as e:
            print (e)

    def on_error(self, status_code):
        #print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        #print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream
        
#******Creating a dataset with NEGATIVE Tweets*********** 

class CustomStreamListenerNEG(tweepy.StreamListener):
    def __init__(self, maxnum, api=None):
        self.n = maxnum
        self.api = api

    def on_status(self, status):
        try:
            tweets = []
            name = status.author.screen_name
            textTwitter = status.text.encode('utf-8')
            
            #Convert into lowercase
            Tweet = textTwitter.lower()
            
            #Convert www.* or https?://* to URL
            Tweet = re.sub('((www\.[\s]+)|(https?://[^\s]+))','URL',Tweet)
            
            #Convert @username to TWITTER_USER
            Tweet = re.sub('@[^\s]+','TWITTER_USER',Tweet)
            
            #Remove additional white spaces
            tweet = re.sub('[\s]+', ' ', Tweet)
            
            #Replace #word with word Handling hashtags
            Tweet = re.sub(r'#([^\s]+)', r'\1', Tweet)
            
            #trim
            Tweet = Tweet.strip('\'"')
            

            # Deleting happy and sad face emoticon from the tweet
            for e in Emoticons.POSITIVE:
                Tweet = Tweet.replace(e, " ")
            for e in Emoticons.NEGATIVE:
                Tweet = Tweet.replace(e, " ")



            #Deleting the Twitter @username tag and reTweets
            tag = 'TWITTER_USER' 
            rt = 'rt'
            Tweet = Tweet.replace(tag,'')
            Tweet = Tweet.replace(rt,'')
            Tweet = Tweet.replace('|', ' ')
            Tweet = Tweet.replace('\n', ' ')
            final_tweet = '|negative|, |%s| ' % (Tweet)

            
            f = open('TrainedTweets.txt', 'r+')
            old = f.read()
            f.write(final_tweet+'\n')
            f.close()
        
            self.n = self.n+1
            if self.n < 3000:
                return True
            else:
                print ('maxnum = '+str(self.n))
                return False
        
        except Exception as e:
            print (e)

    def on_error(self, status_code):
        #print >> sys.stderr, 'Encountered error with status code:', status_code
        return True # Don't kill the stream

    def on_timeout(self):
        #print >> sys.stderr, 'Timeout...'
        return True # Don't kill the stream

#initialize stopWords
stopWords = []
 
#starting the function
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end
 
#starting the function
def getStopWordList(stopWordListFileName):
#read the stopwords file and build a list
    stopWords = []
    stopWords.append('TWITTER_USER')
    stopWords.append('URL')
 
    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end
 
#starting the function
def getFeatureVector(tweet):
    
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector
#end

# Here I am obtaining the positive and negative tweets -

def mainPos():
    # Variables that contains the user credentials to access Twitter API
    consumer_key = "432nTSuut6lzuYXx68S2MUInR"
    consumer_secret = "hOvxCC8AyIq0gFcxNpwtxBm8LOX2oqlWb03Q3zpzAUL9ntmQaR"
    access_token = "795845870344404993-OmppJOhddsDcbxZvqG8odTCcxhYMakS"
    access_token_secret = "DE62fDP6hwoKNvQZK7BPqpvJsYKoVDECsW0Hh6aFVAN5K"


    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth) 

    print ("Establishing stream...\n")

    PosTweets = tweepy.streaming.Stream(auth, CustomStreamListener(maxnum=0))

    print ('done')
    setTerms = Emoticons.POSITIVE

    PosTweets.filter(follow = USERS , track = setTerms, languages=["en"])

    
# Here I obtain the negative tweets - I also do some cleaning of the tweet in the function before save it in the file 
def mainNEG():
    consumer_key = "432nTSuut6lzuYXx68S2MUInR"
    consumer_secret = "hOvxCC8AyIq0gFcxNpwtxBm8LOX2oqlWb03Q3zpzAUL9ntmQaR"
    access_token = "795845870344404993-OmppJOhddsDcbxZvqG8odTCcxhYMakS"
    access_token_secret = "DE62fDP6hwoKNvQZK7BPqpvJsYKoVDECsW0Hh6aFVAN5K"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    print ("Establishing stream...\n")

    #Calling the Function for the dataset with the Negative tweets
    NegTweets = tweepy.streaming.Stream(auth, CustomStreamListenerNEG(maxnum=0))

    print ('done')
    setTermsNEG = Emoticons.NEGATIVE

    NegTweets.filter(follow=USERS, track=setTermsNEG, languages=["en"])

    
def Positive():
    fp = open('TrainedTweets.txt', 'r')
    line = fp.readline()
    
    st = open('StopWords.txt', 'r')
    stopWords = getStopWordList('StopWords.txt')
    
    while line:
        featureVector = getFeatureVector(line)
        #print featureVector
        line = fp.readline()         
    
if __name__ == '__main__':
    try:
        mainPos()
        mainNEG()

        
    except KeyboardInterrupt:
        print ("Disconnecting from Twitter... ",)
        print ("Done")
        
        
        
        
