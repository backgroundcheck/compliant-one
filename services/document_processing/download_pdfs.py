import argparse
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import os
import requests
from bs4 import BeautifulSoup
import sys
from typing import List, Tuple
import logging
import datetime
import re
import urllib3

# Disable only the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pdf_download.log')
        ]
    )
    return logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """Validate if the given string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def normalize_url(url: str) -> str:
    """Normalize the URL by adding scheme if missing."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def get_pdf_links(url: str, headers: dict) -> List[str]:
    """Extract PDF links from the webpage."""
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Find all links ending in .pdf
        pdf_links = []
        for a in soup.find_all('a', href=True):
            href = a['href'].lower()
            if href.endswith('.pdf'):
                # Convert relative URLs to absolute
                abs_url = urljoin(url, a['href'])
                pdf_links.append(abs_url)
        
        return list(set(pdf_links))  # Remove duplicates
    except Exception as e:
        logging.error(f"Failed to fetch or parse the page: {str(e)}")
        return []

def download_pdfs(pdf_links: List[str], output_dir: str, headers: dict) -> Tuple[int, int]:
    """Download PDFs from the given links."""
    os.makedirs(output_dir, exist_ok=True)
    success_count = fail_count = 0

    for pdf_url in tqdm(pdf_links, desc="Downloading PDFs"):
        filename = os.path.join(output_dir, pdf_url.split("/")[-1])
        
        # Skip if file exists
        if os.path.exists(filename):
            logging.info(f"Skipping (already exists): {filename}")
            continue
            
        logging.info(f"Downloading {pdf_url} -> {filename}")
        try:
            pdf_resp = requests.get(pdf_url, headers=headers, verify=False, timeout=30)
            pdf_resp.raise_for_status()
            
            # Verify it's actually a PDF
            content_type = pdf_resp.headers.get('content-type', '').lower()
            if 'application/pdf' not in content_type:
                logging.warning(f"Skipping non-PDF content: {pdf_url} (Content-Type: {content_type})")
                fail_count += 1
                continue
                
            with open(filename, "wb") as f:
                f.write(pdf_resp.content)
            success_count += 1
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to download {pdf_url}: {str(e)}")
            fail_count += 1
            
    return success_count, fail_count

SUPPORTED_EXTS = [
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".csv", ".xml", ".html", ".htm", ".db", ".zip", ".json",
    ".jpg", ".jpeg", ".gif", ".bmp", ".png", ".mp4", ".webp",
    ".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a"
]

def get_file_links(url: str, headers: dict) -> List[Tuple[str, str]]:
    """Extract all supported file links from the webpage, including from buttons."""
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        file_links = []

        # Find <a> tags
        for a in soup.find_all('a', href=True):
            href = a['href']
            ext = os.path.splitext(href.lower())[1]
            print(f"DEBUG: Found link {href} with ext {ext}")  # Add this line for debugging
            if ext in SUPPORTED_EXTS:
                abs_url = urljoin(url, href)
                file_links.append((abs_url, ext))

        # Find <button> tags with file links
        for btn in soup.find_all('button'):
            for attr in ['data-href', 'onclick', 'value']:
                link = btn.get(attr)
                if link:
                    # General regex: match any supported extension in the attribute value
                    for ext in SUPPORTED_EXTS:
                        ext_pattern = re.escape(ext)
                        match = re.search(rf"(https?://[^\s'\";]+{ext_pattern}|/[^\s'\";]+{ext_pattern})", link, re.IGNORECASE)
                        if match:
                            found_link = match.group(0)
                            abs_url = urljoin(url, found_link)
                            file_links.append((abs_url, ext))
        return list(set(file_links))
    except Exception as e:
        logging.error(f"Failed to fetch or parse the page for files: {str(e)}")
        return []

def download_files(file_links: List[Tuple[str, str]], output_dir: str, headers: dict):
    """Download all supported files into date-based folders, checking duplicates by size."""
    today = datetime.date.today().isoformat()
    date_dir = os.path.join(output_dir, today)
    os.makedirs(date_dir, exist_ok=True)
    success_count = fail_count = 0

    for file_url, ext in tqdm(file_links, desc="Downloading files"):
        base_filename = file_url.split("/")[-1]
        filename = os.path.join(date_dir, base_filename)
        # Check for duplicate by name and size
        if os.path.exists(filename):
            try:
                resp = requests.head(file_url, headers=headers, verify=False, timeout=30)
                remote_size = int(resp.headers.get('content-length', -1))
                local_size = os.path.getsize(filename)
                if remote_size == local_size and remote_size > 0:
                    logging.info(f"Skipping (already exists, same size): {filename}")
                    continue
                else:
                    # If size differs, append a counter to filename
                    counter = 1
                    new_filename = os.path.join(date_dir, f"{counter}_{base_filename}")
                    while os.path.exists(new_filename):
                        counter += 1
                        new_filename = os.path.join(date_dir, f"{counter}_{base_filename}")
                    filename = new_filename
            except Exception as e:
                logging.warning(f"Could not compare file sizes for {filename}: {str(e)}")
        try:
            resp = requests.get(file_url, headers=headers, verify=False, timeout=30)
            resp.raise_for_status()
            with open(filename, "wb") as f:
                f.write(resp.content)
            success_count += 1
            logging.info(f"Downloaded {file_url} -> {filename}")
        except Exception as e:
            logging.error(f"Failed to download {file_url}: {str(e)}")
            fail_count += 1
    logging.info(f"Files saved to: {os.path.abspath(date_dir)}")
    logging.info(f"Successfully downloaded: {success_count}")
    logging.info(f"Failed to download: {fail_count}")

def main():
    parser = argparse.ArgumentParser(description='Download PDFs from a webpage')
    parser.add_argument('--url', help='URL to scrape PDFs from')
    parser.add_argument('--output-dir', default='downloaded_pdfs',
                    help='Directory to save PDFs (default: downloaded_pdfs)')
    args = parser.parse_args()

    logger = setup_logging()
    
    # If URL not provided via command line, prompt for it
    url = args.url
    while not url or not is_valid_url(url):
        url = input("Enter the webpage URL to scrape PDFs from: ").strip()
        if not url:
            logger.error("URL cannot be empty")
            continue
        url = normalize_url(url)
        if not is_valid_url(url):
            logger.error("Invalid URL format. Please enter a valid URL")
            continue

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    # Get PDF links
    logger.info(f"Scanning {url} for PDF links...")
    pdf_links = get_pdf_links(url, headers)
    
    if pdf_links:
        logger.info(f"Found {len(pdf_links)} PDF links")
        success_count, fail_count = download_pdfs(pdf_links, args.output_dir, headers)
        logger.info("\nDownload Summary:")
        logger.info(f"Total PDFs found: {len(pdf_links)}")
        logger.info(f"Successfully downloaded: {success_count}")
        logger.info(f"Failed to download: {fail_count}")
        logger.info(f"PDFs saved to: {os.path.abspath(args.output_dir)}")
    else:
        logger.warning("No PDF links found on the page!")

    # Always scan for other file types, even if no PDFs found
    logger.info(f"Scanning {url} for other file types...")
    file_links = get_file_links(url, headers)
    if file_links:
        logger.info(f"Found {len(file_links)} files to download")
        download_files(file_links, args.output_dir, headers)
    else:
        logger.info("No other supported files found on the page.")

if __name__ == "__main__":
    main()

