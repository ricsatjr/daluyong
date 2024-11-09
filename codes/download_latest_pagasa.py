import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from datetime import datetime

def get_latest_file(url):
    try:
        print(f"Fetching from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links and their dates
        files_with_dates = []
        
        # Debug: Print all found links
        links = soup.find_all(['a', 'img'])
        print(f"Found {len(links)} total links")
        
        for link in links:
            file_url = link.get('href') or link.get('src')
            if file_url and file_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                # Find parent row to get date
                row = link.find_parent('tr')
                if row:
                    date_cell = row.find_all('td')[-1]  # Assuming last column is date
                    if date_cell:
                        date_str = date_cell.get_text().strip()
                        print(f"Found file: {file_url} with date: {date_str}")
                        files_with_dates.append((file_url, date_str))

        if not files_with_dates:
            print("No files found with dates")
            return None

        # Sort by date and get the latest
        latest_file = sorted(files_with_dates, key=lambda x: x[1])[-1][0]
        print(f"Latest file selected: {latest_file}")
        return urljoin(url, latest_file)

    except Exception as e:
        print(f"Error in get_latest_file: {str(e)}")
        return None

def download_latest_file(url, save_folder, file_prefix):
    try:
        latest_file_url = get_latest_file(url)
        if not latest_file_url:
            print(f"No suitable files found at {url}")
            return None
            
        print(f"Downloading from: {latest_file_url}")
        file_response = requests.get(latest_file_url)
        file_response.raise_for_status()
        
        # Create filename with prefix and original extension
        extension = os.path.splitext(latest_file_url.split('/')[-1])[1]
        filename = f"{file_prefix}{extension}"
        filepath = os.path.join(save_folder, filename)
        
        print(f"Saving to: {filepath}")
        with open(filepath, 'wb') as f:
            f.write(file_response.content)
        
        # Verify file was created
        if os.path.exists(filepath):
            print(f"File successfully saved: {filepath} (Size: {os.path.getsize(filepath)} bytes)")
        else:
            print(f"Error: File not found after saving: {filepath}")
            
        return filepath

    except Exception as e:
        print(f"Error downloading from {url}: {str(e)}")
        return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Script directory: {script_dir}")
    
    urls = {
        "https://pubfiles.pagasa.dost.gov.ph/tamss/weather/bulletin/": "latest_tcb",
        "https://pubfiles.pagasa.dost.gov.ph/tamss/weather/weather_advisory/": "latest_wa",
        "https://pubfiles.pagasa.dost.gov.ph/climps/tcthreat/": "latest_tcthreat"
    }
    
    for url, prefix in urls.items():
        print(f"\nProcessing URL: {url}")
        print(f"Using prefix: {prefix}")
        downloaded_file = download_latest_file(url, script_dir, prefix)
        if downloaded_file:
            print(f"Successfully processed {prefix}")
        else:
            print(f"Failed to process {prefix}")

if __name__ == "__main__":
    main()
