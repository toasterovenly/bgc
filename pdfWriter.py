import sys
import numbers
import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.units import toLength
import reportlab.lib.pagesizes as pagesizes
from settings import settings

################################################################################
# file-scoped variables

try:
    requestedPagesize = settings["page-size"].upper()
    PAGE_SIZE = getattr(pagesizes, requestedPagesize)
except AttributeError:
    print("Invalid 'page-size' in settings: " + settings["page-size"] + ".")
    sys.exit()
try:
    UNIT = getattr(reportlab.lib.units, settings["unit"])
except AttributeError:
    print("Invalid 'unit' in settings: " + settings["unit"] + ".")
    sys.exit()

def lengthOf(num):
    if isinstance(num, numbers.Real):
        return num * UNIT
    elif isinstance(num, str):
        return toLength(num)
    else:
        print("Invalid value for length: " + num + ".")


PAGE_BORDER = lengthOf(settings["page-border"])
SAFE_AREA = {
    "top": PAGE_SIZE[1] - PAGE_BORDER,
    "left": PAGE_BORDER,
    "bottom": PAGE_BORDER,
    "right": PAGE_SIZE[0] - PAGE_BORDER,
    "width": PAGE_SIZE[0] - 2 * PAGE_BORDER,
    "height": PAGE_SIZE[1] - 2 * PAGE_BORDER,
}
FONT_SIZE = lengthOf(settings["font-size"])
SPACE_AROUND = lengthOf(settings["cell-padding"])
ROW_HEIGHT = FONT_SIZE + SPACE_AROUND
CONTENT_AREA = {}

collectionStats = {}

################################################################################
# generic helper functions

def remap(number, oldMin, oldMax, newMin, newMax):
    return newMin + (number - oldMin) * (newMax - newMin) / (oldMax - oldMin)

def rectTlwh(t, l, w, h):
    return (l * UNIT, -t * UNIT, w * UNIT, -h * UNIT)

def rectTlbr(t, l, b, r):
    return rectTlwh(t, l, b - t, r - l)

def intOrFloat(n, precision):
    # orig = n
    n = float(n)
    if n.is_integer():
        n = int(n)
    else:
        n = float(truncate(n, precision))
    # print("intOrFloat", orig, "precision", precision, "->", n)
    return n

def truncate(f, n):
    '''Truncates a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, _, d = s.partition('.')
    return '.'.join([i, (d)[:n]])

################################################################################
# class for drawing graphs

# candlestick graph:
#      |---[###|##]--------|
# ^    ^   ^   ^  ^        ^   ^
# |    |   |   |  |        |   +- column max
# |    |   |   |  |        +- bar max
# |    |   |   |  +- fill max
# |    |   |   +- center
# |    |   +- fill min
# |    +- bar min
# +- column min

# bar graph:
# [###############]--------|
# ^    ^   ^   ^  ^        ^   ^
# |    |   |   |  |        |   +- column max
# |    |   |   |  |        +- bar max
# |    |   |   |  +- fill max
# |    |   |   +- center
# |    |   +- fill min
# |    +- bar min
# +- column min

class GraphObject:
    leftColor = 0.5
    rightColor = 0.5
    centerColor = 0
    textColor = 1

    def __init__(self, c, minVal, maxVal, drawWidth, precision):
        self.c = c
        self.precision = int(precision)
        self.step = 1 / (10 ** self.precision)
        self.clampMin = intOrFloat(minVal, precision)
        self.clampMax = intOrFloat(maxVal, precision)
        self.minVal = self.clampMin # left extrema
        self.maxVal = self.clampMax + self.step # right extrema
        self.valWidth = self.maxVal - self.minVal
        self.drawWidth = drawWidth
        self.stepWidth = remap(self.step + self.minVal, self.minVal, self.maxVal, 0, drawWidth)
        self.isBarGraph = False
        # print("===", self)

    def __str__(self):
        return ("GraphObject" +
                ": precision " + str(self.precision) +
                ", step " + str(self.step) +
                ", clampMin " + str(self.clampMin) +
                ", clampMax " + str(self.clampMax) +
                ", minVal " + str(self.minVal) +
                ", maxVal " + str(self.maxVal) +
                ", valWidth  " + str(self.valWidth) +
                ", drawWidth " + str(self.drawWidth) +
                ", stepWidth " + str(self.stepWidth) +
                ", isBarGraph " + str(self.isBarGraph))

    def drawLeftSection(self, x, y, right, graphArgs):
        minBar = self.minVal if self.isBarGraph else max(graphArgs["minBar"], self.minVal)
        minFill = self.minVal if self.isBarGraph else max(graphArgs["minFill"], self.minVal)

        if minBar >= minFill:
            return

        minBarPos = remap(minBar, self.minVal, self.maxVal, x, right)
        minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        width = minFillPos - minBarPos

        self.c.setFillGray(self.leftColor)
        self.c.rect(minBarPos, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        if not self.isBarGraph:
            strVal = "{}".format(minBar)
            self.c.setFillGray(self.textColor)
            self.c.drawString(minBarPos, y - FONT_SIZE, strVal)

    def drawRightSection(self, x, y, right, graphArgs):
        maxBar = min(graphArgs["maxBar"], self.maxVal)
        maxFill = min(graphArgs["maxFill"], self.maxVal)

        if maxBar <= maxFill:
            return

        maxBarPos = remap(maxBar + self.step, self.minVal, self.maxVal, x, right)
        maxFillPos = remap(maxFill + self.step, self.minVal, self.maxVal, x, right)
        width = maxBarPos - maxFillPos

        self.c.setFillGray(self.rightColor)
        self.c.rect(maxFill, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        self.c.drawRightString(maxBarPos, y - FONT_SIZE, str(maxBar))

    def drawCenterSection(self, x, y, right, graphArgs):
        minFill = self.minVal if self.isBarGraph else max(graphArgs["minFill"], self.minVal)
        maxFill = min(graphArgs["maxFill"], self.maxVal)
        minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        maxFillPos = remap(maxFill + self.step, self.minVal, self.maxVal, x, right)
        width = maxFillPos - minFillPos

        self.c.setFillGray(self.centerColor)
        self.c.rect(minFillPos, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        if minFill == maxFill:
            self.c.drawCentredString((maxFillPos + minFillPos) / 2, y - FONT_SIZE, str(maxFill))
        else:
            if not self.isBarGraph:
                leftText = graphArgs["minText"]
                if self.c.stringWidth(leftText) < self.stepWidth:
                    leftTextPos = minFillPos + self.stepWidth * 0.5
                    self.c.drawCentredString(leftTextPos, y - FONT_SIZE, leftText)
                else:
                    self.c.drawString(minFillPos, y - FONT_SIZE, leftText)

            rightText = graphArgs["maxText"]
            if self.c.stringWidth(rightText) < self.stepWidth:
                rightTextPos = maxFillPos - self.stepWidth * 0.5
                self.c.drawCentredString(rightTextPos, y - FONT_SIZE, rightText)
            else:
                self.c.drawRightString(maxFillPos, y - FONT_SIZE, rightText)

    def draw(self, x, y, graphArgs):
        # print("draw graph")
        right = x + self.drawWidth
        self.drawLeftSection(x, y, right, graphArgs)
        self.drawRightSection(x, y, right, graphArgs)
        self.drawCenterSection(x, y, right, graphArgs)


################################################################################
# row and column helpers

def rowColor(row):
    if row["index"] % 2 == 1:
        return 0.8 # light gray
    return 1 # white

def colAlign(column):
    return column["align"]

def colWidth(column, c):
    if "width" in column:
        return lengthOf(column["width"])
    return c.stringWidth(column["autoWidth"])

def drawRect(c, left, top, right, bottom):
    path = c.beginPath()
    path.moveTo(left, top)
    path.lineTo(right, top)
    path.lineTo(right, bottom)
    path.lineTo(left, bottom)
    path.lineTo(left, top)
    c.drawPath(path)

################################################################################
# read data and write to the .pdf

def makeStringColumn(c, x, y, column, row, data):
    align = colAlign(column)
    width = colWidth(column, c)
    c.setFillGray(0)
    if align == "right":
        c.drawRightString(x + width, y - FONT_SIZE, str(data))
    elif align == "center":
        c.drawCentredString(x + width, y - FONT_SIZE, str(data))
    else:
        c.drawString(x + SPACE_AROUND, y - FONT_SIZE, str(data))

def makeGraphColumn(c, x, y, column, row):
    # candlestick or bar chart
    param = column["param"]
    paramMin = param["min"]["dest"]
    paramMax = param["max"]["dest"]
    precision = column["graph"]["precision"]

    if not "graphObj" in column:
        colMin = collectionStats[paramMin]
        colMax = collectionStats[paramMax]
        colWid = colWidth(column, c) - SPACE_AROUND
        colGraph = column["graph"]
        if "clampMin" in colGraph:
            clampMin = colGraph["clampMin"]
            colMin = max(colMin, clampMin)
        if "clampMax" in colGraph:
            clampMax = colGraph["clampMax"]
            colMax = min(colMax, clampMax)
        graph = column.setdefault("graphObj", GraphObject(c, colMin, colMax, colWid, precision))
        if colGraph["type"] == "bar":
            graph.leftColor = 0
            graph.isBarGraph = True
    else:
        graph = column["graphObj"]

    minBar = intOrFloat(row[paramMin], precision)
    minFill = intOrFloat(row[paramMin], precision)
    maxFill = intOrFloat(row[paramMax], precision)
    maxBar = intOrFloat(row[paramMax], precision)

    graphArgs = {
        "minBar": max(minBar, graph.clampMin),
        "minFill": max(minFill, graph.clampMin),
        "maxFill": min(maxFill, graph.clampMax),
        "maxBar": min(maxBar, graph.clampMax),
        "minText": str(minFill),
        "maxText": str(maxFill),
    }
    # print(row[paramMin], row[paramMax], "\n", graphArgs, "\n", column)
    graph.draw(x, y, graphArgs)

def makeColumn(c, x, y, column, row):
    width = colWidth(column, c)

    c.setFillGray(rowColor(row))
    c.rect(x, y, width, -ROW_HEIGHT, fill=1, stroke=0)

    columnType = column["type"]
    if columnType == "string":
        data = row[column["param"]]
        makeStringColumn(c, x, y, column, row, data)
    elif columnType == "graph":
        makeGraphColumn(c, x, y, column, row)

    return width

def makeRow(c, row, x, y):
    # print("\n---\n", row["name"])
    columns = settings["columns"]

    for column in columns:
        x += makeColumn(c, x, y, column, row)

def makeRowHeader(c, x, y):
    columns = settings["columns"]
    c.setFont('Helvetica-Bold', FONT_SIZE)
    for column in columns:
        makeStringColumn(c, x, y, column, {}, column["label"])
        x += colWidth(column, c)
    c.setFont('Helvetica', FONT_SIZE)

def makePage(c, gameData):
    x = CONTENT_AREA["left"]
    y = CONTENT_AREA["top"]

    makeRowHeader(c, x, y)
    y -= ROW_HEIGHT

    c.setFont("Helvetica", FONT_SIZE)
    while collectionStats["currentGameIndex"] < len(gameData):
        if y < CONTENT_AREA["bottom"]:
            break
        game = gameData[collectionStats["currentGameIndex"]]
        makeRow(c, game, x, y)
        y -= ROW_HEIGHT
        collectionStats["currentGameIndex"] += 1
    else:
        drawRect(c, SAFE_AREA["left"], SAFE_AREA["top"], SAFE_AREA["right"], SAFE_AREA["bottom"])
        return True # all games done

    drawRect(c, SAFE_AREA["left"], SAFE_AREA["top"], SAFE_AREA["right"], SAFE_AREA["bottom"])
    c.showPage()
    return False

def calculateContentArea(c):
    c.setFont("Helvetica", FONT_SIZE)
    columns = settings["columns"]
    totalWidth = 0
    for column in columns:
        totalWidth += colWidth(column, c)
    CONTENT_AREA["top"] = SAFE_AREA["top"]
    CONTENT_AREA["bottom"] = SAFE_AREA["bottom"]
    CONTENT_AREA["height"] = SAFE_AREA["height"]
    CONTENT_AREA["width"] = totalWidth
    CONTENT_AREA["left"] = (PAGE_SIZE[0] - totalWidth) * 0.5
    CONTENT_AREA["right"] = CONTENT_AREA["left"] + totalWidth

def writeToFile(filename, gameData, _collectionStats):
    c = canvas.Canvas(filename, pagesize=PAGE_SIZE)
    calculateContentArea(c)

    global collectionStats
    collectionStats = _collectionStats
    collectionStats["currentGameIndex"] = 0

    endOfDocument = False
    while not endOfDocument:
        endOfDocument = makePage(c, gameData)
    c.save()
