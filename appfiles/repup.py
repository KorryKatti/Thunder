import requests
from bs4 import BeautifulSoup
import json
import time
import os

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        app_name = soup.find('h1', {'id': 'appName'}).text.strip()
        icon_url = soup.find('h2', {'id': 'iconUrl'}).text.strip()
        version = soup.find('h2', {'id': 'version'}).text.strip()
        repo_url = soup.find('h2', {'id': 'repoUrl'}).text.strip()
        main_file = soup.find('h2', {'id': 'mainFile'}).text.strip()

        application_data = {
            'app_name': app_name,
            'icon_url': icon_url,
            'version': version,
            'repo_url': repo_url,
            'main_file': main_file
        }
        return application_data
    else:
        print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
        return None

def check_for_updates():
    url_base = 'https://korrykatti.github.io/thapps/apps/'
    data_folder = 'data'

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    for i in range(1, 100):  # Assuming maximum of 99 files
        url = f"{url_base}{i:05d}.html"  # Pad number with leading zeros
        data = fetch_data(url)
        if data:
            with open(f"{data_folder}/{i:05d}.json", 'w') as f:
                json.dump(data, f, indent=4)
        else:
            break

def main():
    while True:
        check_for_updates()
        time.sleep(60)  # Check for updates every one minute

if __name__ == "__main__":
    main()
