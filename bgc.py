import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import http
from tryagain import retries
import errno
import os

################################################################################

username = "toasterovenly"
commands = {
	"collection": "collection?",
	"thing": "thing?",
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
		+ filters["brief"] + "&"
		+ filters["own"] + "&"
		+ filters["expansions"],
	"games": baseurl + commands["thing"]
		+ filters["stats"] + "&"
		+ filters["id"],
}

################################################################################

def waitFunc(n):
	out = 2 ** (n-1) # 1,2,4,8,16
	print("retrying in " + str(out))
	return out

@retries(max_attempts=5, wait=waitFunc, exceptions=http.client.ResponseNotReady)
def getUrl(url):
	result = urllib.request.urlopen(url)
	print(result.code, result.reason)
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
	with open(fileName, "w", encoding='utf-8') as text_file:
		someBytes = str(someBytes,'utf-8')
		text_file.write(someBytes)

def getHomeRules():
	tree = ET.parse("home_rules.xml")
	if tree:
		return tree.getroot()

def getExpansionsForGame(game):
	expansions = game.findall("link[@type='boardgameexpansion']")
	expansionIds = ""
	for ex in expansions:
		expansionIds += ex.get("id") + ","
	expansionIds = expansionIds[:-1]
	# print(expansionIds)
	expansions = getUrl(urls["games"] + expansionIds)
	gameName = game.find("name[@type='primary']").get("value")
	dumpToFile(expansions, "expansions/" + gameName + ".xml")
	return getRoot(expansions)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

################################################################################

collection = getUrl(urls["myBoardgames"])
root = getRoot(collection)
dumpToFile(collection, "collection.xml")

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
games = getUrl(urls["games"] + gameIds)
dumpToFile(games, "all.xml")
games = getRoot(games)

eCollection = getUrl(urls["myExpansions"])
eRoot = getRoot(eCollection)
dumpToFile(eCollection, "eCollection.xml")

i = 0
for game in games:
	data = gameData[i]
	data["minplayers"] = data["eMinplayers"] = game.find("minplayers").get("value")
	data["maxplayers"] = data["eMaxplayers"] = game.find("maxplayers").get("value")
	data["minplaytime"] = data["eMinplaytime"] = game.find("minplaytime").get("value")
	data["maxplaytime"] = data["eMaxplaytime"] = game.find("maxplaytime").get("value")
	data["yearpublished"] = game.find("yearpublished").get("value")
	data["weight"] = game.find("statistics/ratings/averageweight").get("value")

	expansions = getExpansionsForGame(game)
	for e in expansions:
		eId = e.get("id")
		eFromCollection = eRoot.findall("item[@objectid='" + eId + "']")
		if len(eFromCollection) > 0:
			eFromCollection = eFromCollection[0]
			name = eFromCollection.find("name").text
			# print(name + " is in collection")
			data["eMinplayers"] = min(data["eMinplayers"], e.find("minplayers").get("value"))
			data["eMaxplayers"] = max(data["eMaxplayers"], e.find("maxplayers").get("value"))
			data["eMinplaytime"] = min(data["eMinplaytime"], e.find("minplaytime").get("value"))
			data["eMaxplaytime"] = max(data["eMaxplaytime"], e.find("maxplaytime").get("value"))
	i += 1

	# read homerules and adjust stats

	# debug, don't do every game on the list
	if len(list(expansions)) > 10:
		break

lines = []
for game in gameData:
	#debug
	if not "minplayers" in game:
		break

	print(game)
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

	# player counts
	gMin = int(game["minplayers"])
	eMin = int(game["eMinplayers"])
	gMax = int(game["maxplayers"])
	eMax = int(game["eMaxplayers"])

	# columns = 15
	# for i in range(1,columns):
	# 	value = ""
	# 	if i >= gMin and i <= gMax: value = str(i)
	# 	elif i >= eMin and i <= eMax: value = str(i) + "*"
	# 	line.append(value)

	# value = max(gMax, eMax, columns)
	# if value == columns: value = ""
	# else: value = str(value)
	# line.append(value)

	# # play time
	# # increment = 15 # minutes
	# # columns = 15
	# # for i in range(1,columns):
	# # 	value = ""
	# # 	if i >= gMin and i <= gMax: value = str(i)
	# # 	elif i >= eMin and i <= eMax: value = str(i) + "*"
	# # 	line.append(value)

	# # value = max(gMax, eMax, columns)
	# # if value == columns: value = ""
	# # else: value = str(value)
	# # line.append(value)

	# gMin = int(game["minplaytime"])
	# eMin = int(game["eMinplaytime"])
	# gMax = int(game["maxplaytime"])
	# eMax = int(game["eMaxplaytime"])

	# value = min(gMin, eMin)
	# value2 = min(gMax, eMax)
	# if value2 == value:
	# 	line.append(str(value) + " Min")
	# else:
	# 	line.append(str(value) + "-" + str(value2) + " Min")

	# # complexity / weight
	# line.append(str(game["weight"]))

	# # year published
	# line.append(str(game["yearpublished"]))

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
