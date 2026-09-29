import pandas as pd
from pathlib import Path
from itertools import combinations
from collections import Counter
PROJECT_ROOT = Path(r'e:/Data analytics project/job-market-analytics')
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'
def main():
    df_jobs = pd.read_csv(PROCESSED_DIR / 'jobs_cleaned.csv')
    df_skills = pd.read_csv(PROCESSED_DIR / 'job_skills.csv')
    merged = pd.merge(df_jobs, df_skills, on='job_id')
    for role in df_jobs['role_category'].unique():
        if pd.isna(role) or role == 'Other': continue
        role_jobs = df_jobs[df_jobs['role_category'] == role]
        total_role = len(role_jobs)
        role_skills = merged[merged['role_category'] == role]['skill'].value_counts()
        if not role_skills.empty:
            top_skill = role_skills.index[0]
            pct = (role_skills.iloc[0] / total_role) * 100
            print(f"Insight 1: {top_skill} appears in {pct:.1f}% of {role} listings")
    
    jobs_with_python = merged[merged['skill'].str.upper() == 'PYTHON']['job_id'].unique()
    jobs_with_sql = merged[merged['skill'].str.upper() == 'SQL']['job_id'].unique()
    jobs_python_only = list(set(jobs_with_python) - set(jobs_with_sql))
    jobs_python_sql = list(set(jobs_with_python) & set(jobs_with_sql))
    
    sal_python_only = df_jobs[df_jobs['job_id'].isin(jobs_python_only)]['salary_avg'].mean()
    sal_python_sql = df_jobs[df_jobs['job_id'].isin(jobs_python_sql)]['salary_avg'].mean()
    if pd.notna(sal_python_only) and pd.notna(sal_python_sql):
        premium = ((sal_python_sql - sal_python_only) / sal_python_only) * 100
        print(f"Insight 2: Salary premium for Python+SQL combo vs Python alone is {premium:.1f}%")
    else:
        print("Insight 2: Not enough salary data for Python vs Python+SQL comparison")
        
    top_cities = df_jobs['city'].value_counts().head(3)
    print("Insight 3: Top 3 cities by listing count with their avg salaries:")
    for city, count in top_cities.items():
        avg_sal = df_jobs[df_jobs['city'] == city]['salary_avg'].mean()
        print(f"  - {city}: {count} listings, Avg Salary: {avg_sal:.1f} Lakhs PA" if pd.notna(avg_sal) else f"  - {city}: {count} listings, Avg Salary: N/A")
        
    fresher_count = len(df_jobs[df_jobs['experience_min'] <= 1])
    fresher_pct = (fresher_count / len(df_jobs)) * 100
    print(f"Insight 4: Fresher demand is {fresher_pct:.1f}% (experience_min <= 1)")
    
    avg_intern = df_jobs[df_jobs['job_type'] == 'internship']['salary_avg'].mean()
    avg_ft = df_jobs[df_jobs['job_type'] == 'full-time']['salary_avg'].mean()
    print(f"Insight 5: Average salary - Internship: {avg_intern:.2f} Lakhs PA, Full-time: {avg_ft:.2f} Lakhs PA")
    
    skill_pairs = []
    for _, group in merged.groupby('job_id'):
        skills = sorted(group['skill'].tolist())
        skill_pairs.extend(combinations(skills, 2))
    
    top_pairs = Counter(skill_pairs).most_common(5)
    print("Insight 6: Top 5 skill pairs by co-occurrence:")
    for pair, count in top_pairs:
        print(f"  - {pair[0]} & {pair[1]}: {count} times")
        
    print("\nLIMITATIONS:")
    print("- Sample bias: Online listings from Naukri and Internshala may overrepresent tech-forward firms and metro locations.")
    print(f"- Missing salary data: {df_jobs['salary_avg'].isna().mean()*100:.1f}% of listings do not disclose salary.")
    print("- Scrape date: All data simulates a single point in time, lacking time-series trends.")
    print("- Geographic coverage: Heavily biased towards top tier-1 Indian cities; rural or tier-3 markets are underrepresented.")
    print("- Text analysis: Job descriptions were not analyzed, missing nuanced context about roles beyond basic skills.")
if __name__ == '__main__':
    main()
