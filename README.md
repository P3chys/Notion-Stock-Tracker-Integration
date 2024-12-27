# Portfolio Tracker

A Python-based portfolio tracking system that aggregates investment positions from multiple sources and saves them to Notion.

## Features

- Fetches portfolio data from Trading212 API
- Scrapes DeFi positions from DeBank
- Stores portfolio data in Notion database
- Supports multiple data sources through a modular architecture

## Prerequisites

- Python 3.8+
- Chrome browser (for DeBank scraping)
- Notion account with API access
- Trading212 account with API access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/portfolio-tracker.git
cd portfolio-tracker
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the config directory with your credentials:
```
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id
TRADING212_API_TOKEN=your_trading212_token
TRADING212_API_URL=https://live.trading212.com/api/v0/equity/portfolio
```

## Usage

Run the portfolio tracker:
```bash
python main.py
```

## Project Structure

```
portfolio-tracker/
├── config/
│   ├── __init__.py
│   ├── .env
│   └── settings.py
├── interfaces/
│   ├── __init__.py
│   ├── data_sink.py
│   └── data_source.py
├── models/
│   ├── __init__.py
│   └── position.py
├── services/
│   ├── __init__.py
│   └── web_driver_service.py
├── sinks/
│   ├── __init__.py
│   └── notion_sink.py
├── sources/
│   ├── __init__.py
│   ├── debank_source.py
│   └── trading212_source.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
