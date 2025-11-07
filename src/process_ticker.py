#!/usr/bin/env python3
"""
Process Ticker Pipeline

Runs the full pipeline to process a ticker from DOCX to PDF report:
1. Convert DOCX to Markdown (with image extraction)
2. Generate PDF report from Markdown

Usage:
    python process_ticker.py TICKER
    
Example:
    python process_ticker.py AZEK
"""

import sys
import subprocess
from pathlib import Path
import click
import yaml


def get_pdf_filename(ticker: str, ticker_dir: Path) -> str:
    """
    Determine the PDF filename based on ticker config.
    Returns just the filename (not full path).
    """
    config_file = ticker_dir / f'{ticker}_config.yaml'
    
    # Try to load config to get report_saving info
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config and 'report_saving' in config:
                    rs = config['report_saving']
                    return f"{rs['ticker']}.{rs['issue']}.{rs['date']}.pdf"
        except Exception:
            pass  # Fall back to default
    
    # Default naming convention
    return f'{ticker}_report.pdf'


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {str(e)}")
        return False


@click.command()
@click.argument('ticker', type=str)
@click.option('--report-type', '-r', type=click.Choice(['Initiation', 'Updates']), default='Initiation',
              help='Report type: Initiation or Updates (default: Initiation)')
@click.option('--skip-conversion', is_flag=True, 
              help='Skip DOCX to Markdown conversion (use existing markdown)')
@click.option('--skip-pdf', is_flag=True,
              help='Skip PDF generation (only convert DOCX to markdown)')
@click.option('--max-height', type=float, default=9.5,
              help='Maximum height in inches for first page content (default: 9.5)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(ticker: str, report_type: str, skip_conversion: bool, skip_pdf: bool, max_height: float, verbose: bool):
    """
    Process a ticker through the full pipeline: DOCX → Markdown → PDF
    
    TICKER: Stock ticker symbol (e.g., AZEK)
    """
    project_root = Path(__file__).parent.parent  # Go up from src/ to project root
    ticker = ticker.upper()
    
    # Define paths with report type subfolder
    ticker_dir = project_root / 'Tickers' / ticker / report_type
    docx_file = ticker_dir / f'{ticker}.docx'
    markdown_file = ticker_dir / f'{ticker}.md'
    pdf_filename = get_pdf_filename(ticker, ticker_dir)
    pdf_file = ticker_dir / pdf_filename
    
    print(f"\n{'='*60}")
    print(f"📊 Processing Ticker: {ticker} ({report_type})")
    print(f"{'='*60}")
    print(f"📂 Ticker directory: {ticker_dir}")
    print(f"📄 DOCX file: {docx_file}")
    print(f"📝 Markdown file: {markdown_file}")
    print(f"📕 PDF report: {pdf_file}")
    
    # Step 1: Convert DOCX to Markdown
    if not skip_conversion:
        # Check if DOCX file exists
        if not docx_file.exists():
            print(f"\n❌ Error: DOCX file not found: {docx_file}")
            print(f"💡 Please place {ticker}.docx in {ticker_dir}")
            sys.exit(1)
        
        # Run conversion
        cmd = [
            sys.executable,
            str(project_root / 'src' / 'docx_to_markdown.py'),
            str(docx_file),
            '--ticker', ticker,
            '--report-type', report_type
        ]
        if verbose:
            cmd.append('--verbose')
        
        if not run_command(cmd, f"Converting {ticker}.docx to Markdown"):
            sys.exit(1)
    else:
        print(f"\n⏭️  Skipping DOCX conversion")
        # Check if markdown exists if we're skipping conversion
        if not skip_pdf and not markdown_file.exists():
            print(f"❌ Error: Markdown file not found: {markdown_file}")
            print(f"💡 Cannot skip conversion without existing markdown file")
            sys.exit(1)
    
    # Step 2: Generate PDF report
    if not skip_pdf:
        # Check if markdown file exists
        if not markdown_file.exists():
            print(f"\n❌ Error: Markdown file not found: {markdown_file}")
            print(f"💡 DOCX conversion may have failed")
            sys.exit(1)
        
        # Run PDF generation
        cmd = [
            sys.executable,
            str(project_root / 'src' / 'generate_report.py'),
            '--ticker', ticker,
            '--report-type', report_type,
            '--max-height', str(max_height)
        ]
        
        if not run_command(cmd, f"Generating PDF report for {ticker}"):
            sys.exit(1)
    else:
        print(f"\n⏭️  Skipping PDF generation")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Pipeline completed for {ticker}")
    print(f"{'='*60}")
    if not skip_conversion:
        print(f"✅ Markdown: {markdown_file}")
    if not skip_pdf:
        print(f"✅ PDF Report: {pdf_file}")
    print()


if __name__ == "__main__":
    main()

