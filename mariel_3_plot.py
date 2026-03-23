# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 00:08:38 2025

@author: jedia
"""

def plot_map_with_mariel_zoom(data, longitude, latitude, title, save_path=None, cmap='afmhot_r', vmin=None, vmax=4.5e15, 
                             shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                             shapefile_path_adm2=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp"):
    """
    Plot a map of Cuba with a zoomed-in inset of the Mariel region with administrative borders.
    The main map shows only province (ADM1) boundaries, while the zoomed inset shows both
    province (ADM1) and municipality (ADM2) boundaries.

    Parameters:
    -----------
    data : numpy.ndarray
        3D array of NO2 data with shape (1, lat, lon)
    longitude : numpy.ndarray
        Array of longitude values
    latitude : numpy.ndarray
        Array of latitude values
    title : str
        Title for the plot
    save_path : str, optional
        Path to save the figure if needed
    cmap : str, optional
        Colormap to use (default: 'afmhot_r')
    vmin, vmax : float, optional
        Min and max values for the colormap
    shapefile_path : str, optional
        Path to Cuba administrative level 1 shapefile
    shapefile_path_adm2 : str, optional
        Path to Cuba level 2 administrative boundaries shapefile

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The created figure
    """
    # Import necessary packages
    import numpy as np
    
    try:
        import geopandas as gpd
        # Load ADM1 (provinces)
        cuba_adm1 = gpd.read_file(shapefile_path)
        mariel_province = cuba_adm1[cuba_adm1['NAME_1'].isin(['Artemisa'])]  # Mariel is in Artemisa province
        
        # Load Level 2 boundaries - only for the zoomed region
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

        # Define manual Mariel borders as backup
        mariel_border_coords = [
            [-83.00, 22.90], # Bottom left
            [-83.00, 23.10], # Top left
            [-82.60, 23.10], # Top right
            [-82.60, 22.90], # Bottom right
            [-83.00, 22.90]  # Back to start
        ]
        mariel_border = np.array(mariel_border_coords)

    # Define Mariel coordinates (harbor area)
    mariel_lon, mariel_lat = -82.75, 23.01

    # Define a zoom box around Mariel region - SHIFTED LEFT to center Mariel
    zoom_width_lon = 0.45  # degrees - slightly wider
    zoom_width_lat = 0.25  # degrees - slightly taller

    # Center the box on Mariel with slight adjustments to include surrounding area
    mariel_lon_center = mariel_lon - 0.05  # Shift slightly west
    mariel_lat_center = mariel_lat - 0.03  # Shift slightly south

    # Define the extent to focus on Mariel area - CENTERED
    mariel_extent = [
        mariel_lon_center - zoom_width_lon*0.5,  # Equal space on left
        mariel_lon_center + zoom_width_lon*0.5,  # Equal space on right
        mariel_lat_center - zoom_width_lat*0.5,  # Equal space below
        mariel_lat_center + zoom_width_lat*0.5   # Equal space above
    ]

    # Create natural earth features for the zoom inset - using higher resolution
    lakes_10m = cfeature.NaturalEarthFeature(
        category='physical', 
        name='lakes', 
        scale='10m', 
        facecolor='skyblue', 
        edgecolor='blue',
        linewidth=0.8
    )

    rivers_10m = cfeature.NaturalEarthFeature(
        category='physical', 
        name='rivers_lake_centerlines', 
        scale='10m', 
        facecolor='none', 
        edgecolor='blue',
        linewidth=1.0
    )

    # Handle 2D vs 3D data
    if isinstance(data, np.ndarray):
        if data.ndim == 2:
            plot_data = data
        elif data.ndim == 3:
            plot_data = data[0, :, :]
        else:
            raise ValueError(f"Unexpected data dimensions: {data.shape}")
    else:
        plot_data = data[0, :, :]  # Assume it's a list of arrays

    # Create the main figure with higher DPI for clarity
    fig = plt.figure(figsize=(12, 9), dpi=200)

    # Create the main map
    main_ax = fig.add_axes([0.1, 0.15, 0.85, 0.75], projection=ccrs.PlateCarree())

    # Add map features for main map - only borders
    main_ax.add_feature(cfeature.BORDERS, linestyle=':')

    # Add ONLY ADM1 borders to main map
    if has_shapefile:
        # Plot ADM1 provinces with thicker lines
        cuba_adm1.plot(ax=main_ax, edgecolor='black', facecolor='none', linewidth=1.5)

    # Set Cuba extent
    main_ax.set_extent([-85.5, -74, 19.5, 24], crs=ccrs.PlateCarree())

    # Plot the NO2 data on the main map - no interpolation or special rendering
    main_mesh = main_ax.pcolormesh(
        longitude, latitude, plot_data,
        cmap=cmap, transform=ccrs.PlateCarree(), 
        shading='auto',  # Use 'auto' instead of 'gouraud' for original data
        vmin=vmin, vmax=vmax
    )

    # Add a rectangle to show the zoom area
    zoom_rect = mpatches.Rectangle(
        (mariel_extent[0], mariel_extent[2]),
        (mariel_extent[1] - mariel_extent[0]), (mariel_extent[3] - mariel_extent[2]),
        fill=False, edgecolor='red', linewidth=2,
        transform=ccrs.PlateCarree()
    )
    main_ax.add_patch(zoom_rect)

    # Add colorbar for the main plot
    shrink_factor = 0.7
    cbar = plt.colorbar(main_mesh, shrink=shrink_factor, pad=0.01)
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)")

    # Add title
    main_ax.set_title(title)

    # Create an inset axes for the zoomed area
    zoom_ax = fig.add_axes([0.15, 0.17, 0.3, 0.3], projection=ccrs.PlateCarree())
    zoom_ax.set_extent(mariel_extent, crs=ccrs.PlateCarree())

    # Plot the NO2 data in the zoom inset - no interpolation
    zoom_mesh = zoom_ax.pcolormesh(
        longitude, latitude, plot_data,
        cmap=cmap, transform=ccrs.PlateCarree(),
        shading='auto',  # Original data without interpolation
        vmin=vmin, vmax=vmax,
        alpha=0.8
    )

    # Add high-resolution features
    zoom_ax.add_feature(lakes_10m)
    zoom_ax.add_feature(rivers_10m)

    # Add admin boundaries with detailed municipality borders ONLY in the zoomed area
    if has_shapefile:
        # Add province boundaries
        cuba_adm1.plot(ax=zoom_ax, edgecolor='black', facecolor='none', linewidth=1.5)
        
        # Add Level 2 boundaries with gray color - ONLY in the zoom inset
        if cuba_adm2 is not None:
            # Clip to zoom extent
            try:
                zoom_bbox = (mariel_extent[0], mariel_extent[2], mariel_extent[1], mariel_extent[3])
                cuba_adm2_clipped = cuba_adm2.cx[zoom_bbox[0]:zoom_bbox[2], zoom_bbox[1]:zoom_bbox[3]]
                cuba_adm2_clipped.plot(ax=zoom_ax, edgecolor='dimgray', facecolor='none', linewidth=0.8)
            except Exception as e:
                print(f"Error clipping level 2 shapefile: {e}. Plotting full dataset.")
                cuba_adm2.plot(ax=zoom_ax, edgecolor='dimgray', facecolor='none', linewidth=0.8)
    else:
        # Use manual border if shapefile not available
        zoom_ax.plot(mariel_border[:, 0], mariel_border[:, 1], 
                    color='black', linewidth=3.0, transform=ccrs.PlateCarree())

    # Add Mariel marker
    zoom_ax.plot(mariel_lon, mariel_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())
    zoom_ax.text(
        mariel_lon + 0.01, mariel_lat - 0.02, 'Mariel',
        transform=ccrs.PlateCarree(),
        fontsize=9, fontweight='bold', color='black'
    )

    # Add title to inset
    zoom_ax.set_title('Mariel Region', fontsize=10)

    # Add border around inset
    for spine in zoom_ax.spines.values():
        spine.set_edgecolor('red')
        spine.set_linewidth(2)

    # Connect the zoom box to the inset
    rect_x_min, rect_y_min = mariel_extent[0], mariel_extent[2]
    rect_x_max, rect_y_max = mariel_extent[1], mariel_extent[3]

    inset_bounds = zoom_ax.get_position().bounds
    inset_x_min, inset_y_min = inset_bounds[0], inset_bounds[1]
    inset_x_max, inset_y_max = inset_bounds[0] + inset_bounds[2], inset_bounds[1] + inset_bounds[3]

    con1_bl = ConnectionPatch(
        xyA=(rect_x_min, rect_y_min), coordsA=main_ax.transData,
        xyB=(inset_x_min, inset_y_min), coordsB=fig.transFigure,
        arrowstyle="-", linewidth=1, color='red'
    )

    con2_tr = ConnectionPatch(
        xyA=(rect_x_max, rect_y_max), coordsA=main_ax.transData,
        xyB=(inset_x_max, inset_y_max), coordsB=fig.transFigure,
        arrowstyle="-", linewidth=1, color='red'
    )

    fig.add_artist(con1_bl)
    fig.add_artist(con2_tr)

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=600)  # High DPI for saved file

    # Display the figure
    plt.show()

    return fig




def plot_map_with_havana_zoom(data, longitude, latitude, title, save_path=None, cmap='afmhot_r', vmin=None, vmax=4.5e15, 
                             shapefile_path=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp"):
    """
    Plot a map of Cuba with a zoomed-in inset of Havana region with administrative borders.

    Parameters:
    -----------
    data : numpy.ndarray
        3D array of NO2 data with shape (1, lat, lon)
    longitude : numpy.ndarray
        Array of longitude values
    latitude : numpy.ndarray
        Array of latitude values
    title : str
        Title for the plot
    save_path : str, optional
        Path to save the figure if needed
    cmap : str, optional
        Colormap to use (default: 'afmhot_r')
    vmin, vmax : float, optional
        Min and max values for the colormap
    shapefile_path : str, optional
        Path to Cuba administrative level 1 shapefile

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The created figure
    """
    try:
        import geopandas as gpd
        cuba_adm1 = gpd.read_file(shapefile_path)
        havana_province = cuba_adm1[cuba_adm1['NAME_1'].isin(['La Habana', 'Ciudad de la Habana'])]
        has_shapefile = True
    except Exception as e:
        print(f"Using manual borders because: {e}")
        has_shapefile = False

        # Define manual Havana borders as backup
        havana_border_coords = [
            [-82.50, 22.95], # Bottom left
            [-82.50, 23.20], # Top left
            [-82.20, 23.20], # Top right
            [-82.20, 22.95], # Bottom right
            [-82.50, 22.95]  # Back to start
        ]
        havana_border = np.array(havana_border_coords)

    # Define Havana coordinates (city center, shifted south)
    havana_lon, havana_lat = -82.366, 23.11

    # Define a tighter zoom box around Havana city, shifted to minimize water
    zoom_width_lon = 0.3  # degrees
    zoom_width_lat = 0.25  # degrees

    # Shift the extent southward to eliminate white space
    havana_extent = [
        havana_lon - zoom_width_lon, 
        havana_lon + zoom_width_lon, 
        havana_lat - zoom_width_lat*0.7,
        havana_lat + zoom_width_lat*1.3
    ]

    # Create natural earth features for the zoom inset
    lakes_10m = cfeature.NaturalEarthFeature(
        category='physical', 
        name='lakes', 
        scale='10m', 
        facecolor='skyblue', 
        edgecolor='blue',
        linewidth=0.8
    )

    rivers_10m = cfeature.NaturalEarthFeature(
        category='physical', 
        name='rivers_lake_centerlines', 
        scale='10m', 
        facecolor='none', 
        edgecolor='blue',
        linewidth=1.0
    )

    # Handle 2D vs 3D data
    if isinstance(data, np.ndarray):
        if data.ndim == 2:
            plot_data = data
        elif data.ndim == 3:
            plot_data = data[0, :, :]
        else:
            raise ValueError(f"Unexpected data dimensions: {data.shape}")
    else:
        plot_data = data[0, :, :]  # Assume it's a list of arrays

    # Create the main figure
    fig = plt.figure(figsize=(12, 9))

    # Create the main map (slightly smaller to leave room for the inset)
    main_ax = fig.add_axes([0.1, 0.15, 0.85, 0.75], projection=ccrs.PlateCarree())

    # Add map features for main map (standard resolution)


    main_ax.add_feature(cfeature.BORDERS, linestyle=':')

    # Add admin borders to main map if available
    if has_shapefile:
        cuba_adm1.plot(ax=main_ax, edgecolor='black', facecolor='none', linewidth=1.5)

    # Set Cuba extent
    main_ax.set_extent([-85.5, -74, 19.5, 24], crs=ccrs.PlateCarree())

    # Plot the NO2 data on the main map
    main_mesh = main_ax.pcolormesh(
        longitude, latitude, plot_data,
        cmap=cmap, transform=ccrs.PlateCarree(), 
        shading='auto', vmin=vmin, vmax=vmax
    )

    # Add a rectangle to show the zoom area
    zoom_rect = mpatches.Rectangle(
        (havana_extent[0], havana_extent[2]),
        (havana_extent[1] - havana_extent[0]), (havana_extent[3] - havana_extent[2]),
        fill=False, edgecolor='red', linewidth=2,
        transform=ccrs.PlateCarree()
    )
    main_ax.add_patch(zoom_rect)

    # Add colorbar for the main plot
    shrink_factor = 0.7
    cbar = plt.colorbar(main_mesh, shrink=shrink_factor, pad=0.01)
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)")

    # Add title
    main_ax.set_title(title)

    # Create an inset axes for the zoomed area
    zoom_ax = fig.add_axes([0.15, 0.17, 0.3, 0.3], projection=ccrs.PlateCarree())
    zoom_ax.set_extent(havana_extent, crs=ccrs.PlateCarree())

    # Add base features


    # Plot the NO2 data with some transparency
    zoom_mesh = zoom_ax.pcolormesh(
        longitude, latitude, plot_data,
        cmap=cmap, transform=ccrs.PlateCarree(),
        shading='auto', vmin=vmin, vmax=vmax,
        alpha=0.8
    )


    # Add high-resolution features
    zoom_ax.coastlines(resolution='10m', linewidth=1.5, color='black')
    zoom_ax.add_feature(lakes_10m)
    zoom_ax.add_feature(rivers_10m)

    # Add admin boundaries
    if has_shapefile:
        # Add all province boundaries
        cuba_adm1.plot(ax=zoom_ax, edgecolor='black', facecolor='none', linewidth=2.0)

        # Add thicker line for Havana province
        if not havana_province.empty:
            havana_province.plot(ax=zoom_ax, edgecolor='black', facecolor='none', linewidth=3.0)
    else:
        # Use manual border if shapefile not available
        zoom_ax.plot(havana_border[:, 0], havana_border[:, 1], 
                    color='black', linewidth=3.0, transform=ccrs.PlateCarree())

    # Add Havana marker
    zoom_ax.plot(havana_lon, havana_lat, 'ko', markersize=6, transform=ccrs.PlateCarree())
    zoom_ax.text(
        havana_lon + 0.01, havana_lat - 0.02, 'La Habana',
        transform=ccrs.PlateCarree(),
        fontsize=9, fontweight='bold', color='black'
    )

    # Add title to inset
    zoom_ax.set_title('La Habana Region', fontsize=10)

    # Add border around inset
    for spine in zoom_ax.spines.values():
        spine.set_edgecolor('red')
        spine.set_linewidth(2)

    # Connect the zoom box to the inset
    rect_x_min, rect_y_min = havana_extent[0], havana_extent[2]
    rect_x_max, rect_y_max = havana_extent[1], havana_extent[3]

    inset_bounds = zoom_ax.get_position().bounds
    inset_x_min, inset_y_min = inset_bounds[0], inset_bounds[1]
    inset_x_max, inset_y_max = inset_bounds[0] + inset_bounds[2], inset_bounds[1] + inset_bounds[3]

    con1_bl = ConnectionPatch(
        xyA=(rect_x_min, rect_y_min), coordsA=main_ax.transData,
        xyB=(inset_x_min, inset_y_min), coordsB=fig.transFigure,
        arrowstyle="-", linewidth=1, color='red'
    )

    con2_tr = ConnectionPatch(
        xyA=(rect_x_max, rect_y_max), coordsA=main_ax.transData,
        xyB=(inset_x_max, inset_y_max), coordsB=fig.transFigure,
        arrowstyle="-", linewidth=1, color='red'
    )

    fig.add_artist(con1_bl)
    fig.add_artist(con2_tr)

    # Save figure if path is provided
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)

    # Display the figure
    plt.show()

    return fig




def create_mariel_pollution_boxplot(before_data, during_data, after_data, longitude, latitude, 
                                   adm2_shapefile=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp", 
                                   adm1_shapefile=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                                   save_path=None):
    """
    Create a box-and-whisker plot of NO2 emissions over the most polluted areas of Mariel 
    with markers for 5th and 95th percentiles.

    Parameters:
    -----------
    before_data : numpy.ndarray
        NO2 data before blackout with shape (1, lat, lon) or (lat, lon)
    during_data : numpy.ndarray
        NO2 data during blackout with shape (1, lat, lon) or (lat, lon)
    after_data : numpy.ndarray
        NO2 data after blackout with shape (1, lat, lon) or (lat, lon)
    longitude : numpy.ndarray
        Array of longitude values
    latitude : numpy.ndarray
        Array of latitude values
    adm2_shapefile : str, optional
        Path to level 2 administrative boundaries shapefile
    adm1_shapefile : str, optional
        Path to level 1 administrative boundaries shapefile
    save_path : str, optional
        Path to save the figure if needed

    Returns:
    --------
    fig : matplotlib.figure.Figure
        The created figure
    stats_dict : dict
        Dictionary containing statistics for each period
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point, box
    from matplotlib.patches import Patch

    try:
        # First, print available provinces and municipalities to help debug
        cuba_adm1 = gpd.read_file(adm1_shapefile)
        print("Available provinces in shapefile:", cuba_adm1['NAME_1'].unique())

        cuba_adm2 = gpd.read_file(adm2_shapefile)
        if 'NAME_2' in cuba_adm2.columns:
            print("Sample municipalities:", cuba_adm2['NAME_2'].unique()[:5], "...")

        # Check if 'Mariel' exists in level 2
        mariel_matches = []
        if 'NAME_2' in cuba_adm2.columns:
            mariel_matches = [name for name in cuba_adm2['NAME_2'].unique() if 'mariel' in str(name).lower()]
            if mariel_matches:
                print(f"Found Mariel-like names: {mariel_matches}")
    except Exception as e:
        print(f"Error inspecting shapefiles: {e}")

    # Define the Mariel region as a bounding box from the map coordinates
    mariel_bounds = [-83.00, 22.90, -82.60, 23.10]  # [min_lon, min_lat, max_lon, max_lat]
    mariel_geom = box(mariel_bounds[0], mariel_bounds[1], mariel_bounds[2], mariel_bounds[3])

    # Define threshold for identifying high pollution areas based on the 'before' data
    if before_data.ndim == 3:
        pollution_data = before_data[0, :, :]
    else:
        pollution_data = before_data

    # Calculate 90th percentile of non-NaN values as threshold for high pollution
    flat_pollution = pollution_data.flatten()
    valid_pollution = flat_pollution[~np.isnan(flat_pollution)]
    pollution_threshold = np.percentile(valid_pollution, 90)

    # Function to extract data points from highly polluted regions within Mariel
    def extract_polluted_regions(data_array):
        all_points = []

        if isinstance(data_array, list):
            data_array = np.array(data_array)
        if data_array.ndim == 3:
            data_2d = data_array[0, :, :]
        elif data_array.ndim == 2:
            data_2d = data_array
        else:
            raise ValueError(f"Unexpected data shape: {data_array.shape}")

        for i, lat in enumerate(latitude):
            for j, lon in enumerate(longitude):
                if not np.isnan(data_2d[i, j]):
                    point = Point(lon, lat)
                    # Check if point is in Mariel region and exceeds pollution threshold
                    if mariel_geom.contains(point) and pollution_data[i, j] >= pollution_threshold:
                        all_points.append(data_2d[i, j])
        return all_points

    # Extract data for each period from highly polluted regions
    before_points = extract_polluted_regions(before_data)
    during_points = extract_polluted_regions(during_data)
    after_points = extract_polluted_regions(after_data)

    # Check if we have enough data points
    if len(before_points) < 5 or len(during_points) < 5 or len(after_points) < 5:
        print(f"Warning: Limited data points for analysis - Before: {len(before_points)}, During: {len(during_points)}, After: {len(after_points)}")

    # Calculate statistics for each period
    def calculate_stats(data):
        if not data or len(data) < 5:
            return {"mean": np.nan, "median": np.nan, "q1": np.nan, "q3": np.nan, 
                    "iqr": np.nan, "p5": np.nan, "p95": np.nan, "min": np.nan, "max": np.nan, 
                    "std": np.nan, "count": len(data) if data else 0}

        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        return {
            "mean": np.mean(data),
            "median": np.median(data),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "p5": np.percentile(data, 5),
            "p95": np.percentile(data, 95),
            "min": np.min(data),
            "max": np.max(data),
            "std": np.std(data),
            "count": len(data)
        }

    mariel_stats = {
        "Before Blackout": calculate_stats(before_points),
        "During Blackout": calculate_stats(during_points),
        "After Blackout": calculate_stats(after_points)
    }

    # Create the figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create custom boxplot without outliers
    boxplot = ax.boxplot(
        [before_points, during_points, after_points],
        patch_artist=True,
        labels=["Before Blackout\n(10/13-10/17)", "During Blackout\n(10/18-10/22)", "After Blackout\n(10/23-10/27)"],
        showmeans=True,
        meanprops={"marker": "x", "markeredgecolor": "black", "markersize": 10},
        showfliers=False  # Hide outliers
    )

    # Customize boxplot appearance with red theme for Mariel (to match map)
    colors = ['#a6dcef', '#a7e9af', '#ffaaa5']  # Light to darker reds
    for patch, color in zip(boxplot['boxes'], colors):
        patch.set_facecolor(color)
    for median in boxplot['medians']:
        median.set_color('black')
        median.set_linewidth(2)

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title('NO₂ Columns in Most Polluted Areas of Mariel During Cuba Blackout', fontsize=14)
    ax.set_ylabel('Vertical Column Troposphere (molecules/cm²)', fontsize=12)

    # Format y-axis with scientific notation, keeping ×10^15 at the top
    formatter = plt.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    ax.yaxis.set_major_formatter(formatter)

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='x', color='black', linestyle='None', markersize=8, label='Mean')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Format numbers to 3 significant figures
    def format_to_3_sig_figs(value):
        """Format number to 3 significant figures in scientific notation"""
        if np.isnan(value):
            return 'N/A'
        return f"{value:.2e}"

    # Create a well-organized stats table in the format requested
    stats_data = {
        'Statistic': ['Mean', 'Median', 'Q1', 'Q3', 'IQR', 'P5', 'P95', 'Min', 'Max', 'Std Dev', 'Count'],
        'Before Blackout': [
            format_to_3_sig_figs(mariel_stats['Before Blackout']['mean']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['median']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['q1']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['q3']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['iqr']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['p5']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['p95']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['min']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['max']),
            format_to_3_sig_figs(mariel_stats['Before Blackout']['std']),
            mariel_stats['Before Blackout']['count']
        ],
        'During Blackout': [
            format_to_3_sig_figs(mariel_stats['During Blackout']['mean']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['median']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['q1']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['q3']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['iqr']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['p5']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['p95']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['min']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['max']),
            format_to_3_sig_figs(mariel_stats['During Blackout']['std']),
            mariel_stats['During Blackout']['count']
        ],
        'After Blackout': [
            format_to_3_sig_figs(mariel_stats['After Blackout']['mean']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['median']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['q1']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['q3']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['iqr']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['p5']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['p95']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['min']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['max']),
            format_to_3_sig_figs(mariel_stats['After Blackout']['std']),
            mariel_stats['After Blackout']['count']
        ]
    }

    stats_df = pd.DataFrame(stats_data)

    print("\nMariel Most Polluted Areas (Top 10%) NO₂ Statistics:")
    print("=" * 85)
    print(stats_df.to_string(index=False))
    print("=" * 85)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.tight_layout()
    plt.show()
    return fig, mariel_stats

# Function call
create_mariel_pollution_boxplot(masked_b4_blackout, masked_in_blackout, masked_aft_blackout, longitude, latitude,
                                   adm2_shapefile=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp", 
                                   adm1_shapefile=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                                   save_path=None)
