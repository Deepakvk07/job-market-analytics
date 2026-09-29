import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title='Indian Tech Job Market Analytics', layout='wide')

@st.cache_data
def load_data():
    base_dir = Path(__file__).resolve().parent.parent / 'data' / 'processed'
    jobs_path = base_dir / 'jobs_cleaned.csv'
    skills_path = base_dir / 'job_skills.csv'
    if not jobs_path.exists() or not skills_path.exists():
        st.error('Cleaned datasets not found. Please run the processing pipeline first.')
        st.stop()
    jobs = pd.read_csv(jobs_path)
    skills = pd.read_csv(skills_path)
    return jobs, skills

jobs_df, skills_df = load_data()

st.sidebar.title('Filter Listings')
roles = sorted(jobs_df['role_category'].dropna().unique())
role_category = st.sidebar.multiselect('Role Category', roles, default=roles)

top_cities = jobs_df['city'].value_counts().nlargest(12).index.tolist()
city = st.sidebar.multiselect('Location / Hub', top_cities, default=top_cities)

job_type = st.sidebar.radio('Employment Type', ['All', 'full-time', 'internship'])

max_sal = float(jobs_df['salary_max'].max()) if pd.notna(jobs_df['salary_max'].max()) else 50.0
salary_range = st.sidebar.slider('Salary Range (LPA)', 0.0, max_sal, (0.0, max_sal), step=1.0)

filtered_df = jobs_df.copy()
if role_category:
    filtered_df = filtered_df[filtered_df['role_category'].isin(role_category)]
if city:
    filtered_df = filtered_df[filtered_df['city'].isin(city)]
if job_type != 'All':
    filtered_df = filtered_df[filtered_df['job_type'] == job_type]
if 'salary_avg' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['salary_avg'].fillna(0).between(salary_range[0], salary_range[1])]

st.title('Indian Tech Job Market Analytics')
st.caption('Analyzing compensation benchmarks, technical skill demand, and hiring hubs across Data Analyst, Data Scientist, and ML Engineer listings.')

col1, col2, col3, col4 = st.columns(4)
total_listings = len(filtered_df)
avg_salary = filtered_df['salary_avg'].mean()
avg_salary_text = f'{avg_salary:.1f} LPA' if pd.notna(avg_salary) else 'N/A'

filtered_jobs_ids = filtered_df['job_id'].tolist()
filtered_skills = skills_df[skills_df['job_id'].isin(filtered_jobs_ids)]
top_skill = filtered_skills['skill'].mode()[0] if not filtered_skills.empty else 'N/A'
top_city = filtered_df['city'].mode()[0] if not filtered_df.empty else 'N/A'

col1.metric('Total Postings', f'{total_listings:,}')
col2.metric('Average Salary', avg_salary_text)
col3.metric('Top Required Skill', top_skill)
col4.metric('Top Location', top_city)

st.divider()

col5, col6 = st.columns(2)
with col5:
    if not filtered_skills.empty:
        skill_counts = filtered_skills['skill'].value_counts().nlargest(10).reset_index()
        skill_counts.columns = ['Skill', 'Count']
        fig1 = px.bar(skill_counts, x='Skill', y='Count', title='Top 10 Technical Skills in Demand', color_discrete_sequence=['#2b5c8f'])
        fig1.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig1, use_container_width=True)

with col6:
    sal_subset = filtered_df.dropna(subset=['salary_avg'])
    if not sal_subset.empty:
        fig2 = px.box(sal_subset, x='role_category', y='salary_avg', title='Salary Distribution by Role (LPA)', color='role_category')
        fig2.update_layout(showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis_title='Role', yaxis_title='Salary (LPA)')
        st.plotly_chart(fig2, use_container_width=True)

col7, col8 = st.columns(2)
with col7:
    if not filtered_df.empty:
        city_counts = filtered_df['city'].value_counts().nlargest(8).reset_index()
        city_counts.columns = ['City', 'Postings']
        fig3 = px.bar(city_counts, x='City', y='Postings', title='Listings by Metropolitan Hub', color_discrete_sequence=['#3b82f6'])
        fig3.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig3, use_container_width=True)

with col8:
    if not filtered_df.empty:
        type_counts = filtered_df['job_type'].value_counts().reset_index()
        type_counts.columns = ['Employment Type', 'Count']
        fig4 = px.pie(type_counts, names='Employment Type', values='Count', title='Full-Time vs. Internship Distribution', hole=0.4)
        fig4.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader('Filtered Job Records')
display_cols = ['title', 'company', 'city', 'salary_text', 'experience', 'job_type', 'posted_date']
available_cols = [c for c in display_cols if c in filtered_df.columns]
st.dataframe(filtered_df[available_cols], use_container_width=True)

latest_date = filtered_df['scrape_date'].dropna().max() if 'scrape_date' in filtered_df.columns else None
if latest_date:
    st.caption(f'Data snapshot timestamp: {latest_date}')
