# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 21:28:24 2026

@author: jedia
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import cross_val_score

features = {
    'log_capacity_mw':  np.log10(df['total_capacity_mw'] + 1),
    'log_population':   np.log10(df['population'] + 1),
    'log_pop_density':  np.log10(df['pop_density'] + 1),
    'has_tpp':          df['has_tpp'],
    'facility_count':   df['facility_count'],
    'log_area_km2':     np.log10(df['area_km2'] + 1),
    'longitude':        df['centroid_x'],
    'latitude':         df['centroid_y'],
}
feature_names = list(features.keys())
X = np.column_stack(list(features.values()))

targets = [
    ('% NO₂ drop\n(before→during)',    df['pct_drop'].values, '#d6604d'),
    ('% NO₂ recovery\n(during→after)', df['pct_rec'].values,  '#1a9850'),
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('white')

for ax, (target_name, y, bar_color) in zip(axes, targets):
    rf = RandomForestRegressor(n_estimators=500, max_depth=5,
                               random_state=42, n_jobs=-1)
    rf.fit(X, y)
    cv_r2 = cross_val_score(rf, X, y, cv=5, scoring='r2').mean()

    perm = permutation_importance(rf, X, y, n_repeats=30, random_state=42)
    importance     = perm.importances_mean
    importance_std = perm.importances_std

    order = np.argsort(importance)
    colors_bar = [bar_color if importance[i] > 0.01 else '#cccccc'
                  for i in order]

    ax.barh(np.arange(len(feature_names)), importance[order],
            height=0.6, color=colors_bar, alpha=0.85, zorder=3)
    ax.errorbar(importance[order], np.arange(len(feature_names)),
                xerr=importance_std[order],
                fmt='none', color='black', linewidth=1.2, zorder=4)
    ax.set_yticks(np.arange(len(feature_names)))
    ax.set_yticklabels([feature_names[i] for i in order], fontsize=10)
    ax.set_xlabel("Permutation importance\n(mean decrease in R²)", fontsize=11)
    ax.set_title(f"Predicting: {target_name}\nCV R²={cv_r2:.3f}", fontsize=12)
    ax.axvline(0, color='black', linewidth=0.6)
    ax.grid(axis='x', alpha=0.2)

fig.suptitle(
    "Random Forest — What predicts NO₂ response to the Cuba blackout?\n"
    "Permutation feature importance",
    fontsize=12, y=1.02
)
plt.tight_layout()
# plt.savefig("model4_rf_v2.png", dpi=150, bbox_inches='tight')
plt.show()