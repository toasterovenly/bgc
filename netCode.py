import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import http
import errno
import os
from tryagain import retries

################################################################################

baseurl = "http://www.boardgamegeek.com/xmlapi2/"
commands = {
    "collection": "collection?",
    "thing": "thing?",
    "user": "user?",
}
filters = {}
urls = {}
def generateURLs(userName):
    global filters
    filters = {
        "own": "own=1",
        "boardgames": "subtype=boardgame",
        "expansions": "subtype=boardgameexpansion",
        "noexpansions": "excludesubtype=boardgameexpansion",
        "userName": "username=" + userName,
        "id": "id=",
        "stats": "stats=1",
        "brief": "brief=1",
        "modifiedsince": "modifiedsince=",
    }
    global urls
    urls = {
        "myBoardgames": baseurl + commands["collection"]
                        + filters["userName"] + "&"
                        + filters["brief"] + "&"
                        + filters["own"] + "&"
                        + filters["noexpansions"],
        "myExpansions": baseurl + commands["collection"]
                        + filters["userName"] + "&"
                        + filters["stats"] + "&"
                        + filters["own"] + "&"
                        + filters["expansions"],
        "games": baseurl + commands["thing"]
                 + filters["stats"] + "&"
                 + filters["id"],
        "myProfile": baseurl + commands["user"]
                     + filters["userName"],
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
        someBytes = str(someBytes, 'utf-8')
        return ET.fromstring(someBytes)
    return None

def dumpToFile(someBytes, fileName):
    pass
    with open(fileName, "w", encoding='utf-8') as text_file:
        someBytes = str(someBytes, 'utf-8')
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

################################################################################

def getUserData(userName, playerName):
    generateURLs(userName)

    # request game data from bgg
    collection = getUrl(urls["myBoardgames"], "get collection")
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
    games = getUrl(urls["games"] + gameIds, "get full game data")
    dumpToFile(games, "allDataForCollection.xml")
    gamesRoot = getRoot(games)

    eCollection = getUrl(urls["myExpansions"], "get expansions in collection")
    eRoot = getRoot(eCollection)
    dumpToFile(eCollection, "eCollection.xml")

    return (gameData, root, gamesRoot, eRoot)
