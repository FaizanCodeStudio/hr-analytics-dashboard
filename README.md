# 📊 HR Analytics Dashboard

An end-to-end **Data Analyst Portfolio Project** analyzing workforce 
attrition and department performance across 2,847 employees.

## 🛠️ Tools Used
| Tool     | Purpose                              |
|----------|--------------------------------------|
| Excel    | Data storage, pivot tables, KPI cards|
| Python   | EDA, visualizations, ML modeling     |
| SQL      | 12 production-ready queries          |
| Power BI | Interactive dashboard & reporting    |

## 📁 Project Structure
| Folder           | Contents                              |
|------------------|---------------------------------------|
| data/            | Excel dataset (2,847 employees)       |
| python/          | EDA script + ML attrition model       |
| python/charts/   | 9 analysis charts (PNG)               |
| sql/             | 12 SQL queries (SQL Server / PG)      |
| powerbi_guide/   | Full Power BI setup guide + DAX       |

## 🔍 Key Findings
- **Overall attrition rate: 16.4%**
- Sales dept highest risk at **27.7%** attrition
- Overtime employees are **1.8× more likely** to leave
- Low satisfaction (score ≤ 2) employees churn at **22.8%**
- Engineering is the benchmark dept with only **9% attrition**

## 🤖 ML Model
- Random Forest + Gradient Boosting classifiers
- AUC Score: **0.64**
- Outputs per-employee **flight risk scores** (High / Medium / Low)

## 🚀 How to Run
pip install pandas openpyxl matplotlib scikit-learn
python python/01_eda_analysis.py
python python/02_attrition_model.py
