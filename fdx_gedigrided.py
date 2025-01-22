import os 
from glob import glob
from uvars import gedi_grid_dpath,base_files_dpath
from utils import  gwr_grid_downscaling
import time 
from pprint import pprint

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
var = 'elev' #'rh100'# 'elev'
meth= 'riofill_si0.tif'#'riofill'

if __name__ == '__main__':
    ti = time.perf_counter()

    for tilename in tilenames:

        tile_lfiles = glob(f"{gedi_grid_dpath}/{tilename}/*.tif")
        tile_hfiles = glob(f"{base_files_dpath}/{tilename}/*.tif")


        lfpath = select_filled_file(tile_lfiles, var,meth)
        hfpath = select_base_file(tile_hfiles)
        rfpath = lfpath.replace('.tif', '_GWR.sdat')
        gwr_grid_downscaling(xpath=hfpath, ypath=lfpath, opath=rfpath, oaux=False,epsg_code=4326)
    
    tf = time.perf_counter() - ti 
    print(f'runtime = {tf/60} mins')


# arg parse to have two options  var meth, to run optional should be gedi_grid_dpath,base_files_dpath 





