import re
import string
from nltk import sent_tokenize,word_tokenize

# functions to clean the tweets off emoticons , non-ascii characters , links , hashes ...

NEGATIONS_PATTERN = r'\b#{0,1}(no|not|isnt|isn\'t|isn;t|don\'t|won\'t|couldn\'t|can\'t|didn\'t|not|didnt|didn;t' \
                                 r'|dont|don;t|don t|won t|can;t|cant|can t|doesn\'t|doesnt|doesn t|doesn;t|cannot|did not|not)\b'
CAPITALS_PATTERN = r'\b[A-Z]{3,}\b'
REFERENCE_PATTERN = r'(@\w+|@\D\w+|@\d\w+)'
NEGATIONS = ['no', 'don\'t', 'won\'t', 'couldn\'t', 'can\'t', 'didn\'t', 'not', 'could not', 'cannot']

POS_SMILEY_PATTERN = r'(:-\)|:-D|:-\)\)|:\)\)|\(:|:\)|:D|=\)|;-\)|XD|=D|=]|;D|:]|:o\))'
NEG_SMILEY_PATTERN = r'(:-\\|:-\(|:-\(\(|:\(|:o|:O|D:|=/|=\(|:\'\(|:\'-\(|:\\|:/|:S)'  # bug fix: ! --> |
SMILEY_FULL_PATTERN = '(:-\)|:-\(|:-\(\(|:-D|:-\)\)|:\)\)|\(:|:\(|:\)|:D|=\)|;-\)|XD|=D|:o|' \
                                   ':O|=]|D:|;D|:]|=/|=\(!:\'\(|:\'-\(|:\\|:/|:S|<3)'

non_word_chars_removed=[]
tweet = ""
sentence_index = 0
new_hashtag_list = []
inal_tweet = ''
uppercase_words_per_sentence = []
stop_words_removed = []
found_negations = False
uppercase_words_per_sentence = []
laughter = []
negating_terms = []
abbreviations = []


# starting the function
def getStopWordList(stopWordListFileName):
    # read the stopwords file and build a list
    stopWords = []
    # stopWords.append('TWITTER_USER')
    stopWords.append('URL')

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords


# end


def remove_non_ascii_chars(tweet):
    """
    to solve problem with extra / weird characters when getting data from database
    :return:
    """
    clean_tweet = str(filter(lambda x: x in string.printable, tweet))
    clean_text = str(filter(lambda x: x in string.printable, clean_tweet))
    return clean_text


def identify_and_remove_emoticons(tweet_sentence):

    clean_tweet_sent = re.sub(SMILEY_FULL_PATTERN, '', tweet_sentence)

    return clean_tweet_sent

def split_sentences(tweet):
    """
        Tokenize sentences with nltk -- will c if it needs changing
        :return:None
    """
    sentences = sent_tokenize(tweet)  # this gives us a list of sentences
    return sentences


def split_words(tweet_sentence):
    tweet_words = []

    try:
            return word_tokenize(tweet_sentence.encode('utf-8'))
    except:
            return word_tokenize(tweet_sentence)



def remove_links(tweet_sentence):
    """
        remove http links, stores them in a list and then removes them from tweet text
        :return:
    """
    clean_sentence = tweet_sentence.replace("URL" , '')
    return clean_sentence

def remove_reference(tweet_sentence):
    """
        Stores reference in a list and then removes it from tweet text
        :return:
    """
    clean_sentence = re.sub('(#|@\w+|@\D\w+|@\w+\D|#\w+|#\D\w+|#\w+\D)', '', tweet_sentence)
    return clean_sentence

def remove_special_chars(tweet_sentence):
    """
        Will store and remove any characters like '?' '!!!' '...' to see if we can infer some meaning for sentiment
        :return:
    """
    non_word_chars_removed.append(re.findall(r'\W|\d|_', tweet_sentence))
    clean_sentence = re.sub(r'\W|\d|_', ' ', tweet_sentence)
    return clean_sentence


def remove_stop_words(tweet_sentence):
    """
        Remove stop words - both from ntlk.stop_words and from stop_words_additional
        :return:
    """
    tweet_words = split_words(tweet_sentence)
    stopwords = getStopWordList('StopWords.txt')
    for word in tweet_words:
          if word in stopwords:
                    tweet_sentence.strip(word)
    return tweet_sentence

rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE);
def rpt_repl(match):
	return match.group(1)+match.group(1)

def processRepeatings(text):
	return re.sub( rpt_regex, rpt_repl, text )

def fix_space(tweet_sentences):
    """
        reduces multiple whitespace characters into a single space.
        :return:
    """
    clean_list = []
    for sentence in tweet_sentences:
        clean_sentence = ' '.join(sentence.split())
        clean_list.append(clean_sentence)
    return clean_list


def convert_to_lower(tweet_word):
    """convert every word to lowercase to have better results in matching
        :return:None
    """
    return tweet_word.lower()


def handle_hashtags(self):
    """
        Tto try get the aspect out of hashtags -- just to have some comparison for pos tag aspect
        assumption is that hashtag will be splittable by capitals //Pascal or camelCase like
        :return:None
    """
    for hashtag in self.tweet.hash_list:
        self.new_hashtag_list.append([a for a in re.split(r'([A-Z][a-z]*\d*)', str(hashtag)) if a])


def set_final_tweet(self):
    self.final_tweet = " ".join(self.tweet.words)
    self.tweet.processed_tweet = self.final_tweet


def identify_negations(self):
    """
        Preliminary negation check. If negations are found, we set flag to True, so that we know we should check
        afterwards
        :return:
        """
    find_negations = re.findall(NEGATIONS_PATTERN, str(self.tweet.text).lower())
    if None != find_negations and find_negations != []:
        self.found_negations = True
        # print "NEGATIONS:::", find_negations, self.found_negations


def has_capitals(self):
    """
        keep all capitalized words along with the sentence index they belong
        :return:None
        """
    for s in self.tweet.sentences:
        if self.tweet.sentences.__len__() > 1:
            for word in s.split(' '):
                if word.isupper():
                    self.tweet.uppercase_words_per_sentence.append([self.tweet.sentences.index(s), word])
        else:  # todo: rethink about it...
            if s.isupper():
                self.tweet.uppercase_words_per_sentence.append([self.tweet.sentences.index(s), s])


def has_negations(self, word):
    """
        :param word:
        :return: :rtype:
    """
    return re.findall(NEGATIONS_PATTERN, word.lower())


def keep_negated_term(self, each, word):
    try:
        self.negating_terms.append(word[word.index(each) + 1])
    except IndexError:
        try:
            if word.__len__() > 1:
                self.negating_terms.append(word[word.index(each) - 1])

        except AttributeError:
            pass


def handle_negations(self):
    """ keep position of negation in sentence and negation
            final list should look like: [[1, 'no'],[4, 'not']] etc
    """
    if self.found_negations:
        for word in self.tweet.words:
            if type(word) == list:
                for each in word:
                    exists = self.has_negations(each)
                    if exists != [] and None != exists:
                        self.tweet.negations.append((each, word.index(each)))
                        self.keep_negated_term(each, word)
            else:
                for word in self.tweet.words[0]:
                    exists = self.has_negations(word)
                    if exists != [] and None != exists:
                        self.tweet.negations.append((word, self.tweet.words[0].index(word)))
                        self.keep_negated_term(word, self.tweet.words[0])
        if self.tweet.negations.__len__() > 0:
            pass
        else:
            pass


def get_tweet_words_in_a_single_list(self):
    """
        To overcome the problem of self.tweet.words = [[''],[''],...] or ['','','']
        :return: returns a single list of words
        :rtype:list
    """
    tweet_words = []
    try:
        if type(self.tweet.words[0]) == list:
            for each in self.tweet.words:
                tweet_words += each
        else:
            tweet_words = self.tweet.words
        return tweet_words
    except IndexError:
        return tweet_words

def cleanUp(sent):
    clean_sent = remove_links(sent)

    clean_sent = remove_reference(clean_sent)

    clean_sent = remove_special_chars(clean_sent)

    clean_sent = remove_stop_words(clean_sent)

    clean_sent = identify_and_remove_emoticons(clean_sent)
    return clean_sent


