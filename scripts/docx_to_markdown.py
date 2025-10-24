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


def convert_docx_to_markdown(docx_path: str, output_dir: str = None) -> str:
    """
    Convert a DOCX file to Markdown while extracting images.
    
    Args:
        docx_path: Path to the input DOCX file
        output_dir: Directory to save the markdown file (defaults to same as input)
    
    Returns:
        Path to the created markdown file
    """
    docx_path = Path(docx_path)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    if not docx_path.suffix.lower() == '.docx':
        raise ValueError(f"File must be a .docx file: {docx_path}")
    
    # Set output directory
    if output_dir is None:
        output_dir = docx_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create assets/Images directory if it doesn't exist
    assets_images_dir = Path("assets/Images")
    assets_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Output markdown file path
    markdown_path = output_dir / f"{docx_path.stem}.md"
    
    try:
        # Convert DOCX to Markdown with image extraction
        # The --extract-media option tells pandoc to extract images to the specified directory
        extra_args = [
            '--extract-media=assets/Images',
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
        # Pandoc extracts images to assets/Images/media/ but we want them in assets/Images/
        markdown_content = fix_image_paths(markdown_content)
        
        # Move images from media/ subdirectory to the main assets/Images/ directory
        move_images_from_media_dir(assets_images_dir)
        
        # Write the markdown file
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Successfully converted {docx_path.name} to {markdown_path.name}")
        print(f"📁 Images extracted to: {assets_images_dir.absolute()}")
        
        return str(markdown_path)
        
    except Exception as e:
        print(f"❌ Error converting {docx_path.name}: {str(e)}")
        raise


def fix_image_paths(markdown_content: str) -> str:
    """
    Fix image paths in markdown content to point to the correct location.
    
    Pandoc extracts images to assets/Images/media/ but we want them in assets/Images/
    """
    # Pattern to match markdown image syntax: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_image_path(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        
        # If the path contains 'media/', remove it to point directly to assets/Images/
        if 'media/' in image_path:
            # Extract just the filename from the media path
            filename = os.path.basename(image_path)
            new_path = f"assets/Images/{filename}"
        else:
            new_path = image_path
            
        return f"![{alt_text}]({new_path})"
    
    return re.sub(image_pattern, replace_image_path, markdown_content)


def move_images_from_media_dir(assets_images_dir: Path):
    """
    Move images from assets/Images/media/ to assets/Images/ and remove the media directory.
    """
    media_dir = assets_images_dir / "media"
    if media_dir.exists():
        # Move all files from media/ to the parent directory
        for image_file in media_dir.iterdir():
            if image_file.is_file():
                target_path = assets_images_dir / image_file.name
                image_file.rename(target_path)
                print(f"📁 Moved {image_file.name} to assets/Images/")
        
        # Remove the now-empty media directory
        media_dir.rmdir()
        print(f"🗑️  Removed empty media directory")


@click.command()
@click.argument('docx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), 
              help='Output directory for the markdown file (defaults to same as input)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def main(docx_file: Path, output_dir: Path = None, verbose: bool = False):
    """
    Convert a DOCX file to Markdown format while extracting and preserving images.
    
    DOCX_FILE: Path to the input DOCX file
    """
    if verbose:
        print(f"🔄 Converting {docx_file} to Markdown...")
        print(f"📂 Output directory: {output_dir or docx_file.parent}")
    
    try:
        # Check if pandoc is available
        pypandoc.get_pandoc_version()
        
        # Convert the file
        markdown_path = convert_docx_to_markdown(docx_file, output_dir)
        
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
