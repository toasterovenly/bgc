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

# print("pageSize", PAGE_SIZE, (toLength("8.5in"), toLength("11in")))

TEXT = """%s    page %d of %d
a wonderful file
created with Sample_Code/makesimple.py"""


def rectTlwh(t, l, w, h):
    return (l * inch, -t * inch, w * inch, -h * inch)

def rectTlbr(t, l, b, r):
    return rectTlwh(t, l, b - t, r - l)

def gameDataToPdfData(gameData):
    pass

def make_pdf_file(output_filename, np):
    # title = output_filename
    c = canvas.Canvas(output_filename, pagesize=PAGE_SIZE)
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", FONT_SIZE)
    c.setLineWidth(0.5)
    # for pn in range(1, np + 1):
    #     v = toLength("1in")
    #     for subtline in (TEXT % (output_filename, pn, np)).split('\n'):
    #         c.drawString(toLength("1in"), v, subtline)
    #         v -= toLength("12pt")
    #     c.showPage()
    return c

def writeToFile(filename, gameData):
    c = make_pdf_file(filename, 1)

    # c.setFillGray(0.8)
    # c.rect(SAFE_AREA["left"], SAFE_AREA["top"], inch, -inch, fill=1)

    x = SAFE_AREA["left"]
    y = SAFE_AREA["top"]
    for game in gameData:
        makeRow(c, game, x, y)
        y -= ROW_HEIGHT
    c.save()
    # print("page created?")
    # print(page)
    # print(gameData)

def makeColumn(c, colData, x, y, bgColor, rightAlign=False, colWidth=1):
    colWidth = colWidth * inch
    width = SAFE_AREA["right"] - x
    c.setFillGray(bgColor)
    c.rect(x, y, width, -ROW_HEIGHT, fill=1, stroke=0)
    c.setFillGray(0)
    if rightAlign:
        c.drawRightString(x + colWidth, y - FONT_SIZE, str(colData))
    else:
        c.drawString(x + SPACE_AROUND, y - FONT_SIZE, str(colData))
    return colWidth

def makeRow(c, rowData, x, y):
    # print("makeRow", rowData)


    if rowData["index"] % 2 == 0:
        bgColor = 1
    else:
        bgColor = 0.8
    # c.rect(x, y, SAFE_AREA["width"], -ROW_HEIGHT, fill=1, stroke=0)

    # c.setFillGray(0)
    # ummmm = c.stringWidth(rowData["name"])
    # print("umm", rowData["name"], ummmm)
    # c.drawString(x + SPACE_AROUND, y - FONT_SIZE, rowData["name"])
    x += makeColumn(c, rowData["index"] + 1, x, y, bgColor, rightAlign=True, colWidth=0.25)
    x += makeColumn(c, rowData["name"], x, y, bgColor, colWidth=2)
    x += makeColumn(c, rowData["yearpublished"], x, y, bgColor, rightAlign=True, colWidth=0.45)


