
import os 
from glob import glob
from rutils import rio_fillna, get_raster_info,gdal_regrid
from uvars import chm_global_fn, dtm_global_fn,ot_basefiles_pattern,tile_dpath

# add time to the script, and make parallel 
files = glob(ot_basefiles_pattern)
 
for fi in files:
    tilename = fi.split('/')[-3]
    dout_path = os.path.join(tile_dpath,tilename)
    os.makedirs(dout_path, exist_ok=True)
    chm_tile = os.path.join(dout_path, f'{tilename}_{os.path.basename(chm_global_fn)}')
    dtm_tile = os.path.join(dout_path, f'{tilename}_{os.path.basename(dtm_global_fn)}')
    proj, xres, yres, xmin, xmax, ymin, ymax, w, h = get_raster_info(fi)

    if os.path.isfile(chm_tile) and os.path.isfile(dtm_tile):
        print(f'! {chm_tile} and {dtm_tile} already exist.')
    else:
        print(f'# Regridding {chm_tile} and {dtm_tile}...')
        gdal_regrid(chm_global_fn, chm_tile, xmin, ymin, xmax, ymax, xres, yres,mode="num", t_epsg='EPSG:4979', overwrite=False)
        gdal_regrid(dtm_global_fn, dtm_tile, xmin, ymin, xmax, ymax, xres, yres,mode="num", t_epsg='EPSG:4979', overwrite=False)

    dtm_tile_fil = dtm_tile.replace('.tif', '_riofill.tif')
    chm_tile_fil = chm_tile.replace('.tif', '_riofill.tif')


    if os.path.isfile(dtm_tile_fil) and os.path.isfile(chm_tile_fil):
        print(f'! {dtm_tile_fil} and {chm_tile_fil} already exist.')
        print('romeving files')
        os.remove(dtm_tile_fil)
        os.remove(chm_tile_fil)
    else:
        print(f'# Filling NoData values in \n{dtm_tile}... \n{chm_tile}...')
        rio_fillna(input_path=chm_tile, output_path=chm_tile_fil, smoothing_iterations=0)
        rio_fillna(input_path=dtm_tile, output_path=dtm_tile_fil, smoothing_iterations=0)