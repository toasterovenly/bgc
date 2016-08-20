import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import http
from tryagain import retries
import errno
import os
import time

################################################################################

username = "toasterovenly"
commands = {
	"collection": "collection?",
	"thing": "thing?",
	"user": "user?",
}
filters = {
	"own": "own=1",
	"boardgames": "subtype=boardgame",
	"expansions": "subtype=boardgameexpansion",
	"noexpansions": "excludesubtype=boardgameexpansion",
	"username": "username="+username,
	"id": "id=",
	"stats": "stats=1",
	"brief": "brief=1",
}
baseurl = "http://www.boardgamegeek.com/xmlapi2/"
urls = {
	"myBoardgames": baseurl + commands["collection"]
		+ filters["username"] + "&"
		+ filters["brief"] + "&"
		+ filters["own"] + "&"
		+ filters["noexpansions"],
	"myExpansions": baseurl + commands["collection"]
		+ filters["username"] + "&"
		+ filters["stats"] + "&"
		+ filters["own"] + "&"
		+ filters["expansions"],
	"games": baseurl + commands["thing"]
		+ filters["stats"] + "&"
		+ filters["id"],
	"myProfile": baseurl + commands["user"]
		+ filters["username"],
}

################################################################################

def waitFunc(n):
	out = 2 ** (n-1) # 1,2,4,8,16
	print("retrying in " + str(out))
	return out

@retries(max_attempts=5, wait=waitFunc, exceptions=http.client.ResponseNotReady)
def getUrl(url, message):
	message = message or ""
	result = urllib.request.urlopen(url)
	print(result.code, result.reason, message)
	if result.code == http.HTTPStatus.ACCEPTED.value:
		raise http.client.ResponseNotReady(result.reason)
	elif result.code == http.HTTPStatus.OK.value:
		return result.read()

def getRoot(someBytes):
	if isinstance(someBytes, bytes):
		someBytes = str(someBytes,'utf-8')
		return ET.fromstring(someBytes)
	else:
		return None

def dumpToFile(someBytes, fileName):
	return # for debugging, remove this line
	with open(fileName, "w", encoding='utf-8') as text_file:
		someBytes = str(someBytes,'utf-8')
		text_file.write(someBytes)

def getHomeRules():
	tree = ET.parse("home_rules.xml")
	if tree:
		return tree.getroot()

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def exportToCsv(gameData):
	lines = []
	for game in gameData:

		line = []
		line.append(game["name"])
		line.append(game["eMinplayers"])
		line.append(game["minplayers"])
		line.append(game["maxplayers"])
		line.append(game["eMaxplayers"])
		line.append(game["eMinplaytime"])
		line.append(game["minplaytime"])
		line.append(game["maxplaytime"])
		line.append(game["eMaxplaytime"])
		line.append(game["weight"])
		line.append(game["yearpublished"])

		# convert to csv
		fileLine = ""
		for v in line:
			fileLine += v + "\t"
		fileLine = fileLine[:-1]
		lines.append(fileLine)

	mkdir_p("output")
	with open("output/collection_" + username + ".csv", "w", encoding='utf-8') as text_file:
		for line in lines:
			text_file.write(line + "\n")

################################################################################

collection = getUrl(urls["myBoardgames"], "get collection")
root = getRoot(collection)
# dumpToFile(collection, "collection.xml")

gameIds = ""
gameData = []
for item in root:
	thing = {
		"id": item.get("objectid"),
		"name": item.find("name").text,
	}
	gameData.append(thing)
	gameIds += str(thing["id"]) + ","
gameIds = gameIds[:-1]
games = getUrl(urls["games"] + gameIds, "get full game data")
dumpToFile(games, "allDataForCollection.xml")
games = getRoot(games)

eCollection = getUrl(urls["myExpansions"], "get expansions in collection")
eRoot = getRoot(eCollection)
dumpToFile(eCollection, "eCollection.xml")

print("")

i = 0
for game in games:
	data = gameData[i]
	data["minplayers"] = data["eMinplayers"] = game.find("minplayers").get("value")
	data["maxplayers"] = data["eMaxplayers"] = game.find("maxplayers").get("value")
	data["minplaytime"] = data["eMinplaytime"] = game.find("minplaytime").get("value")
	data["maxplaytime"] = data["eMaxplaytime"] = game.find("maxplaytime").get("value")
	data["yearpublished"] = game.find("yearpublished").get("value")
	data["weight"] = game.find("statistics/ratings/averageweight").get("value")

	print(gameData[i]["name"])

	expansions = game.findall("link[@type='boardgameexpansion']")
	for e in expansions:
		eId = e.get("id")
		eFromCollection = eRoot.findall("item[@objectid='" + eId + "']")
		if len(eFromCollection) > 0:
			eFromCollection = eFromCollection[0]
			name = eFromCollection.find("name").text
			print("\t" + name)
			stats = eFromCollection.find("stats")
			data["eMinplayers"] = min(data["eMinplayers"], stats.get("minplayers"))
			data["eMaxplayers"] = max(data["eMaxplayers"], stats.get("maxplayers"))
			data["eMinplaytime"] = min(data["eMinplaytime"], stats.get("minplaytime"))
			data["eMaxplaytime"] = max(data["eMaxplaytime"], stats.get("maxplaytime"))
	i += 1

	# read homerules and adjust stats

exportToCsv(gameData)
