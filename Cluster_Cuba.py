# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 21:42:41 2026

@author: jedia
"""

# Reload geometry from shapefile and re-attach to clustered df
import geopandas as gpd

shapefile_path = r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"
gdf_shapes = gpd.read_file(shapefile_path).to_crs(epsg=4326)
gdf_shapes = gdf_shapes[['adm2nm', 'geometry']].rename(columns={'adm2nm': 'region'})

# Re-run clustering on df (which already has b, d, a columns)
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

df_c = df.copy()
X_raw    = df_c[['b','d','a']].values
X_scaled = StandardScaler().fit_transform(X_raw)

# Find best k
sil = [silhouette_score(X_scaled, KMeans(n_clusters=k, random_state=42, n_init=20).fit_predict(X_scaled))
       for k in range(2, 9)]
best_k = range(2, 9)[np.argmax(sil)]
print(f"Best k={best_k}, silhouette={max(sil):.3f}")

km = KMeans(n_clusters=best_k, random_state=42, n_init=20)
df_c['cluster'] = km.fit_predict(X_scaled)

print("\nCluster profiles:")
print(df_c.groupby('cluster')[['b','d','a','pct_drop','pct_rec','total_capacity_mw','population']].mean().round(3))

# Attach geometry
df_geo = df_c.merge(gdf_shapes, on='region', how='left')
gdf_plot = gpd.GeoDataFrame(df_geo, geometry='geometry', crs='EPSG:4326')

# Plot
COLORS = ['#2166ac','#d6604d','#1a9850','#8B5CF6','#F59E0B']
cluster_means = df_c.groupby('cluster')[['b','d','a','pct_drop','pct_rec']].mean()

fig, (ax_map, ax_prof) = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor('white')

# Map
gdf_plot['color'] = gdf_plot['cluster'].map(lambda c: COLORS[c % len(COLORS)])
gdf_plot.plot(color=gdf_plot['color'], ax=ax_map,
              edgecolor='white', linewidth=0.4, missing_kwds={'color':'lightgray'})
ax_map.set_title("Spatial distribution of NO₂ response clusters", fontsize=12)
ax_map.set_xlabel("Longitude"); ax_map.set_ylabel("Latitude")

import matplotlib.patches as mpatches
legend_patches = [
    mpatches.Patch(color=COLORS[c],
                   label=f"Cluster {c+1}  (n={(df_c['cluster']==c).sum()})  "
                         f"drop={cluster_means.loc[c,'pct_drop']:.0f}%  "
                         f"rec={cluster_means.loc[c,'pct_rec']:.0f}%")
    for c in range(best_k)
]
ax_map.legend(handles=legend_patches, fontsize=8.5, loc='lower left', framealpha=0.93)

# Profile lines
for c in range(best_k):
    vals = [cluster_means.loc[c,'b'], cluster_means.loc[c,'d'], cluster_means.loc[c,'a']]
    n = (df_c['cluster']==c).sum()
    ax_prof.plot([0,1,2], vals, 'o-', color=COLORS[c], linewidth=2.2,
                 markersize=8, label=f"Cluster {c+1} (n={n})")
    for i, v in enumerate(vals):
        ax_prof.text(i, v+0.04, f"{v:.2f}", ha='center', fontsize=8,
                     color=COLORS[c], fontweight='bold')

ax_prof.axvspan(0.5, 1.5, color='#ffeedd', alpha=0.4)
ax_prof.set_xticks([0,1,2])
ax_prof.set_xticklabels(['Before','During','After'], fontsize=12)
ax_prof.set_ylabel("Mean NO₂ (×10¹⁵ molecules/cm²)", fontsize=11)
ax_prof.set_title("Cluster NO₂ profiles\n(shaded = blackout period)", fontsize=12)
ax_prof.legend(fontsize=9); ax_prof.grid(alpha=0.2); ax_prof.set_ylim(bottom=0)

fig.suptitle("K-Means Clustering — Cuba October 2024 Blackout NO₂ Response",
             fontsize=13, y=1.02)
plt.tight_layout()
# plt.savefig("model5_cluster_fixed.png", dpi=150, bbox_inches='tight')
plt.show()

#don't use this bottom part
df = prepare_data(result_df)
model_cluster(df)
