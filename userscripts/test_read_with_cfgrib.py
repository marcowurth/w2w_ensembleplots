
import numpy as np
import xarray as xr
import time
t_start = time.time()


path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
            grib_folder = 'forecast_archive/icon-eu-eps/raw_grib/run_2019121918/t_2m/')


filename = 'icon-eu-eps_europe_icosahedral_single-level_2019121918_*_t_2m.grib2'
ds = xr.open_mfdataset(path['base'] + path['grib_folder'] + filename,
                       engine='cfgrib', combine='nested', concat_dim='step', parallel=False)

print(ds)




print('script time:  {:.0f}ms'.format( 1000 * (time.time() - t_start) ))
