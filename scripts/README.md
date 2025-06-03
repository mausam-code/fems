# JSON Data Scraping Scripts

This directory contains scripts for fetching and processing JSON data from web APIs. These scripts demonstrate different approaches to web scraping and data processing.

## Available Scripts

### 1. web_scraper.py

A basic template for web scraping using Puppeteer. This script is designed to be used with the Puppeteer MCP server to navigate to websites and extract data.

**Usage:**
```bash
python web_scraper.py --url "https://example.com" --output "scraped_data.json" --selector "body" --wait 2
```

**Parameters:**
- `--url`: URL of the website to scrape (required)
- `--output`: Output JSON file path (default: scraped_data.json)
- `--selector`: CSS selector to target specific content (default: body)
- `--wait`: Wait time in seconds after page load (default: 2)

### 2. json_scraper.py

A script that uses the requests library to fetch JSON data from APIs and save it to a file.

**Usage:**
```bash
python json_scraper.py --url "https://jsonplaceholder.typicode.com/users" --output "users_data.json"
```

**Parameters:**
- `--url`: URL of the API endpoint (required)
- `--output`: Output JSON file path (default: scraped_data.json)

### 3. json_fetcher.py

A more robust script that uses Python's built-in urllib module to fetch JSON data from APIs.

**Usage:**
```bash
python json_fetcher.py --url "https://jsonplaceholder.typicode.com/posts" --output "posts_data.json"
```

**Parameters:**
- `--url`: URL of the API endpoint (required)
- `--output`: Output JSON file path (default: scraped_data.json)

### 4. combined_data_fetcher.py

A comprehensive script that fetches data from multiple endpoints and combines them into a single JSON file. This script specifically works with the JSONPlaceholder API to fetch users, their posts, and comments on those posts.

**Usage:**
```bash
python combined_data_fetcher.py --output "combined_data.json" --base-url "https://jsonplaceholder.typicode.com"
```

**Parameters:**
- `--output`: Output JSON file path (default: combined_data.json)
- `--base-url`: Base URL for the API (default: https://jsonplaceholder.typicode.com)

## Generated JSON Files

- **users_data.json**: Contains user information from the JSONPlaceholder API
- **posts_data.json**: Contains post information from the JSONPlaceholder API
- **comments_data.json**: Contains comment information from the JSONPlaceholder API
- **combined_data.json**: Contains a comprehensive dataset with users, their posts, and comments on those posts

## Data Structure

All generated JSON files include metadata about the source URL and scrape date, along with the actual data:

```json
{
  "metadata": {
    "source_url": "https://jsonplaceholder.typicode.com/users",
    "scrape_date": "2025-06-02T02:51:53.238058"
  },
  "data": [
    // The actual data from the API
  ]
}
```

The combined data file has a more complex structure that nests posts under users and comments under posts.

## Requirements

- Python 3.6+
- requests library (for json_scraper.py)
- Standard library modules: urllib, json, argparse, os, datetime

## Installation

Install the required packages:

```bash
pip install requests
```

## Examples

### Fetch user data
```bash
python json_fetcher.py --url "https://jsonplaceholder.typicode.com/users" --output "users_data.json"
```

### Fetch and combine data from multiple endpoints
```bash
python combined_data_fetcher.py --output "combined_data.json"
```