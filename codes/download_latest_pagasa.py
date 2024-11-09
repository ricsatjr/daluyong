import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin

def download_latest_file(url, save_folder, file_prefix):
    try:
        # Get the webpage content
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links that might be images or PDFs
        media_links = []
        
        # Check img tags with src
        for img in soup.find_all('img', src=True):
            if img['src'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                media_links.append(img['src'])
        
        # Check a tags with href
        for link in soup.find_all('a', href=True):
            if link['href'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                media_links.append(link['href'])

        if not media_links:
            print(f"No media files found for {url}")
            return None

        # Get the latest file (assuming filenames have date/time info)
        latest_file_url = urljoin(url, sorted(media_links)[-1])
        
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
