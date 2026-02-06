# Market Knowledge Repository

Market-related knowledge and analysis stored in this directory.

## Structure

```
market/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── install_requirements.sh        # Installation script
├── test_connection.py             # Network test script
├── economic_calendar.py           # Investing.com scraper (requires packages)
├── economic_calendar_simple.py    # TradingView version (stdlib only)
├── economic_calendar_stdlib.py    # FRED API version (stdlib only, API key required)
├── daily/                         # Daily market news and updates
├── analysis/                      # Market analysis and research
└── archive/                       # Archived market data
```

## Quick Start

### 1. Test Network Connection

First, verify network connectivity:

```bash
cd /data/data/com.termux/files/home/knowledge/market
python3 test_connection.py
```

### 2. Install Dependencies (for full-featured scraper)

```bash
# Install required Python packages
pip3 install requests beautifulsoup4 lxml pandas python-dateutil pytz

# Or use the provided script
./install_requirements.sh
```

### 3. Run Economic Calendar Scraper

Choose one of the following:

#### Option A: Full-featured (Investing.com scraper)
```bash
python3 economic_calendar.py
```

#### Option B: Simple (TradingView, stdlib only)
```bash
python3 economic_calendar_simple.py
```

#### Option C: FRED API (requires free API key)
```bash
# Get API key from: https://fred.stlouisfed.org/docs/api/api_key.html
python3 economic_calendar_stdlib.py YOUR_API_KEY
```

## Output

Data will be saved to `market/daily/` in JSON format:
- `yesterday_YYYYMMDD_HHMMSS.json` - Yesterday's actuals vs forecasts
- `today_YYYYMMDD_HHMMSS.json` - Today's upcoming indicators

## Economic Indicators Collected

- **Yesterday**: Actual results, forecasts, and variance
- **Today**: Forecasts and previous values
- **Categories**: GDP, unemployment, CPI, interest rates, etc.

## API Keys

### FRED API (Free)
1. Register at https://fred.stlouisfed.org/
2. Get API key from your account
3. Use with `economic_calendar_stdlib.py`

## Troubleshooting

### Connection Issues
- Run `python3 test_connection.py` to verify connectivity
- Some sites may block scraping (try different options)

### Python Packages
- Ensure Python 3.12+ is installed
- Check pip3 is available: `pip3 --version`
- Install packages manually if script fails

## License

For personal use only. Respect website terms of service when scraping.
