import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from datetime import datetime

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d-%b-%Y %H:%M")
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        return None

def get_latest_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get all links and their dates
        files_with_dates = []
        
        # Process all link elements
        for link in soup.find_all('a'):
            href = link.get('href')
            # Skip parent directory link
            if href == "../":
                continue
                
            # Get the file and date from the text that follows the link
            if href and (href.endswith('.pdf') or href.endswith('.png')):
                # Get the text line containing this link
                line_text = link.parent.get_text()
                parts = line_text.split()
                if len(parts) >= 2:
                    # Date and time are typically the last parts before the file size
                    date_str = f"{parts[-3]} {parts[-2]}"
                    date = parse_date(date_str)
                    if date:
                        files_with_dates.append((href, date))
                        print(f"Found file: {href} with date: {date}")

        if not files_with_dates:
            print("No files with valid dates found")
            return None

        # Get the most recent file
        latest_file = max(files_with_dates, key=lambda x: x[1])[0]
        print(f"Selected latest file: {latest_file}")
        return latest_file

    except Exception as e:
        print(f"Error in get_latest_file: {str(e)}")
        return None

def download_latest_file(url, save_folder, file_prefix):
    try:
        latest_file = get_latest_file(url)
        if not latest_file:
            print(f"No suitable files found at {url}")
            return None
            
        full_url = urljoin(url, latest_file)
        print(f"Downloading from: {full_url}")
        
        response = requests.get(full_url)
        response.raise_for_status()
        
        # Get the extension from the original file
        extension = os.path.splitext(latest_file)[1]
        filename = f"{file_prefix}{extension}"
        filepath = os.path.join(save_folder, filename)
        
        # Save the file
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"Successfully saved to: {filepath}")
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
        downloaded_file = download_latest_file(url, script_dir, prefix)
        if downloaded_file:
            print(f"Successfully processed {prefix}")
        else:
            print(f"Failed to process {prefix}")

if __name__ == "__main__":
    main()
