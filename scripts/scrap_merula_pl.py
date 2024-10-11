import requests
from bs4 import BeautifulSoup
import re
import json
import sys

def extract_tablepress_content(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve URL: {url}")
        return None

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find table with an ID that matches 'tablepress-<random_number>'
    table = soup.find('table', id=re.compile(r'tablepress-\d+'))

    if not table:
        print("Table not found.")
        return None

    extracted_data = []
    
    # Loop through rows (ignoring the header row)
    for row in table.find_all('tr')[1:]:
        columns = row.find_all('td')
        if len(columns) == 2:
            polish = columns[0].get_text(strip=True)
            english = columns[1].get_text(strip=True)
            extracted_data.append({"pl": polish, "en": english})

    return extracted_data

def save_to_json(data, filename='input.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved {len(data)} records to {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    table_data = extract_tablepress_content(url)

    if table_data:
        save_to_json(table_data)
        print(f"Data saved to input.json")
    else:
        print("No data extracted.")

