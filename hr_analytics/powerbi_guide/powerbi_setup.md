# Power BI Setup Guide — HR Analytics Dashboard

## Step 1: Connect to Excel Data
1. Open **Power BI Desktop**
2. **Home → Get Data → Excel Workbook**
3. Navigate to `data/HR_Analytics_Data.xlsx`
4. In the Navigator pane, check: `Employee_Data`, `Pivot_Ready`, `Attrition_Summary`
5. Click **Load**

---

## Step 2: Power Query Transformations

Open **Transform Data** and add the following custom columns:

### Salary Band Column
```m
= if [Salary] < 50000 then "1. <$50k"
  else if [Salary] < 70000 then "2. $50-70k"
  else if [Salary] < 90000 then "3. $70-90k"
  else if [Salary] < 110000 then "4. $90-110k"
  else if [Salary] < 140000 then "5. $110-140k"
  else "6. $140k+"
```

### Tenure Band Column
```m
= if [Tenure_Years] < 1 then "0. <1 year"
  else if [Tenure_Years] < 2 then "1. 1-2 years"
  else if [Tenure_Years] < 4 then "2. 2-4 years"
  else if [Tenure_Years] < 7 then "3. 4-7 years"
  else if [Tenure_Years] < 10 then "4. 7-10 years"
  else "5. 10+ years"
```

### Attrition Flag (numeric)
```m
= if [Attrition] = "Yes" then 1 else 0
```

---

## Step 3: DAX Measures

Create a dedicated **Measures** table. Add these DAX formulas:

### Core KPIs
```dax
Total Employees = COUNTROWS('Employee_Data')

Total Attrited =
CALCULATE(COUNTROWS('Employee_Data'), 'Employee_Data'[Attrition] = "Yes")

Attrition Rate =
DIVIDE(
    CALCULATE(COUNTROWS('Employee_Data'), 'Employee_Data'[Attrition] = "Yes"),
    COUNTROWS('Employee_Data'),
    0
)

Attrition Rate % = FORMAT([Attrition Rate], "0.0%")
```

### Financial Metrics
```dax
Avg Salary = AVERAGE('Employee_Data'[Salary])

Avg Salary Attrited =
CALCULATE(AVERAGE('Employee_Data'[Salary]), 'Employee_Data'[Attrition] = "Yes")

Salary Gap = [Avg Salary] - [Avg Salary Attrited]
```

### Engagement Metrics
```dax
Avg Satisfaction = AVERAGE('Employee_Data'[SatisfactionScore])

Avg Performance = AVERAGE('Employee_Data'[PerformanceScore])

Avg Tenure = AVERAGE('Employee_Data'[Tenure_Years])

Avg Training Hours = AVERAGE('Employee_Data'[TrainingHours])
```

### Risk Metrics
```dax
High Risk Count =
CALCULATE(
    COUNTROWS('Employee_Data'),
    'Employee_Data'[SatisfactionScore] <= 2,
    'Employee_Data'[OverTime] = "Yes",
    'Employee_Data'[Attrition] = "No"
)

Overtime Attrition Rate =
CALCULATE([Attrition Rate], 'Employee_Data'[OverTime] = "Yes")

Low Satisfaction Attrition Rate =
CALCULATE([Attrition Rate], 'Employee_Data'[SatisfactionScore] <= 2)
```

---

## Step 4: Dashboard Pages & Visuals

### Page 1 — Executive Overview
| Visual              | Fields                                        | Notes                          |
|---------------------|-----------------------------------------------|--------------------------------|
| Card (x4)           | Total Employees, Attrition Rate, Avg Salary, Avg Satisfaction | Use conditional formatting |
| Clustered Bar Chart | Attrition Rate by Department                  | Add constant line at avg rate  |
| Donut Chart         | Count by ExitReason (attrited only)           | Filter: Attrition = Yes        |
| KPI Card            | High Risk Count                               | Red background                 |

### Page 2 — Attrition Deep Dive
| Visual              | Fields                                        | Notes                          |
|---------------------|-----------------------------------------------|--------------------------------|
| Line Chart          | Monthly Exits over HireDate                   | X-axis: Month, Y-axis: Count   |
| Matrix              | SatisfactionScore × PerformanceScore          | Values: Attrition Rate         |
| Stacked Bar         | Attrition by Gender + Department              |                                |
| Scatter Plot        | Salary vs SatisfactionScore                   | Color: Attrition, Size: Tenure |

### Page 3 — Department Scorecard
| Visual              | Fields                                        | Notes                          |
|---------------------|-----------------------------------------------|--------------------------------|
| Table               | Department + all KPIs                         | Conditional formatting columns |
| Clustered Bar       | Avg Performance by Department                 | Benchmark line at 3.5          |
| Bar Chart           | Overtime % by Department                      |                                |
| Gauge               | Overall Satisfaction vs target (4.0)          |                                |

### Page 4 — Flight Risk Monitor
| Visual              | Fields                                        | Notes                          |
|---------------------|-----------------------------------------------|--------------------------------|
| Table               | Employee, Dept, Satisfaction, OT, Risk Score  | From flight_risk_scores.xlsx   |
| Bar Chart           | Risk Tier Count (High/Medium/Low)             | Color: Red/Amber/Green         |
| Treemap             | High-Risk employees by Department             |                                |

---

## Step 5: Slicers (Add to All Pages)

- **Department** — Dropdown or Tile slicer
- **JobLevel** — Tile slicer
- **Gender** — Tile slicer  
- **WorkMode** — Tile slicer (Remote / Hybrid / On-site)
- **OverTime** — Toggle (Yes / No)
- **Date Range** — HireDate range slicer

---

## Step 6: Conditional Formatting Rules

### Attrition Rate Column in Tables:
- Red background if > 20%
- Amber background if 14%–20%
- Green background if < 14%

### Satisfaction Score:
- Red font if avg < 2.5
- Amber if 2.5–3.5
- Green if > 3.5

---

## Step 7: Publish to Power BI Service

1. **File → Publish → To Power BI**
2. Select your workspace
3. In Power BI Service: **Schedule Refresh** if connected to live data
4. Share dashboard link with stakeholders
5. Set up **Data Alerts** on Attrition Rate KPI card

---

## Connecting to SQL Server (Alternative Data Source)

Instead of Excel, you can connect directly to SQL Server:

1. **Get Data → SQL Server**
2. Server: `your-server-name`
3. Database: `HR_Analytics`
4. Use **Import** mode for best performance
5. Paste queries from `sql/hr_analytics_queries.sql` as custom SQL

```sql
-- Custom SQL for Power BI Direct Query
SELECT Department, JobLevel, Gender, WorkMode, OverTime,
       Attrition, PerformanceScore, SatisfactionScore,
       Salary, Tenure_Years,
       CASE WHEN Attrition='Yes' THEN 1 ELSE 0 END AS Attrition_Flag
FROM dbo.Employee_Data
```

---

## Tips for Best Dashboard Performance

- Use **Import mode** over Direct Query for datasets < 1GB
- Create a **Date Table** for proper time intelligence DAX
- Use **Bookmarks** to create navigation buttons between pages
- Enable **Row-Level Security (RLS)** if managers should only see their dept
- Export visuals as PNG for PowerPoint presentations using **Export → Image**
