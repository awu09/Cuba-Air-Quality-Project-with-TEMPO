# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 13:10:41 2025

@author: jedia
"""

subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]

def plot_mariel_subplots(data_list, title, subplot_titles, longitude, latitude, 
                        shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                        shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Plot multiple Mariel region maps in subplots for different time periods"""
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

    # Define Mariel coordinates and industrial facilities
    mariel_lon, mariel_lat = -82.75, 23.01
    mariel_termoelectrica_lon, mariel_termoelectrica_lat = -82.74887, 23.01906

    # Define Mariel extent
    zoom_width_lon = 0.45
    zoom_width_lat = 0.25
    mariel_lon_center = mariel_lon - 0.05
    mariel_lat_center = mariel_lat - 0.03

    mariel_extent = [
        mariel_lon_center - zoom_width_lon*0.5,
        mariel_lon_center + zoom_width_lon*0.5,
        mariel_lat_center - zoom_width_lat*0.5,
        mariel_lat_center + zoom_width_lat*0.5
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

        # Set Mariel extent
        ax.set_extent(mariel_extent, crs=ccrs.PlateCarree())

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
                    zoom_bbox = (mariel_extent[0], mariel_extent[2], mariel_extent[1], mariel_extent[3])
                    cuba_adm2_clipped = cuba_adm2.cx[zoom_bbox[0]:zoom_bbox[2], zoom_bbox[1]:zoom_bbox[3]]
                    cuba_adm2_clipped.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=1)
                except Exception as e:
                    print(f"Error clipping level 2 shapefile: {e}")
                    cuba_adm2.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=3)

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
            vmax=4.5e15,
            alpha=0.6
        )

        # Add industrial facility marker with leader line - OPTIMIZED POSITIONING
        # Termoeléctrica del Mariel - moved to avoid emissions near facility
        ax.plot(mariel_termoelectrica_lon, mariel_termoelectrica_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())  # INCREASED from 4 to 6

        # OPTIMIZED label positioning - much closer to marker, avoiding emissions
        mariel_label_lon = mariel_termoelectrica_lon - 0.02  # CLOSER: changed from -0.15 to -0.06
        mariel_label_lat = mariel_termoelectrica_lat + 0.04  # CLOSER: changed from -0.05 to -0.03

        ax.plot([mariel_termoelectrica_lon, mariel_label_lon], [mariel_termoelectrica_lat, mariel_label_lat], 
                'k-', linewidth=1.5, alpha=0.8, transform=ccrs.PlateCarree())  # ENHANCED line

        ax.text(
            mariel_label_lon, mariel_label_lat, 'Termoeléctrica\ndel Mariel',  # FIXED line break
            transform=ccrs.PlateCarree(),
            fontsize=11, fontweight='bold', color='darkred',  # INCREASED from 5 to 11
            fontfamily='sans-serif',
            ha='center', va='bottom',  # CHANGED to 'top' for new downward position
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightyellow', edgecolor='darkred', alpha=0.85, linewidth=1)  # ENHANCED
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
test = [masked_b4_blackout, masked_in_blackout, masked_aft_blackout]
plot_mariel_subplots(test, 'NO₂ Columns Over Mariel Region', subplot_titles, longitude, latitude)