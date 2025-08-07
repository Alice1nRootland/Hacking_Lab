print("""
====================================
🕵 Email Scraper by  Al1ce1nR00tl@nd
For educational and ethical use only
====================================
""")

from bs4 import BeautifulSoup
import requests
import urllib.parse
from collections import deque
import re
import time

user_url = input('[+] Enter Target URL To Scan: ').strip()
urls = deque([user_url])
scraped_urls = set()
emails = set()

headers = {'User-Agent': 'Mozilla/5.0 (compatible; EmailScraper/1.0)'}
count = 0

try:
    while urls:
        count += 1
        if count > 100:
            break

        url = urls.popleft()
        scraped_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        base_url = f'{parts.scheme}://{parts.netloc}'
        path = url[:url.rfind('/')+1] if '/' in parts.path else url

        print(f'[{count}] Processing: {url}')
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f'[!] Request failed: {e}')
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        if new_emails:
            print(f'[+] Found {len(new_emails)} email(s) on {url}')
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, 'lxml')
        for anchor in soup.find_all("a"):
            link = anchor.get('href')
            if not link:
                continue
            link = urllib.parse.urljoin(url, link)
            if link.startswith(base_url) and link not in scraped_urls and link not in urls:
                urls.append(link)

        time.sleep(1)  # Be polite

except KeyboardInterrupt:
    print('\n[-] Interrupted by user. Exiting...')

print(f'\n[✓] Finished. Total unique emails found: {len(emails)}')
for mail in sorted(emails):
    print(f'  - {mail}')
                          