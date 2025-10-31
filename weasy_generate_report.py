#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Tuple

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS


def split_markdown(content: str, max_nonempty_lines: int = 15) -> Tuple[str, str]:
    lines = content.splitlines()
    first, rest = [], []
    count = 0
    for i, ln in enumerate(lines):
        if count < max_nonempty_lines:
            first.append(ln)
            if ln.strip():
                count += 1
        else:
            rest = lines[i:]
            break
    return "\n".join(first), "\n".join(rest)


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


def load_markdown_with_front_matter(md_path: Path) -> Tuple[Dict[str, Any], str, str]:
    post = frontmatter.load(md_path)
    meta = dict(post.metadata or {})
    first_md, rest_md = split_markdown(post.content, max_nonempty_lines=15)
    first_html = md_to_html(first_md)
    rest_html = md_to_html(rest_md)
    return meta, first_html, rest_html


def render_pdf(
    markdown_file: str = 'AZEK.md',
    output_file: str = 'templates/AZEK_report_weasy.pdf',
) -> str:
    project_root = Path(__file__).parent
    templates_dir = project_root / 'templates'

    md_path = project_root / markdown_file
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_path}")

    meta, first_html, rest_html = load_markdown_with_front_matter(md_path)

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

    # Defaults (can be overridden by front matter)
    defaults = {
        'issue_number': '37',
        'date': '02.20.2025',
        'theme': 'INVENTORY GLUT',
        'ticker': 'AZEK:US',
        'timeframe': '6-9 MONTHS',
        'current_target': '$49.90 | $30.00',
        'downside': '39.9%',
        'company_data': {
            'SECTOR': 'Industrials',
            'LOCATION': 'United States',
            'MARKET CAP': '$7.3B',
            'EV/EBITDA': '20.94',
            'TRAILING P/E': '51.55',
            'PROFIT MARGIN': '9.85%',
            'TOTAL CASH/DEBT': '$148M / $552M',
            '52 WEEK RANGE': '$35.48 - $54.91',
        },
        'trade_data': {
            'DAILY VOLUME': '$74M',
            'DAYS TO COVER': '3.26',
            'SHARES SHORT': '3.33%',
            'BORROW COST': '0.3%',
        },
        'chart_img': '3_YEAR.png',
        'logo_img': 'assets/Base/bindle_logo.png',
        'font_regular': 'assets/fonts/Source_Sans_3/static/SourceSans3-Regular.ttf',
        'font_bold': 'assets/fonts/Source_Sans_3/static/SourceSans3-Bold.ttf',
    }

    # Front matter overrides defaults
    data = {**defaults, **meta}

    # Jinja environment
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template('report.html')

    html_str = template.render(
        md_first_html=first_html, 
        md_cont_html=rest_html, 
        disclaimer_html=disclaimer_html,
        **data
    )

    css_path = str(templates_dir / 'report.css')
    output_path = project_root / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Base URL is project root so relative paths (images, fonts) resolve
    HTML(string=html_str, base_url=str(project_root)).write_pdf(
        str(output_path), stylesheets=[CSS(css_path)]
    )

    print(f"✅ Created: {output_path}")
    return str(output_path)


if __name__ == '__main__':
    markdown_file = sys.argv[1] if len(sys.argv) > 1 else 'AZEK.md'
    render_pdf(markdown_file=markdown_file)

