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


def convert_docx_to_markdown(docx_path: str, ticker: str = None, output_dir: str = None, report_type: str = 'Initiating') -> str:
    """
    Convert a DOCX file to Markdown while extracting images.
    
    Args:
        docx_path: Path to the input DOCX file
        ticker: Ticker symbol (e.g., 'AZEK') for organizing files
        output_dir: Directory to save the markdown file (defaults to Tickers/{ticker}/{report_type}/)
        report_type: Report type folder ('Initiating' or 'Update')
    
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
    
    # Set output directory to Tickers/{ticker}/{report_type}/ by default
    if output_dir is None:
        output_dir = Path("Tickers") / ticker / report_type
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
        
        # Unescape dollar signs that pandoc escaped (prevents \$ from appearing in PDFs)
        markdown_content = unescape_dollar_signs(markdown_content)
        
        # Convert pandoc superscript syntax ^text^ to HTML <sup>text</sup>
        markdown_content = convert_superscripts(markdown_content)
        
        # Unescape HTML comments (e.g., <!-- APPENDIX -->) that pandoc escaped
        markdown_content = unescape_html_comments(markdown_content)
        
        # Bold all-caps headings that pandoc didn't mark as bold
        markdown_content = bold_all_caps_headings(markdown_content)
        
        # NOTE: Section spacing code disabled - see commented function below
        # This previously added two blank lines before bold headings (except first)
        # Disabled to preserve natural spacing from DOCX conversion
        # markdown_content = add_section_spacing(markdown_content)
        
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


def unescape_dollar_signs(markdown_content: str) -> str:
    r"""
    Remove backslash escaping from dollar signs.
    
    Pandoc escapes $ as \$ to prevent math syntax interpretation,
    but this causes issues in PDF rendering. This function unescapes them.
    """
    # Replace \$ with $ (remove the escape sequence)
    return markdown_content.replace(r'\$', '$')


def convert_superscripts(markdown_content: str) -> str:
    """
    Convert pandoc superscript syntax ^text^ to HTML <sup>text</sup>.
    
    Pandoc uses ^text^ for superscripts, but Python markdown library doesn't
    support this syntax. Convert to HTML sup tags for proper rendering.
    """
    # Replace ^text^ with <sup>text</sup>
    # Match ^ followed by 1-3 characters followed by ^
    # This handles common cases like ^th^, ^st^, ^nd^, ^rd^, etc.
    return re.sub(r'\^([^\^]{1,3})\^', r'<sup>\1</sup>', markdown_content)


def unescape_html_comments(markdown_content: str) -> str:
    """
    Unescape HTML comments that pandoc escaped during conversion.
    
    Pandoc escapes HTML comments like <!-- APPENDIX --> to \<!\-- APPENDIX \--\>
    This function reverts them back to proper HTML comment syntax so they can
    be used as markers in the markdown processing pipeline.
    
    Args:
        markdown_content: Markdown text with escaped HTML comments
    
    Returns:
        Markdown with proper HTML comment syntax
    """
    # Pattern matches: \<!\-- (any content) \--\>
    # Note: The ! is not escaped in pandoc's output
    # Replace with: <!-- content -->
    return re.sub(r'\\<!\\--\s*(.*?)\s*\\--\\>', r'<!-- \1 -->', markdown_content)


def bold_all_caps_headings(markdown_content: str) -> str:
    """
    Convert standalone all-caps lines to bold markdown format.
    
    In DOCX files, section headings are often styled as bold all-caps text.
    Pandoc sometimes converts these as plain text. This function detects
    standalone all-caps lines and wraps them in ** to make them bold.
    
    Args:
        markdown_content: Markdown text
    
    Returns:
        Markdown with all-caps lines bolded
    """
    lines = markdown_content.split('\n')
    result = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Check if this is an all-caps line (at least 2 words, all uppercase letters/spaces)
        # Must be standalone (surrounded by blank lines or start/end of content)
        # Must not already be bold (no ** markers)
        if (stripped and 
            len(stripped.split()) >= 2 and 
            stripped.replace(' ', '').replace('-', '').isalpha() and
            stripped.isupper() and 
            not stripped.startswith('**') and
            not stripped.startswith('#') and
            not stripped.startswith('-') and
            not stripped.startswith('*')):
            
            # Check if it's standalone (surrounded by empty lines)
            prev_empty = (i == 0) or (not lines[i-1].strip())
            next_empty = (i == len(lines)-1) or (not lines[i+1].strip())
            
            if prev_empty and next_empty:
                result.append(f'**{stripped}**')
                continue
        
        result.append(line)
    
    return '\n'.join(result)


# ==============================================================================
# DISABLED: Section Spacing Function
# ==============================================================================
# This function was previously used to add two blank lines before bold headings
# in the markdown output (e.g., before **PREMISE OF THE SHORT**, **COMPANY DESCRIPTION**, etc.)
# 
# REASON FOR DISABLING:
# - Decision made to preserve natural spacing from DOCX conversion
# - Spacing is now handled by CSS in the PDF generation step (see style_bold_headings 
#   in src/generate_report.py which adds margin-top to bold headings)
# 
# HOW IT WORKED:
# - Detected lines that start and end with ** (bold headings)
# - Removed any existing blank lines before the heading
# - Added exactly 2 blank lines before each bold heading
# - Exception: First bold heading (KEY POINTS) received no extra spacing
# 
# TO RE-ENABLE:
# - Uncomment this function and the call on line ~81 above
# - Consider whether CSS styling in generate_report.py should also be adjusted
# 
# LAST ACTIVE: 2025-01-06
# ==============================================================================

# def add_section_spacing(markdown_content: str) -> str:
#     """
#     Add extra blank lines before bold section headings.
#     Exception: First **TEXT** section (KEY POINTS) gets no extra spacing.
#     """
#     lines = markdown_content.split('\n')
#     result = []
#     first_bold_heading = True
#     
#     for i, line in enumerate(lines):
#         stripped = line.strip()
#         
#         # Check if this is a bold heading (starts and ends with **)
#         is_bold_heading = (
#             stripped.startswith('**') and 
#             stripped.endswith('**') and 
#             len(stripped) > 4  # More than just '****'
#         )
#         
#         if is_bold_heading:
#             if first_bold_heading:
#                 # First bold heading - no extra spacing
#                 first_bold_heading = False
#                 result.append(line)
#             else:
#                 # Subsequent bold headings - add two blank lines before
#                 # Remove any existing blank lines before this heading
#                 while result and result[-1].strip() == '':
#                     result.pop()
#                 
#                 # Add exactly two blank lines
#                 result.append('')
#                 result.append('')
#                 result.append(line)
#         else:
#             result.append(line)
#     
#     return '\n'.join(result)


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
@click.option('--report-type', '-r', type=click.Choice(['Initiating', 'Update']), default='Initiating',
              help='Report type: Initiating or Update (default: Initiating)')
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory for the markdown file (defaults to Tickers/{ticker}/{report_type}/)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(docx_file: Path, ticker: str = None, report_type: str = 'Initiating', output_dir: Path = None, verbose: bool = False):
    """
    Convert a DOCX file to Markdown format while extracting and preserving images.
    
    DOCX_FILE: Path to the input DOCX file
    
    Images are extracted to Tickers/{ticker}/{report_type}/images/ and markdown is saved to Tickers/{ticker}/{report_type}/{ticker}.md
    """
    # Determine ticker from filename if not provided
    if ticker is None:
        ticker = docx_file.stem
        if verbose:
            print(f"📊 Using ticker: {ticker} (from filename)")
    
    if verbose:
        print(f"🔄 Converting {docx_file} to Markdown...")
        print(f"📂 Ticker: {ticker}")
        print(f"📂 Report type: {report_type}")
        print(f"📂 Output directory: {output_dir or f'Tickers/{ticker}/{report_type}/'}")
    
    try:
        # Check if pandoc is available
        pypandoc.get_pandoc_version()
        
        # Convert the file
        markdown_path = convert_docx_to_markdown(docx_file, ticker=ticker, output_dir=output_dir, report_type=report_type)
        
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
