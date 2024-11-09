# get_latest_image_pdf.py (in root/codes directory)
import requests
from bs4 import BeautifulSoup
import argparse
import os

def get_latest_image_pdf(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all image and PDF links
        media_links = []
        
        # Handle img tags with src
        for img in soup.find_all('img', src=True):
            if img['src'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                media_links.append(img['src'])
        
        # Handle a tags with href
        for link in soup.find_all('a', href=True):
            if link['href'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf')):
                media_links.append(link['href'])
        
        # If no media links are found, return None
        if not media_links:
            return None
            
        # Sort links in reverse order
        media_links = sorted(media_links, reverse=True)
        return media_links[0]
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get the latest image/PDF URL from a webpage.')
  parser.add_argument('-u', '--url', required=True, help='The URL of the webpage')
  parser.add_argument('-o', '--output', default='latest_media.txt', help='The output file to store the latest URL')
  args = parser.parse_args()

  latest_media_url = get_latest_image_pdf(args.url)
  if latest_media_url:
    with open(args.output, 'w') as f:
      f.write(latest_media_url)
    print(f"Latest image/PDF URL written to '{args.output}'")
  else:
    print("No image or PDF files found on the webpage.")
