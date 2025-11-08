#!/usr/bin/env python3
"""
Interactive Config Creator
Creates/edits ticker configuration YAML files with guided prompts.

Usage:
    uv run scripts/create_config.py TICKER --type Initiation
    uv run scripts/create_config.py TICKER --type Updates
    uv run scripts/create_config.py TICKER --type Initiation --edit
"""

import sys
import yaml
import argparse
import re
from pathlib import Path
from typing import Dict, Any, Optional
import shutil
from datetime import datetime

# Try rich for pretty output, fall back to basic
try:
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich import print as rprint
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None


# ============================================================================
# Field Definitions
# ============================================================================

INITIATION_FIELDS = {
    'issue_number': {
        'prompt': 'Issue Number',
        'required': True,
        'type': 'str',
        'example': '48',
        'description': 'Sequential issue number for the report'
    },
    'date': {
        'prompt': 'Report Date (MM.DD.YYYY)',
        'required': True,
        'type': 'date',
        'example': '01.15.2026',
        'description': 'Publication date of the report'
    },
    'table_date': {
        'prompt': 'Table Date (MM.DD.YYYY)',
        'required': False,
        'type': 'date',
        'example': '01.14.2026',
        'description': 'Date for table data (press Enter to use report date)'
    },
    'theme': {
        'prompt': 'Theme',
        'required': True,
        'type': 'str',
        'example': 'INVENTORY GLUT',
        'description': 'Main investment theme (all caps recommended)'
    },
    'ticker': {
        'prompt': 'Ticker with Exchange',
        'required': True,
        'type': 'ticker',
        'example': 'AAPL:US',
        'description': 'Stock ticker with exchange suffix'
    },
    'timeframe': {
        'prompt': 'Timeframe',
        'required': True,
        'type': 'str',
        'example': '6-9 MONTHS',
        'description': 'Expected timeframe for price target'
    },
    'current_target': {
        'prompt': 'Current/Target Prices',
        'required': True,
        'type': 'str',
        'example': '$100.00 | $75.00',
        'description': 'Current price | Target price (format: $XX.XX | $XX.XX)'
    },
    'downside': {
        'prompt': 'Downside %',
        'required': True,
        'type': 'percentage',
        'example': '25.0%',
        'description': 'Expected downside percentage'
    }
}

COMPANY_FIELDS = {
    'SECTOR': {'example': 'Technology', 'description': 'Industry sector'},
    'LOCATION': {'example': 'United States', 'description': 'Headquarters location'},
    'MARKET CAP': {'example': '$2.5T', 'description': 'Market capitalization'},
    'EV/EBITDA': {'example': '25.5', 'description': 'Enterprise value to EBITDA ratio'},
    'TRAILING P/E': {'example': '30.2', 'description': 'Trailing price-to-earnings ratio'},
    'PROFIT MARGIN': {'example': '25.3%', 'description': 'Net profit margin'},
    'TOTAL CASH/DEBT': {'example': '$100B / $50B', 'description': 'Total cash / Total debt'},
    '52 WEEK RANGE': {'example': '$100.00 - $200.00', 'description': '52-week price range'}
}

TRADE_FIELDS = {
    'DAILY VOLUME': {'example': '$500M', 'description': 'Average daily trading volume'},
    'DAYS TO COVER': {'example': '2.5', 'description': 'Short interest days to cover'},
    'SHARES SHORT': {'example': '5.2%', 'description': 'Percentage of shares shorted'},
    'BORROW COST': {'example': '0.5%', 'description': 'Cost to borrow shares for shorting'}
}

UPDATES_FIELDS = {
    'issue_number': {
        'prompt': 'Issue Number',
        'required': True,
        'type': 'str',
        'example': '37',
        'description': 'Original initiation report issue number'
    },
    'update_number': {
        'prompt': 'Update Number',
        'required': True,
        'type': 'str',
        'example': '1',
        'description': 'Sequential update number for this issue'
    },
    'date': {
        'prompt': 'Update Date (MM.DD.YYYY)',
        'required': True,
        'type': 'date',
        'example': '11.07.2025',
        'description': 'Publication date of this update'
    },
    'title': {
        'prompt': 'Update Title',
        'required': True,
        'type': 'str',
        'example': 'Strong Q1 Results Drive Momentum',
        'description': 'Title for this update report'
    },
    'ticker': {
        'prompt': 'Ticker Symbol',
        'required': True,
        'type': 'str',
        'example': 'AZEK',
        'description': 'Stock ticker symbol (without exchange)'
    },
    'stock': {
        'prompt': 'Full Company Name',
        'required': True,
        'type': 'str',
        'example': 'The AZEK Company Inc. (AZEK)',
        'description': 'Full company name with ticker'
    },
    'initiation_publish_date': {
        'prompt': 'Initiation Report Date (MM.DD.YYYY)',
        'required': True,
        'type': 'date',
        'example': '02.20.2025',
        'description': 'Original initiation report publication date'
    },
    'initiation_report_link': {
        'prompt': 'Initiation Report Link',
        'required': True,
        'type': 'url',
        'example': 'https://bindlepaper.com/reports/AZEK.Issue37.02202025.pdf',
        'description': 'URL to the original initiation report'
    },
    'price_at_publication': {
        'prompt': 'Price at Publication',
        'required': True,
        'type': 'price',
        'example': '52.30',
        'description': 'Stock price when initiation was published'
    },
    'recent_price': {
        'prompt': 'Recent Price',
        'required': True,
        'type': 'price',
        'example': '58.45',
        'description': 'Current stock price'
    },
    'target_price': {
        'prompt': 'Target Price',
        'required': True,
        'type': 'price',
        'example': '65.00',
        'description': 'Price target'
    }
}


# ============================================================================
# Validation Functions
# ============================================================================

def validate_date(date_str: str) -> bool:
    """Validate date format MM.DD.YYYY"""
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, date_str):
        return False
    try:
        month, day, year = date_str.split('.')
        datetime(int(year), int(month), int(day))
        return True
    except ValueError:
        return False


def validate_ticker(ticker: str) -> bool:
    """Validate ticker format (letters, optionally with :XX suffix)"""
    pattern = r'^[A-Z]+(?::[A-Z]{2})?$'
    return bool(re.match(pattern, ticker.upper()))


def validate_percentage(value: str) -> bool:
    """Validate percentage format"""
    # Remove % sign if present
    value = value.strip().rstrip('%')
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_price(value: str) -> bool:
    """Validate price format (can include $ and commas)"""
    # Remove $ sign and commas
    value = value.strip().lstrip('$').replace(',', '')
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """Validate URL format"""
    pattern = r'^https?://.+'
    return bool(re.match(pattern, url))


# ============================================================================
# Input/Output Functions
# ============================================================================

def print_header(message: str, edit_mode: bool = False):
    """Print section header"""
    if HAS_RICH:
        mode = "Editing" if edit_mode else "Creating"
        panel = Panel(f"[bold cyan]{mode} {message}[/bold cyan]", 
                     border_style="cyan", padding=(1, 2))
        console.print(panel)
    else:
        print(f"\n{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}\n")


def print_section(section_name: str):
    """Print section divider"""
    if HAS_RICH:
        console.print(f"\n[bold yellow]━━━ {section_name} ━━━[/bold yellow]\n")
    else:
        print(f"\n--- {section_name} ---\n")


def print_info(message: str):
    """Print info message"""
    if HAS_RICH:
        console.print(f"[dim]{message}[/dim]")
    else:
        print(f"  {message}")


def print_success(message: str):
    """Print success message"""
    if HAS_RICH:
        console.print(f"[bold green]✓[/bold green] {message}")
    else:
        print(f"✓ {message}")


def print_error(message: str):
    """Print error message"""
    if HAS_RICH:
        console.print(f"[bold red]✗[/bold red] {message}")
    else:
        print(f"✗ {message}")


def prompt_field(field_name: str, field_def: dict, current_value: Any = None, 
                 field_num: int = 0, total_fields: int = 0) -> str:
    """Prompt user for a field value with validation"""
    prompt_text = field_def['prompt']
    required = field_def.get('required', True)
    field_type = field_def.get('type', 'str')
    example = field_def.get('example', '')
    description = field_def.get('description', '')
    
    # Build prompt
    if field_num > 0:
        prefix = f"[{field_num}/{total_fields}] "
    else:
        prefix = ""
    
    if current_value:
        prompt_text = f"{prefix}{prompt_text} [{current_value}]"
    else:
        prompt_text = f"{prefix}{prompt_text}"
    
    if not required:
        prompt_text += " (optional)"
    
    # Show example and description
    if HAS_RICH:
        if example:
            print_info(f"Example: {example}")
        if description:
            print_info(f"{description}")
    else:
        if example:
            print(f"  Example: {example}")
        if description:
            print(f"  {description}")
    
    while True:
        if HAS_RICH:
            value = Prompt.ask(prompt_text)
        else:
            value = input(f"{prompt_text}: ").strip()
        
        # If empty and has current value, keep current
        if not value and current_value:
            return str(current_value)
        
        # If empty and optional, return empty
        if not value and not required:
            return ''
        
        # If empty and required, ask again
        if not value and required:
            print_error("This field is required")
            continue
        
        # Validate based on type
        if field_type == 'date':
            if validate_date(value):
                return value
            else:
                print_error("Invalid date format. Use MM.DD.YYYY")
        elif field_type == 'ticker':
            if validate_ticker(value):
                return value.upper()
            else:
                print_error("Invalid ticker format. Use uppercase letters with optional :XX")
        elif field_type == 'percentage':
            if validate_percentage(value):
                # Ensure it has % sign
                value = value.strip().rstrip('%') + '%'
                return value
            else:
                print_error("Invalid percentage format")
        elif field_type == 'price':
            if validate_price(value):
                # Remove $ and commas, keep just the number
                return value.strip().lstrip('$').replace(',', '')
            else:
                print_error("Invalid price format")
        elif field_type == 'url':
            if validate_url(value):
                return value
            else:
                print_error("Invalid URL format. Must start with http:// or https://")
        else:
            # Generic string, no validation
            return value


def load_existing_config(config_path: Path) -> Dict[str, Any]:
    """Load existing configuration file"""
    if not config_path.exists():
        return {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        print_error(f"Error loading config: {e}")
        return {}


def display_yaml_preview(config: Dict[str, Any]):
    """Display YAML preview before saving"""
    if HAS_RICH:
        console.print("\n[bold cyan]━━━ YAML Preview ━━━[/bold cyan]\n")
    else:
        print("\n" + "="*60)
        print("  YAML Preview")
        print("="*60 + "\n")
    
    yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    if HAS_RICH:
        console.print(yaml_str)
    else:
        print(yaml_str)


def save_config(config: Dict[str, Any], config_path: Path, backup: bool = True):
    """Save configuration to YAML file"""
    # Create directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Backup existing file
    if backup and config_path.exists():
        backup_path = config_path.with_suffix('.yaml.backup')
        shutil.copy2(config_path, backup_path)
        print_info(f"Backed up existing config to {backup_path.name}")
    
    # Save new config
    with open(config_path, 'w', encoding='utf-8') as f:
        # Write header comment
        if 'update_number' in config:
            f.write("# Updates Report Configuration\n")
            f.write("# This file defines the metadata and pricing data for Updates reports\n\n")
        else:
            f.write("# Ticker Configuration\n")
            f.write("# This file contains ticker-specific metadata for report generation\n\n")
        
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print_success(f"Saved: {config_path}")


# ============================================================================
# Config Creation Functions
# ============================================================================

def create_initiation_config(ticker: str, existing_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create Initiation report configuration interactively"""
    config = {}
    edit_mode = existing_config is not None
    current = existing_config or {}
    
    # Main fields
    print_section("Report Metadata")
    total_main = len(INITIATION_FIELDS)
    for i, (field_name, field_def) in enumerate(INITIATION_FIELDS.items(), 1):
        current_val = current.get(field_name)
        value = prompt_field(field_name, field_def, current_val, i, total_main)
        if value:
            config[field_name] = value
    
    # Use report date for table_date if not provided
    if not config.get('table_date') and config.get('date'):
        config['table_date'] = config['date']
    
    # Company data
    print_section("Company Data")
    company_data = {}
    current_company = current.get('company_data', {})
    for field_name, field_info in COMPANY_FIELDS.items():
        current_val = current_company.get(field_name)
        if HAS_RICH:
            print_info(f"Example: {field_info['example']}")
        value = prompt_field(field_name, {'prompt': field_name, 'required': False}, current_val)
        if value:
            company_data[field_name] = value
    config['company_data'] = company_data
    
    # Trade data
    print_section("Trade Data")
    trade_data = {}
    current_trade = current.get('trade_data', {})
    for field_name, field_info in TRADE_FIELDS.items():
        current_val = current_trade.get(field_name)
        if HAS_RICH:
            print_info(f"Example: {field_info['example']}")
        value = prompt_field(field_name, {'prompt': field_name, 'required': False}, current_val)
        if value:
            trade_data[field_name] = value
    config['trade_data'] = trade_data
    
    # Report saving
    print_section("Report Saving Convention")
    report_saving = {}
    current_saving = current.get('report_saving', {})
    
    # Ticker (default to uppercase ticker symbol without exchange)
    ticker_symbol = config.get('ticker', ticker).split(':')[0].upper()
    current_ticker = current_saving.get('ticker', ticker_symbol)
    print_info("Report filename ticker (usually just the symbol)")
    value = prompt_field('ticker', {'prompt': 'Filename Ticker', 'required': True}, current_ticker)
    report_saving['ticker'] = value
    
    # Issue (format: IssueXX)
    issue_num = config.get('issue_number', '')
    default_issue = f"Issue{issue_num}" if issue_num else current_saving.get('issue', '')
    print_info("Format: IssueXX")
    value = prompt_field('issue', {'prompt': 'Filename Issue', 'required': True}, default_issue)
    report_saving['issue'] = value
    
    # Date (format: MMDDYYYY - no periods)
    report_date = config.get('date', '')
    default_date = report_date.replace('.', '') if report_date else current_saving.get('date', '')
    print_info("Format: MMDDYYYY (no periods)")
    value = prompt_field('date', {'prompt': 'Filename Date', 'required': True}, default_date)
    report_saving['date'] = value
    
    config['report_saving'] = report_saving
    
    return config


def create_updates_config(ticker: str, existing_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create Updates report configuration interactively"""
    config = {}
    edit_mode = existing_config is not None
    current = existing_config or {}
    
    print_section("Update Report Metadata")
    total_fields = len(UPDATES_FIELDS)
    for i, (field_name, field_def) in enumerate(UPDATES_FIELDS.items(), 1):
        current_val = current.get(field_name)
        value = prompt_field(field_name, field_def, current_val, i, total_fields)
        if value:
            config[field_name] = value
    
    return config


# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Interactive configuration creator for ticker reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create new Initiation config
  uv run scripts/create_config.py AAPL --type Initiation
  
  # Create new Updates config
  uv run scripts/create_config.py AAPL --type Updates
  
  # Edit existing config
  uv run scripts/create_config.py AZEK --type Initiation --edit
        """
    )
    
    parser.add_argument('ticker', type=str, 
                       help='Ticker symbol (e.g., AZEK, AAPL)')
    parser.add_argument('--type', '-t', type=str, required=True,
                       choices=['Initiation', 'Updates'],
                       help='Report type: Initiation or Updates')
    parser.add_argument('--edit', '-e', action='store_true',
                       help='Edit existing config instead of creating new')
    
    args = parser.parse_args()
    
    ticker = args.ticker.upper()
    report_type = args.type
    edit_mode = args.edit
    
    # Determine paths
    project_root = Path(__file__).parent.parent
    ticker_dir = project_root / 'Tickers' / ticker / report_type
    
    if report_type == 'Initiation':
        config_file = ticker_dir / f'{ticker}_config.yaml'
    else:
        config_file = ticker_dir / f'{ticker}_updateconfig.yaml'
    
    # Load existing config if editing
    existing_config = None
    if edit_mode:
        if not config_file.exists():
            print_error(f"Config file not found: {config_file}")
            print_info("Remove --edit flag to create a new config")
            sys.exit(1)
        existing_config = load_existing_config(config_file)
    
    # Print header
    mode_str = "Editing" if edit_mode else "Creating"
    print_header(f"{mode_str} {report_type} Config for {ticker}", edit_mode)
    
    if not HAS_RICH:
        print_info("Tip: Install 'rich' for a better experience: uv pip install rich")
        print()
    
    # Create config based on type
    if report_type == 'Initiation':
        config = create_initiation_config(ticker, existing_config)
    else:
        config = create_updates_config(ticker, existing_config)
    
    # Show preview
    display_yaml_preview(config)
    
    # Confirm save
    if HAS_RICH:
        save_confirm = Confirm.ask("\nSave this configuration?", default=True)
    else:
        response = input("\nSave this configuration? (y/n) [y]: ").strip().lower()
        save_confirm = response in ('', 'y', 'yes')
    
    if save_confirm:
        save_config(config, config_file, backup=edit_mode)
        print_success(f"\n{report_type} config for {ticker} saved successfully!")
    else:
        print_info("Configuration not saved")
        sys.exit(0)


if __name__ == '__main__':
    main()

