import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from datetime import datetime
import re

def get_latest_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the table that contains the files
        table = soup.find('table')
        if not table:
            print(f"No table found in {url}")
            return None
            
        latest_file = None
        latest_date = None
        
        # Look through table rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:  # Ensure row has enough columns
                link_element = cols[0].find('a') or cols[0].find('img')
                if link_element:
                    file_url = link_element.get('href') or link_element.get('src')
                    if file_url and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                        # Get the date from the modified column
                        date_str = cols[2].get_text().strip()
                        try:
                            # Parse the date (adjust format as needed)
                            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            if not latest_date or date > latest_date:
                                latest_date = date
                                latest_file = file_url
                        except ValueError as e:
                            print(f"Could not parse date: {date_str}")
                            continue
        
        if latest_file:
            return urljoin(url, latest_file)
        return None
        
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def download_latest_file(url, save_folder, file_prefix):
    try:
        latest_file_url = get_latest_file(url)
        if not latest_file_url:
            print(f"No suitable files found at {url}")
            return None
            
        # Download the file
        file_response = requests.get(latest_file_url)
        file_response.raise_for_status()
        
        # Create filename with prefix and original extension
        extension = os.path.splitext(latest_file_url.split('/')[-1])[1]
        filename = f"{file_prefix}{extension}"
        
        # Save the file
        filepath = os.path.join(save_folder, filename)
        with open(filepath, 'wb') as f:
            f.write(file_response.content)
        
        print(f"Successfully downloaded: {filepath}")
        return filepath

    except Exception as e:
        print(f"Error downloading from {url}: {str(e)}")
        return None

def main():
    # Get the script's directory (codes folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the URLs and their corresponding file prefixes
    urls = {
        "https://pubfiles.pagasa.dost.gov.ph/tamss/weather/bulletin/": "latest_tcb",
        "https://pubfiles.pagasa.dost.gov.ph/tamss/weather/weather_advisory/": "latest_wa",
        "https://pubfiles.pagasa.dost.gov.ph/climps/tcthreat/": "latest_tcthreat"
    }
    
    # Download from each URL
    for url, prefix in urls.items():
        downloaded_file = download_latest_file(url, script_dir, prefix)
        if downloaded_file:
            print(f"Successfully processed {prefix} from {url}")
        else:
            print(f"Failed to process {prefix} from {url}")

if __name__ == "__main__":
    main()
