#!/usr/bin/env python3
from __future__ import annotations

import sys
import io
import re
from pathlib import Path
from typing import Any, Dict, Tuple, List

import frontmatter
import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS


def parse_markdown_blocks(content: str) -> List[str]:
    """Parse markdown into logical blocks - each bullet point is its own block"""
    blocks = []
    current_block = []
    
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this is a list item
        is_list_item = bool(re.match(r'^[\*\-\+]\s+', stripped) or re.match(r'^\d+\.\s+', stripped))
        
        # Check if this is a heading (**, bold, or #)
        is_heading = stripped.startswith('#') or (stripped.startswith('**') and stripped.endswith('**'))
        
        # Empty line - end current block
        if not stripped:
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            i += 1
            continue
        
        # Heading - save as its own block
        if is_heading:
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            blocks.append(line)
            i += 1
            continue
        
        # List item - each bullet is its own block (allows incremental height checking)
        if is_list_item:
            if current_block:
                blocks.append('\n'.join(current_block))
                current_block = []
            
            # Collect this bullet and any continuation lines
            bullet_lines = [line]
            i += 1
            # Look ahead for continuation lines (indented or part of same bullet)
            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()
                # If next line is another bullet or empty or heading, stop
                if not next_stripped:
                    break
                is_next_bullet = bool(re.match(r'^[\*\-\+]\s+', next_stripped) or re.match(r'^\d+\.\s+', next_stripped))
                is_next_heading = next_stripped.startswith('#') or (next_stripped.startswith('**') and next_stripped.endswith('**'))
                if is_next_bullet or is_next_heading:
                    break
                # Continuation line (indented or part of bullet)
                bullet_lines.append(next_line)
                i += 1
            
            blocks.append('\n'.join(bullet_lines))
            continue
        
        # Regular paragraph line
        current_block.append(line)
        i += 1
    
    # Don't forget the last block
    if current_block:
        blocks.append('\n'.join(current_block))
    
    return blocks


def measure_content_height(html_content: str, project_root: Path) -> float:
    """Render HTML content and return its height in inches"""
    templates_dir = project_root / 'templates'
    
    # Create minimal test HTML that mimics the .fp-left column
    test_html = f'''
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        @font-face {{
          font-family: 'SourceSans3';
          src: url('assets/fonts/Source_Sans_3/static/SourceSans3-Regular.ttf') format('truetype');
          font-weight: 400;
        }}
        @font-face {{
          font-family: 'SourceSans3';
          src: url('assets/fonts/Source_Sans_3/static/SourceSans3-Bold.ttf') format('truetype');
          font-weight: 700;
        }}
        body {{
          font-family: 'SourceSans3', Arial, sans-serif;
          margin: 0;
          padding: 0;
        }}
        .test-container {{
          /* Mimic .fp-left width in grid: 1fr with sidebar taking 2.85in */
          /* Page width 8.5in - margins 0.15in+0.23in - sidebar 2.85in - gap 0.25in = ~4.85in */
          width: 4.85in;
          padding: 0 0 0 0.1in;
          box-sizing: border-box;
        }}
        .md-first > *:first-child {{
          font-size: 22pt;
          font-weight: 400;
          line-height: 1.2;
          margin-bottom: 0.24in;
          margin-top: 0;
          text-align: left;
        }}
        .md p {{ 
          orphans: 2; 
          widows: 2; 
          margin-top: 0.1in; 
          margin-bottom: 0.1in; 
          text-align: justify; 
        }}
        .md > *:first-child {{ margin-top: 0; }}
        .md h1, .md h2, .md h3 {{ 
          break-after: avoid; 
          break-inside: avoid; 
          margin-top: 0.15in; 
        }}
        .md img {{ max-width: 100%; height: auto; }}
      </style>
    </head>
    <body>
      <div class="test-container">
        <div class="md md-first">
          {html_content}
        </div>
      </div>
    </body>
    </html>
    '''
    
    # Render to PDF in memory
    pdf_bytes = HTML(string=test_html, base_url=str(project_root)).write_pdf()
    
    # Parse PDF to get height
    from weasyprint.document import Document
    import fitz  # PyMuPDF for PDF parsing
    
    # Use PyMuPDF to get content height
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if len(doc) == 0:
        return 0.0
    
    page = doc[0]
    # Get the bounding box of all content
    blocks = page.get_text("dict")["blocks"]
    
    if not blocks:
        return 0.0
    
    # Find the bottom-most content
    max_y = 0
    for block in blocks:
        if "bbox" in block:
            max_y = max(max_y, block["bbox"][3])  # bbox[3] is the bottom coordinate
    
    doc.close()
    
    # Convert points to inches (72 points = 1 inch)
    height_inches = max_y / 72.0
    
    return height_inches


def split_markdown_by_height(
    content: str,
    max_height_inches: float,
    project_root: Path
) -> Tuple[str, str]:
    """Split markdown based on rendered height using incremental approach"""
    
    print(f"🔍 Splitting markdown by height (max: {max_height_inches}in)...")
    
    blocks = parse_markdown_blocks(content)
    print(f"   Parsed {len(blocks)} markdown blocks")
    
    accumulated = []
    
    for i, block in enumerate(blocks):
        # Try adding this block
        test_content = "\n\n".join(accumulated + [block])
        test_html = md_to_html(test_content)
        
        # Measure height
        try:
            height = measure_content_height(test_html, project_root)
            block_preview = block[:50].replace('\n', ' ') + ('...' if len(block) > 50 else '')
            print(f"   Block {i+1}/{len(blocks)}: cumulative height = {height:.2f}in | '{block_preview}'")
            
            if height > max_height_inches:
                # This block would overflow
                print(f"   ✂️  Split at block {i} (would exceed {max_height_inches}in)")
                first_part = "\n\n".join(accumulated)
                rest_part = "\n\n".join(blocks[i:])
                return (first_part, rest_part)
            
            accumulated.append(block)
            
        except Exception as e:
            print(f"   ⚠️  Error measuring block {i}: {e}")
            # On error, be conservative and stop here
            if accumulated:
                first_part = "\n\n".join(accumulated)
                rest_part = "\n\n".join(blocks[i:])
                return (first_part, rest_part)
            else:
                # If we can't even measure the first block, fall back to it
                return (block, "\n\n".join(blocks[i+1:]))
    
    # All content fits
    print(f"   ✅ All content fits within {max_height_inches}in")
    return (content, "")


def md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=[
            'extra',          # tables, fenced code, etc.
            'sane_lists',
            'smarty',
        ],
        output_format='html5'
    )


def style_exhibit_source_lines(html: str) -> str:
    """Apply small font size (9pt) to Exhibit and Source lines"""
    # Match paragraphs that start with "Exhibit" or "Source:"
    # Use [\s\S]*? for non-greedy match that includes HTML tags
    pattern = r'<p>((?:Exhibit|Source:)[\s\S]*?)</p>'
    replacement = r'<p style="font-size: 9pt;">\1</p>'
    return re.sub(pattern, replacement, html, flags=re.IGNORECASE)


def style_bold_headings(html: str, first_page: bool = False) -> str:
    """Style KEY POINTS heading on first page only (red, 13pt, bold)"""
    # NOTE: Previously this function added margin-top: 0.35in to all bold headings
    # This was disabled 2025-01-06 to preserve natural spacing from markdown
    # Now only styles KEY POINTS on first page to match sidebar headers
    
    # Match <p><strong>TEXT</strong></p> - paragraphs containing only bold text
    pattern = r'<p><strong>(.*?)</strong></p>'
    
    matches = list(re.finditer(pattern, html))
    if not matches:
        return html
    
    # Replace from end to start to preserve indices
    result = html
    
    # Process all matches in reverse order
    for i, match in enumerate(reversed(matches)):
        actual_index = len(matches) - 1 - i  # Get original index
        start, end = match.span()
        bold_text = match.group(1)
        
        if first_page and actual_index == 0:
            # First bold heading on first page (KEY POINTS): black, 13pt, bold
            styled = f'<p style="color: #000000; font-size: 13pt; font-weight: 700;"><strong>{bold_text}</strong></p>'
        else:
            # All other bold headings: no styling, use natural spacing
            # Previous behavior: styled = f'<p style="margin-top: 0.35in;"><strong>{bold_text}</strong></p>'
            styled = f'<p><strong>{bold_text}</strong></p>'
        
        result = result[:start] + styled + result[end:]
    
    return result


def load_ticker_config(ticker_dir: Path, ticker: str) -> Dict[str, Any]:
    """
    Load ticker-specific configuration from {TICKER}_config.yaml file.
    
    Args:
        ticker_dir: Path to the ticker directory
        ticker: Ticker symbol (e.g., 'AZEK')
    
    Returns:
        Dictionary with config values, or empty dict if not found
    """
    config_file = ticker_dir / f'{ticker}_config.yaml'
    
    if not config_file.exists():
        print(f"ℹ️  No config file found at {config_file}, using defaults")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                return {}
            print(f"✅ Loaded ticker config from {config_file}")
            return config
    except yaml.YAMLError as e:
        print(f"⚠️  Error parsing {config_file}: {e}")
        print(f"   Using defaults instead")
        return {}
    except Exception as e:
        print(f"⚠️  Error reading {config_file}: {e}")
        print(f"   Using defaults instead")
        return {}


def load_update_config(ticker_dir: Path, ticker: str) -> Dict[str, Any]:
    """
    Load update-specific configuration from {TICKER}_updateconfig.yaml file.
    
    Args:
        ticker_dir: Path to the ticker Updates directory
        ticker: Ticker symbol (e.g., 'AZEK')
    
    Returns:
        Dictionary with config values, or empty dict if not found
    """
    config_file = ticker_dir / f'{ticker}_updateconfig.yaml'
    
    if not config_file.exists():
        print(f"ℹ️  No update config file found at {config_file}, using defaults")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config is None:
                return {}
            print(f"✅ Loaded update config from {config_file}")
            return config
    except yaml.YAMLError as e:
        print(f"⚠️  Error parsing {config_file}: {e}")
        print(f"   Using defaults instead")
        return {}
    except Exception as e:
        print(f"⚠️  Error reading {config_file}: {e}")
        print(f"   Using defaults instead")
        return {}


def load_markdown_with_front_matter(md_path: Path, project_root: Path, max_height_inches: float = 9.5) -> Tuple[Dict[str, Any], str, str]:
    post = frontmatter.load(md_path)
    meta = dict(post.metadata or {})
    
    # HEIGHT-BASED SPLIT instead of line count
    first_md, rest_md = split_markdown_by_height(
        post.content,
        max_height_inches=max_height_inches,
        project_root=project_root
    )
    
    # Convert markdown to HTML
    first_html = md_to_html(first_md)
    rest_html = md_to_html(rest_md)
    
    # Apply styling: Exhibit/Source lines and bold headings
    first_html = style_exhibit_source_lines(first_html)
    first_html = style_bold_headings(first_html, first_page=True)
    
    rest_html = style_exhibit_source_lines(rest_html)
    rest_html = style_bold_headings(rest_html, first_page=False)
    
    return meta, first_html, rest_html


def render_pdf(
    ticker: str = 'AZEK',
    markdown_file: str = None,
    output_file: str = None,
    max_height_inches: float = 9.5,
    report_type: str = 'Initiation',  # 'Initiation' or 'Updates'
) -> str:
    project_root = Path(__file__).parent.parent  # Go up from src/ to project root
    templates_dir = Path(__file__).parent / 'templates'  # Templates are in src/templates/

    # Ticker directory with report type subfolder
    ticker_dir = project_root / 'Tickers' / ticker / report_type
    
    # If markdown_file not specified, use ticker-based path in report type folder
    if markdown_file is None:
        md_path = ticker_dir / f'{ticker}.md'
    else:
        md_path = project_root / markdown_file
    
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    meta, first_html, rest_html = load_markdown_with_front_matter(md_path, project_root, max_height_inches)

    # Load disclaimer markdown
    disclaimer_path = project_root / 'assets' / 'Base' / 'disclaimer.md'
    if disclaimer_path.exists():
        with open(disclaimer_path, 'r', encoding='utf-8') as f:
            disclaimer_md = f.read()
            # Remove the ## Disclaimer heading as we'll add it in HTML
            disclaimer_md = disclaimer_md.replace('## Disclaimer\n', '')
            disclaimer_html = md_to_html(disclaimer_md)
    else:
        disclaimer_html = ''

    # Set base URL to the ticker report type directory so relative paths (images) resolve correctly
    base_url = str(ticker_dir) if ticker_dir.exists() else str(project_root)
    
    # Load configuration based on report type
    if report_type == 'Updates':
        ticker_config = load_update_config(ticker_dir, ticker) if ticker_dir.exists() else {}
    else:
        # Initiation reports use standard config
        ticker_config = load_ticker_config(ticker_dir, ticker) if ticker_dir.exists() else {}
    
    # Resolve chart image: ticker-specific only, in report type folder
    ticker_chart = ticker_dir / f'{ticker}_chart.png' if ticker_dir.exists() else None
    if ticker_chart and ticker_chart.exists():
        chart_img = ticker_chart.as_uri()
    else:
        print(f"⚠️  Warning: Chart image not found at {ticker_chart}")
        print(f"   Expected: {ticker}_chart.png in ticker directory")
        chart_img = None
    
    # Minimal global defaults (only truly shared settings)
    # Convert shared assets to absolute file:// URLs so they resolve correctly
    # regardless of base_url (which is set to ticker directory for images)
    global_defaults = {
        # Shared assets (logo and fonts)
        'logo_img': (project_root / 'assets' / 'Base' / 'bindle_logo.png').as_uri(),
        'symbol_logo': (project_root / 'assets' / 'Base' / 'symbol_logo.png').as_uri(),
        'font_regular': (project_root / 'assets' / 'fonts' / 'Source_Sans_3' / 'static' / 'SourceSans3-Regular.ttf').as_uri(),
        'font_bold': (project_root / 'assets' / 'fonts' / 'Source_Sans_3' / 'static' / 'SourceSans3-Bold.ttf').as_uri(),
        # Ticker-specific images
        'chart_img': chart_img,
    }

    # Configuration priority: global_defaults → ticker_config → front_matter
    data = {**global_defaults, **ticker_config, **meta}

    # Jinja environment
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html'])
    )
    
    # Select template and CSS based on report type
    if report_type == 'Updates':
        template = env.get_template('update.html')
        css_path = str(templates_dir / 'update.css')
    else:
        # Initiation reports use standard template
        template = env.get_template('report.html')
        css_path = str(templates_dir / 'report.css')

    html_str = template.render(
        md_first_html=first_html,
        md_cont_html=rest_html,
        disclaimer_html=disclaimer_html,
        **data
    )
    
    # If output_file not specified, use ticker-based path in report type folder
    if output_file is None:
        if report_type == 'Updates':
            # Updates filename format: {ticker}.Issue{issue_number}.Update{update_number}.{date}.pdf
            # Remove periods from date for filename (11.07.2025 -> 1172025)
            date_str = data.get('date', 'MMDDYYYY').replace('.', '')
            filename = f"{data.get('ticker', ticker)}.Issue{data.get('issue_number', '00')}.Update{data.get('update_number', '00')}.{date_str}.pdf"
        else:
            # Initiation reports use report_saving config or default
            if 'report_saving' in data:
                rs = data['report_saving']
                filename = f"{rs['ticker']}.{rs['issue']}.{rs['date']}.pdf"
            else:
                # Fall back to default convention
                filename = f'{ticker}_report.pdf'
        
        output_path = ticker_dir / filename  # Save to report type folder
    else:
        output_path = project_root / output_file
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    HTML(string=html_str, base_url=base_url).write_pdf(
        str(output_path), stylesheets=[CSS(css_path)]
    )

    print(f"✅ Created: {output_path}")
    return str(output_path)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate PDF report from markdown file')
    parser.add_argument('--ticker', '-t', type=str, default='AZEK',
                        help='Ticker symbol (e.g., AZEK)')
    parser.add_argument('--report-type', '-r', type=str, default='Initiation',
                        choices=['Initiation', 'Updates'],
                        help='Report type: Initiation or Updates (default: Initiation)')
    parser.add_argument('--markdown', '-m', type=str, default=None,
                        help='Path to markdown file (defaults to Tickers/{ticker}/{report_type}/{ticker}.md)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Output PDF path (defaults to Tickers/{ticker}/{report_type}/{ticker}_report.pdf)')
    parser.add_argument('--max-height', type=float, default=9.5,
                        help='Maximum height in inches for first page content (default: 9.5)')
    
    args = parser.parse_args()
    
    render_pdf(
        ticker=args.ticker, 
        markdown_file=args.markdown, 
        output_file=args.output, 
        max_height_inches=args.max_height,
        report_type=args.report_type
    )

