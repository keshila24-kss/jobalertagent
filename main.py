import requests
from bs4 import BeautifulSoup
import smtplib
import json
from email.mime.text import MIMEText
import os

# Load environment variables
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
APP_PASSWORD = os.environ.get('APP_PASSWORD')

# Keywords to match against
KEYWORDS = [
    'cmo', 'chief marketing officer', 'vp marketing', 'svp marketing',
    'vp demand generation', 'head of growth', 'growth marketing',
    'demand generation', 'performance marketing', 'global head of marketing'
]

# Job board to scrape (expandable)
URLS = [
    'https://jobs.a16z.com/jobs'
]

# JSON file to track already-seen job URLs
SEEN_FILE = 'seen_jobs.json'

def load_seen_jobs():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, 'r') as f:
        return set(json.load(f))

def save_seen_jobs(seen_jobs):
    with open(SEEN_FILE, 'w') as f:
        json.dump(list(seen_jobs), f)

def fetch_jobs(url):
    jobs = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            title = a.get_text().strip().lower()
            href = a['href']
            if any(k in title for k in KEYWORDS) and '/jobs/' in href:
                full_link = href if href.startswith("http") else f"https://jobs.a16z.com{href}"
                jobs.append((title, full_link))
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return jobs


