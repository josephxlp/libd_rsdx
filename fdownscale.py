

from os.path import basename, join
import time 
from uvars import lfpath, hfpath, out_dpath,epsg_code
from utils import gwr_grid_downscaling



if __name__ == '__main__':
    rfpath = join(out_dpath, basename(lfpath).replace('.tif', '_GWR.sdat'))
    ti = time.perf_counter()
    gwr_grid_downscaling(xpath=hfpath, ypath=lfpath, opath=rfpath, oaux=True,epsg_code=epsg_code)

    tf = time.perf_counter() - ti 
    print(f'run.tim {tf/60} mins')



