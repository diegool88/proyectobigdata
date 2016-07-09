import facebook # pip install facebook-sdk
import json
import time

###API FACEBOOK########################
akey = "869614083168342"
asecret = "4659fed15da699d1c05da51f2e267382"
atoken = "869614083168342|VCenQQofH_iEwiMsdEtCYbhN2yM"
#####################################
###List of FB Pages to search in####
pages = ["MunicipioQuito","ObrasQuito","ecuavisa","rts.quito","elnoticierotc","ultimasnoticiasec","comunidadquitoecuavisa"]

# A helper function to pretty-print Python objects as JSON
def pp(o):
	print json.dumps(o, indent=1)

def get_json_obj(o):
	return json.loads(json.dumps(o, indent=1))

# Create a connection to the Graph API with your access token
g = facebook.GraphAPI(atoken)

# Get Info of each page
for item in pages:
	#pp(g.get_object(item))
	#pp(g.get_connections(get_json_obj(g.get_object(item))['id'],'feed'))
	feeds = get_json_obj(g.get_connections(get_json_obj(g.get_object(item))['id'],'feed'))['data']
	tagged = get_json_obj(g.get_connections(get_json_obj(g.get_object(item))['id'],'tagged'))['data']
	#print feeds
	time.sleep(10)
	for feed in feeds:
		print "Feed id: " + feed['id'] + " has the following JSON Object: "
		print feed['message']
		print "Available comments as follows: "
		comments = get_json_obj(g.get_connections(feed['id'],'comments'))['data']
		for comment in comments:
			print "Comment id: " + comment['id'] + " has the following JSON Object: "
			print comment['message']
		#time.sleep(10)
