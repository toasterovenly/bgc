# import PyPDF2
# import pdftools
from reportlab.pdfgen import canvas

# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import toLength
import reportlab.lib.pagesizes as pagesizes

pageSize = pagesizes.LETTER
styles = getSampleStyleSheet()

# print("pageSize", pageSize)

TEXT = """%s    page %d of %d
a wonderful file
created with Sample_Code/makesimple.py"""

def gameDataToPdfData(gameData):
    pass

def make_pdf_file(output_filename, np):
    # title = output_filename
    c = canvas.Canvas(output_filename, pagesize=(toLength("8.5in"), toLength("11in")))
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(1, 0, 0)
    c.setFont("Helvetica", 12)
    for pn in range(1, np + 1):
        v = toLength("1in")
        for subtline in (TEXT % (output_filename, pn, np)).split('\n'):
            c.drawString(toLength("1in"), v, subtline)
            v -= toLength("12pt")
        c.showPage()
    c.save()
    return c

def writeToFile(filename, gameData):
    page = make_pdf_file(filename, 5)
    # print("page created?")
    # print(page)
    # print(gameData)

# def makeRow(gameData):

