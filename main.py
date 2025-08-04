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
                if href.startswith("http"):
                    full_link = href
                else:
                    full_link = "https://jobs.a16z.com" + href
                jobs.append((title, full_link))
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    return jobs

def send_email(jobs):
    # Compose email content
    body = ""
    for title, link in jobs:
        body += f"{title}\n{link}\n\n"

    msg = MIMEText(body)
    msg['Subject'] = 'New Job Postings'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, APP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    seen_jobs = load_seen_jobs()
    new_jobs = []

    for url in URLS:
        try:
            jobs = fetch_jobs(url)
            for title, link in jobs:
                if link not in seen_jobs:
                    new_jobs.append((title, link))
                    seen_jobs.add(link)
        except Exception as e:
            print(f"Error processing {url}: {e}")

    if new_jobs:
        send_email(new_jobs)
        save_seen_jobs(seen_jobs)
        print(f"Sent notifications for {len(new_jobs)} new jobs.")
    else:
        print("No new jobs found.")


if __name__ == "__main__":
    main()
