# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 09:53:02 2025

@author: jedia
"""

'''
#subplots for zoomed in regions over havana
subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]

def plot_havana_subplots(data_list, title, subplot_titles, longitude, latitude, 
                        shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                        shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Plot multiple Havana region maps in subplots for different time periods"""
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
    
    # Define Havana coordinates and industrial facilities (same as single map)
    havana_lon, havana_lat = -82.38, 23.13
    tallapiedra_lon, tallapiedra_lat = -82.3591, 23.1254
    nico_lopez_lon, nico_lopez_lat = -82.32127, 23.13409
    pollution_lon, pollution_lat = -82.35, 23.10
    
    # Define Havana extent (same as single map)
    zoom_width_lon = 0.5
    zoom_width_lat = 0.35
    havana_lon_center = pollution_lon
    havana_lat_center = pollution_lat
    
    havana_extent = [
        havana_lon_center - zoom_width_lon*0.5,
        havana_lon_center + zoom_width_lon*0.5,
        havana_lat_center - zoom_width_lat*0.5,
        havana_lat_center + zoom_width_lat*0.5
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
        
        # Set Havana extent
        ax.set_extent(havana_extent, crs=ccrs.PlateCarree())
        
        # Add high-resolution features
        ax.add_feature(lakes_10m)
        ax.add_feature(rivers_10m)
        
        # Add administrative boundaries
        if has_shapefile:
            # Add province boundaries
            cuba_adm1.plot(ax=ax, edgecolor='black', facecolor='none', linewidth=1.5)
            
            # Add Level 2 boundaries
            if cuba_adm2 is not None:
                try:
                    zoom_bbox = (havana_extent[0], havana_extent[2], havana_extent[1], havana_extent[3])
                    cuba_adm2_clipped = cuba_adm2.cx[zoom_bbox[0]:zoom_bbox[2], zoom_bbox[1]:zoom_bbox[3]]
                    cuba_adm2_clipped.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=0.8)
                except Exception as e:
                    print(f"Error clipping level 2 shapefile: {e}")
                    cuba_adm2.plot(ax=ax, edgecolor='dimgray', facecolor='none', linewidth=0.8)
        
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
            alpha=0.8
        )
        
        # Add Havana city marker
        ax.plot(havana_lon, havana_lat, 'ko', markersize=4, transform=ccrs.PlateCarree())
        ax.text(
            havana_lon - 0.03, havana_lat + 0.015, 'La Habana',
            transform=ccrs.PlateCarree(),
            fontsize=7, fontweight='bold', color='black',
            fontfamily='sans-serif',
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='black', alpha=0.8)
        )
        
        # Add industrial facility markers with leader lines
        # Termoeléctrica Tallapiedra
        ax.plot(tallapiedra_lon, tallapiedra_lat, 'ko', markersize=4, transform=ccrs.PlateCarree())
        
        tallapiedra_label_lon = tallapiedra_lon - 0.06
        tallapiedra_label_lat = tallapiedra_lat - 0.04
        
        ax.plot([tallapiedra_lon, tallapiedra_label_lon], [tallapiedra_lat, tallapiedra_label_lat], 
                'k-', linewidth=1, alpha=0.7, transform=ccrs.PlateCarree())
        
        ax.text(
            tallapiedra_label_lon, tallapiedra_label_lat, 'Termoeléctrica\\nTallapiedra',
            transform=ccrs.PlateCarree(),
            fontsize=5, fontweight='bold', color='darkred',
            fontfamily='sans-serif',
            ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.15", facecolor='lightyellow', edgecolor='darkred', alpha=0.9)
        )
        
        # Refinería Ñico López
        ax.plot(nico_lopez_lon, nico_lopez_lat, 'ko', markersize=4, transform=ccrs.PlateCarree())
        
        nico_lopez_label_lon = nico_lopez_lon + 0.08
        nico_lopez_label_lat = nico_lopez_lat + 0.03
        
        ax.plot([nico_lopez_lon, nico_lopez_label_lon], [nico_lopez_lat, nico_lopez_label_lat], 
                'k-', linewidth=1, alpha=0.7, transform=ccrs.PlateCarree())
        
        ax.text(
            nico_lopez_label_lon, nico_lopez_label_lat, 'Refinería\\nÑico López',
            transform=ccrs.PlateCarree(),
            fontsize=5, fontweight='bold', color='navy',
            fontfamily='sans-serif',
            ha='left', va='bottom',
            bbox=dict(boxstyle="round,pad=0.15", facecolor='lightcyan', edgecolor='navy', alpha=0.9)
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
# test = [masked_b4_blackout, masked_in_blackout, masked_aft_blackout]
# plot_havana_subplots(test, 'NO₂ Concentrations Over Havana Region', subplot_titles, longitude, latitude)

'''


#better version
subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]

def plot_havana_subplots(data_list, title, subplot_titles, longitude, latitude, 
                        shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                        shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """Plot multiple Havana region maps in subplots for different time periods"""
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
    
    # Define Havana coordinates and industrial facilities (same as single map)
    havana_lon, havana_lat = -82.38, 23.13
    tallapiedra_lon, tallapiedra_lat = -82.3591, 23.1254
    nico_lopez_lon, nico_lopez_lat = -82.32127, 23.13409
    pollution_lon, pollution_lat = -82.35, 23.10
    
    # Define Havana extent (same as single map)
    zoom_width_lon = 0.5
    zoom_width_lat = 0.35
    havana_lon_center = pollution_lon
    havana_lat_center = pollution_lat
    
    havana_extent = [
        havana_lon_center - zoom_width_lon*0.5,
        havana_lon_center + zoom_width_lon*0.5,
        havana_lat_center - zoom_width_lat*0.5,
        havana_lat_center + zoom_width_lat*0.5
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
        
        # Set Havana extent
        ax.set_extent(havana_extent, crs=ccrs.PlateCarree())
        
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
                    zoom_bbox = (havana_extent[0], havana_extent[2], havana_extent[1], havana_extent[3])
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
        
        # REMOVED La Habana city marker and label (redundant with title)
        
        # Add industrial facility markers with leader lines - ENHANCED AND OPTIMIZED
        
        # Termoeléctrica Tallapiedra - moved to right to avoid emissions (as we did before)
        ax.plot(tallapiedra_lon, tallapiedra_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())  # INCREASED from 4 to 6
        
        # OPTIMIZED positioning - moved to right and closer to marker
        tallapiedra_label_lon = tallapiedra_lon + 0.04  # MOVED from left (-0.06) to right (+0.04)
        tallapiedra_label_lat = tallapiedra_lat - 0.03  # CLOSER: reduced from -0.04 to -0.03
        
        ax.plot([tallapiedra_lon, tallapiedra_label_lon], [tallapiedra_lat, tallapiedra_label_lat], 
                'k-', linewidth=1.5, alpha=0.8, transform=ccrs.PlateCarree())  # ENHANCED line
        
        ax.text(
            tallapiedra_label_lon, tallapiedra_label_lat, 'Termoeléctrica\nTallapiedra',  # FIXED line break
            transform=ccrs.PlateCarree(),
            fontsize=11, fontweight='bold', color='darkred',  # INCREASED from 5 to 11
            fontfamily='sans-serif',
            ha='left', va='top',  # CHANGED alignment for new position
            bbox=dict(boxstyle="round,pad=0.2", facecolor='lightyellow', edgecolor='darkred', alpha=0.85, linewidth=1)  # ENHANCED
        )
        
        # Refinería Ñico López - optimized positioning
        ax.plot(nico_lopez_lon, nico_lopez_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())  # INCREASED from 4 to 6
        
        # OPTIMIZED positioning - closer to marker
        nico_lopez_label_lon = nico_lopez_lon + 0.05  # CLOSER: reduced from +0.08 to +0.05
        nico_lopez_label_lat = nico_lopez_lat + 0.02  # CLOSER: reduced from +0.03 to +0.02
        
        ax.plot([nico_lopez_lon, nico_lopez_label_lon], [nico_lopez_lat, nico_lopez_label_lat], 
                'k-', linewidth=1.5, alpha=0.8, transform=ccrs.PlateCarree())  # ENHANCED line
        
        ax.text(
            nico_lopez_label_lon, nico_lopez_label_lat, 'Refinería\nÑico López',  # FIXED line break
            transform=ccrs.PlateCarree(),
            fontsize=11, fontweight='bold', color='navy',  # INCREASED from 5 to 11
            fontfamily='sans-serif',
            ha='left', va='bottom',
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
plot_havana_subplots(test, 'NO₂ Columns Over La Habana Region', subplot_titles, longitude, latitude)