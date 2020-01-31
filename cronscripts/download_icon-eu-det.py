############################################################################
###  script for downloading data from icon-eu                            ###
###  downloads latest run                                                ###
############################################################################

import os

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import download, unzip, calc_latest_run_time


def main():

    # make lists of forecast hours and variables #

    fcst_hours_list = list(range(0,78,1)) + list(range(78,120+1,3))


    # get latest run time #

    date = calc_latest_run_time('icon-eu-det')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2019, month = 4, day = 10, hour = 12)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names #

    var_list = ['tot_prec','t_2m','u_10m','v_10m','pmsl','clct','aswdir_s','aswdifd_s']
    var_list_capitalized = ['TOT_PREC','T_2M','U_10M','V_10M','PMSL','CLCT','ASWDIR_S','ASWDIFD_S']


    # download data #
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/')
    path['data'] = 'forecast_archive/icon-eu/raw_grib/run_{}{:02}{:02}{:02}'.format(
                    date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + path['data']):
        os.mkdir(path['base'] + path['data'])
    path['data'] = path['data'] + '/'

    for i, var in enumerate(var_list):
        temp_subdir = path['data'] + var
        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'

        for fcst_hour in fcst_hours_list:
            filename = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                        date['year'], date['month'], date['day'], date['hour'], fcst_hour, var_list_capitalized[i])
            url = 'https://opendata.dwd.de/weather/nwp/icon-eu/grib/{:02}/{}/'.format(
                   date['hour'], var)

            if download(url, filename, path):
                filename = unzip(path, filename)

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
