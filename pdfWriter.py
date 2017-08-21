# import PyPDF2
# import pdftools
import collections
from reportlab.pdfgen import canvas

# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import toLength
import reportlab.lib.pagesizes as pagesizes

PAGE_SIZE = pagesizes.LETTER
styles = getSampleStyleSheet()
inch = toLength("1in")
PAGE_BORDER = 1 * inch
SAFE_AREA = {
    "top": PAGE_SIZE[1] - PAGE_BORDER,
    "left": PAGE_BORDER,
    "bottom": PAGE_BORDER,
    "right": PAGE_SIZE[0] - PAGE_BORDER,
    "width": PAGE_SIZE[0] - 2 * PAGE_BORDER,
    "height": PAGE_SIZE[1] - 2 * PAGE_BORDER,
}
FONT_SIZE = 8
SPACE_AROUND = 3
ROW_HEIGHT = toLength(str(FONT_SIZE + SPACE_AROUND) + "pt")

collectionStats = {}

################################################################################
# generic helper functions

def remap(number, oldMin, oldMax, newMin, newMax):
    return newMin + (number - oldMin) * (newMax - newMin) / (oldMax - oldMin)

def rectTlwh(t, l, w, h):
    return (l * inch, -t * inch, w * inch, -h * inch)

def rectTlbr(t, l, b, r):
    return rectTlwh(t, l, b - t, r - l)

def intOrFloat(n):
    n = float(n)
    if n.is_integer():
        n = int(n)
    else:
        n = float(truncate(n, 2))
    print("n is a number", n)
    return n

def truncate(f, n):
    '''Truncates a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
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

class RangeGraph:
    leftColor = 0.5
    rightColor = 0.5
    centerColor = 0
    textColor = 1

    def __init__(self, c, minVal, maxVal, drawWidth):
        self.c = c
        self.minVal = intOrFloat(minVal) # left extrema
        self.maxVal = intOrFloat(maxVal) # right extrema
        self.valWidth = self.maxVal - self.minVal
        self.drawWidth = drawWidth
        self.forceMin = False

    def drawLeftSection(self, x, y, right, graphArgs):
        minBar = self.minVal if self.forceMin else max(graphArgs["minBar"], self.minVal)
        minFill = self.minVal if self.forceMin else max(graphArgs["minFill"], self.minVal)

        if minBar >= minFill:
            return

        minBarPos = remap(minBar, self.minVal, self.maxVal, x, right)
        minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        width = minFillPos - minBarPos

        self.c.setFillGray(self.leftColor)
        self.c.rect(minBarPos, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        if not self.forceMin:
            strVal = "{}".format(minBar)
            self.c.setFillGray(self.textColor)
            self.c.drawString(minBarPos, y - FONT_SIZE, strVal)

    def drawRightSection(self, x, y, right, graphArgs):
        maxBar = min(graphArgs["maxBar"], self.maxVal)
        maxFill = min(graphArgs["maxFill"], self.maxVal)

        if maxBar <= maxFill:
            return

        maxBarPos = remap(maxBar, self.minVal, self.maxVal, x, right)
        maxFillPos = remap(maxFill, self.minVal, self.maxVal, x, right)
        width = maxBarPos - maxFillPos

        self.c.setFillGray(self.rightColor)
        self.c.rect(maxFill, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        self.c.drawRightString(maxBarPos, y - FONT_SIZE, str(maxBar))

    def drawCenterSection(self, x, y, right, graphArgs):
        minFill = self.minVal if self.forceMin else max(graphArgs["minFill"], self.minVal)
        maxFill = min(graphArgs["maxFill"], self.maxVal)
        minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        maxFillPos = remap(maxFill, self.minVal, self.maxVal, x, right)
        width = maxFillPos - minFillPos

        self.c.setFillGray(self.centerColor)
        self.c.rect(minFillPos, y, width, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        if minFill == maxFill:
            self.c.drawCentredString((maxFillPos + minFillPos) / 2, y - FONT_SIZE, str(maxFill))
        else:
            self.c.drawString(minFillPos, y - FONT_SIZE, str(minFill))
            self.c.drawRightString(maxFillPos, y - FONT_SIZE, str(maxFill))

    def draw(self, x, y, graphArgs):
        # minBar = self.minVal if self.forceMin else graphArgs["minBar"]
        # minFill = self.minVal if self.forceMin else graphArgs["minFill"]
        # maxFill = graphArgs["maxFill"]
        # maxBar = graphArgs["maxBar"]

        print("draw graph")

        right = x + self.drawWidth
        self.drawLeftSection(x, y, right, graphArgs)
        self.drawRightSection(x, y, right, graphArgs)
        self.drawCenterSection(x, y, right, graphArgs)

        # if minBar and maxBar:
        # minBar = max(minBar, self.minVal)
        # minBarPos = remap(minBar, self.minVal, self.maxVal, x, right)
        # maxBar = min(maxBar, self.maxVal)
        # maxBarPos = remap(maxBar + 1, self.minVal, self.maxVal, x, right)
        # minFill = max(minFill, self.minVal)
        # minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        # maxFill = min(maxFill, self.maxVal)
        # maxFillPos = remap(maxFill + 1, self.minVal, self.maxVal, x, right)

        # self.c.setFillGray(self.leftColor)
        # self.c.rect(minBarPos, y, minFill - minBarPos, -ROW_HEIGHT, fill=1, stroke=0)
        # if minBar < minFill:
        #     self.c.setFillGray(self.textColor)
        #     self.c.drawString(minBarPos, y - FONT_SIZE, str(minBar))

        # self.c.setFillGray(self.rightColor)
        # self.c.rect(maxFill, y, maxBarPos - maxFill, -ROW_HEIGHT, fill=1, stroke=0)
        # if maxBar > maxFill:
        #     self.c.setFillGray(self.textColor)
        #     self.c.drawRightString(maxBarPos, y - FONT_SIZE, str(maxBar))

        # self.c.setFillGray(self.centerColor)
        # self.c.rect(minFillPos, y, maxFillPos - minFillPos, -ROW_HEIGHT, fill=1, stroke=0)
        # self.c.setFillGray(self.textColor)
        # if minFill == maxFill:
        #     self.c.drawCentredString((maxFillPos + minFillPos) / 2, y - FONT_SIZE, str(maxFill))
        # else:
        #     self.c.drawString(minFillPos, y - FONT_SIZE, str(minFill))
        #     self.c.drawRightString(maxFillPos, y - FONT_SIZE, str(maxFill))

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
        return toLength(column["width"])
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

def makeStringColumn(c, x, y, column, row, data=""):
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
    paramMin = param["min"]["shortParam"] or param["min"]["param"]
    paramMax = param["max"]["shortParam"] or param["max"]["param"]

    if not "graphObj" in column:
        colMin = collectionStats[paramMin]
        colMax = collectionStats[paramMax]
        colWid = colWidth(column, c)
        graph = column.setdefault("graphObj", RangeGraph(c, colMin, colMax, colWid))
        if column["type"] == "graph-bar":
            graph.leftColor = 0
            graph.forceMin = True
    else:
        graph = column["graphObj"]

    graphArgs = {
        "minBar": intOrFloat(row[paramMin]),
        "minFill": intOrFloat(row[paramMin]),
        "maxFill": intOrFloat(row[paramMax]),
        "maxBar": intOrFloat(row[paramMax]),
    }
    graph.draw(x, y, graphArgs)

def makeColumn(c, x, y, column, row):
    width = colWidth(column, c)

    c.setFillGray(rowColor(row))
    c.rect(x, y, width, -ROW_HEIGHT, fill=1, stroke=0)

    columnType = column["type"]
    if columnType == "string":
        data = row[column["param"]]
        makeStringColumn(c, x, y, column, row, data=data)
    elif columnType == "graph-bar" or columnType == "graph-candleStick":
        makeGraphColumn(c, x, y, column, row)

    return width

def makeRow(c, row, x, y):
    from settings import settings
    columns = settings["columns"]

    for column in columns:
        x += makeColumn(c, x, y, column, row)

def makeRowHeader(c, x, y):
    from settings import settings
    columns = settings["columns"]
    c.setFont('Helvetica-Bold', FONT_SIZE)
    for column in columns:
        makeStringColumn(c, x, y, column, {}, data=column["label"])
        x += colWidth(column, c)
    c.setFont('Helvetica', FONT_SIZE)

def makePage(c, gameData):
    x = SAFE_AREA["left"]
    y = SAFE_AREA["top"]


    makeRowHeader(c, x, y)
    y -= ROW_HEIGHT

    c.setFont("Helvetica", FONT_SIZE)
    while collectionStats["currentGameIndex"] < len(gameData):
        if y < SAFE_AREA["bottom"]:
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

def writeToFile(filename, gameData, _collectionStats):
    c = canvas.Canvas(filename, pagesize=PAGE_SIZE)

    global collectionStats
    collectionStats = _collectionStats
    collectionStats["currentGameIndex"] = 0

    endOfDocument = False
    while not endOfDocument:
        endOfDocument = makePage(c, gameData)
    c.save()
