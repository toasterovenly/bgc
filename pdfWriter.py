# import PyPDF2
# import pdftools
from reportlab.pdfgen import canvas

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
PAGE_HEIGHT=defaultPageSize[1]
PAGE_WIDTH=defaultPageSize[0]
styles = getSampleStyleSheet()

point = 1
inch = 72

TEXT = """%s    page %d of %d
a wonderful file
created with Sample_Code/makesimple.py"""

def gameDataToPdfData(gameData):
	pass

def make_pdf_file(output_filename, np):
	title = output_filename
	c = canvas.Canvas(output_filename, pagesize=(8.5 * inch, 11 * inch))
	c.setStrokeColorRGB(0,0,0)
	c.setFillColorRGB(1,0,0)
	c.setFont("Helvetica", 12 * point)
	for pn in range(1, np + 1):
		v = 1 * inch
		for subtline in (TEXT % (output_filename, pn, np)).split( '\n' ):
			c.drawString( 1 * inch, v, subtline )
			v -= 12 * point
		c.showPage()
	c.save()
	return c

def writeToFile(filename, gameData):
	page = make_pdf_file(filename, 5)
	print("page created?")
	print(page)


