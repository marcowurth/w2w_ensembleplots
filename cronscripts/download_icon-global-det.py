############################################################################
###  script for downloading data from icon                               ###
###  downloads latest run                                                ###
############################################################################

import os

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import download, unzip, calc_latest_run_time


def main():

    ##### make lists of forecast hours and variables #####

    fcst_hours_list = list(range(0,78,1)) + list(range(78,180+1,3))


    # get latest run time #

    date = calc_latest_run_time('icon-global-det')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2019, month = 1, day = 1, hour = 0)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names #

    var_list = ['tot_prec','t_2m','u_10m','v_10m','clct']
    var_list_capitalized = ['TOT_PREC','T_2M','U_10M','V_10M','CLCT']


    # create paths if necessary #

    path = dict(base = '/')
    path['data'] = 'data/model_data/icon-global-det/forecasts/run_{}{:02}{:02}{:02}'.format(
                    date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + path['data']):
        os.mkdir(path['base'] + path['data'])
    path['data'] = path['data'] + '/'

    for i, var in enumerate(var_list):
        temp_subdir = path['data'] + var
        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'


        # download all grib files from website #

        for fcst_hour in fcst_hours_list:
            filename = 'icon_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                        date['year'], date['month'], date['day'], date['hour'], fcst_hour, var_list_capitalized[i])
            url = 'https://opendata.dwd.de/weather/nwp/icon/grib/{:02}/{}/'.format(
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
