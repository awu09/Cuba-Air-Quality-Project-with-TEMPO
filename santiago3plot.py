# -*- coding: utf-8 -*-
"""
Created on Thu Jul 31 11:29:56 2025

@author: jedia
"""

subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]

def plot_santiago_subplots(data_list, title, subplot_titles, longitude, latitude, 
                          shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                          shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Plot multiple Santiago de Cuba region maps in subplots for different time periods"""
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    
    try:
        import geopandas as gpd
        # Load ADM1 (provinces)
        cuba_adm1 = gpd.read_file(shapefile_path)
        
        # Load Level 2 boundaries
        cuba_adm2 = None
        if shapefile_path_adm2:
            try:
                cuba_adm2 = gpd.read_file(shapefile_path_adm2)
            except Exception as e:
                print(f"Could not load Level 2 shapefile: {e}")
        
        has_shapefile = True
    except Exception as e:
        print(f"Using manual borders because: {e}")
        has_shapefile = False
    
    # Define Santiago coordinates and industrial facilities
    santiago_lon, santiago_lat = -75.82, 20.02
    termoelectrica_lon, termoelectrica_lat = -75.87148, 19.9953
    refineria_lon, refineria_lat = -75.87372, 20.0059
    pollution_lon, pollution_lat = -75.75, 19.95
    
    # Define Santiago extent
    zoom_width_lon = 0.65
    zoom_width_lat = 0.45
    santiago_lon_center = pollution_lon
    santiago_lat_center = pollution_lat
    
    santiago_extent = [
        santiago_lon_center - zoom_width_lon*0.5,
        santiago_lon_center + zoom_width_lon*0.5,
        santiago_lat_center - zoom_width_lat*0.5,
        santiago_lat_center + zoom_width_lat*0.5
    ]
    
    # Create natural earth features
    lakes_10m = cfeature.NaturalEarthFeature(
        category='physical', name='lakes', scale='10m', 
        facecolor='skyblue', edgecolor='blue', linewidth=0.8
    )
    
    rivers_10m = cfeature.NaturalEarthFeature(
        category='physical', name='rivers_lake_centerlines', scale='10m', 
        facecolor='none', edgecolor='blue', linewidth=1.0
    )
    
    # Layout parameters
    left = 0.05
    bottom = 0.02
    right = 0.85
    top = 0.9
    wspace = 0.02
    hspace = 0.3
    
    # Create figure and subplots
    fig, axs = plt.subplots(3, 1, figsize=(10, 12), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Add main title for the entire figure
    fig.suptitle(title, fontsize=14, y=0.97)
    
    # Plot each time period
    for idx in range(len(data_list)):
        ax = axs[idx]
        
        # Set Santiago extent
        ax.set_extent(santiago_extent, crs=ccrs.PlateCarree())
        
        # Add high-resolution features
        ax.add_feature(lakes_10m)
        ax.add_feature(rivers_10m)
        
        # Add administrative boundaries
        if has_shapefile:
            # Add province boundaries
            # cuba_adm1.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=2)
            
            # Add Level 2 boundaries
            if cuba_adm2 is not None:
                try:
                    zoom_bbox = (santiago_extent[0], santiago_extent[2], santiago_extent[1], santiago_extent[3])
                    cuba_adm2_clipped = cuba_adm2.cx[zoom_bbox[0]:zoom_bbox[2], zoom_bbox[1]:zoom_bbox[3]]
                    cuba_adm2_clipped.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=1)
                except Exception as e:
                    print(f"Error clipping level 2 shapefile: {e}")
                    cuba_adm2.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=3)
        
        # Add subplot title
        ax.set_title(subplot_titles[idx], pad=10, fontsize=12)
        
        # Extract and prepare plot data
        plot_data = data_list[idx]
        print(f"Plot {idx} - Type of data: {type(plot_data)}")
        
        # Convert to numpy array if it's a list
        if isinstance(plot_data, list):
            plot_data = np.array(plot_data)
            print(f"  - Converted to array, shape: {plot_data.shape}")
        
        # Extract 2D slice if it's 3D
        if plot_data.ndim == 3:
            plot_data = plot_data[0, :, :]
            print(f"  - Extracted 2D slice, shape: {plot_data.shape}")
        
        # Plot NO2 data using pcolormesh for better quality
        mesh = ax.pcolormesh(
            longitude, latitude, plot_data,
            cmap='afmhot_r', 
            transform=ccrs.PlateCarree(),
            shading='auto',
            vmin=0, 
            vmax=3e15,
            alpha=0.6
        )
        
        # Add industrial facility markers with leader lines - OPTIMIZED POSITIONING
        
        # Termoeléctrica Antonio Maceo (Renté) - moved to avoid emissions
        ax.plot(termoelectrica_lon, termoelectrica_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())  # INCREASED from 4 to 6
        
        # OPTIMIZED label positioning - much closer to marker, avoiding emissions
        termoelectrica_label_lon = termoelectrica_lon + 0.03  # CLOSER: changed from +0.05 to +0.03  
        termoelectrica_label_lat = termoelectrica_lat - 0.06  # CLOSER: changed from -0.12 to -0.06
        
        ax.plot([termoelectrica_lon, termoelectrica_label_lon], [termoelectrica_lat, termoelectrica_label_lat], 
                'k-', linewidth=1.5, alpha=0.8, transform=ccrs.PlateCarree())  # ENHANCED line
        
        ax.text(
            termoelectrica_label_lon, termoelectrica_label_lat, 'Termoeléctrica\nAntonio Maceo (Renté)',  # FIXED line break
            transform=ccrs.PlateCarree(),
            fontsize=10, fontweight='bold', color='darkred',  # INCREASED from 5 to 10
            fontfamily='sans-serif',
            ha='left', va='top',  # CHANGED alignment for new position
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightyellow', edgecolor='darkred', alpha=0.85, linewidth=1)  # ENHANCED
        )
        
        # Refinería de Petroleo Hermanos Díaz - moved to avoid emissions
        ax.plot(refineria_lon, refineria_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())  # INCREASED from 4 to 6
        
        # OPTIMIZED label positioning - much closer to marker, avoiding emissions
        refineria_label_lon = refineria_lon + 0.08  # CLOSER: changed from +0.20 to +0.08
        refineria_label_lat = refineria_lat + 0.03  # CLOSER: changed from +0.05 to +0.03
        
        ax.plot([refineria_lon, refineria_label_lon], [refineria_lat, refineria_label_lat], 
                'k-', linewidth=1.5, alpha=0.8, transform=ccrs.PlateCarree())  # ENHANCED line
        
        ax.text(
            refineria_label_lon, refineria_label_lat, 'Refinería de Petroleo\nHermanos Díaz',  # FIXED line break
            transform=ccrs.PlateCarree(),
            fontsize=10, fontweight='bold', color='navy',  # INCREASED from 5 to 10
            fontfamily='sans-serif',
            ha='left', va='center',  # CHANGED from 'bottom' to 'center'
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightcyan', edgecolor='navy', alpha=0.85, linewidth=1)  # ENHANCED
        )
    
    # Adjust the margins and spaces between panels
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
    
    # Add colorbar
    cax = fig.add_axes([right+0.02, bottom, 0.03, top-bottom])
    cbar = plt.colorbar(mesh, cax=cax)
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)", fontsize=12)  # INCREASED from 10 to 12
    
    plt.show()
    return fig

# Usage example:
test = [mean_b4_blackout, mean_in_blackout, mean_aft_blackout]
test = [masked_b4_blackout, masked_in_blackout, masked_aft_blackout]
plot_santiago_subplots(test, 'NO₂ Columns Over Santiago de Cuba Region', subplot_titles, longitude, latitude)