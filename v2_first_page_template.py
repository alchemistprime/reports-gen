#!/usr/bin/env python3
"""
V2 First Page Template Generator - Using Platypus for body content
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image, PageTemplate, Frame, FrameBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from pathlib import Path


def create_v2_first_page_template(
    issue_number="XX", 
    date="00.00.202X", 
    page_number="1",
    theme="INVENTORY GLUT",
    ticker="AZEK:US",
    timeframe="6-9 MONTHS",
    current_target="$49.90 | $30.00",
    downside="39.9%",
    company_data=None,
    trade_data=None
):
    """Create V2 First Page Template using Platypus for body content
    
    Args:
        issue_number: Issue number (e.g., "01", "15", "2024-Q1")
        date: Publication date (e.g., "10.24.2025", "Jan 15, 2025")
        page_number: Page number (e.g., "1", "5", "12")
        theme: Investment theme (e.g., "INVENTORY GLUT")
        ticker: Stock ticker (e.g., "AZEK:US")
        timeframe: Investment timeframe (e.g., "6-9 MONTHS")
        current_target: Current and target prices (e.g., "$49.90 | $30.00")
        downside: Downside percentage (e.g., "39.9%")
        company_data: Dict with company information
        trade_data: Dict with trade execution data
    """
    
    # Default data if not provided
    if company_data is None:
        company_data = {
            "SECTOR": "Industrials",
            "LOCATION": "United States", 
            "MARKET CAP": "$7.3B",
            "EV/EBITDA": "20.94",
            "TRAILING P/E": "51.55",
            "PROFIT MARGIN": "9.85%",
            "TOTAL CASH / DEBT": "$148M / $552M",
            "52 WEEK RANGE": "$35.48 - $54.91"
        }
    
    if trade_data is None:
        trade_data = {
            "DAILY VOLUME": "$74M",
            "DAYS TO COVER": "3.26",
            "SHARES SHORT": "3.33%",
            "BORROW COST": "0.3%"
        }
    
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
    margin_left = 0.375 * inch
    margin_right = 0.35 * inch
    margin_top = 0.25 * inch
    margin_bottom = 0.25 * inch
    
    # Create output path
    output_path = "templates/v2_first_page_template.pdf"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create SimpleDocTemplate for Platypus
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    
    # Create story (will be populated later)
    story = []
    
    # Prepare issue text
    issue_text = f"ISSUE #{issue_number} | {date} | PAGE {page_number}"
    logo_width = 1.90 * inch
    logo_height = 0.70 * inch
    
    # Create header/footer callback function that captures outer variables
    def draw_header_footer(canvas, doc):
        """Draw header and footer on canvas"""
        # HEADER SECTION
        # Top-left: Bindle logo image (flush to left margin)
        logo_x = margin_left
        logo_y = page_height - 1.0 * inch  # Maintain original position (1.0" from top)
        
        # Draw the actual logo image
        try:
            canvas.drawImage("assets/Base/bindle_logo.png", 
                           logo_x, logo_y, 
                           width=logo_width, height=logo_height, 
                           preserveAspectRatio=True, mask='auto')
            print("✅ Logo loaded successfully")
        except Exception as e:
            print(f"⚠️  Logo not found, using fallback: {e}")
            # Fallback if logo not found
            canvas.setFillColor(HexColor('#FF0000'))
            canvas.rect(logo_x, logo_y, logo_width, logo_height, fill=1, stroke=0)
        
        # Top-right: Issue info with grey background box
        # Calculate text dimensions
        canvas.setFont(bold_font_name, 10)
        canvas.setFillColor(colors.black)
        text_width = canvas.stringWidth(issue_text, bold_font_name, 10)
        text_height = 12  # Approximate height for 10pt font
        
        # Grey box dimensions and position
        box_width = text_width + 0.96 * inch
        box_height = text_height + 0.5 * inch
        box_x = page_width - margin_right - box_width
        box_y = page_height - box_height
        
        # Draw grey background box (no border)
        canvas.setFillColor(HexColor('#F0F0F0'))
        canvas.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)
        
        # Draw text on grey box (centered)
        text_parts = issue_text.split(' | ')
        if len(text_parts) == 3:
            part1 = text_parts[0]
            part2 = "    |    "
            part3 = text_parts[1]
            part4 = "    |    "
            part5 = text_parts[2]
            
            # Calculate individual part widths
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(colors.black)
            part1_width = canvas.stringWidth(part1, bold_font_name, 10)
            part3_width = canvas.stringWidth(part3, bold_font_name, 10)
            part5_width = canvas.stringWidth(part5, bold_font_name, 10)
            
            canvas.setFillColor(HexColor('#666666'))
            part2_width = canvas.stringWidth(part2, bold_font_name, 10)
            part4_width = canvas.stringWidth(part4, bold_font_name, 10)
            
            # Calculate total width for centering
            total_width = part1_width + part2_width + part3_width + part4_width + part5_width
            
            # Calculate text position for perfect centering
            text_x = box_x + (box_width - total_width) / 2
            text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)
            
            # Draw each part with appropriate color
            current_x = text_x
            
            # Part 1: "ISSUE #15" (black)
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(current_x, text_y, part1)
            current_x += part1_width
            
            # Part 2: " | " (grey)
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(HexColor('#666666'))
            canvas.drawString(current_x, text_y, part2)
            current_x += part2_width
            
            # Part 3: "10.24.2025" (black)
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(current_x, text_y, part3)
            current_x += part3_width
            
            # Part 4: " | " (grey)
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(HexColor('#666666'))
            canvas.drawString(current_x, text_y, part4)
            current_x += part4_width
            
            # Part 5: "PAGE 1" (black)
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(colors.black)
            canvas.drawString(current_x, text_y, part5)
        
        # FOOTER SECTION
        footer_y = margin_bottom + 0.4 * inch
        
        # Bottom-left: Confidential info
        canvas.setFont(bold_font_name, 8)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin_left, footer_y, "CONFIDENTIAL")
        canvas.drawString(margin_left, footer_y - 0.12 * inch, "NOT FOR DISTRIBUTION")
        
        canvas.setFont(font_name, 8)
        canvas.drawString(margin_left, footer_y - 0.30 * inch, "INFO@BINDLEPAPER.COM")
        
        # Bottom-right: Disclaimer text (70% width)
        canvas.setFont(font_name, 7)
        canvas.setFillColor(colors.black)
        
        disclaimer_text = """This document and the information contained herein are the exclusive property of The Bindle Paper and are for educational and informational purposes only. This material does not constitute, and should not be construed as, an offer to sell, or a solicitation of an offer to buy, any securities or related financial instruments. This document contains information and views as of the date indicated and such information and views are subject to change without notice. The Bindle Paper has no duty or obligation to update the information contained herein. Please review the full Disclaimer at the end of this document."""
        
        # Text box for disclaimer (70% width, right-aligned, justified)
        disclaimer_width = page_width * 0.7 - margin_right  # 70% of page width
        disclaimer_x = page_width - margin_right - disclaimer_width
        
        # Create text object for wrapping (aligned with confidential section baseline)
        text_obj = canvas.beginText(disclaimer_x, footer_y)
        text_obj.setFont(font_name, 7)
        text_obj.setFillColor(colors.black)
        text_obj.setLeading(8)
        
        # Justified text wrapping for disclaimer
        words = disclaimer_text.split()
        lines = []
        current_line = []
        
        # First, break text into lines
        for word in words:
            test_line = " ".join(current_line + [word])
            if canvas.stringWidth(test_line, font_name, 7) < disclaimer_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(current_line)
                current_line = [word]
        if current_line:
            lines.append(current_line)
        
        # Now justify each line (except the last one)
        for i, line_words in enumerate(lines):
            if i == len(lines) - 1:
                # Last line: no justification
                text_obj.textLine(" ".join(line_words))
            else:
                # Justify line by adding extra spaces
                if len(line_words) > 1:
                    # Calculate how much space we need to add
                    current_width = canvas.stringWidth(" ".join(line_words), font_name, 7)
                    extra_space = disclaimer_width - current_width
                    spaces_needed = len(line_words) - 1
                    
                    if spaces_needed > 0:
                        space_per_gap = extra_space / spaces_needed
                        justified_line = line_words[0]
                        for j in range(1, len(line_words)):
                            # Add extra spaces between words
                            extra_spaces = " " * int(space_per_gap * j) if j == 1 else " " * int(space_per_gap)
                            justified_line += extra_spaces + " " + line_words[j]
                        text_obj.textLine(justified_line)
                    else:
                        text_obj.textLine(" ".join(line_words))
                else:
                    text_obj.textLine(" ".join(line_words))
        
        canvas.drawText(text_obj)
    
    # Create left frame for markdown content (60% width)
    content_frame = Frame(
        margin_left, 
        margin_bottom + 0.5 * inch, 
        page_width * 0.6 - margin_left,  # 60% width minus left margin
        page_height - 1.5 * inch - 0.5 * inch, 
        leftPadding=0.1 * inch, 
        rightPadding=0, 
        topPadding=0, 
        bottomPadding=0
    )
    
    # Create right frame for sidebar (40% width)
    sidebar_start_x = margin_left + (page_width * 0.6)
    sidebar_width = page_width * 0.4 - margin_right
    sidebar_frame = Frame(
        sidebar_start_x,
        margin_bottom + 0.5 * inch,
        sidebar_width - 0.5 * inch,  # Reduce frame width to flush tables to right margin
        page_height - 1.5 * inch - 0.5 * inch,
        leftPadding=0,  # Set to zero to eliminate padding
        rightPadding=0,  # No right padding - tables will be flush to right edge
        topPadding=0,
        bottomPadding=0
    )
    
    # Create page template with both frames and onPage callback
    def on_first_page(canvas, doc):
        draw_header_footer(canvas, doc)
    
    template = PageTemplate(id='FirstPage', frames=[content_frame, sidebar_frame], onPage=on_first_page)
    doc.addPageTemplates([template])
    
    # Create sidebar content for right frame
    styles = getSampleStyleSheet()
    
    # Create custom styles for sidebar
    sidebar_style = ParagraphStyle(
        'Sidebar',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        fontName=font_name
    )
    
    sidebar_title_style = ParagraphStyle(
        'SidebarTitle',
        parent=styles['Normal'],
        fontSize=13,
        textColor=colors.red,
        fontName=bold_font_name,
        spaceAfter=12,  # Increased from 6 to 12 for more space between title and table
        leftIndent=-0.15 * inch,  # Match the frame's leftPadding to align with tables
        rightIndent=0
    )
    
    # Left content (will be populated later with markdown)
    story.append(Paragraph("Left content placeholder", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    
    # Switch to sidebar frame and add info boxes
    story.append(FrameBreak())
    
    # Box 1: Theme/Ticker Info - Create table for proper alignment
    theme_table_data = [
        ["THEME:", theme],
        ["TICKER:", ticker],
        ["TIMEFRAME:", timeframe],
        ["CURRENT/TARGET:", current_target],
        ["DOWNSIDE:", downside],
    ]
    
    theme_table = Table(theme_table_data, colWidths=[1.5*inch, 1.3*inch])  # Match other tables
    theme_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),  # Left column bold
        ('FONTNAME', (1, 0), (1, -1), bold_font_name),  # Right column bold
        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),  # Make THEME value red (first row, right column)
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left align for Theme/Ticker
        ('LEFTPADDING', (0, 0), (-1, -1), 0),  # Match other tables
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),  # Match other tables
        ('TOPPADDING', (0, 0), (-1, -1), 3),  # Match other tables
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Match other tables
    ])
    theme_table.setStyle(theme_table_style)
    story.append(theme_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Box 2: 3-Year Performance
    story.append(Paragraph("3-YEAR PERFORMANCE", sidebar_title_style))
    try:
        # Match table widths: make chart same width as tables
        chart_img = Image("3_YEAR.png", width=2.8*inch, height=1.5*inch)
        story.append(chart_img)
        print("✅ Chart image loaded successfully")
    except Exception as e:
        story.append(Paragraph("Chart placeholder", sidebar_style))
        print(f"⚠️  Could not load chart image: {e}")
    story.append(Spacer(1, 0.2 * inch))
    
    # Box 3: Company Information
    story.append(Paragraph("COMPANY INFORMATION", sidebar_title_style))
    company_table_data = []
    for key, value in company_data.items():
        company_table_data.append([f"{key}", f"{value}"])
    
    company_table = Table(company_table_data, colWidths=[1.4*inch, 1.4*inch])
    company_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ])
    company_table.setStyle(company_table_style)
    story.append(company_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Box 4: Trade Execution
    story.append(Paragraph("TRADE EXECUTION", sidebar_title_style))
    trade_table_data = []
    for key, value in trade_data.items():
        trade_table_data.append([f"{key}", f"{value}"])
    
    trade_table = Table(trade_table_data, colWidths=[1.4*inch, 1.4*inch])
    trade_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#E0E0E0')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ])
    trade_table.setStyle(trade_table_style)
    story.append(trade_table)
    
    # Attribution text - right-aligned, directly below table
    story.append(Spacer(1, 0.05 * inch))  # Reduced spacing to be closer to table
    attribution_style = ParagraphStyle('Attribution', parent=styles['Normal'], fontSize=7, fontName=font_name, alignment=TA_RIGHT)
    story.append(Paragraph(f"All data as of {date}", attribution_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Created: {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    create_v2_first_page_template(
        issue_number="37",
        date="02.20.2025", 
        page_number="1",
        theme="INVENTORY GLUT",
        ticker="AZEK:US",
        timeframe="6-9 MONTHS",
        current_target="$49.90 | $30.00",
        downside="39.9%",
        company_data={
            "SECTOR": "Industrials",
            "LOCATION": "United States", 
            "MARKET CAP": "$7.3B",
            "EV/EBITDA": "20.94",
            "TRAILING P/E": "51.55",
            "PROFIT MARGIN": "9.85%",
            "TOTAL CASH / DEBT": "$148M / $552M",
            "52 WEEK RANGE": "$35.48 - $54.91"
        },
        trade_data={
            "DAILY VOLUME": "$74M",
            "DAYS TO COVER": "3.26",
            "SHARES SHORT": "3.33%",
            "BORROW COST": "0.3%"
        }
    )
