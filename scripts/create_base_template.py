#!/usr/bin/env python3
"""
Base PDF Template Generator

Creates reusable PDF base templates for the Bindle reports system.
Based on base_template.pdf structure:
- Page 1: Content Page Template (main report pages)
- Page 2: Disclaimer Page Template (legal disclaimers)
- Page 3: Back Page Template (final page)
"""

import click
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Frame, PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class BaseTemplateGenerator:
    """Generator for Bindle PDF base templates"""
    
    def __init__(self, output_dir: Path, logo_path: Path, disclaimer_path: Path):
        self.output_dir = Path(output_dir)
        self.logo_path = Path(logo_path)
        self.disclaimer_path = Path(disclaimer_path)
        
        # Page dimensions
        self.page_width, self.page_height = letter
        
        # Margins (based on base_template.pdf)
        self.margin_left = 0.75 * inch
        self.margin_right = 0.75 * inch
        self.margin_top = 1.0 * inch
        self.margin_bottom = 0.75 * inch
        
        # Logo dimensions
        self.logo_width = 2.5 * inch
        self.logo_height = 0.70 * inch  # Maintains aspect ratio for Bindle logo
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def load_disclaimer_text(self) -> str:
        """Load disclaimer text from markdown file"""
        with open(self.disclaimer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Strip markdown headers and return plain text
        lines = []
        for line in content.split('\n'):
            if not line.startswith('##'):
                lines.append(line)
        return '\n'.join(lines).strip()
    
    def create_content_page_template(self):
        """
        Create Page 1: Content Page Template
        - Header with Bindle logo (top-left)
        - Main content area
        - Footer with page numbers
        """
        output_path = self.output_dir / "content_page_template.pdf"
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Draw logo in header (top-left)
        logo_x = self.margin_left
        logo_y = self.page_height - self.margin_top + 0.25 * inch
        c.drawImage(str(self.logo_path), logo_x, logo_y, 
                   width=self.logo_width, height=self.logo_height, 
                   preserveAspectRatio=True, mask='auto')
        
        # Draw header line separator
        line_y = self.page_height - self.margin_top
        c.setStrokeColor(colors.HexColor('#CCCCCC'))
        c.setLineWidth(0.5)
        c.line(self.margin_left, line_y, 
               self.page_width - self.margin_right, line_y)
        
        # Draw content area placeholder text
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        content_y = self.page_height - self.margin_top - 1.0 * inch
        c.drawString(self.margin_left, content_y, 
                    "[Content area - report content will appear here]")
        
        # Draw footer with page number placeholder
        footer_y = self.margin_bottom - 0.25 * inch
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)
        c.drawCentredString(self.page_width / 2, footer_y, "Page 1")
        
        c.save()
        print(f"✅ Created: {output_path}")
        return output_path
    
    def create_disclaimer_page_template(self):
        """
        Create Page 2: Disclaimer Page Template
        - Full page disclaimer text
        - Header with logo
        - Professional legal text formatting
        """
        output_path = self.output_dir / "disclaimer_page_template.pdf"
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Draw logo in header
        logo_x = self.margin_left
        logo_y = self.page_height - self.margin_top + 0.25 * inch
        c.drawImage(str(self.logo_path), logo_x, logo_y, 
                   width=self.logo_width, height=self.logo_height, 
                   preserveAspectRatio=True, mask='auto')
        
        # Draw header line
        line_y = self.page_height - self.margin_top
        c.setStrokeColor(colors.HexColor('#CCCCCC'))
        c.setLineWidth(0.5)
        c.line(self.margin_left, line_y, 
               self.page_width - self.margin_right, line_y)
        
        # Load and draw disclaimer text
        disclaimer_text = self.load_disclaimer_text()
        
        # Set up text object for disclaimer
        text_obj = c.beginText(self.margin_left, self.page_height - self.margin_top - 0.75 * inch)
        text_obj.setFont("Helvetica", 8)
        text_obj.setFillColor(colors.black)
        text_obj.setLeading(10)  # Line spacing
        
        # Calculate available width for text wrapping
        available_width = self.page_width - self.margin_left - self.margin_right
        
        # Simple text wrapping (for production, use Paragraph from platypus)
        words = disclaimer_text.split()
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            # Rough character width estimation
            if len(test_line) * 4.5 < available_width:  # ~4.5 points per char at 8pt font
                line = test_line
            else:
                text_obj.textLine(line)
                line = word
        if line:
            text_obj.textLine(line)
        
        c.drawText(text_obj)
        
        # Footer
        footer_y = self.margin_bottom - 0.25 * inch
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)
        c.drawCentredString(self.page_width / 2, footer_y, "Page 2")
        
        c.save()
        print(f"✅ Created: {output_path}")
        return output_path
    
    def create_back_page_template(self):
        """
        Create Page 3: Back Page Template
        - Final page with Bindle branding
        - Minimal design
        """
        output_path = self.output_dir / "back_page_template.pdf"
        c = canvas.Canvas(str(output_path), pagesize=letter)
        
        # Draw logo centered on page
        logo_x = (self.page_width - self.logo_width) / 2
        logo_y = self.page_height / 2
        c.drawImage(str(self.logo_path), logo_x, logo_y, 
                   width=self.logo_width, height=self.logo_height, 
                   preserveAspectRatio=True, mask='auto')
        
        # Add property ownership text at bottom
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        footer_text = "© The Bindle Paper, LLC. All rights reserved."
        c.drawCentredString(self.page_width / 2, self.margin_bottom, footer_text)
        
        c.save()
        print(f"✅ Created: {output_path}")
        return output_path
    
    def generate_all_templates(self):
        """Generate all three base templates"""
        print("\n🔨 Generating PDF Base Templates...")
        print(f"📂 Output directory: {self.output_dir.absolute()}")
        print(f"🖼️  Logo: {self.logo_path}")
        print(f"📄 Disclaimer: {self.disclaimer_path}\n")
        
        templates = []
        templates.append(self.create_content_page_template())
        templates.append(self.create_disclaimer_page_template())
        templates.append(self.create_back_page_template())
        
        print(f"\n✅ Successfully generated {len(templates)} base templates!")
        print(f"📁 Templates saved to: {self.output_dir.absolute()}\n")
        
        return templates


@click.command()
@click.option('--output-dir', '-o', default='templates', 
              help='Output directory for generated templates')
@click.option('--logo', '-l', default='assets/Base/bindle_logo.png',
              help='Path to Bindle logo image')
@click.option('--disclaimer', '-d', default='assets/Base/bast_template.md',
              help='Path to disclaimer text file')
def main(output_dir: str, logo: str, disclaimer: str):
    """
    Generate PDF base templates for Bindle reports.
    
    Creates three template files:
    - content_page_template.pdf (main report pages)
    - disclaimer_page_template.pdf (legal disclaimers)
    - back_page_template.pdf (final page)
    """
    try:
        generator = BaseTemplateGenerator(
            output_dir=Path(output_dir),
            logo_path=Path(logo),
            disclaimer_path=Path(disclaimer)
        )
        
        generator.generate_all_templates()
        
    except FileNotFoundError as e:
        print(f"❌ Error: Required file not found - {e}")
        print("\nMake sure the following files exist:")
        print(f"  - Logo: {logo}")
        print(f"  - Disclaimer: {disclaimer}")
        raise click.Abort()
    except Exception as e:
        print(f"❌ Error generating templates: {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()

