
from textblob import TextBlob


with open("CollectedTweetsFirstBatch.txt", "r") as input_file:
    for line in input_file:

        tweet = line.split('|')

        # Strips out newline if it has one at the end
        tweet[-1] = tweet[-1].strip()


        tweet_text = tweet[0].decode('utf-8').strip()

        print tweet_text
        #tweet[0].encode('ascii', 'ignore')
        analysis = TextBlob(tweet_text)
        print analysis.sentiment
        print analysis.sentiment.polarity
        if analysis.sentiment.polarity > 0:
            print 'positive'
        elif analysis.sentiment.polarity == 0:
            print  'neutral'
        else:
            print  'negative'