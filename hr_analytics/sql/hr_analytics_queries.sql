-- ============================================================
--  HR ANALYTICS — SQL QUERY LIBRARY
--  Compatible with: SQL Server, PostgreSQL, MySQL (minor tweaks)
--  Table: dbo.Employee_Data  (or your schema equivalent)
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- 0. CREATE TABLE & IMPORT  (SQL Server syntax)
-- ─────────────────────────────────────────────────────────────
CREATE TABLE dbo.Employee_Data (
    EmployeeID       VARCHAR(10)    PRIMARY KEY,
    Department       VARCHAR(50),
    JobTitle         VARCHAR(100),
    JobLevel         VARCHAR(20),
    Age              INT,
    Gender           VARCHAR(20),
    Tenure_Years     DECIMAL(5,1),
    HireDate         DATE,
    Salary           INT,
    PerformanceScore TINYINT,
    SatisfactionScore TINYINT,
    TrainingHours    INT,
    OverTime         VARCHAR(5),
    WorkMode         VARCHAR(20),
    Attrition        VARCHAR(5),
    ExitReason       VARCHAR(50)
);
-- BULK INSERT or Import Wizard from Excel file

-- ─────────────────────────────────────────────────────────────
-- 1. OVERALL KPI SNAPSHOT
-- ─────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                              AS Total_Employees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)  AS Total_Attrited,
    ROUND(
        100.0 * SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                 AS Avg_Salary,
    ROUND(AVG(Tenure_Years), 1)                          AS Avg_Tenure_Years,
    ROUND(AVG(CAST(SatisfactionScore AS FLOAT)), 2)      AS Avg_Satisfaction,
    ROUND(AVG(CAST(PerformanceScore AS FLOAT)), 2)       AS Avg_Performance
FROM dbo.Employee_Data;


-- ─────────────────────────────────────────────────────────────
-- 2. ATTRITION RATE BY DEPARTMENT
-- ─────────────────────────────────────────────────────────────
SELECT
    Department,
    COUNT(*)                                                  AS Headcount,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)       AS Attrited,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                              AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                      AS Avg_Salary,
    ROUND(AVG(CAST(SatisfactionScore AS FLOAT)), 2)           AS Avg_Satisfaction,
    ROUND(AVG(CAST(PerformanceScore AS FLOAT)), 2)            AS Avg_Performance
FROM dbo.Employee_Data
GROUP BY Department
ORDER BY Attrition_Rate_Pct DESC;


-- ─────────────────────────────────────────────────────────────
-- 3. ATTRITION BY JOB LEVEL
-- ─────────────────────────────────────────────────────────────
SELECT
    JobLevel,
    COUNT(*)                                                   AS Headcount,
    SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)          AS Attrited,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                       AS Avg_Salary
FROM dbo.Employee_Data
GROUP BY JobLevel
ORDER BY
    CASE JobLevel
        WHEN 'Junior'    THEN 1 WHEN 'Mid'      THEN 2
        WHEN 'Senior'    THEN 3 WHEN 'Lead'     THEN 4
        WHEN 'Manager'   THEN 5 WHEN 'Director' THEN 6
        WHEN 'VP'        THEN 7 ELSE 99
    END;


-- ─────────────────────────────────────────────────────────────
-- 4. SALARY BAND ANALYSIS
-- ─────────────────────────────────────────────────────────────
SELECT
    SalaryBand,
    COUNT(*)                                                   AS Headcount,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(SatisfactionScore AS FLOAT)), 2)            AS Avg_Satisfaction
FROM (
    SELECT *,
        CASE
            WHEN Salary < 50000              THEN '1. <$50k'
            WHEN Salary BETWEEN 50000 AND 69999  THEN '2. $50-70k'
            WHEN Salary BETWEEN 70000 AND 89999  THEN '3. $70-90k'
            WHEN Salary BETWEEN 90000 AND 109999 THEN '4. $90-110k'
            WHEN Salary BETWEEN 110000 AND 139999 THEN '5. $110-140k'
            ELSE '6. $140k+'
        END AS SalaryBand
    FROM dbo.Employee_Data
) t
GROUP BY SalaryBand
ORDER BY SalaryBand;


-- ─────────────────────────────────────────────────────────────
-- 5. OVERTIME IMPACT ON ATTRITION
-- ─────────────────────────────────────────────────────────────
SELECT
    OverTime,
    WorkMode,
    COUNT(*)                                                   AS Headcount,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(SatisfactionScore AS FLOAT)), 2)            AS Avg_Satisfaction
FROM dbo.Employee_Data
GROUP BY OverTime, WorkMode
ORDER BY OverTime, Attrition_Rate_Pct DESC;


-- ─────────────────────────────────────────────────────────────
-- 6. SATISFACTION × PERFORMANCE ATTRITION MATRIX
-- ─────────────────────────────────────────────────────────────
SELECT
    SatisfactionScore,
    PerformanceScore,
    COUNT(*)                                                   AS Employees,
    SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)          AS Attrited,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Attrition_Rate_Pct
FROM dbo.Employee_Data
GROUP BY SatisfactionScore, PerformanceScore
ORDER BY SatisfactionScore, PerformanceScore;


-- ─────────────────────────────────────────────────────────────
-- 7. TENURE COHORT ANALYSIS
-- ─────────────────────────────────────────────────────────────
SELECT
    TenureBand,
    COUNT(*)                                                   AS Employees,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Attrition_Rate_Pct,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                       AS Avg_Salary
FROM (
    SELECT *,
        CASE
            WHEN Tenure_Years < 1    THEN '0. <1 year'
            WHEN Tenure_Years < 2    THEN '1. 1-2 years'
            WHEN Tenure_Years < 4    THEN '2. 2-4 years'
            WHEN Tenure_Years < 7    THEN '3. 4-7 years'
            WHEN Tenure_Years < 10   THEN '4. 7-10 years'
            ELSE '5. 10+ years'
        END AS TenureBand
    FROM dbo.Employee_Data
) t
GROUP BY TenureBand
ORDER BY TenureBand;


-- ─────────────────────────────────────────────────────────────
-- 8. EXIT REASON BREAKDOWN
-- ─────────────────────────────────────────────────────────────
SELECT
    ExitReason,
    COUNT(*)                                                   AS Total_Exits,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2)         AS Pct_of_Exits,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                       AS Avg_Salary,
    ROUND(AVG(Tenure_Years), 1)                                AS Avg_Tenure
FROM dbo.Employee_Data
WHERE Attrition = 'Yes'
  AND ExitReason IS NOT NULL
  AND ExitReason <> ''
GROUP BY ExitReason
ORDER BY Total_Exits DESC;


-- ─────────────────────────────────────────────────────────────
-- 9. HIGH-FLIGHT-RISK EMPLOYEES  (rule-based scoring)
-- ─────────────────────────────────────────────────────────────
SELECT
    EmployeeID, Department, JobTitle, JobLevel, Salary,
    SatisfactionScore, PerformanceScore, OverTime, Tenure_Years,
    (
        CASE WHEN SatisfactionScore <= 2  THEN 30 ELSE 0 END +
        CASE WHEN OverTime = 'Yes'        THEN 20 ELSE 0 END +
        CASE WHEN Tenure_Years BETWEEN 1 AND 4 THEN 15 ELSE 0 END +
        CASE WHEN PerformanceScore <= 2   THEN 15 ELSE 0 END +
        CASE WHEN Salary < 60000          THEN 10 ELSE 0 END +
        CASE WHEN SatisfactionScore = 3   THEN  5 ELSE 0 END
    )                                                          AS RiskScore,
    CASE
        WHEN (
            CASE WHEN SatisfactionScore <= 2  THEN 30 ELSE 0 END +
            CASE WHEN OverTime = 'Yes'        THEN 20 ELSE 0 END +
            CASE WHEN Tenure_Years BETWEEN 1 AND 4 THEN 15 ELSE 0 END +
            CASE WHEN PerformanceScore <= 2   THEN 15 ELSE 0 END +
            CASE WHEN Salary < 60000          THEN 10 ELSE 0 END +
            CASE WHEN SatisfactionScore = 3   THEN  5 ELSE 0 END
        ) >= 50 THEN 'HIGH'
        WHEN (
            CASE WHEN SatisfactionScore <= 2  THEN 30 ELSE 0 END +
            CASE WHEN OverTime = 'Yes'        THEN 20 ELSE 0 END +
            CASE WHEN Tenure_Years BETWEEN 1 AND 4 THEN 15 ELSE 0 END +
            CASE WHEN PerformanceScore <= 2   THEN 15 ELSE 0 END +
            CASE WHEN Salary < 60000          THEN 10 ELSE 0 END +
            CASE WHEN SatisfactionScore = 3   THEN  5 ELSE 0 END
        ) >= 25 THEN 'MEDIUM'
        ELSE 'LOW'
    END                                                        AS RiskTier
FROM dbo.Employee_Data
WHERE Attrition = 'No'   -- Active employees only
ORDER BY RiskScore DESC;


-- ─────────────────────────────────────────────────────────────
-- 10. DEPARTMENT PERFORMANCE SCORECARD (for Power BI)
-- ─────────────────────────────────────────────────────────────
SELECT
    Department,
    COUNT(*)                                                       AS Headcount,
    ROUND(AVG(CAST(PerformanceScore AS FLOAT)), 2)                 AS Avg_Performance,
    ROUND(AVG(CAST(SatisfactionScore AS FLOAT)), 2)                AS Avg_Satisfaction,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                           AS Avg_Salary,
    ROUND(AVG(Tenure_Years), 1)                                    AS Avg_Tenure,
    ROUND(100.0 * SUM(CASE WHEN OverTime='Yes' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                                   AS OT_Rate_Pct,
    ROUND(AVG(CAST(TrainingHours AS FLOAT)), 0)                    AS Avg_Training_Hrs,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                   AS Attrition_Rate_Pct,
    -- Composite score 0–100 (higher = better)
    ROUND(
        (AVG(CAST(PerformanceScore AS FLOAT)) / 5.0 * 40) +
        (AVG(CAST(SatisfactionScore AS FLOAT)) / 5.0 * 40) +
        (1 - SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) * 20
    , 1)                                                           AS Composite_Score
FROM dbo.Employee_Data
GROUP BY Department
ORDER BY Composite_Score DESC;


-- ─────────────────────────────────────────────────────────────
-- 11. MONTHLY ATTRITION TREND
-- ─────────────────────────────────────────────────────────────
SELECT
    YEAR(HireDate)                                             AS [Year],
    MONTH(HireDate)                                            AS [Month],
    FORMAT(HireDate, 'MMM yyyy')                               AS Month_Label,
    COUNT(*)                                                   AS Total_Employees,
    SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END)          AS Monthly_Exits,
    ROUND(100.0 * SUM(CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                               AS Monthly_Attrition_Pct
FROM dbo.Employee_Data
GROUP BY YEAR(HireDate), MONTH(HireDate), FORMAT(HireDate, 'MMM yyyy')
ORDER BY [Year], [Month];


-- ─────────────────────────────────────────────────────────────
-- 12. GENDER DIVERSITY & PAY GAP
-- ─────────────────────────────────────────────────────────────
SELECT
    Department,
    Gender,
    COUNT(*)                                                   AS Headcount,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(PARTITION BY Department), 1)
                                                               AS Dept_Pct,
    ROUND(AVG(CAST(Salary AS FLOAT)), 0)                       AS Avg_Salary,
    ROUND(AVG(CAST(PerformanceScore AS FLOAT)), 2)             AS Avg_Performance
FROM dbo.Employee_Data
GROUP BY Department, Gender
ORDER BY Department, Gender;
