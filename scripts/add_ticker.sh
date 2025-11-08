#!/bin/bash
#
# Add New Ticker Script
# Creates directory structure for a new ticker with Initiation and Updates folders
#
# Usage:
#   ./scripts/add_ticker.sh TICKER
#
# Example:
#   ./scripts/add_ticker.sh AAPL

set -e  # Exit on error

# Check if ticker argument is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: No ticker symbol provided"
    echo ""
    echo "Usage: $0 TICKER"
    echo ""
    echo "Example:"
    echo "  $0 AAPL"
    exit 1
fi

# Get ticker and convert to uppercase
TICKER=$(echo "$1" | tr '[:lower:]' '[:upper:]')

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Define paths
TICKER_DIR="$PROJECT_ROOT/Tickers/$TICKER"
INITIATION_DIR="$TICKER_DIR/Initiation"
UPDATES_DIR="$TICKER_DIR/Updates"

echo ""
echo "============================================================"
echo "📊 Adding New Ticker: $TICKER"
echo "============================================================"
echo ""

# Check if ticker already exists
if [ -d "$TICKER_DIR" ]; then
    echo "⚠️  Warning: Ticker directory already exists: $TICKER_DIR"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Cancelled"
        exit 0
    fi
    echo ""
fi

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p "$INITIATION_DIR/images"
mkdir -p "$UPDATES_DIR/images"

echo "✅ Created: $INITIATION_DIR/"
echo "✅ Created: $INITIATION_DIR/images/"
echo "✅ Created: $UPDATES_DIR/"
echo "✅ Created: $UPDATES_DIR/images/"
echo ""

# Create template config files
echo "📝 Creating template configuration files..."

# Initiation config template
cat > "$INITIATION_DIR/${TICKER}_config.yaml" << EOF
# ${TICKER} Initiation Report Configuration

# Report metadata
issue_number: '00'
date: 'MM.DD.YYYY'
table_date: 'MM.DD.YYYY'
theme: 'THEME HERE'
ticker: '${TICKER}:US'
timeframe: '6-9 MONTHS'
current_target: '\$00.00 | \$00.00'
downside: '0.0%'

# Report saving format (filename generation)
report_saving:
  ticker: '${TICKER}'
  issue: 'Issue00'
  date: 'MMDDYYYY'  # No periods in date for filename

# Company data
company_data:
  SECTOR: 'Sector Name'
  LOCATION: 'Country'
  MARKET CAP: '\$0.0B'
  EV/EBITDA: '0.00'
  TRAILING P/E: '0.00'
  PROFIT MARGIN: '0.0%'
  TOTAL CASH/DEBT: '\$0M / \$0M'
  52 WEEK RANGE: '\$0.00 - \$0.00'

# Trading data
trade_data:
  DAILY VOLUME: '\$0M'
  DAYS TO COVER: '0.00'
  SHARES SHORT: '0.0%'
  BORROW COST: '0.0%'
EOF

echo "✅ Created: ${TICKER}_config.yaml (Initiation)"

# Updates config template
cat > "$UPDATES_DIR/${TICKER}_updateconfig.yaml" << EOF
# ${TICKER} Updates Report Configuration

# Report identification
issue_number: "00"
update_number: "1"
date: "MM.DD.YYYY"  # Periods will be removed in filename

# Report title and ticker
title: "Update Title Here"
ticker: "${TICKER}"
stock: "Company Name Inc. (${TICKER})"

# Reference to initiation report
initiation_publish_date: "MM.DD.YYYY"
initiation_report_link: "https://bindlepaper.com/reports/${TICKER}.Issue00.MMDDYYYY.pdf"

# Pricing data
price_at_publication: "0.00"
recent_price: "0.00"
target_price: "0.00"
EOF

echo "✅ Created: ${TICKER}_updateconfig.yaml (Updates)"
echo ""

# Summary
echo "============================================================"
echo "🎉 Ticker Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Initiation Report:"
echo "   • Place DOCX file: $INITIATION_DIR/${TICKER}.docx"
echo "   • Edit config: $INITIATION_DIR/${TICKER}_config.yaml"
echo "   • Add chart: $INITIATION_DIR/${TICKER}_chart.png"
echo "   • Run: uv run src/process_ticker.py $TICKER"
echo ""
echo "2. Updates Report:"
echo "   • Place DOCX file: $UPDATES_DIR/${TICKER}.docx"
echo "   • Edit config: $UPDATES_DIR/${TICKER}_updateconfig.yaml"
echo "   • Run: uv run src/process_ticker.py $TICKER --report-type Updates"
echo ""


