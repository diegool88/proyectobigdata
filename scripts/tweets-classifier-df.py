# This python script help us to clean the harvested tweets and facebook posts to get just those that can give us any value to our project
# Author: Diego Flores
# from googleapiclient.discovery import build
import couchdb
import urllib2
import json
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from nltk import tokenize
from textblob import TextBlob
from textblob.exceptions import *

def main():
	#google_service = build('translate', 'v2', developerKey='AIzaSyCAN1nFmkgIWhQ-74XB9Or_Bks-D25OGSQ')
	#string = "Esto es injusto, no permitire que nos maltraten"
	#API URL
	#api_url = "http://text-processing.com/api/sentiment/"
	#json_object = render_to_json(api_url + "language=spanish&text=" + string)
	#string_to_translate = "Este viernes ire al cine a ver la mejor pelicula del mundo"
	#json_object = google_service.translations().list(
	#	source='sp',
	#	target='en',
	#	q=[string_to_translate]
	#	).execute()
	#print json_object
  n_instances = 100
  subj_docs = [(sent, 'subj') for sent in subjectivity.sents(categories='subj')[:n_instances]]
  obj_docs = [(sent, 'obj') for sent in subjectivity.sents(categories='obj')[:n_instances]]

  train_subj_docs = subj_docs[:80]
  test_subj_docs = subj_docs[80:100]
  train_obj_docs = obj_docs[:80]
  test_obj_docs = obj_docs[80:100]
  training_docs = train_subj_docs+train_obj_docs
  testing_docs = test_subj_docs+test_obj_docs
  sentim_analyzer = SentimentAnalyzer()
  all_words_neg = sentim_analyzer.all_words([mark_negation(doc) for doc in training_docs])
  unigram_feats = sentim_analyzer.unigram_word_feats(all_words_neg, min_freq=4)

  sentim_analyzer.add_feat_extractor(extract_unigram_feats, unigrams=unigram_feats)
  training_set = sentim_analyzer.apply_features(training_docs)
  test_set = sentim_analyzer.apply_features(testing_docs)
  trainer = NaiveBayesClassifier.train
  classifier = sentim_analyzer.train(trainer, training_set)
  
  for key,value in sorted(sentim_analyzer.evaluate(test_set).items()):
    print('{0}: {1}'.format(key, value))

  #http://localhost:5984/quito_tweets/_design/proj/_view/ecuadorTweets?limit=10
  server = couchdb.Server('http://localhost:5984/')  #('http://115.146.93.184:5984/')
  server.resource.credentials = ('admin','admin')
  db_tweets = server['quito_tweets']
  db_facebook = server['quito_fb_posts']
  rows_t = db_tweets.view('proj/filtered_tweets',limit=10)
  rows_f = db_facebook.view('proj/filtered_fbk_feed',limit=10)
  #rows = db.view('proj/ecuadorTweets',limit=100)
  sid = SentimentIntensityAnalyzer()
  #print rows.rows

  for row_t, row_f in zip(rows_t.rows, rows_f.rows):
    #print row
    sentences_t = []
    sentences_t = tokenize.sent_tokenize(row_t.value['text'])
    sentences_f = []
    sentences_f = tokenize.sent_tokenize(row_f.value['message'])

    for sentence in sentences_t:
      try:
        print '==============================================='
        print('Espanol: ' + sentence)
        translation = TextBlob(sentence)
        print('Ingles: ' + str(translation.translate(to='en')))
        ss = sid.polarity_scores(str(translation.translate(to='en')))
        for k in sorted(ss):
          print('{0}: {1}, '.format(k, ss[k]))
        print '==============================================='
      except NotTranslated:
        pass

    for sentence in sentences_f:
      try:
        print '==============================================='
        print('Espanol: ' + sentence)
        translation = TextBlob(sentence)
        print('Ingles: ' + str(translation.translate(to='en')))
        ss = sid.polarity_scores(str(translation.translate(to='en')))
        for k in sorted(ss):
          print('{0}: {1}, '.format(k, ss[k]))
        print '==============================================='
      except NotTranslated:
        pass



    #sentim_analyzer.evaluate()


if __name__ == '__main__': main() 