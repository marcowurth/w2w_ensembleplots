############################################################################
###  script for downloading data from icon-eps                           ###
###  downloads latest run                                                ###
############################################################################

import os

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import download, unzip, calc_latest_run_time
from w2w_ensembleplots.core.download_forecast import convert_gribfiles_to_one_netcdf


def main():

    # list of forecast hours #

    fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120,6)) + list(range(120,180+1,12))


    # get latest run time #

    date = calc_latest_run_time('icon-global-eps')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2019, month = 5, day = 1, hour = 12)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names #

    var_list = ['tot_prec','t_2m','u_10m','v_10m','clct']


    # create paths if necessary #

    path = dict(base = '/')
    path['data'] = 'data/model_data/icon-global-eps/forecasts/run_{}{:02}{:02}{:02}'.format(
                    date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + path['data']):
        os.mkdir(path['base'] + path['data'])
    path['data'] = path['data'] + '/'

    for var in var_list:
        temp_subdir = path['data'] + var
        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'


        # download all grib files from website #

        for fcst_hour in fcst_hours_list:
            filename = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                        date['year'], date['month'], date['day'], date['hour'], fcst_hour, var)
            url = 'https://opendata.dwd.de/weather/nwp/icon-eps/grib/{:02}/{}/'.format(
                   date['hour'], var)

            if download(url, filename, path):
                filename = unzip(path, filename)


        # read in all grib files of variable and save as one combined netcdf file #

        grib_filename = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_*_{}.grib2'.format(
                         date['year'], date['month'], date['day'], date['hour'], var)
        netcdf_filename = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{}.nc'.format(
                           date['year'], date['month'], date['day'], date['hour'], var)
        convert_gribfiles_to_one_netcdf(path, grib_filename, netcdf_filename)

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))
