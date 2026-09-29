# Job Market Analytics Dashboard

An end-to-end data analytics and engineering project analyzing hiring trends, technical skill requirements, and compensation benchmarks across Data Analyst, Data Scientist, and Machine Learning Engineer positions in the Indian tech market.

---

## Overview

Entry-level and early-career data professionals often face ambiguity regarding which technical stacks to prioritize, how compensation varies across metro hubs, and what realistic expectations exist between internships and full-time hiring. 

This project implements a complete data pipeline to ingest, clean, model, analyze, and visualize thousands of active job market postings from Indian job boards (Naukri and Internshala). The final deliverable includes a relational SQLite database, an analytical query suite, and an interactive Streamlit dashboard.

---

## Data Pipeline Architecture

```
  [ Web Scraper / Public Datasets ]
                 │
                 ▼
     [ Raw Ingestion Layer ] ──> data/raw/combined_raw_jobs.csv
                 │
                 ▼
     [ Data Preprocessing ]  ──> Regex Salary & Experience Parsing, City Standardization
                 │
                 ├───────────────────────────────┐
                 ▼                               ▼
       [ Normalized Jobs Table ]       [ Normalized Skills Table (1NF) ]
       (data/processed/jobs_cleaned.csv) (data/processed/job_skills.csv)
                 │                               │
                 └───────────────┬───────────────┘
                                 ▼
                     [ SQLite Database (jobs.db) ]
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       [ SQL Analytical Queries ]      [ Streamlit Web Application ]
       (sql/queries.sql)               (app/streamlit_app.py)
```

---

## Dataset & Preprocessing

The dataset comprises **3,357 raw listings** resulting in **2,842 deduplicated records** across 1,404 companies:

1. **City Normalization**: Locations often contained unstructured text (e.g., `Bengaluru / Bangalore`, `Navi Mumbai`, `Gurgaon / Gurugram`). A standardization function mapped these into consolidated metropolitan hubs (`Bangalore`, `Mumbai`, `Delhi NCR`, `Hyderabad`, `Pune`, `Remote`).
2. **Salary Normalization**: Compensation strings vary widely across platforms:
   - Annual ranges: `12-15 Lacs PA` -> `salary_min: 12.0`, `salary_max: 15.0`, `salary_avg: 13.5` (in LPA).
   - Monthly stipends: `₹15,000 /month` -> normalized to annualized Lakhs Per Annum (`0.15 * 12 = 1.8 LPA`).
   - Undisclosed listings were preserved as `NaN` rather than imputed with zeros to prevent skewing distribution metrics.
3. **Skill Entity Normalization (1NF)**: Multi-valued comma-separated skill lists were unnested into an atomic `(job_id, skill)` junction table containing 16,000+ skill instances, enabling efficient indexing and SQL self-join queries.

---

## Key Market Findings

* **Skill Co-occurrence**: The most frequent complementary skill pair in Indian tech recruitment is **Python & SQL** (appearing together in 500+ listings), followed by **Data Science & Machine Learning** (336 co-occurrences).
* **Metropolitan Concentration**: Bangalore represents the highest concentration of technical data hiring (1,247 postings with an average salary of 16.2 LPA), followed by Delhi NCR (345 postings, avg 11.4 LPA).
* **Full-Time vs. Internship Compensation**: Across technical data roles, full-time postings average 18.72 LPA, while internships average an annualized equivalent of 1.62 LPA.
* **Early Career Demand**: Approximately 21.3% of listings target early-career candidates (0-1 year experience), predominantly through junior analytics positions and data science internships.

---

## SQL Analytical Queries

The analytical layer (`sql/queries.sql`) features 10 production SQL queries run against SQLite. Key queries include:

### 1. Skill Co-Occurrence Analysis (Self-Join)
Identifies complementary skills that recruiters frequently bundle together:
```sql
SELECT 
    a.skill AS primary_skill, 
    b.skill AS secondary_skill, 
    COUNT(*) AS co_occurrence_count
FROM job_skills a
JOIN job_skills b 
    ON a.job_id = b.job_id 
    AND a.skill < b.skill
GROUP BY a.skill, b.skill
ORDER BY co_occurrence_count DESC
LIMIT 15;
```

### 2. City Salary Rank per Role (Window Function)
Ranks tech hubs by average compensation within each functional discipline:
```sql
SELECT
    role_category,
    city,
    ROUND(AVG(salary_avg), 2) AS avg_salary_lpa,
    RANK() OVER (PARTITION BY role_category ORDER BY AVG(salary_avg) DESC) AS salary_rank
FROM jobs
WHERE salary_avg IS NOT NULL AND city != 'Unknown'
GROUP BY role_category, city
HAVING COUNT(*) >= 3
ORDER BY role_category, salary_rank;
```

---

## Interactive Dashboard

The Streamlit application (`app/streamlit_app.py`) provides an interactive interface to explore market trends:
- **KPI Metrics**: Dynamic cards showing total listings, average compensation, top in-demand skills, and leading cities based on active filters.
- **Visualizations (Plotly)**: Interactive breakdowns of skills demand, compensation spreads across roles, geographic volume, and internship vs. full-time distribution.
- **Faceted Filtering**: Multiselect filters for role category, city, employment type, and salary range sliders with in-memory dataframe caching (`@st.cache_data`).

To launch the dashboard locally:
```bash
streamlit run app/streamlit_app.py
```

---

## Repository Structure

```
job-market-analytics/
├── app/
│   └── streamlit_app.py             # Streamlit web application
├── data/
│   ├── raw/
│   │   └── combined_raw_jobs.csv    # Raw ingested job listings
│   └── processed/
│       ├── jobs_cleaned.csv         # Cleaned jobs dataset
│       ├── job_skills.csv           # 1NF normalized skill relationship table
│       └── jobs.db                  # SQLite database
├── notebooks/
│   ├── 01_data_cleaning.ipynb       # Data cleaning & schema export walkthrough
│   └── 02_exploratory_data_analysis.ipynb # Visual EDA and statistical distributions
├── screenshots/                     # Exported EDA visualization figures
├── src/
│   ├── data_collection.py           # Ingestion and web scraping pipeline
│   ├── data_cleaning.py             # Preprocessing and SQLite database export
│   ├── eda_visualization.py         # Static Matplotlib/Seaborn figure generator
│   └── generate_insights.py         # Statistical metrics and insight calculator
├── sql/
│   └── queries.sql                  # Analytical SQL queries
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- SQLite3

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Deepakvk07/job-market-analytics.git
   cd job-market-analytics
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the processing pipeline:
   ```bash
   # Ingest raw data
   python src/data_collection.py

   # Clean data and populate SQLite database
   python src/data_cleaning.py

   # Generate visual reports
   python src/eda_visualization.py

   # Launch dashboard
   streamlit run app/streamlit_app.py
   ```

---

## Limitations

- **Salary Non-Disclosure**: Approximately 85% of online postings in the Indian market do not explicitly disclose compensation figures ("Not Disclosed by Recruiter"), meaning salary statistics represent the subset of listings with public compensation.
- **Geographic Bias**: Data heavily reflects Tier-1 tech clusters (Bangalore, Mumbai, NCR), with smaller regional markets having lower representation.
- **Temporal Scope**: Listings capture an active recruitment snapshot and do not account for cyclical seasonal recruitment swings.

---

## License

This project is licensed under the MIT License.
