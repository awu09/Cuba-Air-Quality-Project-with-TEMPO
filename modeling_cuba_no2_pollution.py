# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 22:13:39 2026

@author: jedia
"""

"""
Cuba October 2024 Blackout — Advanced NO2 Analysis
====================================================
Five models, each self-contained in its own function.
Run all: run_all_models(result_df, gdf)
Or run individually: model_did(df), model_glm(df), etc.

Requirements:
    pip install pysal mgwr scikit-learn scipy statsmodels geopandas matplotlib
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import geopandas as gpd
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# SHARED DATA PREP — call this first, returns df ready for all models
# =============================================================================

FACILITIES = [
    {"municipality": "Mariel",               "type": "Thermoelectric",  "capacity_mw": 270},
    {"municipality": "Regla",                "type": "Thermoelectric",  "capacity_mw": 150},
    {"municipality": "La Habana Del Este",   "type": "Thermoelectric",  "capacity_mw": 300},
    {"municipality": "Santa Cruz del Norte", "type": "Thermoelectric",  "capacity_mw": 400},
    {"municipality": "Matanzas",             "type": "Thermoelectric",  "capacity_mw": 330},
    {"municipality": "Cienfuegos",           "type": "Thermoelectric",  "capacity_mw": 316},
    {"municipality": "Nuevitas",             "type": "Thermoelectric",  "capacity_mw": 375},
    {"municipality": "Frank País",           "type": "Thermoelectric",  "capacity_mw": 480},
    {"municipality": "Santiago de Cuba",     "type": "Thermoelectric",  "capacity_mw": 380},
    {"municipality": "Cerro",                "type": "Dist. Generation","capacity_mw":  80},
    {"municipality": "Diez De Octubre",      "type": "Dist. Generation","capacity_mw":  80},
    {"municipality": "Marianao",             "type": "Dist. Generation","capacity_mw":  60},
    {"municipality": "La Lisa",              "type": "Dist. Generation","capacity_mw":  50},
    {"municipality": "Centro Habana",        "type": "Dist. Generation","capacity_mw":  50},
    {"municipality": "La Habana Vieja",      "type": "Dist. Generation","capacity_mw":  40},
    {"municipality": "Plaza de la Revolución","type":"Dist. Generation","capacity_mw":  40},
    {"municipality": "Boyeros",              "type": "Dist. Generation","capacity_mw":  35},
    {"municipality": "Arroyo Naranjo",       "type": "Dist. Generation","capacity_mw":  30},
    {"municipality": "La Habana Del Este",   "type": "Oil Refinery",    "capacity_mw": 200},
    {"municipality": "Cienfuegos",           "type": "Oil Refinery",    "capacity_mw": 130},
    {"municipality": "Santiago de Cuba",     "type": "Oil Refinery",    "capacity_mw":  30},
    {"municipality": "Moa",                  "type": "Nickel/Cobalt",   "capacity_mw": 250},
    {"municipality": "Mayarí",               "type": "Nickel/Cobalt",   "capacity_mw": 150},
    {"municipality": "Holguín",              "type": "Nickel/Cobalt",   "capacity_mw": 150},
    {"municipality": "Mariel",               "type": "Cement Plant",    "capacity_mw":  80},
    {"municipality": "Cienfuegos",           "type": "Cement Plant",    "capacity_mw":  80},
    {"municipality": "Santiago de Cuba",     "type": "Cement Plant",    "capacity_mw":  35},
    {"municipality": "Nuevitas",             "type": "Cement Plant",    "capacity_mw":  15},
    {"municipality": "Mariel",               "type": "Industrial Port", "capacity_mw": 100},
    {"municipality": "La Habana Vieja",      "type": "Industrial Port", "capacity_mw":  60},
    {"municipality": "Santiago de Cuba",     "type": "Industrial Port", "capacity_mw":  40},
    {"municipality": "Cienfuegos",           "type": "Industrial Port", "capacity_mw":  30},
    {"municipality": "Nuevitas",             "type": "Industrial Port", "capacity_mw":  25},
    {"municipality": "Moa",                  "type": "Industrial Port", "capacity_mw":  20},
    {"municipality": "La Habana Del Este",   "type": "Oil Production",  "capacity_mw":  60},
    {"municipality": "Santa Cruz del Norte", "type": "Oil Production",  "capacity_mw":  40},
    {"municipality": "Cárdenas",             "type": "Oil Production",  "capacity_mw":  30},
]

POP = {
    "Alquízar": 30364, "Artemisa": 82873, "Bahía Honda": 43483,
    "Bauta": 47628, "Caimito": 39792, "Candelaria": 20492,
    "Guanajay": 27784, "Gaira De Melena": 38907, "Mariel": 44480,
    "San Antonio de los Baños": 48197, "San Cristóbal": 70631,
    "Camagüey": 323309, "Carlos Manuel de Céspedes": 24488,
    "Esmeralda": 30206, "Florida": 71854, "Guáimaro": 39118,
    "Jimaguayú": 20680, "Minas": 37667, "Najasa": 15816,
    "Nuevitas": 61625, "Santa Cruz del Sur": 45710,
    "Sibanicú": 30937, "Sierra de Cubitas": 18704, "Vertientes": 51791,
    "Baraguá": 32538, "Bolivia": 15876, "Chambas": 38396,
    "Ciego De Ávila": 147745, "Ciro Redondo": 29896, "Florencia": 19484,
    "Majagua": 25800, "Morón": 66287, "Primero de  Enero": 23361,
    "Venezuela": 26671,
    "Abreus": 30906, "Aguada De Pasajeros": 32159, "Cienfuegos": 171946,
    "Cruces": 30941, "Cumanayagua": 48962, "Lajas": 21999,
    "Palmira": 32939, "Rodas": 34376,
    "Arroyo Naranjo": 200451, "Boyeros": 188217, "Centro Habana": 140234,
    "Cerro": 122999, "Cotorro": 77066, "Diez De Octubre": 206052,
    "Guanabacoa": 115180, "La Habana Del Este": 174493,
    "La Habana Vieja": 87772, "La Lisa": 136231, "Marianao": 134529,
    "Playa": 179647, "Plaza de la Revolución": 147789,
    "Regla": 42420, "San Miguel del Padrón": 153066,
    "Bartolomé Masó": 50734, "Bayamo": 235107, "Buey Arriba": 32010,
    "Campechuela": 44994, "Cauto Cristo": 20461, "Guisa": 48335,
    "Jiguaní": 60573, "Manzanillo": 130616, "Media Luna": 34226,
    "Niquero": 42878, "Pilón": 30067, "Rio Cauto": 47189, "Yara": 57190,
    "Baracoa": 81968, "Caimanera": 11091, "El Salvador": 43094,
    "Guantánamo": 228436, "Imías": 21309, "Maisí": 28333,
    "Manuel Tames": 39365, "Niceto Pérez": 16949,
    "San Antonio del Sur": 25804, "Yateras": 19079,
    "Antilla": 12415, "Banes": 79856, "Cacocum": 41558,
    "Calixto García": 55622, "Cueto": 32999, "Frank País": 24334,
    "Gibara": 71991, "Holguín": 346195, "Mayarí": 102354,
    "Moa": 75020, "Rafael Freyre": 52699, "Sagua de Tánamo": 48213,
    "Urbano Noris": 41116, "Isla de la Juventud": 84751,
    "Amancio Rodriguez": 38957, "Colombia": 32612,
    "Jesús Menéndez": 49205, "Jobabo": 37948, "Las Tunas": 132063,
    "Majibacoa": 41524, "Manatí": 46488, "Puerto Padre": 65818,
    "Cárdenas": 136095, "Calimete": 29023, "Ciénaga de Zapata": 12390,
    "Colón": 82073, "Jagüey Grande": 56813, "Jovellanos": 63278,
    "Limonar": 36073, "Los Arabos": 32076, "Martí": 29777,
    "Matanzas": 147235, "Pedro Betancourt": 38067, "Perico": 36500,
    "Unión de Reyes": 49327, "Batabanó": 27441, "Bejucal": 36267,
    "Jaruco": 34673, "Madruga": 29340, "Melena del Sur": 38065,
    "Nueva Paz": 42521, "Quivicán": 30134,
    "San José de las Lajas": 90876, "San Nicolás": 28867,
    "Santa Cruz del Norte": 56398,
    "Consolación del Sur": 87076, "Guane": 60497, "La Palma": 51001,
    "Los Palacios": 58040, "Mantua": 30319, "Minas De Matahambre": 35226,
    "Pinar del Río": 186895, "San Juan y Martínez": 48524,
    "San Luís": 57539, "Sandino": 47413, "Viñales": 28734,
    "Cabaiguán": 71827, "Fomento": 43753, "Jatibonico": 53617,
    "La Sierpe": 26813, "Sancti Spíritus": 97859, "Taguasco": 40097,
    "Trinidad": 73749, "Yaguajay": 55225,
    "Contramaestre": 66832, "Guamá": 40440, "Mella": 55076,
    "Palma Soriano": 84688, "Santiago de Cuba": 494337,
    "Segundo Frente": 38151, "Songo - La Maya": 72141,
    "Tercer Frente": 36621,
    "Caibarién": 43208, "Camajuaní": 60832, "Cifuentes": 35068,
    "Corralillo": 28780, "Encrucijada": 33065, "Manicaragua": 79396,
    "Placetas": 77042, "Quemado de Güines": 34019, "Ranchuelo": 57036,
    "Remedios": 48006, "Sagua La Grande": 57700, "Santa Clara": 241769,
    "Santo Domingo": 61213, "Boguano": 35000, "Base Naval": 11091,
    "Gaines": 20000,
}


def prepare_data(result_df, shapefile_path=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Merge NO2 data with population, facilities, and geometry."""
    df_fac = pd.DataFrame(FACILITIES)
    fac_agg = df_fac.groupby('municipality').agg(
        facility_count=('type', 'count'),
        total_capacity_mw=('capacity_mw', 'sum')
    ).reset_index()

    df = result_df.copy()
    df['population'] = df['region'].map(POP)

    # Load shapefile for geometry and area
    gdf = gpd.read_file(shapefile_path)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    gdf['area_km2']  = gdf['st_area_sh'] * 12321
    gdf['centroid_x'] = gdf.geometry.centroid.x
    gdf['centroid_y'] = gdf.geometry.centroid.y

    df = df.merge(gdf[['adm2nm','area_km2','centroid_x','centroid_y','geometry']],
                  left_on='region', right_on='adm2nm', how='left')
    df = df.merge(fac_agg, left_on='region', right_on='municipality', how='left')
    df['facility_count']    = df['facility_count'].fillna(0)
    df['total_capacity_mw'] = df['total_capacity_mw'].fillna(0)
    df['pop_density']       = df['population'] / df['area_km2']
    df['has_tpp']           = (df['total_capacity_mw'] > 200).astype(int)

    SCALE = 1e15
    df['b'] = df['no2_before'] / SCALE
    df['d'] = df['no2_during'] / SCALE
    df['a'] = df['no2_after']  / SCALE
    df['pct_drop'] = (df['no2_during'] - df['no2_before']) / df['no2_before'] * 100
    df['pct_rec']  = (df['no2_after']  - df['no2_during']) / df['no2_during'] * 100

    df = df.dropna(subset=['b','d','a','population','area_km2'])
    print(f"Data prepared: {len(df)} municipalities")
    return df


# =============================================================================
# MODEL 1 — DIFFERENCE-IN-DIFFERENCES (DiD)
# =============================================================================
def model_did(df):
    import statsmodels.formula.api as smf

    print("\n" + "="*60)
    print("MODEL 1: Difference-in-Differences (DiD)")
    print("="*60)

    # Treatment = has at least one confirmed major industrial facility
    df = df.copy()
    df['high_industrial'] = (df['total_capacity_mw'] > 0).astype(int)
    n_treat = df['high_industrial'].sum()
    n_ctrl  = len(df) - n_treat
    print(f"Treatment (has facility): {n_treat} municipalities")
    print(f"Control   (no facility):  {n_ctrl} municipalities")

    # Reshape to long panel
    rows = []
    for _, row in df.iterrows():
        for period, no2_val, period_code in [
            ('before', row['b'], 0),
            ('during', row['d'], 1),
            ('after',  row['a'], 2),
        ]:
            rows.append({
                'region':          row['region'],
                'no2':             no2_val,
                'period':          period,
                'period_code':     period_code,
                'during':          int(period == 'during'),
                'after':           int(period == 'after'),
                'high_industrial': row['high_industrial'],
                'log_pop':         np.log10(row['population'] + 1),
            })
    panel = pd.DataFrame(rows)

    # Verify both groups exist
    print(f"\nPanel group counts:")
    print(panel.groupby(['period','high_industrial'])['no2'].count())

    model = smf.ols(
        'no2 ~ during + after + high_industrial '
        '+ during:high_industrial + after:high_industrial '
        '+ log_pop',
        data=panel
    ).fit(cov_type='cluster', cov_kwds={'groups': panel['region']})

    print(model.summary())

    # ── Plot DiD means ──────────────────────────────────────────────────────
    means = panel.groupby(['period_code','high_industrial'])['no2'].mean().unstack()
    print("\nMeans table:")
    print(means)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('white')

    C_LOW  = '#888780'
    C_HIGH = '#2166ac'

    for col, label, color in [
        (0, f'Low industrial (no facility, n={n_ctrl})',  C_LOW),
        (1, f'High industrial (has facility, n={n_treat})', C_HIGH),
    ]:
        if col not in means.columns:
            print(f"Warning: group {col} not in means — skipping")
            continue
        vals = [means.loc[p, col] for p in [0, 1, 2]]
        ax1.plot([0,1,2], vals, 'o-', color=color, linewidth=2.2,
                 markersize=8, label=label)
        for i, v in enumerate(vals):
            ax1.text(i, v + 0.03, f"{v:.2f}", ha='center',
                     fontsize=9, color=color, fontweight='bold')

    ax1.axvspan(0.5, 1.5, color='#ffeedd', alpha=0.5, label='Blackout period')
    ax1.set_xticks([0,1,2])
    ax1.set_xticklabels(['Before', 'During', 'After'], fontsize=11)
    ax1.set_ylabel("Mean NO₂ (×10¹⁵ molecules/cm²)", fontsize=11)
    ax1.set_title("DiD: Mean NO₂ by industrial group & period", fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.2)

    # Coefficient plot
    coefs = model.params
    cis   = model.conf_int()
    interest = ['during', 'after', 'high_industrial',
                'during:high_industrial', 'after:high_industrial']
    coef_labels = {
        'during':                  'Blackout period\n(all municipalities)',
        'after':                   'Post-blackout\n(all municipalities)',
        'high_industrial':         'Has facility\n(baseline difference)',
        'during:high_industrial':  'DiD: Blackout × Facility ← KEY',
        'after:high_industrial':   'DiD: Recovery × Facility ← KEY',
    }

    y_pos = np.arange(len(interest))
    for i, term in enumerate(interest):
        if term not in coefs:
            continue
        c  = coefs[term]
        lo = cis.loc[term, 0]
        hi = cis.loc[term, 1]
        is_key = 'KEY' in coef_labels[term]
        color  = ('#8B0000' if c < 0 else '#0d4f8c') if is_key \
                 else ('#d6604d' if c < 0 else '#2166ac')
        ax2.barh(i, c, height=0.5, color=color, alpha=0.8, zorder=3)
        ax2.plot([lo, hi], [i, i], 'k-', linewidth=2, zorder=4)
        ax2.plot([lo, lo, hi, hi], [i-0.1, i+0.1, i-0.1, i+0.1],
                 'k-', linewidth=1.5, zorder=5)
        pval = model.pvalues[term]
        sig  = '***' if pval < 0.001 else '**' if pval < 0.01 \
               else '*' if pval < 0.05 else 'ns'
        ax2.text(max(abs(hi), abs(c)) * np.sign(c) + 0.02 * np.sign(c) + 0.01,
                 i, f"p={pval:.3f} {sig}", va='center', fontsize=8.5)

    ax2.axvline(0, color='black', linewidth=0.8)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([coef_labels[t] for t in interest
                          if t in coefs], fontsize=9)
    ax2.set_xlabel("Coefficient (×10¹⁵ molecules/cm²)", fontsize=11)
    ax2.set_title("DiD regression coefficients\n(95% CI, clustered SE)", fontsize=12)
    ax2.grid(axis='x', alpha=0.2)

    fig.suptitle("Difference-in-Differences — Cuba Blackout NO₂ Effect",
                 fontsize=13, y=1.01)
    plt.tight_layout()
    plt.show()
    return model, panel

# =============================================================================
# MODEL 2 — NEGATIVE BINOMIAL GLM
# =============================================================================
def model_glm(df):
    """
    Negative binomial GLM with log link.
    Models NO2 (scaled to integer counts) as a function of
    industrial capacity, population density, and period.
    More appropriate than OLS for right-skewed count-like data.
    """
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    print("\n" + "="*60)
    print("MODEL 2: Negative Binomial GLM (log link)")
    print("="*60)

    # Scale NO2 to integer counts for NB model (molecules/cm² × 1e-13)
    df = df.copy()
    df['no2_count_b'] = (df['no2_before'] / 1e13).round().astype(int)
    df['no2_count_d'] = (df['no2_during'] / 1e13).round().astype(int)
    df['no2_count_a'] = (df['no2_after']  / 1e13).round().astype(int)
    df['log_cap']     = np.log10(df['total_capacity_mw'] + 1)
    df['log_pop_den'] = np.log10(df['pop_density'] + 1)

    results = {}
    fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=False)
    fig.patch.set_facecolor('white')

    for ax, (period, ycol, title) in zip(axes, [
        ('before', 'no2_count_b', 'Before blackout'),
        ('during', 'no2_count_d', 'During blackout'),
        ('after',  'no2_count_a', 'After blackout'),
    ]):
        model = smf.glm(
            f'{ycol} ~ log_cap + log_pop_den',
            data=df,
            family=sm.families.NegativeBinomial()
        ).fit()
        results[period] = model
        print(f"\n--- {title} ---")
        print(model.summary().tables[1])

        # Fitted vs actual
        fitted = model.fittedvalues * 1e13 / 1e15
        actual = df[ycol] * 1e13 / 1e15

        ax.scatter(fitted, actual, alpha=0.4, s=30, color='#2166ac',
                   edgecolors='none', label='Municipalities')
        lim = max(fitted.max(), actual.max()) * 1.05
        ax.plot([0, lim], [0, lim], 'r--', linewidth=1.2, label='Perfect fit')

        # Highlight top industrial municipalities
        top_ind = df.nlargest(8, 'total_capacity_mw')
        for _, row in top_ind.iterrows():
            idx = row.name
            ax.annotate(row['region'].split()[0],
                        xy=(fitted[idx], actual[idx]),
                        fontsize=6.5, color='#8B0000', alpha=0.8)

        r2 = np.corrcoef(fitted, actual)[0,1]**2
        ax.set_title(f"{title}\nPseudo-R² (corr²) = {r2:.3f}", fontsize=11)
        ax.set_xlabel("Fitted NO₂ (×10¹⁵)", fontsize=10)
        ax.set_ylabel("Actual NO₂ (×10¹⁵)", fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.2)

    fig.suptitle("Negative Binomial GLM — Fitted vs. Actual NO₂\n"
                 "Predictors: log(industrial capacity MW), log(population density)",
                 fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()
    return results


# =============================================================================
# MODEL 3 — GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)
# =============================================================================
def model_gwr(df):
    """
    GWR: fits a local regression at each municipality, allowing coefficients
    to vary spatially. Shows WHERE population/capacity predicts NO2 well.
    """
    try:
        from mgwr.gwr import GWR
        from mgwr.sel_bw import Sel_BW
    except ImportError:
        print("mgwr not installed. Run: pip install mgwr")
        return None

    print("\n" + "="*60)
    print("MODEL 3: Geographically Weighted Regression (GWR)")
    print("="*60)

    df = df.copy().dropna(subset=['centroid_x','centroid_y'])
    coords = list(zip(df['centroid_x'], df['centroid_y']))
    y  = df['b'].values.reshape(-1, 1)
    X  = np.column_stack([
        np.log10(df['total_capacity_mw'] + 1),
        np.log10(df['pop_density'] + 1),
    ])

    # Select optimal bandwidth
    selector = Sel_BW(coords, y, X)
    bw = selector.search(bw_min=10)
    print(f"Optimal bandwidth: {bw:.1f} municipalities")

    model = GWR(coords, y, X, bw).fit()
    print(f"Global R²: {model.R2:.3f}")
    print(f"AICc: {model.aicc:.1f}")

    # Map the local R² and capacity coefficient
    df['local_r2']      = model.localR2
    df['coef_capacity'] = model.params[:, 1]
    df['coef_popden']   = model.params[:, 2]

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.patch.set_facecolor('white')

    for ax, col, title, cmap in [
        (axes[0], 'local_r2',      'Local R²\n(how well model fits locally)',  'YlOrRd'),
        (axes[1], 'coef_capacity', 'Local coeff: Industrial capacity\n(effect on NO₂)', 'RdBu_r'),
        (axes[2], 'coef_popden',   'Local coeff: Population density\n(effect on NO₂)',  'RdBu_r'),
    ]:
        gdf_plot = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
        gdf_plot.plot(column=col, cmap=cmap, ax=ax, legend=True,
                      legend_kwds={'shrink': 0.6, 'label': col},
                      edgecolor='gray', linewidth=0.3)
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
        ax.set_aspect('equal')

    fig.suptitle(f"Model 3: Geographically Weighted Regression (GWR)\n"
                 f"Global R²={model.R2:.3f}  |  Bandwidth={bw:.0f} municipalities  |  "
                 f"Pre-blackout NO₂ ~ industrial capacity + pop. density",
                 fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()
    return model, df


# =============================================================================
# MODEL 4 — RANDOM FOREST FEATURE IMPORTANCE
# =============================================================================
def model_rf(df):
    """
    Random forest regression predicting NO2 drop % from municipal features.
    Feature importance reveals what best predicts the blackout response.
    """
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler

    print("\n" + "="*60)
    print("MODEL 4: Random Forest / Gradient Boosting Feature Importance")
    print("="*60)

    df = df.copy().dropna(subset=['population','area_km2','pct_drop','pct_rec'])

    features = {
        'log_capacity_mw':  np.log10(df['total_capacity_mw'] + 1),
        'log_population':   np.log10(df['population'] + 1),
        'log_pop_density':  np.log10(df['pop_density'] + 1),
        'has_tpp':          df['has_tpp'],
        'facility_count':   df['facility_count'],
        'log_area_km2':     np.log10(df['area_km2'] + 1),
        'longitude':        df['centroid_x'],
        'latitude':         df['centroid_y'],
        'no2_baseline':     df['b'],
    }
    feature_names = list(features.keys())
    X = np.column_stack(list(features.values()))

    targets = {
        '% NO₂ drop\n(before→during)': df['pct_drop'].values,
        '% NO₂ recovery\n(during→after)': df['pct_rec'].values,
        'NO₂ before\n(baseline level)': df['b'].values,
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.patch.set_facecolor('white')

    for ax, (target_name, y) in zip(axes, targets.items()):
        rf = RandomForestRegressor(n_estimators=500, max_depth=5,
                                   random_state=42, n_jobs=-1)
        rf.fit(X, y)
        cv_r2 = cross_val_score(rf, X, y, cv=5, scoring='r2').mean()

        # Permutation importance (more reliable than impurity-based)
        perm = permutation_importance(rf, X, y, n_repeats=30, random_state=42)
        importance = perm.importances_mean
        importance_std = perm.importances_std

        # Sort
        order = np.argsort(importance)
        colors_bar = ['#d6604d' if importance[i] > 0.01 else '#cccccc'
                      for i in order]

        ax.barh(np.arange(len(feature_names)),
                importance[order], height=0.6,
                color=colors_bar, alpha=0.85, zorder=3)
        ax.errorbar(importance[order], np.arange(len(feature_names)),
                    xerr=importance_std[order],
                    fmt='none', color='black', linewidth=1.2, zorder=4)
        ax.set_yticks(np.arange(len(feature_names)))
        ax.set_yticklabels([feature_names[i] for i in order], fontsize=9)
        ax.set_xlabel("Permutation importance\n(mean decrease in R²)", fontsize=10)
        ax.set_title(f"Predicting: {target_name}\nCV R²={cv_r2:.3f}",
                     fontsize=11, pad=8)
        ax.axvline(0, color='black', linewidth=0.6)
        ax.grid(axis='x', alpha=0.2)

        print(f"\nTarget: {target_name.replace(chr(10),' ')}")
        print(f"  CV R² = {cv_r2:.3f}")
        for i in np.argsort(-importance):
            print(f"  {feature_names[i]:22s}  importance={importance[i]:.4f} "
                  f"± {importance_std[i]:.4f}")

    fig.suptitle("Model 4: Random Forest — Permutation Feature Importance\n"
                 "What best predicts NO₂ level, drop, and recovery during the Cuba blackout?",
                 fontsize=12, y=1.02)
    plt.tight_layout()
    plt.show()
    return rf


# =============================================================================
# MODEL 5 — K-MEANS CLUSTERING ON NO2 RESPONSE PROFILE
# =============================================================================
def model_cluster(df):
    """
    K-means clustering on the (before, during, after) NO2 profile.
    Finds natural groups of municipalities with similar blackout responses.
    """
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score

    print("\n" + "="*60)
    print("MODEL 5: K-Means Clustering on NO₂ Response Profile")
    print("="*60)

    df = df.copy()
    X_raw = df[['b','d','a']].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_raw)

    # Find optimal k via silhouette score
    sil_scores = []
    K_range = range(2, 9)
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = km.fit_predict(X_scaled)
        sil_scores.append(silhouette_score(X_scaled, labels))
    best_k = K_range[np.argmax(sil_scores)]
    print(f"Best k by silhouette: {best_k}  (score={max(sil_scores):.3f})")

    km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
    df['cluster'] = km_final.fit_predict(X_scaled)

    # Characterize clusters
    cluster_means = df.groupby('cluster')[['b','d','a','pct_drop','pct_rec',
                                            'total_capacity_mw','population']].mean()
    print("\nCluster profiles:")
    print(cluster_means.round(3).to_string())

    # Assign descriptive names based on NO2 level and drop
    cluster_names = {}
    for c in range(best_k):
        b_val   = cluster_means.loc[c,'b']
        drop    = cluster_means.loc[c,'pct_drop']
        cap     = cluster_means.loc[c,'total_capacity_mw']
        if b_val > 3:
            cluster_names[c] = f"Cluster {c+1}: High-emission\nurban/industrial"
        elif cap > 100:
            cluster_names[c] = f"Cluster {c+1}: Industrial\nfacility"
        elif drop < -40:
            cluster_names[c] = f"Cluster {c+1}: High drop\n(grid-dependent)"
        else:
            cluster_names[c] = f"Cluster {c+1}: Rural\nbackground"

    CLUSTER_COLORS = ['#2166ac','#d6604d','#1a9850','#8B5CF6','#F59E0B',
                      '#EC4899','#06B6D4','#84CC16']

    fig = plt.figure(figsize=(18, 12))
    gs  = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.3)
    fig.patch.set_facecolor('white')

    # ── Top left: silhouette scores ──────────────────────────────────────────
    ax_sil = fig.add_subplot(gs[0, 0])
    ax_sil.plot(list(K_range), sil_scores, 'o-', color='#2166ac',
                linewidth=2, markersize=7)
    ax_sil.axvline(best_k, color='#d6604d', linestyle='--', linewidth=1.5,
                   label=f'Best k={best_k}')
    ax_sil.set_xlabel("Number of clusters (k)", fontsize=11)
    ax_sil.set_ylabel("Silhouette score", fontsize=11)
    ax_sil.set_title("Optimal k selection", fontsize=11)
    ax_sil.legend(); ax_sil.grid(alpha=0.2)

    # ── Top center: cluster profiles (parallel coordinates style) ────────────
    ax_prof = fig.add_subplot(gs[0, 1])
    periods = ['Before', 'During', 'After']
    for c in range(best_k):
        vals = [cluster_means.loc[c,'b'],
                cluster_means.loc[c,'d'],
                cluster_means.loc[c,'a']]
        n = (df['cluster'] == c).sum()
        ax_prof.plot([0,1,2], vals, 'o-',
                     color=CLUSTER_COLORS[c], linewidth=2.2, markersize=8,
                     label=f"{cluster_names[c].split(chr(10))[0]} (n={n})")
    ax_prof.axvspan(0.5, 1.5, color='#ffeedd', alpha=0.4)
    ax_prof.set_xticks([0,1,2])
    ax_prof.set_xticklabels(periods, fontsize=11)
    ax_prof.set_ylabel("Mean NO₂ (×10¹⁵ molecules/cm²)", fontsize=10)
    ax_prof.set_title("Cluster NO₂ profiles\n(shaded = blackout period)", fontsize=11)
    ax_prof.legend(fontsize=8); ax_prof.grid(alpha=0.2)

    # ── Top right: % drop vs % recovery scatter, colored by cluster ──────────
    ax_sc = fig.add_subplot(gs[0, 2])
    for c in range(best_k):
        mask = df['cluster'] == c
        ax_sc.scatter(df.loc[mask,'pct_drop'], df.loc[mask,'pct_rec'],
                      color=CLUSTER_COLORS[c], s=40, alpha=0.7,
                      edgecolors='none', zorder=3,
                      label=cluster_names[c].split('\n')[0])
    ax_sc.axhline(0, color='black', linewidth=0.6)
    ax_sc.axvline(0, color='black', linewidth=0.6)
    ax_sc.set_xlabel("% change during blackout\n(before→during)", fontsize=10)
    ax_sc.set_ylabel("% recovery after blackout\n(during→after)", fontsize=10)
    ax_sc.set_title("Drop vs. Recovery by cluster", fontsize=11)
    ax_sc.set_xlim(-110, 50); ax_sc.set_ylim(-50, 260)
    ax_sc.legend(fontsize=8); ax_sc.grid(alpha=0.2)

    # ── Bottom: spatial map of clusters ──────────────────────────────────────
    ax_map = fig.add_subplot(gs[1, :])
    gdf_plot = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326')
    gdf_plot['color'] = gdf_plot['cluster'].map(
        lambda c: CLUSTER_COLORS[c] if c < len(CLUSTER_COLORS) else 'gray')
    gdf_plot.plot(color=gdf_plot['color'], ax=ax_map,
                  edgecolor='white', linewidth=0.4)
    ax_map.set_title("Spatial distribution of NO₂ response clusters", fontsize=12)
    ax_map.set_xlabel("Longitude"); ax_map.set_ylabel("Latitude")

    # Cluster legend
    legend_patches = [
        mpatches.Patch(color=CLUSTER_COLORS[c],
                       label=f"{cluster_names[c].replace(chr(10),' ')}  "
                             f"(n={(df['cluster']==c).sum()})")
        for c in range(best_k)
    ]
    ax_map.legend(handles=legend_patches, fontsize=9,
                  loc='lower left', framealpha=0.93)

    fig.suptitle("Model 5: K-Means Clustering on NO₂ Before/During/After Profile\n"
                 "Cuba October 2024 Blackout",
                 fontsize=13, y=1.01)
    plt.show()
    return km_final, df


# =============================================================================
# RUN ALL MODELS
# =============================================================================
def run_all_models(result_df,
                   shapefile_path=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    df = prepare_data(result_df, shapefile_path)

    print("\n>>> Running Model 1: Difference-in-Differences")
    m1, panel = model_did(df)

    print("\n>>> Running Model 2: Negative Binomial GLM")
    m2 = model_glm(df)

    print("\n>>> Running Model 3: Geographically Weighted Regression")
    m3 = model_gwr(df)

    print("\n>>> Running Model 4: Random Forest Feature Importance")
    m4 = model_rf(df)

    print("\n>>> Running Model 5: K-Means Clustering")
    m5, df_clustered = model_cluster(df)

    print("\n" + "="*60)
    print("All 5 models complete.")
    print("Output files: model1_did.png, model2_glm.png, model3_gwr.png,")
    print("              model4_rf.png, model5_cluster.png")
    return df, m1, m2, m3, m4, m5, df_clustered


# ── Entry point ───────────────────────────────────────────────────────────────
# Run all:
# df, *models = run_all_models(result_df)
#
# Or run individually after preparing data:
df = prepare_data(result_df)
model_did(df)
model_glm(df)
model_gwr(df)
model_rf(df)
model_cluster(df)

#use improve cluster and random forest models