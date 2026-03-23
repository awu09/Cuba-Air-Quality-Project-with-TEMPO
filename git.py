# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 20:14:12 2026

@author: jedia
"""

from datetime import datetime 
import pytz 
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap
import os
from scipy.ndimage import median_filter
from cartopy.io import shapereader
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.prepared import prep

import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
from matplotlib.patches import ConnectionPatch




#Function provides timestamps on Cuba's air quality visualizations
def filename_to_cuba_time(file_path):
    datetime_str = str(file_path).split('\\')[-1].split('_')[4]
    
    # Remove the 'Z' and parse the datetime
    dt_utc = datetime.strptime(datetime_str[:-1], '%Y%m%dT%H%M%S')
    
    # Set the timezone to UTC
    utc_tz = pytz.timezone('UTC')
    dt_utc = utc_tz.localize(dt_utc)
    
    # Convert to Cuba timezone
    cuba_tz = pytz.timezone('America/Havana')
    dt_cuba = dt_utc.astimezone(cuba_tz)
    
    return "Cuba local time: " + dt_cuba.strftime('%Y-%m-%d %H:%M:%S %Z')


# Directory containing files
d_b4_blackout = Path(r"C:\Users\jedia\TEMPO\good data\TEMPO_NO2_L3_V03-20241128_024826") #Before Blackout
d_in_blackout = Path(r"C:\Users\jedia\TEMPO\good data\TEMPO_NO2_L3_V03-20241128_024722") #During Blackout
d_charts = Path(r"C:\Users\jedia\TEMPO\charts") #During Blackout
d_aft_blackout = Path(r"C:\Users\jedia\TEMPO\good data\TEMPO_NO2_L3_V03-20241128_024832") #After Black Out



# Dimensions of the grid (363 x 718)
grid_shape = (363, 718)


#Function loads TEMPO data and filters cloud fraction and solar zenith angle. 
#Gives an Array with all the NO2 columns of a certain longitude and latitude
def load_tempo_data(dir_data):

    latitude = []
    longitude = []
    all_data = []

    # Loop through files
    for f_name in dir_data.glob("*.nc4"):  # Adjust extension if needed               
        # Read the current file
        with Dataset(f_name) as file_id:
        
        # Extract variables (adjust names based on your file)
            latitude = file_id.variables['latitude'][:]
            longitude = file_id.variables['longitude'][:]
            product = file_id.groups['product']
            vertical_column_troposphere = product.variables['vertical_column_troposphere'][:].filled(fill_value=np.nan)
            quality_flag = product.variables['main_data_quality_flag'][:]
            support = file_id.groups['support_data']
            eff_cloud_fraction = support.variables['eff_cloud_fraction'][:]
            geoloc = file_id.groups['geolocation']
            solar_angle = geoloc.variables['solar_zenith_angle'][:]
            
            
            vertical_column_troposphere = np.ma.masked_where(vertical_column_troposphere < -1e20, vertical_column_troposphere)
            vertical_column_troposphere = vertical_column_troposphere.filled(np.nan)
    
            # # Filter out invalid data
            solar_angle_cutoff = 60
            mask = np.logical_or.reduce([
                quality_flag == 2, 
                eff_cloud_fraction > 0.2, 
                solar_angle >= solar_angle_cutoff
                ])
            vertical_column_troposphere = np.ma.masked_where(mask, vertical_column_troposphere)
            vertical_column_troposphere = vertical_column_troposphere.filled(np.nan)
            
            # Add to list, ensuring shape consistency
            if vertical_column_troposphere.shape == (1, 363, 718):
                all_data.append(vertical_column_troposphere)
            else:
                print(f"Skipping {f_name} - unexpected shape: {vertical_column_troposphere.shape}")

    return all_data, longitude, latitude

#Function Provides the difference between two time periods of TEMPO data
#In this case, before the blackout - during
def compute_map_difference(before_data, during_data):
    
    mean_b4_blackout = np.nanmean(before_data, axis=0)
    mean_in_blackout = np.nanmean(during_data, axis=0)
    difference = np.subtract(mean_b4_blackout, mean_in_blackout)

    return difference, mean_b4_blackout, mean_in_blackout

#Function plots the difference between two time period in a given area  
def plot_map_diff(data, longitude, latitude, f_name):

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
        cmap=plt.get_cmap('bwr',21), transform=ccrs.PlateCarree(), shading='auto', vmin=-4.5e15, vmax=4.5e15
    )

    # Add colorbar and labels
    plt.colorbar(mesh, label="Vertical Column Troposphere (molecules/cm^2)")
    plt.title(f"Change in NO₂ Concentrations Over Cuba - {f_name}")
    plt.show()

    return fig

#Funtion denoises the map by taking the mean
def denoise_map(data):
    
    data_2d = data[0, :, :]
    map_mean = np.nanmean(data_2d)
    row_mean = np.nanmean(data_2d, axis=1)
    row_mean_dev = row_mean - map_mean

    data[0, :, :] = data[0, :, :] - row_mean_dev[:, np.newaxis]
    
    return data



#Function plots NO2 Columns over Cuba
def plot_map1(data, longitude, latitude, f_name):
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
        cmap='hot_r', transform=ccrs.PlateCarree(), shading='auto', vmin=0, vmax=4.5e15
    )

    # Add colorbar with increased shrink factor to match map height
    shrink_factor = 0.4
    cbar = plt.colorbar(mesh, shrink=shrink_factor, pad=0.01)

    # Manually set the colorbar label with adjusted size
    fontsize = 9  # Smaller font size for the label
    cbar.set_label("Vertical Column Troposphere (molecules/cm²)", 
                  size=fontsize, labelpad=10)

    # Also adjust the tick label sizes
    cbar.ax.tick_params(labelsize=8)

    # Add title
    ax.set_title(f"NO₂ Concentrations Over Cuba - {f_name}", pad=10)

    plt.tight_layout()
    plt.show()
    return fig

#Applies a nxn median filter over TEMPO data
def median(data):
    filtered_no2plot = [median_filter(data[0, :, :], size=(3,3))]
#     filtered_no2plot = [median_filter(i, size=(5, 5), mode='mirror') for i in data]
    # filtered_no2plot = [median_filter(i, size=(5, 5), mode='mirror') for i in filtered_no2plot]
    # filtered_no2plot = [median_filter(i, size=(5,5), mode='mirror') for i in filtered_no2plot]
    # filtered_no2plot = [median_filter(data[0, :, :], size=(1, 5))]
    
    return filtered_no2plot



#Creates a land mask over Cuba, so that only land NO2 columns are displayed
def create_land_mask(lon, lat):
    """Create a binary mask where True is land and False is water"""
    # Load land geometry using Natural Earth data
    
    resolution = '10m'  # Options: '110m', '50m', '10m'
    category = 'physical'
    name = 'land'
    
    # Get the land polygons
    shpfilename = shapereader.natural_earth(resolution, category, name)
    reader = shapereader.Reader(shpfilename)
    
    # Create a mask the same shape as the data grid
    mask = np.zeros((len(lat), len(lon)), dtype=bool)
    
    # Prepare all land geometries for faster operations
    land_geoms = list(reader.geometries())
    prepared_geoms = [prep(geom) for geom in land_geoms]
    
    # For each grid point, check if it's on land
    for i in range(len(lat)):
        for j in range(len(lon)):
            point = Point(lon[j], lat[i])
            # Check if point is in any of the land geometries
            for prepared_geom in prepared_geoms:
                if prepared_geom.contains(point):
                    mask[i, j] = True
                    break  # No need to check other geometries if we found land
    
    return mask



def apply_land_mask(data, land_mask):
    """Apply land mask to data, setting water areas to NaN"""
    # Make a copy to avoid modifying the original data
    masked_data = data.copy()
    
    # For 3D array (like your original data)
    if len(masked_data.shape) == 3:
        # Broadcast the 2D mask to the 3D array
        for i in range(masked_data.shape[0]):
            # Set water areas to NaN
            masked_data[i, ~land_mask] = np.nan
    # For 2D array
    elif len(masked_data.shape) == 2:
        # Set water areas to NaN
        masked_data[~land_mask] = np.nan
        
    return masked_data


#Creates an array where the dataset provides the number of non-NaN values used in an average at each pixel
def number_of_point(data):
    non_nan_count = []
    for i in data:
        non_nan_count += ~np.isnan(i[0, :, :])

    return data


#Plotting 3 subplots 
subplot_titles = [
    'Before the Blackout',
    'During the Blackout',
    'After the Blackout'
]
def plot_map_subplots(data_list, title, subplot_titles, longitude, latitude):
    """Plot multiple maps in subplots"""
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    # data_list: list containing [before_data, during_data, after_data]
    left = 0.05 # The position of the LEFT edge of the subplots, as a fraction of the figure width.
    bottom = 0.02 # The position of the BOTTOM edge of the subplots, as a fraction of the figure height.
    right = 0.85 # The position of the RIGHT edge of the subplots, as a fraction of the figure width.
    top = 0.9 # The position of the TOP edge of the subplots, as a fraction of the figure height.
    wspace = 0.02 # The WIDTH of the padding between subplots, as a fraction of the average Axes width.
    hspace = 0.3

    # Plot the results
    fig, axs = plt.subplots(3, 1, figsize=(10,8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Add main title for the entire figure
    fig.suptitle(title, fontsize=14, y=0.97)

    # Subplot titles


    for idx in range(len(data_list)):
        # Add map features
        ax = axs[idx]
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.COASTLINE)
        ax.set_extent([-85, -71, 19, 24], crs=ccrs.PlateCarree())

        # Add subplot title
        ax.set_title(subplot_titles[idx], pad=10, fontsize=12)

        # Extract plot data and ensure it's a NumPy array
        plot_data = data_list[idx]

        # Debug print to see what we're dealing with
        print(f"Plot {idx} - Type of data: {type(plot_data)}")

        # Convert to numpy array if it's a list
        if isinstance(plot_data, list):
            plot_data = np.array(plot_data)
            print(f"  - Converted to array, shape: {plot_data.shape}")

        # Extract 2D slice if it's 3D
        if plot_data.ndim == 3:
            plot_data = plot_data[0, :, :]
            print(f"  - Extracted 2D slice, shape: {plot_data.shape}")

        # Use imshow instead of pcolormesh to avoid dimension issues
        mesh = ax.imshow(
            plot_data,
            extent=[longitude.min(), longitude.max(), latitude.min(), latitude.max()],
            cmap='hot_r', 
            transform=ccrs.PlateCarree(),
            origin='lower',  # Important for correct orientation
            vmin=0, 
            vmax=4.5e15
        )

    # Adjust the margins and the spaces between panels in the figure, using the parameters determined above.
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

    # Add an axis for a color bar.
    cax = fig.add_axes([right+0.02, bottom, 0.03, top-bottom])

    # Add colorbar and labels
    cbar = plt.colorbar(mesh, cax=cax)
    cbar.set_label("Vertical Column Troposphere (molecules/cm^2)", fontsize=10)

    plt.show()
    return fig



#Calling the Load data function:
before_data, longitude, latitude = load_tempo_data(d_b4_blackout)
during_data, _, _ = load_tempo_data(d_in_blackout)  # We already have lon/lat from first call
after_data, _, _ = load_tempo_data(d_aft_blackout)

land_mask = create_land_mask(longitude, latitude)



d1, mean_in_blackout, mean_aft_blackout = compute_map_difference(during_data, after_data)
difference, mean_b4_blackout, mean_in_blackout = compute_map_difference(before_data, during_data)


    
masked_b4_blackout = apply_land_mask(mean_b4_blackout, land_mask)
masked_in_blackout = apply_land_mask(mean_in_blackout, land_mask)
masked_aft_blackout = apply_land_mask(mean_aft_blackout, land_mask)


test = [masked_b4_blackout, masked_in_blackout, masked_aft_blackout]
plot_map_subplots(test, 'NO₂ Concentrations Over Cuba (Land Areas Only)', subplot_titles, longitude, latitude)

#Plotting two subplots
def plot_map_subplots2(data_list, title, subplot_titles, longitude, latitude):
    """Plot multiple maps in subplots"""
    import numpy as np
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    # data_list: list containing [before_data, during_data, after_data]
    left = 0.05 # The position of the LEFT edge of the subplots, as a fraction of the figure width.
    bottom = 0.02 # The position of the BOTTOM edge of the subplots, as a fraction of the figure height.
    right = 0.85 # The position of the RIGHT edge of the subplots, as a fraction of the figure width.
    top = 0.9 # The position of the TOP edge of the subplots, as a fraction of the figure height.
    wspace = 0.02 # The WIDTH of the padding between subplots, as a fraction of the average Axes width.
    hspace = 0.3

    # Plot the results
    fig, axs = plt.subplots(2, 1, figsize=(10,8), subplot_kw={'projection': ccrs.PlateCarree()})

    # Add main title for the entire figure
    fig.suptitle('Differences in NO₂ Concentrations Over Cuba (Land Areas Only)', fontsize=14, y=0.97)

    # Subplot titles


    for idx in range(len(data_list)):
        # Add map features
        ax = axs[idx]
        ax.add_feature(cfeature.LAND, edgecolor='black')
        ax.add_feature(cfeature.COASTLINE)
        ax.set_extent([-85, -71, 19, 24], crs=ccrs.PlateCarree())

        # Add subplot title
        ax.set_title(subplot_titles[idx], pad=10, fontsize=12)

        # Extract plot data and ensure it's a NumPy array
        plot_data = data_list[idx]

        # Debug print to see what we're dealing with
        print(f"Plot {idx} - Type of data: {type(plot_data)}")

        # Convert to numpy array if it's a list
        if isinstance(plot_data, list):
            plot_data = np.array(plot_data)
            print(f"  - Converted to array, shape: {plot_data.shape}")

        # Extract 2D slice if it's 3D
        if plot_data.ndim == 3:
            plot_data = plot_data[0, :, :]
            print(f"  - Extracted 2D slice, shape: {plot_data.shape}")

        # Use imshow instead of pcolormesh to avoid dimension issues
        mesh = ax.imshow(
            plot_data,
            extent=[longitude.min(), longitude.max(), latitude.min(), latitude.max()],
            cmap=plt.get_cmap('bwr',21), 
            transform=ccrs.PlateCarree(),
            origin='lower',  # Important for correct orientation
            vmin=-4e15, 
            vmax=4e15
        )


    # Adjust the margins and the spaces between panels in the figure, using the parameters determined above.
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

    # Add an axis for a color bar.
    cax = fig.add_axes([right+0.02, bottom, 0.03, top-bottom])

    # Add colorbar and labels
    cbar = plt.colorbar(mesh, cax=cax)
    cbar.set_label("Vertical Column Troposphere (molecules/cm^2)", fontsize=10)

    plt.show()
    return fig






#Plotting Average over Cuba
fig = plot_map1(masked_b4_blackout,longitude, latitude, "Before Blackout 10/13-10/18")
fig = plot_map1(masked_in_blackout, longitude, latitude, "During Blackout 10/18-10/22")
fig = plot_map1(masked_aft_blackout, longitude, latitude, "After Blackout 10/22-10/27")


#Plotting differences
mean_b4_blackout = median(denoise_map(masked_b4_blackout)) 
mean_in_blackout = median(denoise_map(masked_in_blackout))
difference = np.subtract(mean_in_blackout, mean_b4_blackout)
difference1 = np.subtract(mean_aft_blackout, mean_b4_blackout)
fig = plot_map_diff(difference, longitude, latitude, "(During-Before Blackout)")
fig = plot_map_diff(difference1, longitude, latitude, "(After-Before Blackout)")


subplot_titles = ["(During-Before Blackout)",
                  "(After-Before Blackout)"]
test = [difference, difference1]

plot_map_subplots2(test, 'Difference Plots Over Cuba', subplot_titles, longitude, latitude)