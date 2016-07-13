# This python script help us to clean the harvested tweets and facebook posts to get just those that can give us any value to our project
# Author: Diego Flores
# Packages/Libraries import
import couchdb
import urllib2
import json
import random
import math
import time
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from nltk import tokenize
from textblob import TextBlob
from textblob.exceptions import *
from datetime import datetime

#Set category function
def set_category(json, category):
  json.value['categoria'] = category
  return json

#Get Random Geo Location for Facebook Posts and empty Tweets Geo Data within Quito limits
def get_random_geo():
  lat = random.uniform(-78.586922,-78.274155)
  lon = random.uniform(-0.395161, 0.021973)
  return (lat, lon)

#Main function
def main():
  #Init all category arrays
  obr_list = []

  seg_list = []

  tra_list = []

  sal_list = []

  lim_list = []

  #Load all category files
  with open('obr.txt','r') as txtfile:
    obr_list = [w for w in txtfile]
    txtfile.close()

  with open('seg.txt','r') as txtfile:
    seg_list = [w for w in txtfile]
    txtfile.close()

  with open('tra.txt','r') as txtfile:
    tra_list = [w for w in txtfile]
    txtfile.close()

  with open('lim.txt','r') as txtfile:
    lim_list = [w for w in txtfile]
    txtfile.close()

  #Set DB configuration and variables
  server = couchdb.Server('http://localhost:5984/')
  server.resource.credentials = ('admin','admin')
  db_tweets = server['quito_tweets']
  db_facebook = server['quito_fb_posts']
  #rows_t = db_tweets.view('proj/view_df_vm_tweets',limit=5000)
  #Get all filtered tweets Couch DB View
  rows_t = db_tweets.view('proj/view_df_vm_tweets')
  #rows_f = db_facebook.view('proj/view_df_vm_facebook',limit=5000)
  #Get all filtered facebook feed Couch DB View
  rows_f = db_facebook.view('proj/view_df_vm_facebook')
  
  #Twitter classification
  rows_t_obr = [set_category(t,'obr') for t in rows_t.rows if any(word in t.value['texto'].encode('utf-8') for word in obr_list)]
  rows_t_seg = [set_category(t,'seg') for t in rows_t.rows if any(word in t.value['texto'].encode('utf-8') for word in seg_list)]
  rows_t_tra = [set_category(t,'tra') for t in rows_t.rows if any(word in t.value['texto'].encode('utf-8') for word in tra_list)]
  rows_t_lim = [set_category(t,'lim') for t in rows_t.rows if any(word in t.value['texto'].encode('utf-8') for word in lim_list)]

  print 'Obras Publicas Twitter: ' + str(len(rows_t_obr))
  print 'Seguridad Twitter: ' + str(len(rows_t_seg))
  print 'Transito Twitter: ' + str(len(rows_t_tra))
  print 'Limpieza Twitter: ' + str(len(rows_t_lim))

  #Facebook classification
  rows_f_obr = [set_category(f,'obr') for f in rows_f.rows if any(word in f.value['texto'].encode('utf-8') for word in obr_list)]
  rows_f_seg = [set_category(f,'seg') for f in rows_f.rows if any(word in f.value['texto'].encode('utf-8') for word in seg_list)]
  rows_f_tra = [set_category(f,'tra') for f in rows_f.rows if any(word in f.value['texto'].encode('utf-8') for word in tra_list)]
  rows_f_lim = [set_category(f,'lim') for f in rows_f.rows if any(word in f.value['texto'].encode('utf-8') for word in lim_list)]

  print 'Obras Publicas Facebook: ' + str(len(rows_f_obr))
  print 'Seguridad Facebook: ' + str(len(rows_f_seg))
  print 'Transito Facebook: ' + str(len(rows_f_tra))
  print 'Limpieza Facebook: ' + str(len(rows_f_lim))

  time.sleep(500)
  #Set Twitter and facebook arrays
  rows_t = rows_t_obr + rows_t_seg + rows_t_tra + rows_t_lim  
  rows_f = rows_f_obr + rows_f_seg + rows_f_tra + rows_f_lim

  #Create or set DB
  try:
    db_master = server.create('db_master')
  except:
    db_master = server['db_master']

  #Init SentimentIntensityAnalyzer
  sid = SentimentIntensityAnalyzer()
  
  #print retrieved rows after cleaning
  print rows_t
  print rows_f

  for row_t in rows_t:
    #Init Facebook Feed sentences and tokenize
    sentences_t = []
    sentences_t = tokenize.sent_tokenize(row_t.value['texto'])

    #Translate Text and get Compound Polarity value
    average = 0
    for sentence in sentences_t:
      try:
        print '==============================================='
        print('Espanol: ' + sentence)
        translation = TextBlob(sentence)
        print('Ingles: ' + str(translation.translate(to='en')))
        ss = sid.polarity_scores(str(translation.translate(to='en')))
        average += ss['compound']
        
        for k in sorted(ss):
          print('{0}: {1}, '.format(k, ss[k]))
        print '==============================================='
      except NotTranslated:
        pass

    #Set necessary variables
    row_t.value['intensidad'] = math.ceil((100*average / (len(sentences_t) if len(sentences_t) > 0 else 1)))
    row_t.value['origen'] = str('twitter')
    date = datetime.strptime(row_t.value['fecha'],'%a %b %d %H:%M:%S +0000 %Y')#.replace(tzinfo=pytz.UTC)
    date_string = date.strftime('%Y-%m-%d')
    row_t.value['fecha'] = str(date_string)
    if row_t.value['coordenadas'] is None:
      lat, lon = get_random_geo()
      row_t.value['coordenadas'] = {'type':'Point', 'coordinates':[lat,lon]}

    try:
      #Save to the DB
      doc_t = db_master.save(row_t.value)
    except:
      print 'Error Saving Register ' + row_t.value['codigo']
      pass

  for row_f in rows_f:
    #Init Facebook Feed sentences and tokenize
    sentences_f = []
    sentences_f = tokenize.sent_tokenize(row_f.value['texto'])

    #Translate Text and get Compound Polarity value
    average = 0
    for sentence in sentences_f:
      try:
        print '==============================================='
        print('Espanol: ' + sentence)
        translation = TextBlob(sentence)
        print('Ingles: ' + str(translation.translate(to='en')))
        ss = sid.polarity_scores(str(translation.translate(to='en')))
        average += ss['compound']
        for k in sorted(ss):
          print('{0}: {1}, '.format(k, ss[k]))
        print '==============================================='
      except NotTranslated:
        pass

    #Set necessary variables
    row_f.value['intensidad'] = math.ceil((100*average / (len(sentences_f) if len(sentences_f) > 0 else 1)))
    row_f.value['origen'] = str('facebook')
    date = datetime.strptime(row_f.value['fecha'],'%Y-%m-%dT%H:%M:%S+0000')
    date_string = date.strftime('%Y-%m-%d')
    row_f.value['fecha'] = str(date_string)
    if row_f.value['coordenadas'] is None:
      lat, lon = get_random_geo()
      row_f.value['coordenadas'] = {'type':'Point', 'coordinates':[lat,lon]}

    try:
      #Save to the DB
      doc_f = db_master.save(row_f.value)
    except:
      print 'Error Saving Register ' + row_f.value['codigo']
      pass

#Main function call
if __name__ == '__main__': main() 