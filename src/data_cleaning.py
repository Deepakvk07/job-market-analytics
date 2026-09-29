import pandas as pd
import numpy as np
import re
import sqlite3
from pathlib import Path
PROJECT_ROOT = Path(r'e:/Data analytics project/job-market-analytics')
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
def standardize_city(loc):
    if pd.isna(loc):
        return 'Unknown'
    loc = str(loc).lower()
    if any(x in loc for x in ['bengaluru', 'bangalore']): return 'Bangalore'
    if any(x in loc for x in ['mumbai', 'bombay', 'navi mumbai']): return 'Mumbai'
    if any(x in loc for x in ['delhi', 'new delhi', 'gurgaon', 'gurugram', 'noida', 'ghaziabad', 'faridabad']): return 'Delhi NCR'
    if any(x in loc for x in ['hyderabad', 'secunderabad']): return 'Hyderabad'
    if any(x in loc for x in ['chennai', 'madras']): return 'Chennai'
    if any(x in loc for x in ['kolkata', 'calcutta']): return 'Kolkata'
    if any(x in loc for x in ['pune', 'puna']): return 'Pune'
    if any(x in loc for x in ['work from home', 'remote', 'wfh']): return 'Remote'
    if 'ahmedabad' in loc: return 'Ahmedabad'
    if 'jaipur' in loc: return 'Jaipur'
    if 'kochi' in loc: return 'Kochi'
    if 'indore' in loc: return 'Indore'
    if 'chandigarh' in loc: return 'Chandigarh'
    if 'coimbatore' in loc: return 'Coimbatore'
    if 'lucknow' in loc: return 'Lucknow'
    if 'nagpur' in loc: return 'Nagpur'
    return 'Other'
def categorize_role(title):
    if pd.isna(title):
        return 'Other'
    t = str(title).lower()
    if any(x in t for x in ['ml', 'machine learning', 'deep learning', 'ai engineer']): return 'ML Engineer'
    if any(x in t for x in ['data scientist', 'data science']): return 'Data Scientist'
    if any(x in t for x in ['data analyst', 'analytics', 'business analyst']): return 'Data Analyst'
    return 'Other'
def parse_salary(salary_text, job_type):
    if pd.isna(salary_text) or str(salary_text).strip() in ['Not disclosed', 'Unpaid', '']:
        return np.nan, np.nan, np.nan
    s = str(salary_text).lower().replace(',', '')
    if 'unpaid' in s or 'not disclosed' in s:
        return np.nan, np.nan, np.nan
    m = re.search(r'([\d.]+)\s*-\s*([\d.]+)\s*(?:lacs?|lakhs?|lpa)', s)
    if m:
        cmin, cmax = float(m.group(1)), float(m.group(2))
        return cmin, cmax, (cmin + cmax) / 2
    m2 = re.search(r'([\d.]+)\s*(?:lacs?|lakhs?|lpa)', s)
    if m2:
        val = float(m2.group(1))
        return val, val, val
    m3 = re.search(r'₹?\s*(\d+)\s*-\s*₹?\s*(\d+)\s*(?:/month|/\s*month|per month)', s)
    if m3:
        cmin = float(m3.group(1)) * 12 / 100000
        cmax = float(m3.group(2)) * 12 / 100000
        return cmin, cmax, (cmin + cmax) / 2
    m4 = re.search(r'₹?\s*(\d+)\s*(?:/month|/\s*month|per month)', s)
    if m4:
        val = float(m4.group(1)) * 12 / 100000
        return val, val, val
    return np.nan, np.nan, np.nan
def parse_experience(exp_text):
    if pd.isna(exp_text):
        return np.nan, np.nan
    e = str(exp_text).lower()
    if 'fresher' in e:
        return 0.0, 0.0
    m = re.search(r'(\d+)\s*-\s*(\d+)', e)
    if m:
        return float(m.group(1)), float(m.group(2))
    m2 = re.search(r'(\d+)\+', e)
    if m2:
        return float(m2.group(1)), np.nan
    return np.nan, np.nan
def extract_skills(df):
    records = []
    acronyms = {'Sql': 'SQL', 'Nlp': 'NLP', 'Aws': 'AWS', 'Gcp': 'GCP', 'Ml': 'ML', 'Etl': 'ETL', 'Ai': 'AI', 'Mlops': 'MLOps'}
    for _, row in df.iterrows():
        if pd.notna(row['skills']):
            for s in str(row['skills']).split(','):
                s_clean = s.strip()
                if not s_clean:
                    continue
                s_title = acronyms.get(s_clean.title(), s_clean.title())
                if 1 < len(s_title) < 50:
                    records.append({'job_id': row['job_id'], 'skill': s_title})
    return pd.DataFrame(records)
def main():
    df = pd.read_csv(RAW_DIR / 'combined_raw_jobs.csv')
    orig_len = len(df)
    df = df.drop_duplicates(subset=['title', 'company', 'location', 'salary_text'])
    df['job_id'] = ['JOB' + str(i).zfill(6) for i in range(1, len(df) + 1)]
    df['city'] = df['location'].apply(standardize_city)
    df['role_category'] = df['title'].apply(categorize_role)
    salaries = df.apply(lambda row: pd.Series(parse_salary(row['salary_text'], row['job_type'])), axis=1)
    df[['salary_min', 'salary_max', 'salary_avg']] = salaries
    df['experience_text'] = df['experience']
    exps = df['experience_text'].apply(lambda x: pd.Series(parse_experience(x)))
    df[['experience_min', 'experience_max']] = exps
    output_cols = ['job_id', 'title', 'role_category', 'company', 'location', 'city', 'salary_text', 'salary_min', 'salary_max', 'salary_avg', 'experience_text', 'experience_min', 'experience_max', 'posted_date', 'job_type', 'source', 'scrape_date']
    df_clean = df[output_cols]
    df_skills = extract_skills(df)
    df_clean.to_csv(PROCESSED_DIR / 'jobs_cleaned.csv', index=False)
    df_skills.to_csv(PROCESSED_DIR / 'job_skills.csv', index=False)
    conn = sqlite3.connect(PROCESSED_DIR / 'jobs.db')
    df_clean.to_sql('jobs', conn, if_exists='replace', index=False)
    df_skills.to_sql('job_skills', conn, if_exists='replace', index=False)
    conn.close()
    print(f"Original records: {orig_len}")
    print(f"Cleaned records: {len(df_clean)}")
    print(f"Unique cities: {df_clean['city'].nunique()}")
    print(f"Unique companies: {df_clean['company'].nunique()}")
    print(f"Unique skills: {df_skills['skill'].nunique()}")
    print("\nRole Distribution:")
    print(df_clean['role_category'].value_counts())
    print("\nJob Type Distribution:")
    print(df_clean['job_type'].value_counts())
    sal_cov = df_clean['salary_avg'].notna().mean() * 100
    exp_cov = df_clean['experience_min'].notna().mean() * 100
    print(f"\nSalary Coverage: {sal_cov:.1f}%")
    print(f"Experience Coverage: {exp_cov:.1f}%")
if __name__ == '__main__':
    main()
