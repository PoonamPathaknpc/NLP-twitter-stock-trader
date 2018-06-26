
import csv
import re
import nltk
import pickle
import nltk.classify.util
import Tweet_CleanUp
from nltk.classify import MaxentClassifier



# initialize stopWords
stopWords = []
training_set = []
test_set = []
st = open('StopWords.txt', 'r')
stopWords = Tweet_CleanUp.getStopWordList('StopWords.txt')




# starting the function
def replaceTwoOrMore(s):
    # look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
# end

# starting the function
def getFeatureVector(tweet):
    featureVector = []

    clean_tweet = Tweet_CleanUp.remove_non_ascii_chars(tweet)

    sentences = Tweet_CleanUp.split_sentences(clean_tweet)

    for sent in sentences:
        clean_sent = Tweet_CleanUp.cleanUp(sent)

        t_words = Tweet_CleanUp.split_words(clean_sent)

        for word in t_words:


            word = Tweet_CleanUp.processRepeatings(word)

            word = Tweet_CleanUp.convert_to_lower(word)

            word = replaceTwoOrMore(word)

            featureVector.append(word)

    #print featureVector
    return featureVector

# end


# starting the function
def featureExtraction():

    # Here I am reading the tweets one by one and process it
    inpTweets = csv.reader(open('TrainedTweets.txt', 'r'), delimiter=',', quotechar='|')
    tweets = []

    for rTweet in inpTweets:

        sentiment = rTweet[0]
        tweet = rTweet[1]

        featureVector = getFeatureVector(tweet)
        tweets.append((featureVector, sentiment))
    # print "Printing the tweets con su sentiment"
    #print tweets
    return tweets  # Here I am returning the tweets inside the array plus its sentiment


# end




# print tweets

# Classifier
def get_words_in_tweets(tweets):
    all_words = []
    for (text, sentiment) in tweets:
        all_words.extend(text)
    return all_words


def get_word_features(wordlist):
    # This line calculates the frequency distrubtion of all words in tweets
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()

    # This prints out the list of all distinct words in the text in order
    # of their number of occurrences.
    return word_features


def extract_features(tweet):
    global classified_tweets
    classified_tweets = featureExtraction()
    settweet = set(tweet)
    features = {}
    word_features = get_word_features(get_words_in_tweets(classified_tweets))  # my list of many words
    for word in word_features:
        features['contains(%s)' % word] = (word in settweet)
    return features


def train_data_sets():
   global classified_tweets
   classified_tweets = featureExtraction()
   global training_set
   training_set = nltk.classify.apply_features(extract_features, classified_tweets)

   global test_set
   test_set = nltk.classify.apply_features(extract_features, classified_tweets[:250])

   #classifier = nltk.NaiveBayesClassifier.train(training_set)
   algorithm = nltk.classify.MaxentClassifier.ALGORITHMS[0]
   classifier = nltk.MaxentClassifier.train(training_set, algorithm,max_iter=3)

   return classifier

"""
#global classified_tweets
#classified_tweets = featureExtraction()

#Saving the Classifier
#MEM_classifier = train_data_sets()
#save_classifier = open("MEM.pickle","wb")
#pickle.dump(MEM_classifier, save_classifier)
#save_classifier.close()

#opening the classifier to calculate Accuracy

classifier_f = open("MEM.pickle", "rb")
MEM_classifier = pickle.load(classifier_f,encoding='latin1')
classifier_f.close()

#training_set = nltk.classify.apply_features(extract_features, classified_tweets)

#test_set = nltk.classify.apply_features(extract_features, classified_tweets[:250])
# calclulate accuracy
accuracy = nltk.classify.accuracy(MEM_classifier, training_set)

# Printing the accuracy
print (accuracy)

total = accuracy * 100
print ('MEM Accuracy for sentiment analysis: %4.2f' % total)

# Accuracy Test Set
accuracyTestSet = nltk.classify.accuracy(MEM_classifier, test_set)

# Printing the accuracy for the test set
print (accuracyTestSet)
totalTest = accuracyTestSet * 100
print ('\nMEM Accuracy for sentiment analysis with the Test Set: %4.2f' % totalTest)

print ('\nInformative features')
print (MEM_classifier.show_most_informative_features(n=15))
# **************************

var = ''
while (var != 'exit'):
    input = raw_input('\nPlease write a sentence to be tested sentiment. If you type - exit- the program will exit \n')
    print ('\n')
    if input == 'exit':
        print ('Exiting the program')
        var = 'exit'
        # break
    else:
        input = input.lower()
        input = input.split()

        print ('I think that the sentiment was ' + MEM_classifier.classify(extract_features(input)) + ' in that sentence.\n')
        #print (sorted(MEM_classifier.labels()))
        prob_dist = MEM_classifier.prob_classify(extract_features(input))


        p_pos = prob_dist.prob('positive')
        p_neg = prob_dist.prob('negative')
        print ('polarity is positve - ')
        print (p_pos)
        print ('negative -')
        print (p_neg)
"""