import os 
from glob import glob
from uvars import gedi_grid_dpath, base_files_dpathx
#,base_files_dpathx,text #, var1, var2
from utils import  gwr_grid_downscaling
import time 
from utils import select_base_file,select_filled_file,print_context



def tile_gwr_grid_downscaling(tilename, gedi_grid_dpath, base_files_dpathx, X):
    meth= 'riofill_si0.tif'
    var1 = 'elev' #'rh100'# 'elev'
    var2 = 'rh100'
    text = "mean_2019108_2022019_002_03_EPSG4326_riofill_si0"
    base_files_dpath = base_files_dpathx + str(X)

    ta = time.perf_counter()
    tile_lfiles = glob(f"{gedi_grid_dpath}/{tilename}/*.tif")
    tile_hfiles = glob(f"{base_files_dpath}/{tilename}/*.tif")
    print('*'*50)
    print(len(tile_lfiles), len(tile_hfiles))

    lfpath1 = select_filled_file(tile_lfiles, var1,meth)
    hfpath = select_base_file(tile_hfiles)
    rfpath1 = lfpath1.replace('.tif', f'_GWR_{str(X)}.sdat')
    rfpath1 = rfpath1.replace(text,'__').replace('elev_lowestmode','dtm')
    print_context(f"Processing {tilename} @{var1} \nSaving to {rfpath1}")
    gwr_grid_downscaling(xpath=hfpath, ypath=lfpath1, opath=rfpath1, oaux=False,epsg_code=4326,clean=True)

    lfpath2 = select_filled_file(tile_lfiles, var2,meth)
    rfpath2 = lfpath2.replace('.tif', f'_GWR_{str(X)}.sdat')
    rfpath2 = rfpath2.replace(text,'__').replace('rh100','dsm')
    
    print_context(f"Processing {tilename} @{var2}\nSaving to {rfpath2}")
    gwr_grid_downscaling(xpath=hfpath, ypath=lfpath2, opath=rfpath2, oaux=False,epsg_code=4326,clean=True)
    print('*'*50)
    tb = time.perf_counter() - ta
    print(f'runtime = {tb/60} mins')
    print(' ')
     

tilenames = sorted(os.listdir(gedi_grid_dpath), reverse=True)
XGRID_LIST = [90,30,12]# trying this out 
if __name__ == '__main__':
   
    ti = time.perf_counter()
    for X in XGRID_LIST:
        print('#---------------------------------------------------------#')
        for i,tilename in enumerate(tilenames):
            ta = time.perf_counter()
            print('#+++++++++++++++++++++++++++++++++++++++++++++++++++++++#')
            print(f'Processing {tilename} at {X}m')
            tile_gwr_grid_downscaling(tilename, gedi_grid_dpath, base_files_dpathx, X)
            tb = time.perf_counter() - ta 
            print(f'runtime = {tb/60} mins')
        
    tf = time.perf_counter() - ti 
    print(f'runtime = {tf/60} mins')







