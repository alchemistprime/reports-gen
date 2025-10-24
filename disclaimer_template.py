#!/usr/bin/env python3
"""
Disclaimer Page Template Generator
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from pathlib import Path


def create_disclaimer_page_template(issue_number="XX", date="00.00.202X", page_number="X"):
    """Create the Disclaimer Page Template with disclaimer text in the body
    
    Args:
        issue_number: Issue number (e.g., "01", "15", "2024-Q1")
        date: Publication date (e.g., "10.24.2025", "Jan 15, 2025")
        page_number: Page number (e.g., "1", "5", "12")
    """
    
    # Register fonts (try Source Sans 3 first, then Ubuntu Sans, then Helvetica)
    try:
        # Try Source Sans 3 (Google Fonts)
        pdfmetrics.registerFont(TTFont('SourceSans3', 'assets/fonts/Source_Sans_3/static/SourceSans3-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('SourceSans3-Bold', 'assets/fonts/Source_Sans_3/static/SourceSans3-Bold.ttf'))
        font_name = 'SourceSans3'
        bold_font_name = 'SourceSans3-Bold'
        print("✅ Source Sans 3 font registered successfully")
    except:
        try:
            # Try Ubuntu Sans (system font)
            pdfmetrics.registerFont(TTFont('UbuntuSans', '/usr/share/fonts/truetype/ubuntu/UbuntuSans[wdth,wght].ttf'))
            pdfmetrics.registerFont(TTFont('UbuntuSans-Bold', '/usr/share/fonts/truetype/ubuntu/UbuntuSans-Bold[wdth,wght].ttf'))
            font_name = 'UbuntuSans'
            bold_font_name = 'UbuntuSans-Bold'
            print("✅ Ubuntu Sans font registered successfully")
        except:
            # Fallback to Helvetica
            font_name = 'Helvetica'
            bold_font_name = 'Helvetica-Bold'
            print("⚠️  Custom fonts not found, using Helvetica fallback")
    
    # Page dimensions
    page_width, page_height = letter
    
    # Margins (aligned with logo and grey box positioning)
    margin_left = 0.375 * inch  # Match current logo position (margin_left / 2)
    margin_right = 0.35 * inch  # Match current grey box right edge position
    margin_top = 0.25 * inch
    margin_bottom = 0.25 * inch
    
    # Logo dimensions
    logo_width = 1.90 * inch
    logo_height = 0.70 * inch
    
    # Create the PDF directly with canvas
    output_path = "templates/disclaimer_page_template.pdf"
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # HEADER SECTION
    # Top-left: Bindle logo image (flush to left margin, maintaining position)
    logo_x = margin_left  # Now flush to the updated left margin
    logo_y = page_height - 1.0 * inch  # Maintain original position (1.0" from top)
    
    # Draw the actual logo image
    try:
        c.drawImage("assets/Base/bindle_logo.png", 
                   logo_x, logo_y, 
                   width=logo_width, height=logo_height, 
                   preserveAspectRatio=True, mask='auto')
        print("✅ Logo loaded successfully")
    except Exception as e:
        print(f"⚠️  Logo not found, using fallback: {e}")
        # Fallback if logo not found
        c.setFillColor(HexColor('#FF0000'))
        c.rect(logo_x, logo_y, logo_width, logo_height, fill=1, stroke=0)
    
    # Top-right: Issue info with grey background box
    issue_text = f"ISSUE #{issue_number} | {date} | PAGE {page_number}"
    
    # Calculate text dimensions
    c.setFont(bold_font_name, 10)
    c.setFillColor(colors.black)  # Set black color before calculating width
    text_width = c.stringWidth(issue_text, bold_font_name, 10)
    text_height = 12  # Approximate height for 10pt font
    
    # Grey box dimensions and position (larger, flush to top edge)
    box_width = text_width + 0.96 * inch  # Another 20% wider (0.80 * 1.2 = 0.96)
    box_height = text_height + 0.5 * inch  # Increased height while maintaining centering
    box_x = page_width - margin_right - box_width  # Flush to right margin
    box_y = page_height - box_height  # Flush to top edge (no margin)
    
    # Draw grey background box (no border)
    c.setFillColor(HexColor('#F0F0F0'))  # Light grey
    c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)  # No border
    
    # Draw text on top of grey box (perfectly centered with equal margins)
    # Split text into parts: "ISSUE #15", "  |  ", "10.24.2025", "  |  ", "PAGE 1"
    text_parts = issue_text.split(' | ')
    if len(text_parts) == 3:
        part1 = text_parts[0]  # "ISSUE #15"
        part2 = "    |    "  # "    |    " (four spaces before and after)
        part3 = text_parts[1]  # "10.24.2025"
        part4 = "    |    "  # "    |    " (four spaces before and after)
        part5 = text_parts[2]  # "PAGE 1"
        
        # Calculate individual part widths
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        part1_width = c.stringWidth(part1, bold_font_name, 10)
        part3_width = c.stringWidth(part3, bold_font_name, 10)
        part5_width = c.stringWidth(part5, bold_font_name, 10)
        
        c.setFillColor(HexColor('#666666'))  # Grey for separators
        part2_width = c.stringWidth(part2, bold_font_name, 10)
        part4_width = c.stringWidth(part4, bold_font_name, 10)
        
        # Calculate total width for centering
        total_width = part1_width + part2_width + part3_width + part4_width + part5_width
        
        # Calculate text position for perfect centering
        text_x = box_x + (box_width - total_width) / 2  # Horizontal centering
        
        # Fix vertical centering - account for baseline positioning
        text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)  # Adjust for baseline
        
        # Draw each part with appropriate color
        current_x = text_x
        
        # Part 1: "ISSUE #15" (black)
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        c.drawString(current_x, text_y, part1)
        current_x += part1_width
        
        # Part 2: " | " (grey)
        c.setFont(bold_font_name, 10)
        c.setFillColor(HexColor('#666666'))
        c.drawString(current_x, text_y, part2)
        current_x += part2_width
        
        # Part 3: "10.24.2025" (black)
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        c.drawString(current_x, text_y, part3)
        current_x += part3_width
        
        # Part 4: " | " (grey)
        c.setFont(bold_font_name, 10)
        c.setFillColor(HexColor('#666666'))
        c.drawString(current_x, text_y, part4)
        current_x += part4_width
        
        # Part 5: "PAGE 1" (black)
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        c.drawString(current_x, text_y, part5)
    else:
        # Fallback: draw entire text in black if format is unexpected
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        text_x = box_x + (box_width - text_width) / 2
        text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)
        c.drawString(text_x, text_y, issue_text)
    
    # BODY SECTION - Disclaimer Text
    # Read disclaimer text from base_template.md
    try:
        with open("assets/Base/base_template.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract disclaimer section
        disclaimer_section = ""
        in_disclaimer = False
        for line in content.split('\n'):
            if line.strip() == "## Disclaimer":
                in_disclaimer = True
                continue
            elif line.strip().startswith("##") and in_disclaimer:
                break
            elif in_disclaimer:
                disclaimer_section += line + "\n"
        
        disclaimer_text = disclaimer_section.strip()
        print("✅ Disclaimer text loaded successfully")
        
    except Exception as e:
        print(f"⚠️  Could not load disclaimer text: {e}")
        disclaimer_text = "Disclaimer text not available. Please check assets/Base/base_template.md"
    
    # Position "DISCLAIMER" heading
    disclaimer_heading_x = margin_left
    disclaimer_heading_y = page_height - 1.0 * inch - (6 * 0.15 * inch)  # 6 line spaces below logo
    
    # Draw "DISCLAIMER" heading in red, size 27
    c.setFont(bold_font_name, 27)
    c.setFillColor(colors.red)
    c.drawString(disclaimer_heading_x, disclaimer_heading_y, "DISCLAIMER")
    
    # Position disclaimer text 3 line spaces below heading
    body_x = margin_left
    body_y = disclaimer_heading_y - (3 * 0.15 * inch)  # 3 line spaces below heading
    body_width = page_width - margin_left - margin_right - 0.2 * inch  # Larger buffer for justified text
    body_height = page_height - 2.0 * inch  # Leave space for footer
    
    # Use ReportLab's proper justification instead of custom code
    # Create a frame for the text area
    frame = Frame(body_x, body_y - body_height, body_width, body_height, 
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    
    # Create justified paragraph style
    style = ParagraphStyle(
        'DisclaimerStyle',
        fontName=font_name,
        fontSize=12,
        leading=16,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=0,
        spaceAfter=0
    )
    
    # Create paragraph with proper justification
    para = Paragraph(disclaimer_text, style)
    
    # Draw the paragraph in the frame
    frame.add(para, c)
    
    # FOOTER SECTION
    # Both sections aligned on same horizontal line
    footer_y = margin_bottom + 0.4 * inch
    
    # Bottom-left: Confidential info (30% width)
    # Make "CONFIDENTIAL NOT FOR DISTRIBUTION" bold
    c.setFont(bold_font_name, 8)
    c.setFillColor(colors.black)
    c.drawString(margin_left, footer_y, "CONFIDENTIAL")
    c.drawString(margin_left, footer_y - 0.12 * inch, "NOT FOR DISTRIBUTION")
    
    # Add line space (reduced spacing)
    c.setFont(font_name, 8)
    c.drawString(margin_left, footer_y - 0.30 * inch, "INFO@BINDLEPAPER.COM")
    
    
    # Save the PDF
    c.save()
    print(f"✅ Created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_disclaimer_page_template(
        issue_number="15",
        date="10.24.2025",
        page_number="2"
    )
