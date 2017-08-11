# import PyPDF2
# import pdftools
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

################################################################################
# generic helper functions

def remap(number, oldMin, oldMax, newMin, newMax):
    return newMin + (number - oldMin) * (newMax - newMin) / (oldMax - oldMin)

def rectTlwh(t, l, w, h):
    return (l * inch, -t * inch, w * inch, -h * inch)

def rectTlbr(t, l, b, r):
    return rectTlwh(t, l, b - t, r - l)

################################################################################
# class for drawing graphs

class RangeGraph:
    extensionColor = 0.5
    filledColor = 0
    textColor = 1

    def __init__(self, canvas, minVal, maxVal, drawWidth):
        self.c = canvas
        self.minVal = minVal
        self.maxVal = maxVal
        self.valWidth = maxVal - minVal
        self.drawWidth = drawWidth

    def draw(self, x, y, minFill, maxFill, minExt, maxExt):
        right = x + self.drawWidth

        # if minExt and maxExt:
        minExt = max(minExt, self.minVal)
        minExtPos = remap(minExt, self.minVal, self.maxVal, x, right)
        maxExt = min(maxExt, self.maxVal)
        maxExtPos = remap(maxExt + 1, self.minVal, self.maxVal, x, right)

        self.c.setFillGray(self.extensionColor)
        self.c.rect(minExtPos, y, maxExtPos - minExtPos, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        if minExt < minFill:
            self.c.drawString(minExtPos, y - FONT_SIZE, str(minExt))
        if maxExt > maxFill:
            self.c.drawRightString(maxExtPos, y - FONT_SIZE, str(maxExt))

        minFill = max(minFill, self.minVal)
        minFillPos = remap(minFill, self.minVal, self.maxVal, x, right)
        maxFill = min(maxFill, self.maxVal)
        maxFillPos = remap(maxFill + 1, self.minVal, self.maxVal, x, right)

        self.c.setFillGray(self.filledColor)
        self.c.rect(minFillPos, y, maxFillPos - minFillPos, -ROW_HEIGHT, fill=1, stroke=0)
        self.c.setFillGray(self.textColor)
        if minFill == maxFill:
            self.c.drawCentredString((maxFillPos + minFillPos) / 2, y - FONT_SIZE, str(maxFill))
        else:
            self.c.drawString(minFillPos, y - FONT_SIZE, str(minFill))
            self.c.drawRightString(maxFillPos, y - FONT_SIZE, str(maxFill))

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
    # minFill = float(row["min" + colData])
    # playerCount = RangeGraph(c, int(collectionStats["minplayers"]), int(collectionStats["maxplayers"]), 2 * inch)
    # playerCount.draw(x, y, int(rowData["minplayers"]), int(rowData["maxplayers"]), int(rowData["minplayers"]) - 1, int(rowData["maxplayers"]) + 1)
    pass

def makeColumn(c, x, y, column, row):
    width = colWidth(column, c)

    c.setFillGray(rowColor(row))
    c.rect(x, y, width, -ROW_HEIGHT, fill=1, stroke=0)

    if column["type"] == "string":
        data = row[column["param"]]
        makeStringColumn(c, x, y, column, row, data=data)
    elif column["type"] == "graph":
        makeGraphColumn(c, x, y, column, row)

    return width

def makeRow(c, row, x, y, collectionStats):
    from settings import settings
    columns = settings["columns"]

    for column in columns:
        x += makeColumn(c, x, y, column, row)

def makeHeader(c, x, y, collectionStats):
    from settings import settings
    columns = settings["columns"]
    c.setFont('Helvetica-Bold', FONT_SIZE)
    for column in columns:
        makeStringColumn(c, x, y, column, {}, data=column["label"])
        x += colWidth(column, c)
    c.setFont('Helvetica', FONT_SIZE)

def make_pdf_file(output_filename, np):
    c = canvas.Canvas(output_filename, pagesize=PAGE_SIZE)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", FONT_SIZE)
    c.setLineWidth(0.5)
    return c

def writeToFile(filename, gameData, collectionStats):
    c = make_pdf_file(filename, 1)
    x = SAFE_AREA["left"]
    y = SAFE_AREA["top"]

    makeHeader(c, x, y, collectionStats)
    y -= ROW_HEIGHT

    for game in gameData:
        makeRow(c, game, x, y, collectionStats)
        y -= ROW_HEIGHT

    c.save()
