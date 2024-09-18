import requests
from bs4 import BeautifulSoup
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("download_log.txt"),
                        logging.StreamHandler()
                    ])

def download_file(url, local_filename):
    if os.path.exists(local_filename):
        logging.info(f"File already exists: {local_filename}")
        return

    logging.info(f"Downloading {url} to {local_filename}")
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded {url} to {local_filename}")
    except requests.HTTPError as e:
        logging.error(f"Failed to download {url}: {e}")
    except requests.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")

def main():
    base_url = "https://razgovor.edsoo.ru/video/"
    start_number = 270  # You can change this to start from a different number
    end_number = 10000    # You can change this to end at a different number

    os.makedirs('downloads', exist_ok=True)

    for n in range(start_number, end_number + 1):
        url = f"{base_url}{n}"
        logging.info(f"Checking URL: {url}")

        retries = 5
        while retries > 0:
            try:
                response = requests.get(url)
                response.raise_for_status()
                break
            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    logging.warning(f"Rate limited: {url}. Retrying in 30 seconds...")
                    time.sleep(30)
                    retries -= 1
                else:
                    logging.error(f"Failed to retrieve {url}: {e}")
                    break
            except requests.RequestException as e:
                logging.error(f"Failed to retrieve {url}: {e}")
                break

        if retries == 0:
            logging.error(f"Failed to retrieve {url} after multiple attempts")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        media_link = soup.find('source', {'src': True})

        if media_link:
            media_url = media_link['src']
            if '/ie/' not in media_url:
                logging.info(f"Found media URL: {media_url}")
                local_filename = os.path.join('downloads', os.path.basename(media_url))
                download_file(media_url, local_filename)
            else:
                logging.info(f"Skipping URL: {media_url}")
        else:
            logging.info(f"No media link found on {url}")

if __name__ == "__main__":
    main()
