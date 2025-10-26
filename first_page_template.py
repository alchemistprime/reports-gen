#!/usr/bin/env python3
"""
First Page Template Generator - With Yellow Info Boxes and Markdown Content
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path


def create_first_page_template(
    issue_number="XX", 
    date="00.00.202X", 
    page_number="1",
    markdown_file="AZEK.md",
    theme="INVENTORY GLUT",
    ticker="AZEK:US",
    timeframe="6-9 MONTHS",
    current_target="$49.90 | $30.00",
    downside="39.9%",
    chart_image="",
    company_data=None,
    trade_data=None
):
    """Create the First Page Template with yellow info boxes and markdown content
    
    Args:
        issue_number: Issue number (e.g., "01", "15", "2024-Q1")
        date: Publication date (e.g., "10.24.2025", "Jan 15, 2025")
        page_number: Page number (e.g., "1", "5", "12")
        markdown_file: Path to markdown file to load content from
        theme: Investment theme (e.g., "INVENTORY GLUT")
        ticker: Stock ticker (e.g., "AZEK:US")
        timeframe: Investment timeframe (e.g., "6-9 MONTHS")
        current_target: Current and target prices (e.g., "$49.90 | $30.00")
        downside: Downside percentage (e.g., "39.9%")
        chart_image: Path to chart image file
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
    margin_left = 0.375 * inch  # Match current logo position
    margin_right = 0.35 * inch  # Match current grey box right edge position
    margin_top = 0.25 * inch
    margin_bottom = 0.25 * inch
    
    # Logo dimensions
    logo_width = 1.90 * inch
    logo_height = 0.70 * inch
    
    # Create the PDF directly with canvas
    output_path = "templates/first_page_template.pdf"
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # HEADER SECTION (reuse from content_template.py)
    # Top-left: Bindle logo image
    logo_x = margin_left
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
    c.setFillColor(colors.black)
    text_width = c.stringWidth(issue_text, bold_font_name, 10)
    text_height = 12  # Approximate height for 10pt font
    
    # Grey box dimensions and position
    box_width = text_width + 0.96 * inch
    box_height = text_height + 0.5 * inch
    box_x = page_width - margin_right - box_width
    box_y = page_height - box_height  # Flush to top edge
    
    # Draw grey background box
    c.setFillColor(HexColor('#F0F0F0'))
    c.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)
    
    # Draw text on grey box (same logic as content_template.py)
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
        text_x = box_x + (box_width - total_width) / 2
        text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)
        
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
    
    # YELLOW INFO BOXES (right sidebar)
    # Calculate sidebar dimensions
    sidebar_width = page_width * 0.4  # 40% of page width
    sidebar_x = page_width - margin_right - sidebar_width
    sidebar_start_y = box_y - 0.5 * inch  # Start below grey box
    
    # Box dimensions
    box_padding = 0.1 * inch
    box_spacing = 0.3 * inch  # Increased from 0.15 to 0.3 for better spacing
    box_width = sidebar_width - 2 * box_padding
    
    # Box 1: Theme/Ticker Info
    box1_height = 1.0 * inch
    box1_y = sidebar_start_y - box1_height
    
    # Draw white background
    c.setFillColor(colors.white)
    c.rect(sidebar_x + box_padding, box1_y, box_width, box1_height, fill=1, stroke=0)
    
    # Draw box content - all font size 12, all black
    c.setFont(bold_font_name, 12)
    c.setFillColor(colors.black)
    
    # THEME
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box1_y + box1_height - 0.3 * inch, "THEME:")
    c.drawString(sidebar_x + box_padding + 1.8 * inch, box1_y + box1_height - 0.3 * inch, theme)

    # TICKER
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box1_y + box1_height - 0.5 * inch, "TICKER:")
    c.drawString(sidebar_x + box_padding + 1.8 * inch, box1_y + box1_height - 0.5 * inch, ticker)
    
    # TIMEFRAME
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box1_y + box1_height - 0.7 * inch, "TIMEFRAME:")
    c.drawString(sidebar_x + box_padding + 1.8 * inch, box1_y + box1_height - 0.7 * inch, timeframe)
    
    # CURRENT/TARGET
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box1_y + box1_height - 0.9 * inch, "CURRENT/TARGET:")
    c.drawString(sidebar_x + box_padding + 1.8 * inch, box1_y + box1_height - 0.9 * inch, current_target)
    
    # DOWNSIDE
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box1_y + box1_height - 1.1 * inch, "DOWNSIDE:")
    c.drawString(sidebar_x + box_padding + 1.8 * inch, box1_y + box1_height - 1.1 * inch, downside)
    
    # Box 2: 3-Year Performance Chart
    box2_height = 2.0 * inch
    box2_y = box1_y - box_spacing - box2_height
    
    # Draw white background
    c.setFillColor(colors.white)
    c.rect(sidebar_x + box_padding, box2_y, box_width, box2_height, fill=1, stroke=0)
    
    # Draw header in red
    c.setFont(bold_font_name, 13)
    c.setFillColor(colors.red)
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box2_y + box2_height - 0.2 * inch, "3-YEAR PERFORMANCE")
    
    # Draw chart image
    try:
        chart_width = box_width - 0.2 * inch
        chart_height = box2_height - 0.4 * inch
        chart_x = sidebar_x + box_padding + 0.1 * inch
        chart_y = box2_y + 0.1 * inch
        c.drawImage("3_YEAR.png", chart_x, chart_y, width=chart_width, height=chart_height, preserveAspectRatio=True)
        print("✅ Chart image loaded successfully")
    except Exception as e:
        print(f"⚠️  Could not load chart image: {e}")
        # Draw placeholder
        c.setFillColor(HexColor('#F5F5F5'))
        c.rect(sidebar_x + box_padding + 0.1 * inch, box2_y + 0.1 * inch, box_width - 0.2 * inch, box2_height - 0.4 * inch, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont(font_name, 8)
        c.drawString(sidebar_x + box_padding + 0.2 * inch, box2_y + box2_height/2, "Chart placeholder")
    
    # Box 3: Company Information
    box3_height = 2.5 * inch
    box3_y = box2_y - box_spacing - box3_height
    
    # Draw header in red
    c.setFont(bold_font_name, 13)
    c.setFillColor(colors.red)
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box3_y + box3_height - 0.2 * inch, "COMPANY INFORMATION")
    
    # Draw line between header and table - BLOCKED OUT FOR TESTING
    # c.setStrokeColor(colors.black)
    # c.setLineWidth(1)
    # c.line(sidebar_x + box_padding + 0.1 * inch, box3_y + box3_height - 0.35 * inch, 
    #        sidebar_x + box_padding + box_width - 0.1 * inch, box3_y + box3_height - 0.35 * inch)
    
    # Create company data table using ReportLab Table (refactored approach)
    company_table_data = []
    for key, value in company_data.items():
        company_table_data.append([key, str(value)])

    # Create table
    company_table = Table(company_table_data, colWidths=[1.425*inch, 1.425*inch])  # 1.5 * 0.95 = 1.425

    # Style the table
    company_table_style = TableStyle([
        # Column backgrounds - left column grey, right column white
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),  # Left column grey
        ('BACKGROUND', (1, 0), (1, -1), colors.white),         # Right column white
        # Text alignment - center both columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Font - left column bold, right column normal
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),  # Left column bold
        ('FONTNAME', (1, 0), (1, -1), font_name),      # Right column normal
        ('FONTSIZE', (0, 0), (0, -1), 10),             # Left column size 10
        ('FONTSIZE', (1, 0), (1, -1), 10),             # Right column size 10
        # Borders
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        # Vertical line down the middle
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        # Internal lines (exclude last row to avoid artifacts)
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#E0E0E0')),
        # Padding - increased by 73% total for taller rows
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 7),  # 6 * 1.2 = 7.2 ≈ 7
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),  # 6 * 1.2 = 7.2 ≈ 7
    ])
    
    company_table.setStyle(company_table_style)
    
    # Draw the table with space below heading, flush to right margin
    company_table_x = sidebar_x + box_padding + box_width - 2.85 * inch  # Flush to right margin (2.85" = 1.425" + 1.425")
    company_table_y = box3_y + 0.05 * inch - 0.4 * inch - 0.36 * inch  # Move down 3 lines (3 * 0.12" = 0.36")
    company_table.wrapOn(c, 2.85 * inch, box3_height - 0.9 * inch)
    company_table.drawOn(c, company_table_x, company_table_y)
    
    # Box 4: Trade Execution
    box4_height = 1.5 * inch
    box4_y = box3_y - box_spacing - box4_height - 0.3 * inch  # Maximum extra space for very tall Company table
    
    # Draw header in red
    c.setFont(bold_font_name, 13)
    c.setFillColor(colors.red)
    c.drawString(sidebar_x + box_padding + 0.1 * inch, box4_y + box4_height - 0.2 * inch, "TRADE EXECUTION")
    
    # Draw line between header and table - BLOCKED OUT FOR TESTING
    # c.setStrokeColor(colors.black)
    # c.setLineWidth(1)
    # c.line(sidebar_x + box_padding + 0.1 * inch, box4_y + box4_height - 0.35 * inch, 
    #        sidebar_x + box_padding + box_width - 0.1 * inch, box4_y + box4_height - 0.35 * inch)
    
    # Create trade data table using ReportLab Table (refactored approach)
    trade_table_data = []
    for key, value in trade_data.items():
        trade_table_data.append([key, str(value)])

    # Create table
    trade_table = Table(trade_table_data, colWidths=[1.425*inch, 1.425*inch])  # 1.5 * 0.95 = 1.425

    # Style the table
    trade_table_style = TableStyle([
        # Column backgrounds - left column grey, right column white
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),  # Left column grey
        ('BACKGROUND', (1, 0), (1, -1), colors.white),         # Right column white
        # Text alignment - center both columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Font - left column bold, right column normal
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),  # Left column bold
        ('FONTNAME', (1, 0), (1, -1), font_name),      # Right column normal
        ('FONTSIZE', (0, 0), (0, -1), 10),             # Left column size 10
        ('FONTSIZE', (1, 0), (1, -1), 10),             # Right column size 10
        # Borders
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        # Vertical line down the middle
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        # Internal lines (exclude last row to avoid artifacts)
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#E0E0E0')),
        # Padding - increased by 73% total for taller rows
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 7),  # 6 * 1.2 = 7.2 ≈ 7
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),  # 6 * 1.2 = 7.2 ≈ 7
    ])
    
    trade_table.setStyle(trade_table_style)
    
    # Draw the table flush to right margin
    trade_table_x = sidebar_x + box_padding + box_width - 2.85 * inch  # Flush to right margin (2.85" = 1.425" + 1.425")
    trade_table_y = box4_y + 0.05 * inch - 0.36 * inch  # Move down 3 lines (3 * 0.12" = 0.36")
    trade_table.wrapOn(c, 2.85 * inch, box4_height - 0.7 * inch)
    trade_table.drawOn(c, trade_table_x, trade_table_y)
    
    # Attribution text - outside the table, below the bottom border, right-justified
    c.setFont(font_name, 7)
    c.setFillColor(colors.black)
    # Position text closer to the table border
    attribution_y = box4_y - 0.1 * inch  # Closer to the table
    # Right-justify the text to align with the right edge of the table
    attribution_text = f"All data as of {date}"
    text_width = c.stringWidth(attribution_text, font_name, 7)
    attribution_x = sidebar_x + box_padding + box_width - text_width  # Align with right edge of table
    c.drawString(attribution_x, attribution_y, attribution_text)
    
    # MAIN CONTENT AREA (left side) - Markdown content
    content_x = margin_left
    content_width = page_width * 0.6  # 60% width for content
    content_y = page_height - margin_top - 1.5 * inch  # Start below header
    content_height = content_y - margin_bottom - 0.5 * inch  # Leave space for footer
    
    
    # Ensure content area is reasonable
    if content_height < 1.0 * inch:
        content_height = 1.0 * inch
    
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Read and parse markdown content
    # try:
    #     with open(markdown_file, 'r', encoding='utf-8') as f:
    #         md_content = f.read()
    #     print("✅ Markdown content loaded successfully")
    # except Exception as e:
    #     print(f"⚠️  Could not load markdown file: {e}")
    #     md_content = "Markdown content not available."
    
    # Parse markdown and create styled content
    # Display actual content from AZEK.md
    
    # Main title - BLOCKED OUT FOR TESTING
    # c.setFont(bold_font_name, 16)
    # c.setFillColor(colors.black)
    # title_text = "The AZEK Company, Inc.: High Inventory Levels, Accounting Issues, and Slowing Market Spell Trouble"
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Wrap title text to fit content width
    # words = title_text.split()
    words = []  # Empty list to prevent error
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        if c.stringWidth(test_line, bold_font_name, 16) < content_width - 0.2 * inch:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Draw title lines
    # y_pos = content_y - 0.3 * inch
    # for line in lines:
    #     c.drawString(content_x + 0.1 * inch, y_pos, line)
    #     y_pos -= 0.25 * inch
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Key Points section
    # y_pos -= 0.1 * inch
    # c.setFont(bold_font_name, 12)
    # c.setFillColor(colors.red)
    # c.drawString(content_x + 0.1 * inch, y_pos, "Key Points")
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Draw first few key points
    # y_pos -= 0.2 * inch
    # c.setFont(font_name, 10)
    # c.setFillColor(colors.black)
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # key_points = [
    #     "1. The company's finished goods inventory is high (see Inventory section).",
    #     "2. The company's backlog was 8 weeks in 2023, 7 plus weeks in 2024, and now it is 6-7 weeks in Feb of 2025.",
    #     "3. Channel inventory levels are below historical levels and sell-in will be less than the company is saying.",
    #     "4. Trex customers are carrying less inventory (see Trex Aug 6, 2024 CC).",
    #     "5. Inventories are at a 10-quarter high (see our model, row 764)."
    # ]
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # for point in key_points:
        # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
        # Wrap long lines
        # words = point.split()
        # current_line = []
        # line_started = False
        
        # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
        # for word in words:
            # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
            # test_line = " ".join(current_line + [word])
            # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
            # if c.stringWidth(test_line, font_name, 10) < content_width - 0.3 * inch:
                # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                # current_line.append(word)
            # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
            # else:
                # if current_line:
                    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                    # if line_started:
                        # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                        # Indent continuation lines
                        # c.drawString(content_x + 0.2 * inch, y_pos, " ".join(current_line))
                    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                    # else:
                        # c.drawString(content_x + 0.1 * inch, y_pos, " ".join(current_line))
                        # line_started = True
                    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                    # y_pos -= 0.15 * inch
                # current_line = [word]
        
        # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
        # if current_line:
            # if line_started:
                # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                # c.drawString(content_x + 0.2 * inch, y_pos, " ".join(current_line))
            # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
            # else:
                # c.drawString(content_x + 0.1 * inch, y_pos, " ".join(current_line))
            # y_pos -= 0.15 * inch
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Premise of the Short section
    # y_pos -= 0.1 * inch
    # c.setFont(bold_font_name, 12)
    # c.setFillColor(colors.red)
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # c.drawString(content_x + 0.1 * inch, y_pos, "Premise of the Short")
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Draw premise text
    # y_pos -= 0.2 * inch
    # c.setFont(font_name, 10)
    # c.setFillColor(colors.black)
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # premise_text = "Remodels of homes were flat in 2024 and will be close to flat in 2025. AZEK thinks it will outgrow the weak market. Customers are lowering channel inventory, and it isn't likely to come back. AZEK made a mention of this, but they expect channel inventories to fall back to historical levels."
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # Wrap premise text
    # words = premise_text.split()
    # current_line = []
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # for word in words:
        # test_line = " ".join(current_line + [word])
        # if c.stringWidth(test_line, font_name, 10) < content_width - 0.2 * inch:
            # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
            # current_line.append(word)
        # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
        # else:
            # if current_line:
                # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
                # c.drawString(content_x + 0.1 * inch, y_pos, " ".join(current_line))
                # y_pos -= 0.15 * inch
            # current_line = [word]
    
    # MARKDOWN RENDERING BLOCKED OUT FOR TESTING
    # if current_line:
        # c.drawString(content_x + 0.1 * inch, y_pos, " ".join(current_line))
    
    # FOOTER SECTION (reuse from content_template.py)
    footer_y = margin_bottom + 0.4 * inch
    
    # Bottom-left: Confidential info
    c.setFont(bold_font_name, 8)
    c.setFillColor(colors.black)
    c.drawString(margin_left, footer_y, "CONFIDENTIAL")
    c.drawString(margin_left, footer_y - 0.12 * inch, "NOT FOR DISTRIBUTION")
    
    c.setFont(font_name, 8)
    c.drawString(margin_left, footer_y - 0.30 * inch, "INFO@BINDLEPAPER.COM")
    
    # Bottom-right: Disclaimer text
    c.setFont(font_name, 7)
    c.setFillColor(colors.black)
    
    disclaimer_text = """This document and the information contained herein are the exclusive property of The Bindle Paper and are for educational and informational purposes only. This material does not constitute, and should not be construed as, an offer to sell, or a solicitation of an offer to buy, any securities or related financial instruments. This document contains information and views as of the date indicated and such information and views are subject to change without notice. The Bindle Paper has no duty or obligation to update the information contained herein. Please review the full Disclaimer at the end of this document."""
    
    # Text box for disclaimer (70% width, right-aligned, justified)
    disclaimer_width = page_width * 0.7 - margin_right
    disclaimer_x = page_width - margin_right - disclaimer_width
    
    # Create text object for wrapping
    text_obj = c.beginText(disclaimer_x, footer_y)
    text_obj.setFont(font_name, 7)
    text_obj.setFillColor(colors.black)
    text_obj.setLeading(8)
    
    # Justified text wrapping for disclaimer (same logic as content_template.py)
    words = disclaimer_text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        if c.stringWidth(test_line, font_name, 7) < disclaimer_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(current_line)
            current_line = [word]
    if current_line:
        lines.append(current_line)
    
    # Justify each line (except the last one)
    for i, line_words in enumerate(lines):
        if i == len(lines) - 1:
            text_obj.textLine(" ".join(line_words))
        else:
            if len(line_words) > 1:
                current_width = c.stringWidth(" ".join(line_words), font_name, 7)
                extra_space = disclaimer_width - current_width
                spaces_needed = len(line_words) - 1
                
                if spaces_needed > 0:
                    space_per_gap = extra_space / spaces_needed
                    justified_line = line_words[0]
                    for j in range(1, len(line_words)):
                        extra_spaces = " " * int(space_per_gap * j) if j == 1 else " " * int(space_per_gap)
                        justified_line += extra_spaces + " " + line_words[j]
                    text_obj.textLine(justified_line)
                else:
                    text_obj.textLine(" ".join(line_words))
            else:
                text_obj.textLine(" ".join(line_words))
    
    c.drawText(text_obj)
    
    # Save the PDF
    
    c.save()
    print(f"✅ Created: {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage with sample data
    create_first_page_template(
        issue_number="37",
        date="02.20.2025", 
        page_number="1",
        markdown_file="AZEK.md",
        theme="INVENTORY GLUT",
        ticker="AZEK:US",
        timeframe="6-9 MONTHS",
        current_target="$49.90 | $30.00",
        downside="39.9%",
        chart_image="",  # Add path to chart image if available
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
