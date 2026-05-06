"""
HR Analytics — Exploratory Data Analysis
=========================================
Run:  python python/01_eda_analysis.py
Output: python/eda_report.txt + python/charts/ (PNG files)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ────────────────────────────────────────────────────────────────────
DATA_PATH   = 'data/HR_Analytics_Data.xlsx'
CHARTS_DIR  = 'python/charts'
COLORS      = {'primary': '#2E75B6', 'danger': '#C00000', 'success': '#70AD47',
               'warning': '#FFC000', 'muted': '#7F7F7F'}

import os
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── LOAD ──────────────────────────────────────────────────────────────────────
df = pd.read_excel(DATA_PATH, sheet_name='Employee_Data')
df['HireDate'] = pd.to_datetime(df['HireDate'])
df['Attrition_Flag'] = (df['Attrition'] == 'Yes').astype(int)
print(f"Loaded {len(df):,} employee records\n")

# ── HELPER ───────────────────────────────────────────────────────────────────
def save_fig(name):
    path = f"{CHARTS_DIR}/{name}.png"
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved chart: {path}")

plt.rcParams.update({
    'font.family': 'sans-serif', 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.grid': True,
    'grid.alpha': 0.3, 'figure.facecolor': 'white'
})

# ── 1. ATTRITION BY DEPARTMENT ────────────────────────────────────────────────
print("Generating charts...")
dept_attr = (df.groupby('Department')['Attrition_Flag']
               .agg(['sum','count'])
               .assign(rate=lambda x: x['sum']/x['count'])
               .sort_values('rate', ascending=True))

fig, ax = plt.subplots(figsize=(10, 5))
colors = [COLORS['danger'] if r > 0.20 else COLORS['warning'] if r > 0.14 else COLORS['success']
          for r in dept_attr['rate']]
bars = ax.barh(dept_attr.index, dept_attr['rate']*100, color=colors, height=0.6, zorder=3)
ax.set_xlabel('Attrition Rate (%)', fontsize=11)
ax.set_title('Attrition Rate by Department', fontsize=14, fontweight='bold', pad=12)
ax.axvline(df['Attrition_Flag'].mean()*100, color='black', linestyle='--', alpha=0.5, label='Company avg')
for bar, (_, row) in zip(bars, dept_attr.iterrows()):
    ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2,
            f"{row['rate']*100:.1f}%  (n={row['count']})",
            va='center', fontsize=9)
ax.legend(fontsize=9)
save_fig('01_attrition_by_department')

# ── 2. ATTRITION BY JOB LEVEL ─────────────────────────────────────────────────
level_order = ['Junior','Mid','Senior','Lead','Manager','Director','VP']
level_attr = (df.groupby('JobLevel')['Attrition_Flag']
                .agg(['sum','count'])
                .assign(rate=lambda x: x['sum']/x['count'])
                .reindex(level_order))

fig, ax = plt.subplots(figsize=(10, 4))
bars = ax.bar(level_attr.index, level_attr['rate']*100,
              color=COLORS['primary'], alpha=0.85, zorder=3)
ax.set_ylabel('Attrition Rate (%)', fontsize=11)
ax.set_title('Attrition Rate by Job Level', fontsize=14, fontweight='bold', pad=12)
for bar, val in zip(bars, level_attr['rate']):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
            f"{val*100:.1f}%", ha='center', fontsize=9)
save_fig('02_attrition_by_level')

# ── 3. SALARY VS ATTRITION ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))
bins = [0, 50000, 70000, 90000, 110000, 140000, 300000]
labels = ['<50k', '50-70k', '70-90k', '90-110k', '110-140k', '140k+']
df['SalaryBand'] = pd.cut(df['Salary'], bins=bins, labels=labels)
sal_attr = df.groupby('SalaryBand', observed=True)['Attrition_Flag'].mean() * 100
ax.bar(sal_attr.index, sal_attr.values, color=COLORS['primary'], alpha=0.85, zorder=3)
ax.set_ylabel('Attrition Rate (%)', fontsize=11)
ax.set_xlabel('Salary Band', fontsize=11)
ax.set_title('Attrition Rate by Salary Band', fontsize=14, fontweight='bold', pad=12)
for i, (idx, val) in enumerate(sal_attr.items()):
    ax.text(i, val+0.2, f"{val:.1f}%", ha='center', fontsize=9)
save_fig('03_salary_vs_attrition')

# ── 4. SATISFACTION HEATMAP ───────────────────────────────────────────────────
pivot = pd.crosstab(df['SatisfactionScore'], df['PerformanceScore'],
                    values=df['Attrition_Flag'], aggfunc='mean') * 100

fig, ax = plt.subplots(figsize=(8, 5))
im = ax.imshow(pivot.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=40)
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels([f'Perf {c}' for c in pivot.columns])
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels([f'Sat {i}' for i in pivot.index])
ax.set_title('Attrition Rate Heatmap\nSatisfaction vs Performance Score', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax, label='Attrition Rate (%)')
for i in range(len(pivot.index)):
    for j in range(len(pivot.columns)):
        val = pivot.values[i, j]
        ax.text(j, i, f"{val:.1f}%", ha='center', va='center',
                fontsize=10, color='white' if val > 25 else 'black')
plt.tight_layout()
save_fig('04_satisfaction_performance_heatmap')

# ── 5. TENURE DISTRIBUTION ───────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, group, label, color in zip(
    axes, ['No', 'Yes'],
    ['Retained Employees', 'Attrited Employees'],
    [COLORS['success'], COLORS['danger']]
):
    data = df[df['Attrition']==group]['Tenure_Years']
    ax.hist(data, bins=20, color=color, alpha=0.8, edgecolor='white', zorder=3)
    ax.axvline(data.mean(), color='black', linestyle='--', label=f"Mean: {data.mean():.1f}yr")
    ax.set_title(label, fontsize=12, fontweight='bold')
    ax.set_xlabel('Tenure (Years)', fontsize=10)
    ax.set_ylabel('Count', fontsize=10)
    ax.legend(fontsize=9)
fig.suptitle('Tenure Distribution: Retained vs Attrited', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
save_fig('05_tenure_distribution')

# ── 6. EXIT REASONS PIE ───────────────────────────────────────────────────────
reasons = df[df['Attrition']=='Yes']['ExitReason'].value_counts()
fig, ax = plt.subplots(figsize=(9, 6))
wedge_colors = ['#2E75B6','#4472C4','#70AD47','#FFC000','#FF7F00','#C00000','#7030A0','#00B0F0']
wedges, texts, autotexts = ax.pie(
    reasons.values, labels=reasons.index, autopct='%1.1f%%',
    colors=wedge_colors[:len(reasons)], startangle=140,
    pctdistance=0.75, labeldistance=1.12,
    wedgeprops={'edgecolor':'white','linewidth':2}
)
for t in texts: t.set_fontsize(10)
for at in autotexts: at.set_fontsize(9); at.set_color('white'); at.set_fontweight('bold')
ax.set_title('Attrition by Exit Reason', fontsize=14, fontweight='bold', pad=20)
save_fig('06_exit_reasons')

# ── 7. OVERTIME IMPACT ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
ot_attr = df.groupby('OverTime')['Attrition_Flag'].mean() * 100
bars = ax.bar(['No Overtime','Overtime'], ot_attr.values,
              color=[COLORS['success'], COLORS['danger']], alpha=0.85, zorder=3, width=0.4)
ax.set_ylabel('Attrition Rate (%)', fontsize=11)
ax.set_title('Impact of Overtime on Attrition', fontsize=14, fontweight='bold', pad=12)
for bar, val in zip(bars, ot_attr.values):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
            f"{val:.1f}%", ha='center', fontweight='bold', fontsize=12)
save_fig('07_overtime_impact')

# ── STATISTICAL SUMMARY ───────────────────────────────────────────────────────
print("\n" + "="*55)
print("  HR ANALYTICS — KEY FINDINGS")
print("="*55)

total = len(df)
attrited = df['Attrition_Flag'].sum()
print(f"\n  Total Employees:     {total:>6,}")
print(f"  Attrited:            {attrited:>6,}")
print(f"  Overall Attrition:   {attrited/total*100:>6.1f}%")
print(f"  Avg Salary:          ${df['Salary'].mean():>10,.0f}")
print(f"  Avg Tenure:          {df['Tenure_Years'].mean():>6.1f} years")
print(f"  Avg Satisfaction:    {df['SatisfactionScore'].mean():>6.2f}/5.0")
print(f"  Avg Performance:     {df['PerformanceScore'].mean():>6.2f}/5.0")

print("\n  ATTRITION BY DEPT (Top 3 Highest):")
dept_attr_sorted = dept_attr.sort_values('rate', ascending=False)
for dept, row in dept_attr_sorted.head(3).iterrows():
    print(f"    {dept:<22} {row['rate']*100:.1f}%  ({int(row['sum'])} left)")

print("\n  OVERTIME IMPACT:")
ot = df.groupby('OverTime')['Attrition_Flag'].mean()
print(f"    With OT:    {ot.get('Yes', 0)*100:.1f}%")
print(f"    Without OT: {ot.get('No', 0)*100:.1f}%")

print("\n  SATISFACTION IMPACT:")
sat = df.groupby('SatisfactionScore')['Attrition_Flag'].mean()
print(f"    Score 1 (lowest): {sat.get(1, 0)*100:.1f}%")
print(f"    Score 5 (highest): {sat.get(5, 0)*100:.1f}%")

print("\n  Charts saved to:", CHARTS_DIR)
print("="*55)
