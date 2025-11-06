#!/usr/bin/env python3
"""
DOCX to Markdown Converter

Converts DOCX files to Markdown format while extracting and preserving all images.
Images are extracted to the assets/Images directory and properly referenced in the markdown.
"""

import os
import sys
import click
from pathlib import Path
import pypandoc
import re


def convert_docx_to_markdown(docx_path: str, ticker: str = None, output_dir: str = None) -> str:
    """
    Convert a DOCX file to Markdown while extracting images.
    
    Args:
        docx_path: Path to the input DOCX file
        ticker: Ticker symbol (e.g., 'AZEK') for organizing files
        output_dir: Directory to save the markdown file (defaults to Tickers/{ticker}/)
    
    Returns:
        Path to the created markdown file
    """
    docx_path = Path(docx_path)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    if not docx_path.suffix.lower() == '.docx':
        raise ValueError(f"File must be a .docx file: {docx_path}")
    
    # Determine ticker from docx filename if not provided
    if ticker is None:
        ticker = docx_path.stem
    
    # Set output directory to Tickers/{ticker}/ by default
    if output_dir is None:
        output_dir = Path("Tickers") / ticker
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create images directory within the ticker folder
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Output markdown file path
    markdown_path = output_dir / f"{ticker}.md"
    
    try:
        # Convert DOCX to Markdown with image extraction
        # The --extract-media option tells pandoc to extract images to the specified directory
        # Extract to a temp location first, then move
        extract_path = str(images_dir.parent)  # Extract to Tickers/{ticker}/
        extra_args = [
            f'--extract-media={extract_path}',
            '--wrap=none',  # Don't wrap lines
            '--markdown-headings=atx'  # Use # style headings
        ]
        
        # Convert the file
        markdown_content = pypandoc.convert_file(
            str(docx_path),
            'markdown',
            extra_args=extra_args
        )
        
        # Fix image paths in the markdown content
        # Pandoc extracts images to {extract_path}/media/ but we want them referenced as images/
        markdown_content = fix_image_paths(markdown_content)
        
        # Add section spacing (two blank lines before bold headings, except the first)
        markdown_content = add_section_spacing(markdown_content)
        
        # Move images from media/ subdirectory to the images/ directory
        move_images_from_media_dir(images_dir)
        
        # Write the markdown file
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Successfully converted {docx_path.name} to {markdown_path.name}")
        print(f"📁 Images extracted to: {images_dir.absolute()}")
        print(f"📄 Markdown saved to: {markdown_path.absolute()}")
        
        return str(markdown_path)
        
    except Exception as e:
        print(f"❌ Error converting {docx_path.name}: {str(e)}")
        raise


def fix_image_paths(markdown_content: str) -> str:
    """
    Fix image paths in markdown content to point to the correct location.
    
    Pandoc extracts images to media/ subdirectory but we want them referenced as images/
    """
    # Pattern to match markdown image syntax: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image_path(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # If the path contains 'media/', replace with 'images/'
        if 'media/' in image_path:
            # Extract just the filename from the media path
            filename = os.path.basename(image_path)
            new_path = f"images/{filename}"
        else:
            new_path = image_path
            
        return f"![{alt_text}]({new_path})"
    
    return re.sub(image_pattern, replace_image_path, markdown_content)


def add_section_spacing(markdown_content: str) -> str:
    """
    Add extra blank lines before bold section headings.
    Exception: First **TEXT** section (KEY POINTS) gets no extra spacing.
    """
    lines = markdown_content.split('\n')
    result = []
    first_bold_heading = True
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this is a bold heading (starts and ends with **)
        is_bold_heading = (
            stripped.startswith('**') and 
            stripped.endswith('**') and 
            len(stripped) > 4  # More than just '****'
        )
        
        if is_bold_heading:
            if first_bold_heading:
                # First bold heading - no extra spacing
                first_bold_heading = False
                result.append(line)
            else:
                # Subsequent bold headings - add two blank lines before
                # Remove any existing blank lines before this heading
                while result and result[-1].strip() == '':
                    result.pop()
                
                # Add exactly two blank lines
                result.append('')
                result.append('')
                result.append(line)
        else:
            result.append(line)
    
    return '\n'.join(result)


def move_images_from_media_dir(images_dir: Path):
    """
    Move images from media/ subdirectory to images/ directory and remove the media directory.
    """
    # media directory is created by pandoc at the parent level
    media_dir = images_dir.parent / "media"
    if media_dir.exists() and media_dir.is_dir():
        # Move all files from media/ to the images directory
        for image_file in media_dir.iterdir():
            if image_file.is_file():
                target_path = images_dir / image_file.name
                # Handle if file already exists (don't overwrite)
                if not target_path.exists():
                    image_file.rename(target_path)
                    print(f"📁 Moved {image_file.name} to images/")
                else:
                    print(f"⚠️  Skipped {image_file.name} (already exists)")
                    # Delete the duplicate from media directory
                    image_file.unlink()
        
        # Remove the now-empty media directory
        try:
            media_dir.rmdir()
            print(f"🗑️  Removed empty media directory")
        except OSError as e:
            # If rmdir fails, force remove with shutil
            import shutil
            try:
                shutil.rmtree(media_dir)
                print(f"🗑️  Removed media directory (forced)")
            except Exception as cleanup_error:
                print(f"⚠️  Could not remove media directory: {cleanup_error}")


@click.command()
@click.argument('docx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--ticker', '-t', type=str, 
              help='Ticker symbol (e.g., AZEK). If not provided, uses the filename stem.')
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory for the markdown file (defaults to Tickers/{ticker}/)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(docx_file: Path, ticker: str = None, output_dir: Path = None, verbose: bool = False):
    """
    Convert a DOCX file to Markdown format while extracting and preserving images.
    
    DOCX_FILE: Path to the input DOCX file
    
    Images are extracted to Tickers/{ticker}/images/ and markdown is saved to Tickers/{ticker}/{ticker}.md
    """
    # Determine ticker from filename if not provided
    if ticker is None:
        ticker = docx_file.stem
        if verbose:
            print(f"📊 Using ticker: {ticker} (from filename)")
    
    if verbose:
        print(f"🔄 Converting {docx_file} to Markdown...")
        print(f"📂 Ticker: {ticker}")
        print(f"📂 Output directory: {output_dir or f'Tickers/{ticker}/'}")
    
    try:
        # Check if pandoc is available
        pypandoc.get_pandoc_version()
        
        # Convert the file
        markdown_path = convert_docx_to_markdown(docx_file, ticker=ticker, output_dir=output_dir)
        
        if verbose:
            print(f"📄 Markdown file created: {markdown_path}")
            
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        if "pandoc" in str(e).lower():
            print("\n💡 Make sure pandoc is installed:")
            print("   sudo apt install pandoc")
            print("   or")
            print("   uv run --with pypandoc-binary python -c \"import pypandoc; pypandoc.download_pandoc()\"")
        sys.exit(1)


if __name__ == "__main__":
    main()
