# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:24:53 2025

@author: jedia
"""

subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]

def plot_nipe_subplots(data_list, title, subplot_titles, longitude, latitude, 
                      shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                      shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Plot multiple Nipe Bay region maps in subplots for different time periods"""
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
    
    # Define Nipe Bay coordinates and industrial facilities
    nipe_lon, nipe_lat = -75.85, 20.8
    felton_lon, felton_lat = -75.5949, 20.72929
    
    # Define Nipe Bay extent
    zoom_width_lon = 0.85
    zoom_width_lat = 0.65
    nipe_lon_center = nipe_lon + 0.25
    nipe_lat_center = nipe_lat - 0.05
    
    nipe_extent = [
        nipe_lon_center - zoom_width_lon*0.5,
        nipe_lon_center + zoom_width_lon*0.5,
        nipe_lat_center - zoom_width_lat*0.5,
        nipe_lat_center + zoom_width_lat*0.5
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
        
        # Set Nipe Bay extent
        ax.set_extent(nipe_extent, crs=ccrs.PlateCarree())
        
        # Add high-resolution features
        ax.add_feature(lakes_10m)
        ax.add_feature(rivers_10m)
        
        # Add administrative boundaries
        if has_shapefile:
            # Add province boundaries
            # cuba_adm1.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=2.5)
            
            # Add Level 2 boundaries
            if cuba_adm2 is not None:
                try:
                    zoom_bbox = (nipe_extent[0], nipe_extent[2], nipe_extent[1], nipe_extent[3])
                    cuba_adm2_clipped = cuba_adm2.cx[zoom_bbox[0]:zoom_bbox[2], zoom_bbox[1]:zoom_bbox[3]]
                    cuba_adm2_clipped.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=1.5)
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
            vmax=2.5e15,
            alpha=0.8
        )
        

        
        # Add industrial facility marker with leader line
        # Termoeléctrica Felton
        ax.plot(felton_lon, felton_lat, 'ko', markersize=4, transform=ccrs.PlateCarree())
        
        felton_label_lon = felton_lon + 0.05
        felton_label_lat = felton_lat - 0.04
        
        ax.plot([felton_lon, felton_label_lon], [felton_lat, felton_label_lat], 
                'k-', linewidth=1, alpha=0.7, transform=ccrs.PlateCarree())
        
        ax.text(
            felton_label_lon, felton_label_lat, 'Termoeléctrica\nFelton',
            transform=ccrs.PlateCarree(),
            fontsize=11, fontweight='bold', color='darkred',
            fontfamily='sans-serif',
            ha='left', va='center',
            bbox=dict(boxstyle="round,pad=0.15", facecolor='lightyellow', edgecolor='darkred', alpha=0.9)
        )
    
    # Adjust the margins and spaces between panels
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)
    
    # Add colorbar
    cax = fig.add_axes([right+0.02, bottom, 0.03, top-bottom])
    cbar = plt.colorbar(mesh, cax=cax)
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)", fontsize=10)
    
    plt.show()
    return fig

# Usage example:
test = [masked_b4_blackout, masked_in_blackout, masked_aft_blackout]
plot_nipe_subplots(test, 'NO₂ Columns Over Bahía de Nipe Region', subplot_titles, longitude, latitude)