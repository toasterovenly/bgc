import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import http
from tryagain import retries

username = "DarthEd"
commands = {
	"collection": "collection?",
}
filters = {
	"own": "own=1",
	"boardgames": "subtype=boardgame",
	"expansions": "subtype=boardgameexpansion",
	"noexpansions": "excludesubtype=boardgameexpansion",
	"username": "username="+username,
}
baseurl = "http://www.boardgamegeek.com/xmlapi2/"
urls = {
	"boardgames": baseurl + commands["collection"] + filters["username"] + "&" + filters["own"] + "&" + filters["noexpansions"],
	"expansions": baseurl + commands["collection"] + filters["username"] + "&" + filters["own"] + "&" + filters["expansions"],
}

def waitFunc(n):
	out = 2 ** (n-1) # 1,2,4,8,16
	print("retrying in " + str(out))
	return out

@retries(max_attempts=5, wait=waitFunc)
def getCollection():
	result = urllib.request.urlopen(urls["boardgames"])\
	print(result.code, result.reason)
	if result.code == http.HTTPStatus.ACCEPTED.value:
		raise Exception(result.reason)
	else:
		return result.read()

collection = getCollection()
if isinstance(collection, bytes):
	with open("bgc_dump.xml", "w") as text_file:
		collection = str(collection,'utf-8')
		text_file.write(collection)
		# print(str(collection))
		root = ET.fromstring(collection)
		xmlstr = ET.tostring(root)
		# text_file.write(xmlstr)
