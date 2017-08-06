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

################################################################################

def process(args):
    gameData, gamesRoot = netCode.getUserData(args)

    print("")

    if len(gamesRoot) == 0:
        return

    i = 0
    for game in gamesRoot:
        data = gameData[i]
        data["minplayers"] = data["eMinplayers"] = game.find("minplayers").get("value")
        data["maxplayers"] = data["eMaxplayers"] = game.find("maxplayers").get("value")
        data["minplaytime"] = data["eMinplaytime"] = game.find("minplaytime").get("value")
        data["maxplaytime"] = data["eMaxplaytime"] = game.find("maxplaytime").get("value")
        data["yearpublished"] = game.find("yearpublished").get("value")
        data["weight"] = game.find("statistics/ratings/averageweight").get("value")

    print(gameData[i]["name"])

    expansions = gamesRoot.findall("link[@type='boardgameexpansion']")
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

    # todo:
    # read homerules and adjust stats

    # exportToCsv(gameData)
    pdfWriter.writeToFile(args.outFile, gameData)

###############################################################################
# handle command line args

def parse():
    parser = argparse.ArgumentParser(description="Get your boardgame collection from Board Game Geek.")
    parser.add_argument("userName",
                        help="The username of the player whose collection you want.")
    parser.add_argument("-p", "--playerName",
                        help="The name of the human player that this user represents.")
    parser.add_argument("-f", "--force", action='store_true',
                        help="Force retrieve the user's full collection from bgg.com,"
                        + " otherwise only updates will be retrieved. You'll need to do"
                        + " this if you delete items from your collection.")
    parser.add_argument("-t", "--timestamp", action='store_true',
                        help="Output files will have a timestamp appended to their name.")

    args = parser.parse_args()
    args.time = datetime.now()
    if args.timestamp:
        args.filePostfix = args.time.strftime("-%Y%m%d%H%M%S")
    else:
        args.filePostfix = ""
    args.outFile = outPath + args.userName + args.filePostfix + ".pdf"
    args.outPath = outPath

    print("got args", args)
    return args

process(parse())
