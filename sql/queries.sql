SELECT skill, COUNT(*) AS demand_count
FROM job_skills
GROUP BY skill
ORDER BY demand_count DESC
LIMIT 15;


SELECT city, COUNT(*) AS listing_count, ROUND(AVG(salary_avg), 2) AS avg_salary_lakhs
FROM jobs
WHERE salary_avg IS NOT NULL AND city != '' AND city != 'Unknown'
GROUP BY city
ORDER BY listing_count DESC
LIMIT 10;


SELECT company, COUNT(*) AS job_count
FROM jobs
WHERE company != ''
GROUP BY company
ORDER BY job_count DESC
LIMIT 15;


SELECT
    CASE
        WHEN experience_min IS NULL THEN 'Not Specified'
        WHEN experience_min <= 1 THEN 'Fresher (0-1 yr)'
        WHEN experience_min <= 3 THEN 'Junior (2-3 yr)'
        WHEN experience_min <= 5 THEN 'Mid (4-5 yr)'
        ELSE 'Senior (5+ yr)'
    END AS experience_level,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_avg), 2) AS avg_salary_lakhs
FROM jobs
GROUP BY experience_level
ORDER BY job_count DESC;


SELECT a.skill AS skill_1, b.skill AS skill_2, COUNT(*) AS co_occurrence
FROM job_skills a
JOIN job_skills b ON a.job_id = b.job_id AND a.skill < b.skill
GROUP BY a.skill, b.skill
ORDER BY co_occurrence DESC
LIMIT 15;


SELECT
    role_category,
    city,
    ROUND(AVG(salary_avg), 2) AS avg_salary,
    RANK() OVER (PARTITION BY role_category ORDER BY AVG(salary_avg) DESC) AS salary_rank
FROM jobs
WHERE salary_avg IS NOT NULL AND city != '' AND city != 'Unknown'
GROUP BY role_category, city
HAVING COUNT(*) >= 3
ORDER BY role_category, salary_rank;


SELECT role_category, skill, skill_count
FROM (
    SELECT
        j.role_category,
        js.skill,
        COUNT(*) AS skill_count,
        ROW_NUMBER() OVER (PARTITION BY j.role_category ORDER BY COUNT(*) DESC) AS rn
    FROM jobs j
    JOIN job_skills js ON j.job_id = js.job_id
    GROUP BY j.role_category, js.skill
) ranked
WHERE rn <= 5
ORDER BY role_category, skill_count DESC;


SELECT
    job_type,
    COUNT(*) AS total_listings,
    ROUND(AVG(salary_avg), 2) AS avg_salary_lakhs,
    ROUND(MIN(salary_min), 2) AS min_salary,
    ROUND(MAX(salary_max), 2) AS max_salary
FROM jobs
WHERE salary_avg IS NOT NULL
GROUP BY job_type;


SELECT
    role_category,
    COUNT(*) AS listing_count,
    ROUND(AVG(salary_avg), 2) AS avg_salary,
    ROUND(MIN(salary_min), 2) AS min_salary,
    ROUND(MAX(salary_max), 2) AS max_salary
FROM jobs
WHERE salary_avg IS NOT NULL
GROUP BY role_category
ORDER BY avg_salary DESC;


SELECT
    company,
    COUNT(*) AS job_count,
    ROUND(AVG(salary_avg), 2) AS avg_salary_lakhs,
    GROUP_CONCAT(DISTINCT role_category) AS roles_offered
FROM jobs
WHERE salary_avg IS NOT NULL AND company != ''
GROUP BY company
HAVING job_count >= 3
ORDER BY avg_salary_lakhs DESC
LIMIT 15;
