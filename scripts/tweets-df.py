
import couchdb
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json


###API ########################
ckey = "JYEpQsYMOaMqGarnHqax7oD46"
csecret = "uAZMbbauYqFIG9O3Z3kLKgaqHl5BrSlnXY8v0w8pwwr8DjTbdz"
atoken = "602223127-k6qGCjKQGFvj3cQI72rlmpVXu48mCSjYjXKjNZxH"
asecret = "3cfdKNo5spXV55R2N8aGWF5Wy68DLaQCQ32PhHAoQ2mqj"
#####################################

class listener(StreamListener):
    
    def __init__(self, instance_db):
        self.instance_db = instance_db

    def on_data(self, data):
        dictTweet = json.loads(data)
        try:
            dictTweet["_id"] = str(dictTweet['id'])
            doc = self.instance_db.save(dictTweet)
            print "SAVED" + str(doc) +"=>" + str(data)
        except:
            print "Already exists"
            pass
        return True
    
    def on_error(self, status):
        print status

class TweetsHarvester:
    #Static Content
    instance_count = 0

    def __init__(self, t_ckey, t_csecret, t_atoken, t_asecret, db_url, db_user, db_pass, db_name, h_map_coordinates, h_keyword):
        self.t_ckey = t_ckey
        self.t_csecret = t_csecret
        self.t_atoken = t_atoken
        self.t_asecret = t_asecret
        self.db_url = db_url
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name
        self.h_map_coordinates = h_map_coordinates
        self.h_keyword = h_keyword
        self.object_id = TweetsHarvester.instance_count
        TweetsHarvester.instance_count += 1

    def create_tweeter_connection(self):
        self.auth = OAuthHandler(self.t_ckey, self.t_csecret)
        self.auth.set_access_token(self.t_atoken, self.t_asecret)
        self.twitterStream = Stream(self.auth, listener(self.db))

    def create_database_connection(self):
        self.server = couchdb.Server(self.db_url)  #('http://115.146.93.184:5984/')
        self.server.resource.credentials = (self.db_user,self.db_pass)
        try:
            self.db = self.server.create(self.db_name)
        except:
            self.db = self.server[self.db_name]

    def initiate_harvesting(self):
        #Create connections
        self.create_database_connection()
        self.create_tweeter_connection()        
        #Begin Search
        print 'Search Criteria: ' + 'Coordinates: ' + ', '.join(map(str,self.h_map_coordinates)) + ', Words: ' + ', '.join(self.h_keyword)
        #self.twitterStream.filter(locations=self.h_map_coordinates,track=self.h_keyword)
        self.twitterStream.filter(locations=self.h_map_coordinates)
        print 'Harvesting for object_id: ' + self.object_id
  
def main():
    harvest_object = TweetsHarvester(ckey,csecret,atoken,asecret,'http://localhost:5984/','admin','admin','quito_tweets_filtered',[-78.586922,-0.205307,-78.203087,0.021973],['@vecinomario','quito','alcalde'])
    harvest_object.initiate_harvesting()

if __name__ == "__main__": main()
#auth = OAuthHandler(ckey, csecret)
#auth.set_access_token(atoken, asecret)
#twitterStream = Stream(auth, listener())

#'''========couchdb'=========='''
#server = couchdb.Server('http://localhost:5984/')  #('http://115.146.93.184:5984/')
#server.resource.credentials = ("admin","admin")
#try:
#    db = server.create('quito_tweets')
#except:
#    db = server['quito_tweets']
    
#'''===============LOCATIONS=============='''    

#twitterStream.filter(locations=[-78.586922,-0.205307,-78.203087,0.021973]) #Quito Norte y Valle de Tumbaco
#twitterStream.filter(track=['ecuador'])