#!/usr/bin/env python3
"""
Report Generator - Starting with Page 1 only
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image, PageTemplate, Frame, FrameBreak, PageBreak, NextPageTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from pathlib import Path


def generate_report(
    issue_number="37",
    date="02.20.2025",
    theme="INVENTORY GLUT",
    ticker="AZEK:US",
    timeframe="6-9 MONTHS",
    current_target="$49.90 | $30.00",
    downside="39.9%",
    company_data=None,
    trade_data=None,
    markdown_file="AZEK.md",
    output_file="templates/AZEK_report.pdf"
):
    """
    Generate full report with header/footer on every page
    
    Page 1: 60% content (left) + 40% sidebar (right)
    Pages 2+: Two-column content flow
    """
    
    # Default data
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
    
    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('SourceSans3', 'assets/fonts/Source_Sans_3/static/SourceSans3-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('SourceSans3-Bold', 'assets/fonts/Source_Sans_3/static/SourceSans3-Bold.ttf'))
        font_name = 'SourceSans3'
        bold_font_name = 'SourceSans3-Bold'
        print("✅ Source Sans 3 font registered")
    except:
        font_name = 'Helvetica'
        bold_font_name = 'Helvetica-Bold'
        print("⚠️  Using Helvetica fallback")
    
    # Page dimensions
    page_width, page_height = letter
    
    # Margins
    margin_left = 0.375 * inch
    margin_right = 0.35 * inch
    margin_top = 0.25 * inch
    margin_bottom = 0.25 * inch
    
    # Create output
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    
    story = []
    # Force first page to use the single-column 'Page' template
    story.append(NextPageTemplate('Page'))
    
    # Issue text template (page number added dynamically)
    issue_text_template = f"ISSUE #{issue_number} | {date} | PAGE "
    logo_width = 1.90 * inch
    logo_height = 0.70 * inch
    
    # Header/Footer callback
    def draw_header_footer(canvas, doc):
        """Draw header and footer on every page"""
        # Draw logo
        logo_x = margin_left
        logo_y = page_height - 1.0 * inch
        try:
            canvas.drawImage("assets/Base/bindle_logo.png",
                           logo_x, logo_y,
                           width=logo_width, height=logo_height,
                           preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"⚠️  Logo error: {e}")
        
        # Draw grey box with issue info
        issue_text = issue_text_template + str(doc.page)
        canvas.setFont(bold_font_name, 10)
        canvas.setFillColor(colors.black)
        text_width = canvas.stringWidth(issue_text, bold_font_name, 10)
        text_height = 12
        
        box_width = text_width + 0.96 * inch
        box_height = text_height + 0.5 * inch
        box_x = page_width - margin_right - box_width
        box_y = page_height - box_height
        
        # Draw grey box
        canvas.setFillColor(HexColor('#F0F0F0'))
        canvas.rect(box_x, box_y, box_width, box_height, fill=1, stroke=0)
        
        # Draw text on box
        text_parts = issue_text.split(' | ')
        if len(text_parts) == 3:
            part1, part2, part3 = text_parts[0], text_parts[1], text_parts[2]
            
            canvas.setFont(bold_font_name, 10)
            canvas.setFillColor(colors.black)
            part1_width = canvas.stringWidth(part1, bold_font_name, 10)
            part2_width = canvas.stringWidth("    |    ", bold_font_name, 10)
            part3_width = canvas.stringWidth(part2, bold_font_name, 10)
            part4_width = canvas.stringWidth("    |    ", bold_font_name, 10)
            part5_width = canvas.stringWidth(part3, bold_font_name, 10)
            
            total_width = part1_width + part2_width + part3_width + part4_width + part5_width
            text_x = box_x + (box_width - total_width) / 2
            text_y = box_y + (box_height - text_height) / 2 + (text_height * 0.20)
            
            # Draw parts
            canvas.setFillColor(colors.black)
            canvas.drawString(text_x, text_y, part1)
            canvas.setFillColor(HexColor('#666666'))
            canvas.drawString(text_x + part1_width, text_y, "    |    ")
            canvas.setFillColor(colors.black)
            canvas.drawString(text_x + part1_width + part2_width, text_y, part2)
            canvas.setFillColor(HexColor('#666666'))
            canvas.drawString(text_x + part1_width + part2_width + part3_width, text_y, "    |    ")
            canvas.setFillColor(colors.black)
            canvas.drawString(text_x + part1_width + part2_width + part3_width + part4_width, text_y, part3)
        
        # Draw footer
        footer_y = margin_bottom + 0.4 * inch
        
        # Left side: Confidential info
        canvas.setFont(bold_font_name, 8)
        canvas.setFillColor(colors.black)
        canvas.drawString(margin_left, footer_y, "CONFIDENTIAL")
        canvas.drawString(margin_left, footer_y - 0.12 * inch, "NOT FOR DISTRIBUTION")
        canvas.setFont(font_name, 8)
        canvas.drawString(margin_left, footer_y - 0.30 * inch, "INFO@BINDLEPAPER.COM")
        
        # Right side: Disclaimer text
        disclaimer_text = """This document and the information contained herein are the exclusive property of The Bindle Paper and are for educational and informational purposes only. This material does not constitute, and should not be construed as, an offer to sell, or a solicitation of an offer to buy, any securities or related financial instruments. This document contains information and views as of the date indicated and such information and views are subject to change without notice. The Bindle Paper has no duty or obligation to update the information contained herein. Please review the full Disclaimer at the end of this document."""
        
        disclaimer_width = page_width * 0.7 - margin_right
        disclaimer_x = page_width - margin_right - disclaimer_width
        
        canvas.setFont(font_name, 7)
        canvas.setFillColor(colors.black)
        
        # Create text object for wrapping
        text_obj = canvas.beginText(disclaimer_x, footer_y)
        text_obj.setFont(font_name, 7)
        text_obj.setFillColor(colors.black)
        text_obj.setLeading(8)
        
        # Wrap text manually
        words = disclaimer_text.split()
        lines = []
        current_line = []
        
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
        
        # Draw lines
        for line_words in lines:
            text_obj.textLine(" ".join(line_words))
        
        canvas.drawText(text_obj)
    
    # Create frames for page 1: 60/40 split
    content_frame = Frame(
        margin_left,
        margin_bottom + 0.5 * inch,
        page_width * 0.6 - margin_left,
        page_height - 1.5 * inch - 0.5 * inch,
        leftPadding=0.1 * inch,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0
    )
    
    sidebar_start_x = margin_left + (page_width * 0.6)
    sidebar_width = page_width * 0.4 - margin_right
    sidebar_frame = Frame(
        sidebar_start_x,
        margin_bottom + 0.5 * inch,
        sidebar_width - 0.5 * inch,
        page_height - 1.5 * inch - 0.5 * inch,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0
    )
    
    # Page template for page 1
    def on_page(canvas, doc):
        draw_header_footer(canvas, doc)
    
    # Continuation frames for pages 2+
    available_width = page_width - margin_left - margin_right
    col_width = available_width * 0.5
    left_col_frame = Frame(
        margin_left,
        margin_bottom + 0.5 * inch,
        col_width,
        page_height - 1.5 * inch - 0.5 * inch,
        leftPadding=0.1 * inch,
        rightPadding=0.05 * inch,
        topPadding=0,
        bottomPadding=0
    )
    right_col_frame = Frame(
        margin_left + col_width,
        margin_bottom + 0.5 * inch,
        col_width,
        page_height - 1.5 * inch - 0.5 * inch,
        leftPadding=0.05 * inch,
        rightPadding=0.1 * inch,
        topPadding=0,
        bottomPadding=0
    )
    
    page_template = PageTemplate(id='Page', frames=[content_frame, sidebar_frame], onPage=on_page)
    continuation_template = PageTemplate(id='Continuation', frames=[left_col_frame, right_col_frame], onPage=on_page)
    # Make Continuation the default template; we'll force page 1 to 'Page' explicitly
    doc.addPageTemplates([continuation_template, page_template])
    
    # Create styles
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'],
        fontSize=10, textColor=colors.black, fontName=font_name,
        alignment=TA_LEFT, leading=12, spaceAfter=4
    )
    
    heading1_style = ParagraphStyle(
        'Heading1', parent=styles['Heading1'],
        fontSize=16, textColor=colors.black, fontName=bold_font_name,
        spaceBefore=12, spaceAfter=8, alignment=TA_LEFT
    )
    
    # Title style for first line (size 22, NOT bold)
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'],
        fontSize=22, textColor=colors.black, fontName=font_name,  # Not bold
        spaceBefore=0, spaceAfter=24, alignment=TA_LEFT  # Double space = 24
    )
    
    # Section header style (all caps should be bold, size 11)
    section_header_style = ParagraphStyle(
        'SectionHeader', parent=styles['Normal'],
        fontSize=11, textColor=colors.black, fontName=bold_font_name,
        spaceBefore=10, spaceAfter=10, alignment=TA_LEFT  # Single space after
    )
    
    # KEY POINTS style (bold and red, size 11)
    key_points_style = ParagraphStyle(
        'KeyPoints', parent=styles['Normal'],
        fontSize=11, textColor=colors.red, fontName=bold_font_name,
        spaceBefore=10, spaceAfter=10, alignment=TA_LEFT  # Single space after
    )
    
    # Add content to left frame
    if markdown_file and Path(markdown_file).exists():
        with open(markdown_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        line_count = 0
        max_lines = 15  # Limit first page content
        
        for i, line in enumerate(lines):
            if line_count >= max_lines:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # First line is the title (not bold)
            if i == 0 and line:
                story.append(Paragraph(line, title_style))
                line_count += 1
            # Check if it's "KEY POINTS" (red and bold)
            elif line == "**KEY POINTS**":
                story.append(Paragraph("KEY POINTS", key_points_style))
                line_count += 1
            # Check if it's an all-caps section header (bold)
            elif line.startswith('**') and line.endswith('**'):
                text = line[2:-2]
                # Check if it's all caps
                if text.isupper() or (text.replace(' ', '').replace(':', '').isupper()):
                    story.append(Paragraph(f"<b>{text}</b>", section_header_style))
                else:
                    story.append(Paragraph(f"<b>{text}</b>", normal_style))
                line_count += 1
            elif line.startswith('# '):
                text = line[2:]
                story.append(Paragraph(f"<b>{text}</b>", heading1_style))
                line_count += 1
            else:
                text = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                if text and len(text) > 3:
                    story.append(Paragraph(text, normal_style))
                    line_count += 1
    
    # Switch to sidebar frame and add info boxes
    story.append(FrameBreak())
    # Add a bit of spacing before the first sidebar table
    story.append(Spacer(1, 0.1 * inch))
    
    # Theme/Ticker table
    theme_table = Table([
        ["THEME:", theme],
        ["TICKER:", ticker],
        ["TIMEFRAME:", timeframe],
        ["CURRENT/TARGET:", current_target],
        ["DOWNSIDE:", downside],
    ], colWidths=[1.5*inch, 1.3*inch])
    
    theme_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), bold_font_name),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),  # Make THEME red
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])
    theme_table.setStyle(theme_table_style)
    story.append(theme_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # 3-Year Performance section header
    performance_header_style = ParagraphStyle(
        'PerformanceHeader', parent=styles['Normal'],
        fontSize=13, textColor=colors.red, fontName=bold_font_name,
        spaceAfter=10, alignment=TA_LEFT,
        leftIndent=-0.10 * inch
    )
    story.append(Paragraph("3-YEAR PERFORMANCE", performance_header_style))
    
    # 3-Year Performance chart
    try:
        chart_img = Image("3_YEAR.png", width=2.8*inch, height=1.5*inch)
        story.append(chart_img)
    except Exception as e:
        print(f"⚠️  Chart error: {e}")
    
    story.append(Spacer(1, 0.2 * inch))
    
    # Company Information section header
    company_header_style = ParagraphStyle(
        'CompanyHeader', parent=styles['Normal'],
        fontSize=13, textColor=colors.red, fontName=bold_font_name,
        spaceAfter=10, alignment=TA_LEFT,
        leftIndent=-0.10 * inch
    )
    story.append(Paragraph("COMPANY INFORMATION", company_header_style))
    
    # Company Information table
    company_table_data = [[k, v] for k, v in company_data.items()]
    company_table = Table(company_table_data, colWidths=[1.4*inch, 1.4*inch])
    company_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        # Interior horizontal lines between rows (exclude last row)
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#D0D0D0')),
    ])
    company_table.setStyle(company_table_style)
    story.append(company_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Trade Execution section header
    trade_header_style = ParagraphStyle(
        'TradeHeader', parent=styles['Normal'],
        fontSize=13, textColor=colors.red, fontName=bold_font_name,
        spaceAfter=10, alignment=TA_LEFT,
        leftIndent=-0.10 * inch
    )
    story.append(Paragraph("TRADE EXECUTION", trade_header_style))
    
    # Trade Execution table
    trade_table_data = [[k, v] for k, v in trade_data.items()]
    trade_table = Table(trade_table_data, colWidths=[1.4*inch, 1.4*inch])
    trade_table_style = TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), bold_font_name),
        ('FONTNAME', (1, 0), (1, -1), font_name),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#F5F5F5')),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#D0D0D0')),
        ('LINEAFTER', (0, 0), (0, -1), 1, HexColor('#D0D0D0')),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        # Interior horizontal lines between rows (exclude last row)
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#D0D0D0')),
    ])
    trade_table.setStyle(trade_table_style)
    story.append(trade_table)
    
    # Switch to continuation template BEFORE page break so page 2+ use it
    story.append(NextPageTemplate('Continuation'))
    
    # Force page break after sidebar - subsequent content goes to continuation pages
    story.append(PageBreak())
    
    # Add remaining markdown content (lines after the first-page limit)
    if markdown_file and Path(markdown_file).exists():
        with open(markdown_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Reuse styles; define heading2 if needed
        heading2_style = ParagraphStyle(
            'Heading2', parent=styles['Heading2'],
            fontSize=14, textColor=colors.black, fontName=bold_font_name,
            spaceBefore=10, spaceAfter=6, alignment=TA_LEFT
        )
        normal_style_cont = ParagraphStyle(
            'NormalCont', parent=styles['Normal'],
            fontSize=10, textColor=colors.black, fontName=font_name,
            alignment=TA_LEFT, leading=12, spaceAfter=4
        )
        
        # Count how many content lines were consumed on page 1 (excluding images)
        consumed = 0
        for i, raw in enumerate(lines):
            line = raw.strip()
            if not line:
                continue
            if consumed >= 15:
                break
            if line.startswith('!['):
                # images were not counted on page 1 body; skip counting
                continue
            consumed += 1
        
        # Add the rest
        for raw in lines[i+1:]:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('**') and line.endswith('**'):
                text = line[2:-2]
                story.append(Paragraph(f"<b>{text}</b>", normal_style_cont))
            elif line.startswith('# '):
                text = line[2:]
                story.append(Paragraph(f"<b>{text}</b>", heading1_style))
            elif line.startswith('## '):
                text = line[3:]
                story.append(Paragraph(f"<b>{text}</b>", heading2_style))
            elif line.startswith('- ') or line.startswith('* '):
                text = line[2:]
                story.append(Paragraph(f"• {text}", normal_style_cont))
            elif line.startswith('!['):
                import re
                match = re.search(r'!\[.*?\]\((.*?)\)\{width="([^"]+)" height="([^"]+)"\}', line)
                if match:
                    img_path = match.group(1)
                    orig_width = float(match.group(2).replace('in', '')) * inch
                    orig_height = float(match.group(3).replace('in', '')) * inch
                    max_img_width = 2.75 * inch
                    if orig_width > max_img_width:
                        scale = max_img_width / orig_width
                        img_width = max_img_width
                        img_height = orig_height * scale
                    else:
                        img_width = orig_width
                        img_height = orig_height
                    try:
                        img = Image(img_path, width=img_width, height=img_height)
                        story.append(img)
                        story.append(Spacer(1, 0.2 * inch))
                    except Exception:
                        pass
                continue
            else:
                text = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                text = text.replace('**', '<b>').replace('**', '</b>')
                story.append(Paragraph(text, normal_style_cont))
        # Attribution text - right-aligned, directly below table
    story.append(Spacer(1, 0.05 * inch))  # Reduced spacing to be closer to table
    attribution_style = ParagraphStyle('Attribution', parent=styles['Normal'], fontSize=7, fontName=font_name, alignment=TA_RIGHT)
    story.append(Paragraph(f"All data as of {date}", attribution_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ Created: {output_file}")
    return output_file


if __name__ == "__main__":
    generate_report()

