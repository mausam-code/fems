import urllib.request
import json
import argparse
import os
from datetime import datetime

def setup_argparse():
    parser = argparse.ArgumentParser(description='Fetch and combine JSON data from multiple API endpoints')
    parser.add_argument('--output', type=str, default='combined_data.json', 
                        help='Output JSON file path')
    parser.add_argument('--base-url', type=str, default='https://jsonplaceholder.typicode.com',
                        help='Base URL for the API')
    return parser.parse_args()

def fetch_json_data(url):
    """Fetch JSON data from the specified URL using urllib"""
    try:
        print(f"Fetching data from: {url}")
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"Error fetching data from {url}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error: The response from {url} is not valid JSON")
        return None

def fetch_user_posts(base_url, user_id):
    """Fetch posts for a specific user"""
    url = f"{base_url}/posts?userId={user_id}"
    return fetch_json_data(url)

def fetch_post_comments(base_url, post_id):
    """Fetch comments for a specific post"""
    url = f"{base_url}/comments?postId={post_id}"
    return fetch_json_data(url)

def save_json(data, output_path):
    """Save the combined data as JSON"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved to {output_path}")

def main():
    args = setup_argparse()
    base_url = args.base_url
    
    # Fetch all users
    users = fetch_json_data(f"{base_url}/users")
    if not users:
        print("Failed to fetch users data. Exiting.")
        return
    
    # Create result structure with metadata
    result = {
        "metadata": {
            "source_url": base_url,
            "scrape_date": datetime.now().isoformat(),
            "endpoints": ["users", "posts", "comments"]
        },
        "data": []
    }
    
    # For each user, fetch their posts
    for user in users:
        user_data = {
            "user": user,
            "posts": []
        }
        
        # Fetch posts for this user
        posts = fetch_user_posts(base_url, user["id"])
        if posts:
            for post in posts:
                post_data = {
                    "post": post,
                    "comments": []
                }
                
                # Fetch comments for this post
                comments = fetch_post_comments(base_url, post["id"])
                if comments:
                    post_data["comments"] = comments
                
                user_data["posts"].append(post_data)
        
        result["data"].append(user_data)
    
    # Save the combined data
    save_json(result, args.output)
    print(f"Successfully combined data for {len(result['data'])} users")

if __name__ == "__main__":
    main()