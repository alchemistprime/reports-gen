#!/usr/bin/env python3

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("templates/minimal_test.pdf", pagesize=letter)
c.drawString(100, 750, "Hello World")
c.save()
print("Minimal test completed")

