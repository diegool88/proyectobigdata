import couchdb
import urllib2
import json
import threading
import os
import time

class NoMoreRows(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FacebookPostsHarvester:
    #Resource Path Array
    search_path = ['/feed/','/comments/']
    #Thread Lock
    lock = threading.RLock()

    def __init__(self, f_akey, f_asecret, root_url, facebook_pages, db_url, db_user, db_password, db_name):
        self.f_akey = f_akey
        self.f_asecret = f_asecret
        self.root_url = root_url
        self.search_path = FacebookPostsHarvester.search_path
        self.facebook_pages = facebook_pages
        self.db_user = db_user
        self.db_password = db_password
        self.db_url = db_url
        self.db_name = db_name

    def initiate_harvesting(self):
        self.initiate_db()
        for page in self.facebook_pages:
            #with FacebookPostsHarvester.lock:
            print 'Harvesting Posts and Comments of page ' + page + '....'
            # Page Posts/Feed
            request_url = self.create_rest_url_request(None, page)
            json_data = self.render_to_json(request_url)
            self.save_post_to_db(json_data)

    def initiate_db(self):
        self.server = couchdb.Server(self.db_url)  #('http://115.146.93.184:5984/')
        self.server.resource.credentials = (self.db_user,self.db_password)
        try:
            self.db = self.server.create(self.db_name)
        except:
            self.db = self.server[self.db_name]

    def create_rest_url_request(self, post_id, page_name):
        request_url = ""
        if page_name:
            request_url = self.root_url + "/" + page_name + self.search_path[0] + "?limit=100&key=value&access_token=" + self.f_akey + "|" + self.f_asecret
        else:
            request_url = self.root_url + "/" + post_id + self.search_path[1] + "?limit=100&key=value&access_token=" + self.f_akey + "|" + self.f_asecret
        return request_url

    def render_to_json(self, request_url):
        #render graph url call to JSON
        web_response = urllib2.urlopen(request_url)
        readable_page = web_response.read()
        json_data = json.loads(readable_page)   
        return json_data

    def save_post_to_db(self, json_data):
        #print json_post_data
        #print str(JSONPOSTDATA)
        dictFacebookPosts = json_data['data']
        for item in dictFacebookPosts:
            try:
                if item["message"] is None:
                    continue
                item["_id"] = str(item['id'])
                doc = self.db.save(item)
                print "SAVED" + str(doc) +"=>" + str(item)
                request_url = self.create_rest_url_request(str(item['id']),None)
                json_data = self.render_to_json(request_url)
                self.save_comments_to_db(str(item['id']), json_data)
                ###Get all comments of the post###
                #get_fb_data(akey, asecret, graph_url, str(item['id']) + comments_path)
            except:
                os.system('clear')
                print "Post with id: " + item['id'] + " Already exists!..."
                request_url = self.create_rest_url_request(str(item['id']),None)
                json_data = self.render_to_json(request_url)
                self.save_comments_to_db(str(item['id']), json_data)
                pass
            #return True
        #Loop to next page
        #with FacebookPostsHarvester.lock:
        try:        
            if 'paging' in json_data and 'next' in json_data['paging']:
                nextPage = json_data['paging']['next']
                json_data_np = self.render_to_json(nextPage)
                self.save_post_to_db(json_data_np)
            else:
                raise NoMoreRows('Error looping JSON, there is no more data available')
        except NoMoreRows:
            print "Error looping JSON, there is no more data available"
            pass

    def save_comments_to_db(self, post_id, json_data):
        dictFacebookComments = json_data['data']
        for item in dictFacebookComments:
            try:
                item["_id"] = str(item['id'])
                item["post_id"] = str(post_id)
                doc = self.db.save(item)
                print "SAVED" + str(doc) +"=>" + str(item)
            except:
                os.system('clear')
                print "Comment with id: " + item['id'] + " Already exists!..."
                #time.sleep(1)
                pass
        #Loop to next page
        #with FacebookPostsHarvester.lock:
        try:        
            if 'paging' in json_data and 'next' in json_data['paging']:
                nextPage = json_data['paging']['next']
                json_comment_np = self.render_to_json(nextPage)
                self.save_comments_to_db(post_id, json_comment_np)
            else:
                raise NoMoreRows('Error looping JSON, there is no more data available')
        except NoMoreRows:
            print "Error looping JSON, there is no more data available"
            pass

def main():
    ###API FACEBOOK########################
    akey = "869614083168342"
    asecret = "4659fed15da699d1c05da51f2e267382"
    #####################################
    ###List of FB Pages to search in####
    pages = ["MunicipioQuito","ObrasQuito","ecuavisa","rts.quito","elnoticierotc","ultimasnoticiasec","comunidadquitoecuavisa"]
    #pages = ["comunidadquitoecuavisa"]
    ###Root URL of Facebook Graph###
    graph_url = "https://graph.facebook.com"
    #Create Facebook Harvest Object
    harvest_object = FacebookPostsHarvester(akey, asecret, graph_url, pages, 'http://localhost:5984/','admin','admin','quito_fb_posts')
    while True:
        harvest_object.initiate_harvesting()
        pass
    #harvest_object.initiate_harvesting()

if __name__ == "__main__": main()


