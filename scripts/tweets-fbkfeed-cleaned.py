# This python script help us to clean the harvested tweets and facebook posts to get just those that can give us any value to our project
# Author: Diego Flores
# from googleapiclient.discovery import build
import couchdb
import urllib2
import json

pos_tweets = [('I love this car', 'positive'),
              ('This view is amazing', 'positive'),
              ('I feel great this morning', 'positive'),
              ('I am so excited about the concert', 'positive'),
              ('He is my best friend', 'positive')]

neg_tweets = [('I do not like this car', 'negative'),
              ('This view is horrible', 'negative'),
              ('I feel tired this morning', 'negative'),
              ('I am not looking forward to the concert', 'negative'),
              ('He is my enemy', 'negative')]

tweets = []
for (words, sentiment) in pos_tweets + neg_tweets:
    words_filtered = [e.lower() for e in words.split() if len(e) >= 3] 
    tweets.append((words_filtered, sentiment))

word_features = get_word_features(get_words_in_tweets(tweets))

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
      all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

def render_to_json(request_url):
        #render graph url call to JSON
        web_response = urllib2.urlopen(request_url)
        readable_page = web_response.read()
        json_data = json.loads(readable_page)   
        return json_data

def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

def main():
	#google_service = build('translate', 'v2', developerKey='AIzaSyCAN1nFmkgIWhQ-74XB9Or_Bks-D25OGSQ')
	string = "Esto es injusto, no permitire que nos maltraten"
	#API URL
	api_url = "http://text-processing.com/api/sentiment/"
	json_object = render_to_json(api_url + "language=spanish&text=" + string)
	string_to_translate = "Este viernes ire al cine a ver la mejor pelicula del mundo"
	#json_object = google_service.translations().list(
	#	source='sp',
	#	target='en',
	#	q=[string_to_translate]
	#	).execute()
	
	print json_object

if __name__ == '__main__': main() 