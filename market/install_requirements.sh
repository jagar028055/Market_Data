#!/bin/bash
# Install required Python packages for market data collection

# Set up custom temp directory
export TMPDIR="$HOME/.cache/python-tmp"
mkdir -p "$TMPDIR"
export TEMP="$TMPDIR"
export TMP="$TMPDIR"

# Install packages using pip
/data/data/com.termux/files/usr/bin/python3 -m pip install --cache-dir="$HOME/.cache/pip" --no-warn-script-location \
    requests \
    beautifulsoup4 \
    lxml \
    pandas \
    python-dateutil \
    pytz 2>&1

echo "Installation complete!"
echo "Run the data collection script with: ./market/economic_calendar.py"
