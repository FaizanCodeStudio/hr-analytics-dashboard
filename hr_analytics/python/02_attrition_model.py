"""
HR Analytics — Attrition Prediction Model
==========================================
Trains a Random Forest classifier to predict employee attrition.
Run:  python python/02_attrition_model.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, roc_curve)
from sklearn.inspection import permutation_importance
import warnings
warnings.filterwarnings('ignore')

import os
os.makedirs('python/charts', exist_ok=True)

plt.rcParams.update({'font.family': 'sans-serif', 'axes.spines.top': False,
                     'axes.spines.right': False, 'figure.facecolor': 'white'})

# ── LOAD & PREPARE ────────────────────────────────────────────────────────────
df = pd.read_excel('data/HR_Analytics_Data.xlsx', sheet_name='Employee_Data')
df['Attrition_Flag'] = (df['Attrition'] == 'Yes').astype(int)

features = ['Age', 'Tenure_Years', 'Salary', 'PerformanceScore',
            'SatisfactionScore', 'TrainingHours', 'Department',
            'JobLevel', 'Gender', 'OverTime', 'WorkMode']

le = LabelEncoder()
df_model = df[features].copy()
cat_cols = ['Department', 'JobLevel', 'Gender', 'OverTime', 'WorkMode']
for col in cat_cols:
    df_model[col] = le.fit_transform(df_model[col].astype(str))

X = df_model.values
y = df['Attrition_Flag'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# ── TRAIN MODELS ──────────────────────────────────────────────────────────────
rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, class_weight='balanced')
gb = GradientBoostingClassifier(n_estimators=150, max_depth=4, learning_rate=0.1, random_state=42)

rf.fit(X_train, y_train)
gb.fit(X_train, y_train)

rf_probs = rf.predict_proba(X_test)[:, 1]
gb_probs = gb.predict_proba(X_test)[:, 1]
rf_preds = rf.predict(X_test)

print("=" * 55)
print("  MODEL PERFORMANCE SUMMARY")
print("=" * 55)
print(f"\n  Random Forest AUC:         {roc_auc_score(y_test, rf_probs):.4f}")
print(f"  Gradient Boosting AUC:     {roc_auc_score(y_test, gb_probs):.4f}")

cv_scores = cross_val_score(rf, X, y, cv=5, scoring='roc_auc')
print(f"  RF 5-Fold CV AUC:          {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

print("\n  Classification Report (Random Forest):")
print(classification_report(y_test, rf_preds, target_names=["Retained", "Attrited"]))

# ── FEATURE IMPORTANCE ────────────────────────────────────────────────────────
importances = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 5))
colors = ['#2E75B6' if v < importances.max()*0.5 else '#C00000' for v in importances.values]
bars = ax.barh(importances.index, importances.values * 100, color=colors, height=0.6, zorder=3)
ax.set_xlabel('Importance Score (%)', fontsize=11)
ax.set_title('Feature Importance — Random Forest Attrition Model',
             fontsize=13, fontweight='bold', pad=12)
ax.grid(axis='x', alpha=0.3)
for bar, val in zip(bars, importances.values):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f"{val*100:.1f}%", va='center', fontsize=9)
plt.tight_layout()
plt.savefig('python/charts/08_feature_importance.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

# ── ROC CURVE ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
for model, probs, label, color in [
    (rf, rf_probs, f"Random Forest (AUC={roc_auc_score(y_test, rf_probs):.3f})", '#2E75B6'),
    (gb, gb_probs, f"Gradient Boost (AUC={roc_auc_score(y_test, gb_probs):.3f})", '#C00000'),
]:
    fpr, tpr, _ = roc_curve(y_test, probs)
    ax.plot(fpr, tpr, label=label, linewidth=2, color=color)
ax.plot([0,1],[0,1], 'k--', alpha=0.4, label='Random classifier')
ax.set_xlabel('False Positive Rate', fontsize=11)
ax.set_ylabel('True Positive Rate', fontsize=11)
ax.set_title('ROC Curve — Attrition Prediction Models', fontsize=13, fontweight='bold', pad=12)
ax.legend(fontsize=10)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('python/charts/09_roc_curve.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

# ── FLIGHT RISK SCORING ───────────────────────────────────────────────────────
all_probs = rf.predict_proba(X)[:, 1]
df_risk = df[['EmployeeID', 'Department', 'JobTitle', 'JobLevel',
              'Salary', 'SatisfactionScore', 'PerformanceScore', 'Attrition']].copy()
df_risk['FlightRiskScore'] = np.round(all_probs * 100, 1)
df_risk['RiskTier'] = pd.cut(df_risk['FlightRiskScore'],
                              bins=[0, 30, 60, 100],
                              labels=['Low', 'Medium', 'High'])

print("\n  FLIGHT RISK DISTRIBUTION:")
risk_dist = df_risk['RiskTier'].value_counts()
for tier, count in risk_dist.items():
    pct = count / len(df_risk) * 100
    print(f"    {tier:<10} {count:>5,} employees  ({pct:.1f}%)")

print("\n  TOP 10 HIGH-RISK EMPLOYEES:")
top_risk = df_risk[df_risk['RiskTier']=='High'].sort_values('FlightRiskScore', ascending=False).head(10)
print(top_risk[['EmployeeID','Department','JobTitle','FlightRiskScore']].to_string(index=False))

df_risk.to_excel('python/flight_risk_scores.xlsx', index=False)
print("\n  Flight risk scores saved: python/flight_risk_scores.xlsx")

print("\n  Charts saved to: python/charts/")
print("=" * 55)
