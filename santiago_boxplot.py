# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 09:52:26 2025

@author: jedia
"""

def create_santiago_pollution_boxplot(before_data, during_data, after_data, longitude, latitude, 
                                     adm2_shapefile=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp", 
                                     adm1_shapefile=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                                     save_path=None):
    """
    Create a box-and-whisker plot of NO2 emissions over the most polluted areas of Santiago de Cuba 
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

        # Check if 'Santiago de Cuba' exists in level 2
        santiago_matches = []
        if 'NAME_2' in cuba_adm2.columns:
            santiago_matches = [name for name in cuba_adm2['NAME_2'].unique() if 'santiago' in str(name).lower()]
            if santiago_matches:
                print(f"Found Santiago-like names: {santiago_matches}")
    except Exception as e:
        print(f"Error inspecting shapefiles: {e}")

    # Define the Santiago de Cuba region as a bounding box from the map coordinates
    # Using the coordinates shown in the image for Santiago de Cuba
    santiago_bounds = [-76.50, 19.90, -75.80, 20.30]  # [min_lon, min_lat, max_lon, max_lat]
    santiago_geom = box(santiago_bounds[0], santiago_bounds[1], santiago_bounds[2], santiago_bounds[3])

    # Define threshold for identifying high pollution areas based on the 'before' data
    if before_data.ndim == 3:
        pollution_data = before_data[0, :, :]
    else:
        pollution_data = before_data

    # Calculate 90th percentile of non-NaN values as threshold for high pollution
    flat_pollution = pollution_data.flatten()
    valid_pollution = flat_pollution[~np.isnan(flat_pollution)]
    pollution_threshold = np.percentile(valid_pollution, 90)

    # Function to extract data points from highly polluted regions within Santiago de Cuba
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
                    # Check if point is in Santiago de Cuba region and exceeds pollution threshold
                    if santiago_geom.contains(point) and pollution_data[i, j] >= pollution_threshold:
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

    santiago_stats = {
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

    # Customize boxplot appearance with blue theme for Santiago de Cuba (to differentiate from other regions)
    colors = ['#a6dcef', '#a7e9af', '#ffaaa5']  # Light to darker blues
    for patch, color in zip(boxplot['boxes'], colors):
        patch.set_facecolor(color)
    for median in boxplot['medians']:
        median.set_color('black')
        median.set_linewidth(2)

    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_title('NO₂ Columns in Most Polluted Areas of Santiago de Cuba During Cuba Blackout', fontsize=14)
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
            format_to_3_sig_figs(santiago_stats['Before Blackout']['mean']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['median']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['q1']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['q3']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['iqr']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['p5']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['p95']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['min']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['max']),
            format_to_3_sig_figs(santiago_stats['Before Blackout']['std']),
            santiago_stats['Before Blackout']['count']
        ],
        'During Blackout': [
            format_to_3_sig_figs(santiago_stats['During Blackout']['mean']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['median']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['q1']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['q3']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['iqr']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['p5']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['p95']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['min']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['max']),
            format_to_3_sig_figs(santiago_stats['During Blackout']['std']),
            santiago_stats['During Blackout']['count']
        ],
        'After Blackout': [
            format_to_3_sig_figs(santiago_stats['After Blackout']['mean']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['median']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['q1']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['q3']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['iqr']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['p5']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['p95']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['min']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['max']),
            format_to_3_sig_figs(santiago_stats['After Blackout']['std']),
            santiago_stats['After Blackout']['count']
        ]
    }

    stats_df = pd.DataFrame(stats_data)

    print("\nSantiago de Cuba Most Polluted Areas (Top 10%) NO₂ Statistics:")
    print("=" * 85)
    print(stats_df.to_string(index=False))
    print("=" * 85)

    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.tight_layout()
    plt.show()
    return fig, santiago_stats

# Function call
create_santiago_pollution_boxplot(masked_b4_blackout, masked_in_blackout, masked_aft_blackout, longitude, latitude,
                                   adm2_shapefile=r"C:\Users\jedia\TEMPO\BNDA_CUB_2010-01-01_lastupdate\BNDA_CUB_2010-01-01_lastupdate.shp", 
                                   adm1_shapefile=r"C:\Users\jedia\TEMPO\cub_adm1\CUB_adm1.shp",
                                   save_path=None)