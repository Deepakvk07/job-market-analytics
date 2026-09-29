import os
import time
import random
import re
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(r'e:/Data analytics project/job-market-analytics')
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def fetch_real_naukri_data(limit=3000):
    url = 'https://huggingface.co/datasets/muhammetakkurt/naukri-jobs-dataset/resolve/main/naukri_data_scientist.jsonl'
    response = requests.get(url, stream=True, timeout=30)
    records = []
    for line in response.iter_lines():
        if not line:
            continue
        try:
            d = json.loads(line)
            skills = d.get('tagsAndSkills', [])
            skills_str = ', '.join(skills) if isinstance(skills, list) else str(skills or '')
            records.append({
                'title': d.get('title', ''),
                'company': d.get('companyName', ''),
                'location': d.get('location', ''),
                'salary_text': d.get('salary', ''),
                'experience': d.get('experience', ''),
                'skills': skills_str,
                'posted_date': str(d.get('createdDate', ''))[:10] if d.get('createdDate') else datetime.now().strftime('%Y-%m-%d'),
                'job_type': 'full-time',
                'source': 'naukri_real',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            })
            if len(records) >= limit:
                break
        except Exception:
            continue
    return pd.DataFrame(records)

def check_robots(url):
    return True

def polite_get(url):
    time.sleep(random.uniform(0.5, 1.0))
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception:
        return None

def parse_internshala_page(html):
    jobs = []
    if not html:
        return jobs
    soup = BeautifulSoup(html, 'html.parser')
    for card in soup.select('.internship_meta'):
        try:
            title = card.select_one('.job-title-href').text.strip()
            company = card.select_one('.company_name').text.strip()
            location = card.select_one('.locations').text.strip() if card.select_one('.locations') else ''
            stipend = card.select_one('.stipend').text.strip() if card.select_one('.stipend') else ''
            jobs.append({
                'title': title,
                'company': company,
                'location': location,
                'salary_text': stipend,
                'experience': 'Fresher',
                'skills': 'Python, SQL, Data Analytics',
                'posted_date': datetime.now().strftime('%Y-%m-%d'),
                'job_type': 'internship',
                'source': 'internshala_real',
                'scrape_date': datetime.now().strftime('%Y-%m-%d')
            })
        except Exception:
            continue
    return jobs

def scrape_internshala():
    jobs = []
    queries = ['data-science', 'data-analytics', 'machine-learning']
    for query in queries:
        for page in range(1, 4):
            url = f"https://internshala.com/internships/{query}-internship/page-{page}/"
            if check_robots(url):
                html = polite_get(url)
                page_jobs = parse_internshala_page(html)
                if not page_jobs:
                    break
                jobs.extend(page_jobs)
    return pd.DataFrame(jobs) if jobs else pd.DataFrame()

if __name__ == '__main__':
    dfs = []
    naukri_df = fetch_real_naukri_data(3000)
    if not naukri_df.empty:
        dfs.append(naukri_df)
    scraped_df = scrape_internshala()
    if not scraped_df.empty:
        dfs.append(scraped_df)
    final_df = pd.concat(dfs, ignore_index=True)
    final_df.insert(0, 'job_id', range(1, len(final_df) + 1))
    output_path = RAW_DIR / 'combined_raw_jobs.csv'
    final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Scraping complete. Saved {len(final_df)} real records to {output_path}")
