import requests
from bs4 import BeautifulSoup
import json
import os

# Define the URL pattern for the HTML pages
url_pattern = "https://korrykatti.github.io/thapps/apps/{:05d}.html"

# Function to fetch application data from HTML pages
def fetch_application_data(num):
    url = url_pattern.format(num)
    response = requests.get(url)
    print(f"Fetching data from {url}. Status code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        app_name = soup.find('h1', {'id': 'appName'})
        icon_url = soup.find('h2', {'id': 'iconUrl'})
        version = soup.find('h2', {'id': 'version'})
        repo_url = soup.find('h2', {'id': 'repoUrl'})
        main_file = soup.find('h2', {'id': 'mainFile'})
        if all((app_name, icon_url, version, repo_url, main_file)):
            return {
                'app_name': app_name.text.strip(),
                'icon_url': icon_url.text.strip(),
                'version': version.text.strip(),
                'repo_url': repo_url.text.strip(),
                'main_file': main_file.text.strip()
            }
    return None

# Fetch application data for all HTML pages
def fetch_all_application_data():
    app_data = {}
    num = 1
    while True:
        data = fetch_application_data(num)
        if data is None:
            break
        app_data[num] = data
        num += 1
    return app_data

# Main function
def main():
    # Fetch application data from HTML pages
    application_data = fetch_all_application_data()

    # Print the fetched data
    for num, data in application_data.items():
        print(f"Application {num}:")
        print(f"Name: {data['app_name']}")
        print(f"Icon URL: {data['icon_url']}")
        print(f"Version: {data['version']}")
        print(f"Repo URL: {data['repo_url']}")
        print(f"Main File: {data['main_file']}")
        print()

    # Save application data to a file
    file_path = os.path.join(os.path.dirname(__file__), 'app_data.json')
    if application_data:
        with open(file_path, 'w') as f:
            json.dump(application_data, f, indent=4)
        print("Application data saved to app_data.json")
    else:
        print("No application data fetched. No JSON file created.")

if __name__ == "__main__":
    main()
