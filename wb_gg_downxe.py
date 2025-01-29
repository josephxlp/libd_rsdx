import os 
from glob import glob
from uvars import gedi_grid_dpath,base_files_dpathx,text, var1, var2
from utils import  gwr_grid_downscaling
import time 
from utils import select_base_file,select_filled_file,print_context
from pprint import pprint

def select_hfile(tile_hfiles,X, name='tdem_DEM'):
    bfile = [i for i in tile_hfiles if name in i]
    if X == 12:
        excluded_suffixes = ('F.tif', 'M_M.tif', 'Fw.tif', 'Mw.tif', '__RIO_0.tif','VFILL')
    else:
        excluded_suffixes = (f'F_{X}.tif', f'M_M_{X}.tif', f'Fw_{X}.tif', 
                             f'Mw_{X}.tif', f'__RIO_0_{X}.tif', f'{X}_VFILL.tif',
                             'M__Fw.tif'
                             )
   
    filtered_bfile = [i for i in bfile if not i.endswith(excluded_suffixes)]
    print('#---------selected file-----------------#')
    pprint(filtered_bfile)
    assert len(filtered_bfile) == 1, f"More than one DEM file found in {os.path.dirname(tile_hfiles[0])}"
    return filtered_bfile[0]
    

tilenames = sorted(os.listdir(gedi_grid_dpath), reverse=True)

# this fucntions to be corrected to transform into the loop 
# if the tif exists, skipp []
meth= 'riofill_si0.tif'#'riofill_si0.tif'#'riofill'
bname = 'edem_W84'#options tdem_W84 and edem_W84
#tdem_W84##90:5mins #30:33mins #12:88mins
#edem_W84##12:
X = 12 
base_files_dpath = base_files_dpathx + str(X)

if __name__ == '__main__':
   
    ti = time.perf_counter()

    for i,tilename in enumerate(tilenames):
        #if i > 0: break
        
        ta = time.perf_counter()
        tile_lfiles = glob(f"{gedi_grid_dpath}/{tilename}/*.tif")
        tile_hfiles = glob(f"{base_files_dpath}/{tilename}/*.tif")
        print('*'*50)
        print(len(tile_lfiles), len(tile_hfiles))

        lfpath1 = select_filled_file(tile_lfiles, var1,meth)
        rfpath1 = lfpath1.replace('.tif', f'_GWR_{str(X)}.sdat')
        rfpath1 = rfpath1.replace(text,'_').replace('elev_lowestmode','dtm')

        lfpath2 = select_filled_file(tile_lfiles, var2,meth)
        rfpath2 = lfpath2.replace('.tif', f'_GWR_{str(X)}.sdat')
        rfpath2 = rfpath2.replace(text,'_').replace('rh100','dsm')

        if bname == 'edem_W84':
            hfpath = select_base_file(tile_hfiles)
            rfpath1 = rfpath1.replace('dtm','dtmE')
            rfpath2 = rfpath2.replace('dsm','dsmE')

        elif bname == 'tdem_W84':
            hfpath = select_hfile(tile_hfiles,X, name='tdem_DEM')
            rfpath1 = rfpath1.replace('dtm','dtmT')
            rfpath2 = rfpath2.replace('dsm','dsmT')

        
        # the check for the file is should be code inside the function from tifs 
        print_context(f"Processing {tilename} @{var1} \nSaving to {rfpath1}")
        gwr_grid_downscaling(xpath=hfpath, ypath=lfpath1, opath=rfpath1, oaux=False,epsg_code=4326,clean=True)

        
        print_context(f"Processing {tilename} @{var2}\nSaving to {rfpath2}")
        gwr_grid_downscaling(xpath=hfpath, ypath=lfpath2, opath=rfpath2, oaux=False,epsg_code=4326,clean=True)
        
        print('*'*50)
        
        print(f"Processing @@{rfpath1}")
        print(f"Processing @@{rfpath2}")
        tb = time.perf_counter() - ta
        print(f'runtime = {tb/60} mins')
        print(' ')
        
    
    tf = time.perf_counter() - ti 
    print(f'runtime = {tf/60} mins')







