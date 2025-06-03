import requests
import json
import argparse
import os
from datetime import datetime

def setup_argparse():
    parser = argparse.ArgumentParser(description='Fetch JSON data from an API and save it to a file')
    parser.add_argument('--url', type=str, required=True, help='URL of the API endpoint')
    parser.add_argument('--output', type=str, default='scraped_data.json', help='Output JSON file path')
    return parser.parse_args()

def fetch_json_data(url):
    """Fetch JSON data from the specified URL"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: The response is not valid JSON")
        return None

def save_json(data, output_path):
    """Save the scraped data as JSON"""
    # Create metadata to include with the data
    result = {
        "metadata": {
            "source_url": args.url,
            "scrape_date": datetime.now().isoformat(),
        },
        "data": data
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {output_path}")

def main():
    global args
    args = setup_argparse()
    
    print(f"Fetching JSON data from URL: {args.url}")
    data = fetch_json_data(args.url)
    
    if data:
        save_json(data, args.output)
        print(f"Successfully scraped {len(data) if isinstance(data, list) else 1} records")
    else:
        print("Failed to fetch data")

if __name__ == "__main__":
    main()