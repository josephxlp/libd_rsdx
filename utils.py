import os 
import time
from pprint import pprint

def print_context(text):
    print(' ')
    """
    Prints the given text in a styled format, mimicking SAGA GIS console output.

    Parameters:
        text (str): The text to print.
    """
    # Border symbols
    border_char = "=" * 60
    padding_char = " " * 4

    # Print formatted text
    print(border_char)
    print(f"{padding_char}ML - Process Log")
    print(border_char)

    for line in text.split("\n"):
        print(f"{padding_char}{line}")

    print(border_char)

    

def select_base_file(tile_hfiles):
    bfile = [i for i in tile_hfiles if 'edem_W84' in i]
    pprint(bfile)
    assert len(bfile) == 1, 'More than 1 file were selected'
    return bfile[0]

def select_filled_file(files, var,meth):
    varpath = [i for i in files if var in i and meth in i]
    pprint(varpath)
    assert len(varpath) == 1, 'More than 1 file were selected'
    return varpath[0]


# def sdat_to_geotif(sdat_path, gtif_path, epsg_code=4979):
#     #if os.path.isfile(sdat_path):
#     #sdat_path = sdat_path.replace('.sgrd','.sdat')
#     if not os.path.isfile(gtif_path):
#         cmd = f'gdal_translate -a_srs EPSG:{epsg_code} -of GTiff {sdat_path} {gtif_path}'
#         os.system(cmd)
#         print('#convert sagasdat to geotiff file')
#     else:
#         print('!the file already created')

def sdat_to_geotif(sdat_path, gtif_path, epsg_code=4979):
    """
    Converts a Saga .sdat file to a GeoTIFF file using GDAL.

    Parameters:
        sdat_path (str): Path to the input .sdat file.
        gtif_path (str): Path to the output GeoTIFF file.
        epsg_code (int): EPSG code for the spatial reference system. Default is 4979.
    """
    # Ensure the input file has the correct extension
    if not sdat_path.endswith('.sdat'):
        sdat_path = sdat_path.replace('.sgrd', '.sdat')

    # Check if the output file already exists
    if os.path.isfile(gtif_path):
        print(f'! The file "{gtif_path}" already exists.')
        return

    # Construct and execute the GDAL command
    cmd = f'gdal_translate -a_srs EPSG:{epsg_code} -of GTiff "{sdat_path}" "{gtif_path}"'
    result = os.system(cmd)

    if result == 0:
        print(f'# Successfully converted "{sdat_path}" to "{gtif_path}".')
    else:
        print(f'! Failed to convert "{sdat_path}" to "{gtif_path}". Check the input files and GDAL installation.')



def gwr_grid_downscaling(xpath, ypath, opath, oaux=False,epsg_code=4979, clean=True):
    """
    Perform Geographically Weighted Regression (GWR) for grid downscaling.
    
    Parameters:
    - xpath (str): Path to the high-resolution DEM (predictor variable).
    - ypath (str): Path to the coarse-resolution data (dependent variable).
    - opath (str): Path to save the output SAGA grid (.sdat file).
    - oaux (bool, optional): If True, generate additional outputs like regression correction, quality, and residuals.

    Returns:
    - None: Saves the output files to the specified paths.

    Documentation:
    https://saga-gis.sourceforge.io/saga_tool_doc/8.2.2/statistics_regression_14.html
    """
    otif = opath.replace('.sdat', '.tif')

    # Construct the base SAGA command
    cmd = (
        f"saga_cmd statistics_regression 14 "
        f"-PREDICTORS {xpath} "
        f"-DEPENDENT {ypath} "
        f"-REGRESSION {opath} "
        f"-SEARCH_RANGE 0 "  # Local search range
        f"-DW_WEIGHTING 3 "  # Gaussian weighting
        f"-DW_BANDWIDTH 4 "  # Default bandwidth for Gaussian
        f"-MODEL_OUT 1"       # Output model parameters
    )

    if oaux:
        # Add optional outputs for residual correction, quality, and residuals
        opath_rescorr = opath.replace('.sdat', '_RESCORR.sdat')
        opath_quality = opath.replace('.sdat', '_QUALITY.sdat')
        opath_residuals = opath.replace('.sdat', '_RESIDUALS.sdat')
        cmd += (
            f" -REG_RESCORR {opath_rescorr} "
            f"-QUALITY {opath_quality} "
            f"-RESIDUALS {opath_residuals}"
        )

    # Run the SAGA command
    os.system(cmd)

    # Convert the output SAGA grid to GeoTIFF
    sdat_to_geotif(opath, otif,epsg_code)

    print("GWR Grid Downscaling completed.")
    if oaux:
        print(f"Additional outputs saved: \n{opath_rescorr}, \n{opath_quality}, \n{opath_residuals}")

    if clean:
        time.sleep(1)
        
        dirpath = os.path.dirname(opath)
        print(f'Cleaning up intermediate files...\n{dirpath}')
        for f in os.listdir(dirpath):
            if not f.endswith('.tif'):
                fo = os.path.join(dirpath, f)
                print(f'Removing {fo}...')
                os.remove(fo)


import numpy as np
import rasterio

def read_raster(raster_path):
    """
    Reads a raster file and returns the data array and profile.
    Args:
        raster_path (str): Path to the raster file.
    Returns:
        tuple: A tuple containing the raster data array and the metadata profile.
    """
    with rasterio.open(raster_path) as src:
        data = src.read(1)
        profile = src.profile
    return data, profile

def mask_nodata(data, nodata_value):
    # should include high and low values 
    """
    Masks out the nodata values in the raster data.
    Args:
        data (numpy.ndarray): The raster data.
        nodata_value (float): The nodata value to be masked.
    Returns:
        numpy.ndarray: The masked data array.
    """
    return np.where(data == nodata_value, np.nan, data)

def calculate_r_squared(observed, predicted):
    """
    Calculates the Coefficient of Determination (R²) between observed and predicted values.
    Args:
        observed (numpy.ndarray): The observed values.
        predicted (numpy.ndarray): The predicted values.
    Returns:
        float: The R² value.
    """
    ss_total = np.sum((observed - np.mean(observed)) ** 2)
    ss_residual = np.sum((observed - predicted) ** 2)
    return 1 - (ss_residual / ss_total)

def calculate_residuals(observed, predicted):
    """
    Calculates residuals (observed - predicted) for each grid cell.
    Args:
        observed (numpy.ndarray): The observed values.
        predicted (numpy.ndarray): The predicted values.
    Returns:
        numpy.ndarray: The residuals for each cell.
    """
    return observed - predicted

def write_raster(output_path, data, profile):
    """
    Writes the processed data to a new raster file.
    Args:
        output_path (str): The path where the output raster will be saved.
        data (numpy.ndarray): The data to be written to the raster.
        profile (dict): The metadata profile for the raster.
    """
    profile.update(dtype=rasterio.float32)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data.astype(rasterio.float32), 1)

def process_rasters(pred_raster_path, obs_raster_path, output_r_squared_path, output_residuals_path):
    """
    Processes prediction and observation rasters to compute R² and residuals.
    Args:
        pred_raster_path (str): Path to the prediction raster file.
        obs_raster_path (str): Path to the observation raster file.
        output_r_squared_path (str): Path to save the R² output raster.
        output_residuals_path (str): Path to save the residuals output raster.
    """
    # Read input rasters
    pred, pred_profile = read_raster(pred_raster_path)
    obs, obs_profile = read_raster(obs_raster_path)

    # Mask nodata values
    nodata = pred_profile.get('nodata', np.nan)
    pred = mask_nodata(pred, nodata)
    obs = mask_nodata(obs, nodata)

    # Initialize output arrays
    r_squared_grid = np.empty_like(pred)
    residuals_grid = np.empty_like(pred)

    # Loop through grid cells
    for i in range(pred.shape[0]):
        for j in range(pred.shape[1]):
            observed_value = obs[i, j]
            predicted_value = pred[i, j]
            if np.isnan(observed_value) or np.isnan(predicted_value):
                r_squared_grid[i, j] = np.nan
                residuals_grid[i, j] = np.nan
            else:
                # Calculate R² and residuals for each cell
                r_squared_grid[i, j] = calculate_r_squared(np.array([observed_value]), np.array([predicted_value]))
                residuals_grid[i, j] = calculate_residuals(observed_value, predicted_value)

    # Write output rasters
    write_raster(output_r_squared_path, r_squared_grid, pred_profile)
    write_raster(output_residuals_path, residuals_grid, pred_profile)

    print(f"R² and Residuals grids have been saved as '{output_r_squared_path}' and '{output_residuals_path}'.")



        