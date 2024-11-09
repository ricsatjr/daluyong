import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, unquote
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
        
        # Get raw text and remove <pre> tags
        raw_text = response.text.replace('<pre>', '').replace('</pre>', '')
        
        # Split into lines
        lines = [line for line in raw_text.split('\n') if line.strip()]
        
        files_with_dates = []
        for line in lines:
            # Skip parent directory link
            if '../' in line:
                continue
                
            # Check if line contains a file link
            if '<a href="' in line and ('pdf' in line.lower() or 'png' in line.lower()):
                # Extract the href and split the remaining content
                href_end = line.find('</a>')
                if href_end != -1:
                    # Get the remainder of the line after the </a> tag
                    remainder = line[href_end + 4:].strip()
                    # Split by multiple spaces to get date and size
                    parts = [p for p in remainder.split('    ') if p.strip()]
                    if parts:
                        date_str = parts[0].strip()
                        if date_str:
                            date = parse_date(date_str)
                            if date:
                                # Extract filename from href
                                href_start = line.find('href="') + 6
                                filename = line[href_start:line.find('"', href_start)]
                                files_with_dates.append((filename, date))
                                print(f"Found file: {filename} with date: {date}")

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
        extension = os.path.splitext(unquote(latest_file))[1]
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
