#!/usr/bin/env python3
"""
Back Page Template Generator
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path


def create_back_page_template(issue_number="XX", date="00.00.202X", page_number="X"):
    """Create the Back Page Template with centered elements
    
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
    
    # Margins
    margin_left = 0.375 * inch
    margin_right = 0.35 * inch
    margin_top = 0.25 * inch
    margin_bottom = 0.25 * inch
    
    # Logo dimensions (increased by 25% + 20% = 50% total)
    logo_width = 1.90 * inch * 1.25 * 1.20  # 25% + 20% larger
    logo_height = 0.70 * inch * 1.25 * 1.20  # 25% + 20% larger
    
    # Create the PDF directly with canvas
    output_path = "templates/back_page_template.pdf"
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # HEADER SECTION
    # Top-center: Issue info with grey background box (centered horizontally, flush to top)
    issue_text = f"ISSUE #{issue_number} | {date}"
    
    # Calculate text dimensions
    c.setFont(bold_font_name, 10)
    c.setFillColor(colors.black)  # Set black color before calculating width
    text_width = c.stringWidth(issue_text, bold_font_name, 10)
    text_height = 12  # Approximate height for 10pt font
    
    # Grey box dimensions and position (centered horizontally, flush to top)
    box_width = (text_width + 0.96 * inch) * 0.90  # Reduce width by 10% (0.90 = 1 - 0.10)
    box_height = text_height + 0.5 * inch  # Same height as other templates
    box_x = (page_width - box_width) / 2  # Center horizontally
    box_y = page_height - box_height  # Flush to top edge
    
    # Draw grey background box (no border)
    c.setFillColor(HexColor('#F0F0F0'))  # Light grey
    c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)  # No border
    
    # Draw text on top of grey box (perfectly centered with equal margins)
    # Split text into parts: "ISSUE #15", "  |  ", "10.24.2025"
    text_parts = issue_text.split(' | ')
    if len(text_parts) == 2:
        part1 = text_parts[0]  # "ISSUE #15"
        part2 = "    |    "  # "    |    " (four spaces before and after)
        part3 = text_parts[1]  # "10.24.2025"
        
        # Calculate individual part widths
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        part1_width = c.stringWidth(part1, bold_font_name, 10)
        part3_width = c.stringWidth(part3, bold_font_name, 10)
        
        c.setFillColor(HexColor('#666666'))  # Grey for separators
        part2_width = c.stringWidth(part2, bold_font_name, 10)
        
        # Calculate total width for centering
        total_width = part1_width + part2_width + part3_width
        
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
    else:
        # Fallback: draw entire text in black if format is unexpected
        c.setFont(bold_font_name, 10)
        c.setFillColor(colors.black)
        text_x = box_x + (box_width - text_width) / 2
        text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)
        c.drawString(text_x, text_y, issue_text)
    
    # CENTER: Bindle logo image (centered in entire document)
    logo_x = (page_width - logo_width) / 2  # Center horizontally
    logo_y = (page_height - logo_height) / 2  # Center vertically
    
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
    
    # FOOTER SECTION
    # Bottom-center: Confidential info (centered horizontally)
    # "CONFIDENTIAL" (bold), "NOT FOR DISTRIBUTION" (next line), one line space, "INFO@BINDLEPAPER.COM"
    
    # Calculate confidential text dimensions
    c.setFont(bold_font_name, 8)
    c.setFillColor(colors.black)
    
    # First line: "CONFIDENTIAL" (bold)
    line1 = "CONFIDENTIAL"
    line1_width = c.stringWidth(line1, bold_font_name, 8)
    line1_x = (page_width - line1_width) / 2  # Center horizontally
    line1_y = margin_bottom + 0.4 * inch
    c.drawString(line1_x, line1_y, line1)
    
    # Second line: "NOT FOR DISTRIBUTION" (bold)
    c.setFont(bold_font_name, 8)
    line2 = "NOT FOR DISTRIBUTION"
    line2_width = c.stringWidth(line2, bold_font_name, 8)
    line2_x = (page_width - line2_width) / 2  # Center horizontally
    line2_y = line1_y - 0.12 * inch  # Next line
    c.drawString(line2_x, line2_y, line2)
    
    # One line space, then "INFO@BINDLEPAPER.COM" (regular)
    c.setFont(font_name, 8)
    line3 = "INFO@BINDLEPAPER.COM"
    line3_width = c.stringWidth(line3, font_name, 8)
    line3_x = (page_width - line3_width) / 2  # Center horizontally
    line3_y = line2_y - 0.24 * inch  # One line space
    c.drawString(line3_x, line3_y, line3)
    
    # Save the PDF
    c.save()
    print(f"✅ Created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_back_page_template(
        issue_number="15",
        date="10.24.2025",
        page_number="3"
    )
