import requests
from bs4 import BeautifulSoup
import argparse
import os

def get_latest_image_pdf(url):
  """
  Fetches the latest image or PDF file from the given webpage.

  Args:
    url (str): The URL of the webpage to search.

  Returns:
    str: The URL of the latest image or PDF file, or None if none found.
  """
  try:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all image and PDF links
    media_links = soup.find_all('img', src=True) + soup.find_all('a', href=True)

    # Filter for image and PDF links
    media_links = [link['src'] for link in media_links if link['src'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf'))]

    # If no media links are found, return None
    if not media_links:
      return None

    # Sort links by their 'href' or 'src' attribute in reverse order
    media_links = sorted(media_links, reverse=True)

    # Return the most recent link (the one with the highest 'href' or 'src' value)
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
