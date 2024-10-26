import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import http
import errno
import os
import sys
import math
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
                        + filters["own"],
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
    print("BGG has queued the request, retrying in " + str(out) + "s")
    return out

def getUrlFactory(args):
    """sets up the getUrl function to have a dynamic number of retries"""
    @retries(max_attempts=args.retries+1, wait=waitFunc, exceptions=http.client.ResponseNotReady)
    def getUrl(url, message):
        message = message or ""

        try:
            result = urllib.request.urlopen(url)
        except urllib.error.HTTPError as exc:  # Python >2.5
            header = http.client.parse_headers(exc.fp)
            exc.add_note(header.as_string())
            raise

        print(message, "-", result.code, result.reason, "-", url)

        if result.code == http.HTTPStatus.ACCEPTED.value:
            raise http.client.ResponseNotReady(result.reason)
        elif result.code == http.HTTPStatus.OK.value:
            return result.read()
        # else:
        #     raise urllib.error.HTTPError(url, result.code, result.reason)

    return getUrl

def getRoot(someBytes):
    if isinstance(someBytes, bytes):
        someBytes = str(someBytes, 'utf-8')
        return ET.fromstring(someBytes)
    return None

def mergeGamesXml(root1, root2):
    if root1 is None:
        return root2
    root1.extend(root2)
    return root1

def dumpToFile(xmlRoot, fileName):
    ET.indent(xmlRoot)
    xml = ET.ElementTree(xmlRoot)
    xml.write(fileName, encoding='utf-8', xml_declaration=True)
    print("wrote file:", fileName)

def dumpStringToFile(someBytes, fileName):
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

def getUserData(args):
    getUrl = getUrlFactory(args)
    generateURLs(args.userName)
    def outFileName(tag):
        return args.outPath + args.userName + "-" + tag + args.filePostfix + ".xml"

    try:
        collectionXml = getUrl(urls["myBoardgames"], "get collection")
    except http.client.ResponseNotReady:
        print("The server is processing your request. Try again in a little bit.")
        sys.exit()
    collectionRoot = getRoot(collectionXml)
    if args.intermediate:
        dumpToFile(collectionRoot, outFileName("collection"))

    gamesById = {}
    maxThingsPerRequest = 20
    itemCount = len(collectionRoot)
    requestCount = math.ceil(itemCount / maxThingsPerRequest)
    gamesRoot = None

    for requestNumber in range (0, requestCount):
        startIndex = requestNumber * maxThingsPerRequest
        endIndex = min(startIndex + maxThingsPerRequest, itemCount)

        # for item in collectionRoot:
        gameIdsStr = ""
        for itemIndex in range(startIndex, endIndex):
            item = collectionRoot[itemIndex]
            gameId = item.get("objectid")
            gamesById[gameId] = {"name": item.find("name").text}
            gameIdsStr += gameId + ","
        gameIdsStr = gameIdsStr[:-1] # remove trailing comma

        try:
            gamesXml = getUrl(urls["games"] + gameIdsStr, "get full game data")
            # dumpStringToFile(gamesXml, args.outPath + "raw" + str(requestNumber) + ".xml")
        except http.client.ResponseNotReady:
            print("The server is processing your request. Try again in a little bit.")
            sys.exit()

        if gamesRoot is None:
            gamesRoot = getRoot(gamesXml)
        else:
            gamesRoot = mergeGamesXml(gamesRoot, getRoot(gamesXml))

    if args.intermediate:
        dumpToFile(gamesRoot, outFileName("games"))

    return (gamesRoot, gamesById)
