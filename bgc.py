import sys
import argparse
from datetime import datetime
import netCode
import pdfWriter

################################################################################

outPath = "output\\"

################################################################################

def exportToCsv(gameData):
    lines = []
    for game in gameData:

        line = []
        line.append(game.get("name"))
        line.append(game.get("eMinplayers", -1))
        line.append(game.get("minplayers", -1))
        line.append(game.get("maxplayers", -1))
        line.append(game.get("eMaxplayers", -1))
        line.append(game.get("eMinplaytime", -1))
        line.append(game.get("minplaytime", -1))
        line.append(game.get("maxplaytime", -1))
        line.append(game.get("eMaxplaytime", -1))
        line.append(game.get("weight", -1))
        line.append(game.get("yearpublished", -1))

        # convert to csv
        fileLine = ""
        for v in line:
            fileLine += v + "\t"
        fileLine = fileLine[:-1]
        lines.append(fileLine)

    # mkdir_p("output")
    with open(outPath + "collection.csv", "w", encoding='utf-8') as text_file:
        for line in lines:
            text_file.write(line + "\n")
    with open(outPath + "userName.csv", "w", encoding='utf-8') as text_file:
        if playerName != None:
            text_file.write(playerName + "\n")
        else:
            text_file.write(userName + "\n")

def setv(obj, k, v, pred):
    """
    sets or updates a value
    if pred is supplied, the new value is the result of pred(oldVal, newVal)
    """
    if pred and k in obj:
        obj[k] = pred(obj[k], v)
        return
    obj[k] = v


################################################################################

def process(args):
    gamesXmlRoot, gamesById = netCode.getUserData(args)

    print("")
    gameData = [] # alphabetical
    collectionStats = {
    }

    # do it all in one pass!
    for game in gamesXmlRoot:
        thingId = game.get("id")
        thingType = game.get("type")
        data = gamesById.get(thingId)

        data["name"] = game.find("name").get("value")
        data["minplayers"] = game.find("minplayers").get("value")
        data["maxplayers"] = game.find("maxplayers").get("value")
        data["minplaytime"] = game.find("minplaytime").get("value")
        data["maxplaytime"] = game.find("maxplaytime").get("value")
        data["yearpublished"] = game.find("yearpublished").get("value")
        data["weight"] = game.find("statistics/ratings/averageweight").get("value")

        # there are issues with some games that have 0 as values
        # TODO: figure out a valid range
        setv(collectionStats, "minPlayers", data["minplayers"], min)
        setv(collectionStats, "maxPlayers", data["maxplayers"], max)
        setv(collectionStats, "minplaytime", data["minplaytime"], min)
        setv(collectionStats, "maxplaytime", data["maxplaytime"], max)
        setv(collectionStats, "minweight", data["weight"], min)
        setv(collectionStats, "maxweight", data["weight"], max)

        if thingType == "boardgame":
            data["index"] = len(gameData)
            data.setdefault("expansions", [])
            gameData.append(data)
            gamesById[thingId] = data
        elif thingType == "boardgameexpansion":
            parents = game.findall("link[@type='boardgameexpansion']")
            for p in parents:
                parentId = p.get("id")
                if parentId not in gamesById:
                    continue
                parent = gamesById.get(parentId)
                parent.setdefault("expansions", [])
                parent["expansions"].append(data)

        if args.verbose:
            print(data["name"])

    # todo:
    # read homerules and adjust stats
    print("collectionStats", collectionStats)

    # exportToCsv(gameData)
    pdfWriter.writeToFile(args.outFile, gameData)

###############################################################################
# handle command line args

def parse():
    parser = argparse.ArgumentParser(description="Get your boardgame collection"
                                     + " from Board Game Geek.")
    parser.add_argument("userName",
                        help="The username of the player whose collection you want.")
    # parser.add_argument("-f", "--force", action='store_true',
    #                     help="Force retrieve the user's full collection from bgg.com,"
    #                     + " otherwise only updates will be retrieved. You'll need to do"
    #                     + " this if you delete items from your collection.")
    parser.add_argument("-i", "--intermediate", action='store_true',
                        help="Output intermediate xml files. This is useful if you want"
                        + " to create homerules.")
    parser.add_argument("-p", "--playerName",
                        help="The name of the human player that this user represents.")
    parser.add_argument("-t", "--timestamp", action='store_true',
                        help="Output files will have a timestamp appended to their name.")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="Print verbose output.")

    args = parser.parse_args()
    args.time = datetime.now()
    if args.timestamp:
        args.filePostfix = args.time.strftime("-%Y%m%d%H%M%S")
    else:
        args.filePostfix = ""
    args.outFile = outPath + args.userName + args.filePostfix + ".pdf"
    args.outPath = outPath

    if args.verbose:
        print("got args", args)
    return args

process(parse())
print("done.")
