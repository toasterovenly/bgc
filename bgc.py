import sys
import netCode
import pdfWriter

################################################################################

userName = "toasterovenly"
playerName = None
outPath = "output\\"
outFile = outPath + userName + ".pdf"


pdfWriter.writeToFile(outFile, [])


################################################################################

def exportToCsv(gameData):
    pdfWriter.writeToFile(outFile, gameData)
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

# # handle command line args
# if len(sys.argv) < 2 or len(sys.argv) > 3:
#   print("usage: python bgc.py userName [player name]")
#   exit()

# userName = sys.argv[1]

# if len(sys.argv) > 2:
#   playerName = sys.argv[2]
# else:
#   playerName = userName

# gameData, root, gamesRoot, eRoot = netCode.getUserData(userName, playerName)

# print("")

# i = 0
# for game in gamesRoot:
#   data = gameData[i]
#   data["minplayers"] = data["eMinplayers"] = game.find("minplayers").get("value")
#   data["maxplayers"] = data["eMaxplayers"] = game.find("maxplayers").get("value")
#   data["minplaytime"] = data["eMinplaytime"] = game.find("minplaytime").get("value")
#   data["maxplaytime"] = data["eMaxplaytime"] = game.find("maxplaytime").get("value")
#   data["yearpublished"] = game.find("yearpublished").get("value")
#   data["weight"] = game.find("statistics/ratings/averageweight").get("value")

#   print(gameData[i]["name"])

#   expansions = game.findall("link[@type='boardgameexpansion']")
#   for e in expansions:
#       eId = e.get("id")
#       eFromCollection = eRoot.findall("item[@objectid='" + eId + "']")
#       if len(eFromCollection) > 0:
#           eFromCollection = eFromCollection[0]
#           name = eFromCollection.find("name").text
#           print("\t" + name)
#           stats = eFromCollection.find("stats")
#           data["eMinplayers"] = min(data["eMinplayers"], stats.get("minplayers"))
#           data["eMaxplayers"] = max(data["eMaxplayers"], stats.get("maxplayers"))
#           data["eMinplaytime"] = min(data["eMinplaytime"], stats.get("minplaytime"))
#           data["eMaxplaytime"] = max(data["eMaxplaytime"], stats.get("maxplaytime"))
#   i += 1

#   # todo:
#   # read homerules and adjust stats

# exportToCsv(gameData)
