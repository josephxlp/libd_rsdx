import os 
from glob import glob
from uvars import gedi_grid_dpath,base_files_dpathx
from utils import  gwr_grid_downscaling
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


# remove all the unwanted files from the main function 
# rh100:90:
# elev:rh100
tilenames = os.listdir(gedi_grid_dpath)
#tilename = 'N09E105'
var1 = 'elev' #'rh100'# 'elev'
var2 = 'rh100'
meth= 'riofill_si0.tif'#'riofill'

X = 30 
base_files_dpath = base_files_dpathx + str(X)
if __name__ == '__main__':
    ti = time.perf_counter()

    for tilename in tilenames:

        tile_lfiles = glob(f"{gedi_grid_dpath}/{tilename}/*.tif")
        tile_hfiles = glob(f"{base_files_dpath}/{tilename}/*.tif")

        print(len(tile_lfiles), len(tile_hfiles))

        

        lfpath1 = select_filled_file(tile_lfiles, var1,meth)
        hfpath = select_base_file(tile_hfiles)
        rfpath1 = lfpath1.replace('.tif', f'_GWR_{str(X)}.sdat')
        print_context(f"Processing {tilename} @{var1} \nSaving to {rfpath1}")
        gwr_grid_downscaling(xpath=hfpath, ypath=lfpath1, opath=rfpath1, oaux=False,epsg_code=4326)

        
        lfpath2 = select_filled_file(tile_lfiles, var2,meth)
        rfpath2 = lfpath2.replace('.tif', f'_GWR_{str(X)}.sdat')
        print_context(f"Processing {tilename} @{var2}\nSaving to {rfpath2}")
        gwr_grid_downscaling(xpath=hfpath, ypath=lfpath2, opath=rfpath2, oaux=False,epsg_code=4326)

    
    tf = time.perf_counter() - ti 
    print(f'runtime = {tf/60} mins')


# arg parse to have two options  var meth, to run optional should be gedi_grid_dpath,base_files_dpath 





