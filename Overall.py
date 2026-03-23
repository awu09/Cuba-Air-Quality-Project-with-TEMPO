# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:46:40 2025

@author: jedia
"""


#Provides a overall graph with areas of interest (four most populous region) in Cuba labeled
def plot_map1(data, longitude, latitude, f_name):
    """Plot Cuba-wide NO2 map with labeled regions - EXACT replica"""
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    
    # Plot the results
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.COASTLINE)
    ax.set_extent([-85.5, -71, 19, 24], crs=ccrs.PlateCarree())
    
    # Use pcolormesh with edges
    mesh = ax.pcolormesh(
        longitude, latitude, data[0, :, :],
        cmap='hot_r', transform=ccrs.PlateCarree(), shading='auto', vmin=0, vmax=3e15
    )
    
    # Add colorbar
    shrink_factor = 0.7
    cbar = plt.colorbar(mesh, shrink=shrink_factor, pad=0.01)
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)", 
                  size=9, labelpad=10)
    cbar.ax.tick_params(labelsize=8)
    
    # Define region locations
    havana_lon, havana_lat = -82.35, 23.13
    mariel_lon, mariel_lat = -82.75, 23.01
    nipe_lon, nipe_lat = -75.85, 20.8
    santiago_lon, santiago_lat = -75.82, 20.02
    
    # Square size
    sq = 0.15
    
    # HAVANA
    # Draw filled black square
    havana_sq_lon = [havana_lon-sq/2, havana_lon+sq/2, havana_lon+sq/2, havana_lon-sq/2, havana_lon-sq/2]
    havana_sq_lat = [havana_lat-sq/2, havana_lat-sq/2, havana_lat+sq/2, havana_lat+sq/2, havana_lat-sq/2]
    ax.fill(havana_sq_lon, havana_sq_lat, color='black', transform=ccrs.PlateCarree(), zorder=5)
    # Label position - to the right and slightly up
    havana_label_lon, havana_label_lat = havana_lon + 0.8, havana_lat + 0.4
    # Draw line from square to label
    ax.plot([havana_lon, havana_label_lon], [havana_lat, havana_label_lat], 
            'k-', linewidth=2, transform=ccrs.PlateCarree(), zorder=4)
    # Add label
    ax.text(havana_label_lon, havana_label_lat, 'La Habana',
            transform=ccrs.PlateCarree(), fontsize=11, fontweight='bold', color='black',
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='black', linewidth=2))
    
    # MARIEL
    # Draw filled black square
    mariel_sq_lon = [mariel_lon-sq/2, mariel_lon+sq/2, mariel_lon+sq/2, mariel_lon-sq/2, mariel_lon-sq/2]
    mariel_sq_lat = [mariel_lat-sq/2, mariel_lat-sq/2, mariel_lat+sq/2, mariel_lat+sq/2, mariel_lat-sq/2]
    ax.fill(mariel_sq_lon, mariel_sq_lat, color='black', transform=ccrs.PlateCarree(), zorder=5)
    # Label position - to the left and up
    mariel_label_lon, mariel_label_lat = mariel_lon - 0.8, mariel_lat + 0.5
    # Draw line from square to label
    ax.plot([mariel_lon, mariel_label_lon], [mariel_lat, mariel_label_lat], 
            'k-', linewidth=2, transform=ccrs.PlateCarree(), zorder=4)
    # Add label
    ax.text(mariel_label_lon, mariel_label_lat, 'Mariel',
            transform=ccrs.PlateCarree(), fontsize=11, fontweight='bold', color='black',
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='black', linewidth=2))
    
    # NIPE BAY
    # Draw filled black square
    nipe_sq_lon = [nipe_lon-sq/2, nipe_lon+sq/2, nipe_lon+sq/2, nipe_lon-sq/2, nipe_lon-sq/2]
    nipe_sq_lat = [nipe_lat-sq/2, nipe_lat-sq/2, nipe_lat+sq/2, nipe_lat+sq/2, nipe_lat-sq/2]
    ax.fill(nipe_sq_lon, nipe_sq_lat, color='black', transform=ccrs.PlateCarree(), zorder=5)
    # Label position - far to the right, matching reference image
    nipe_label_lon, nipe_label_lat = nipe_lon + 2.5, nipe_lat - 0.15
    # Draw line from square to label
    ax.plot([nipe_lon, nipe_label_lon], [nipe_lat, nipe_label_lat], 
            'k-', linewidth=2, transform=ccrs.PlateCarree(), zorder=4)
    # Add label
    ax.text(nipe_label_lon, nipe_label_lat, 'Bahía de Nipe',
            transform=ccrs.PlateCarree(), fontsize=11, fontweight='bold', color='black',
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='black', linewidth=2))
    
    # SANTIAGO DE CUBA
    # Draw filled black square
    santiago_sq_lon = [santiago_lon-sq/2, santiago_lon+sq/2, santiago_lon+sq/2, santiago_lon-sq/2, santiago_lon-sq/2]
    santiago_sq_lat = [santiago_lat-sq/2, santiago_lat-sq/2, santiago_lat+sq/2, santiago_lat+sq/2, santiago_lat-sq/2]
    ax.fill(santiago_sq_lon, santiago_sq_lat, color='black', transform=ccrs.PlateCarree(), zorder=5)
    # Label position - to the right and down (away from colorbar)
    santiago_label_lon, santiago_label_lat = santiago_lon + 1.3, santiago_lat - 0.6
    # Draw line from square to label
    ax.plot([santiago_lon, santiago_label_lon], [santiago_lat, santiago_label_lat], 
            'k-', linewidth=2, transform=ccrs.PlateCarree(), zorder=4)
    # Add label
    ax.text(santiago_label_lon, santiago_label_lat, 'Santiago de Cuba',
            transform=ccrs.PlateCarree(), fontsize=11, fontweight='bold', color='black',
            ha='center', va='center', zorder=6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor='white', edgecolor='black', linewidth=2))
    
    # Add title
    ax.set_title(f"NO₂ Columns Over Cuba - {f_name}", pad=10)
    
    plt.tight_layout()
    plt.show()
    return fig

# Usage:
merged = np.concatenate([before_data, during_data, after_data], axis=0)
mean_merged = np.nanmean(merged, axis=0)
masked_merged = apply_land_mask(mean_merged, land_mask)
plot_map1(masked_merged, longitude, latitude, "Overall")