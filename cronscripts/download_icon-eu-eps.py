############################################################################
###  script for downloading data from icon-eu-eps                        ###
###  downloads latest run                                                ###
############################################################################

import os

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import download, unzip, calc_latest_run_time


def main():

    # list of forecast hours #

    fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))


    # get latest run time #

    date = calc_latest_run_time('icon-eu-eps')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2019, month = 12, day = 13, hour = 6)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names and level types, sl: single level #

    if date['hour'] == 0 or date['hour'] == 12:
        var_list = [['tot_prec','sl'],['t_2m','sl'],['u_10m','sl'],['v_10m','sl'],['ps','sl'],['clct','sl'],
                    ['aswdir_s','sl'],['aswdifd_s','sl'],['vmax_10m','sl'],['tqv','sl'],
                    ['fi','500hPa'],['t','500hPa'],['u','500hPa'],['v','500hPa'],
                    ['fi','850hPa'],['t','850hPa'],['u','850hPa'],['v','850hPa']]

    elif date['hour'] == 6 or date['hour'] == 18:
        var_list = [['tot_prec','sl'],['t_2m','sl'],['u_10m','sl'],['v_10m','sl'],['ps','sl'],['clct','sl'],
                    ['aswdir_s','sl'],['aswdifd_s','sl'],['vmax_10m','sl']]


    # download data #
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/forecast_archive/icon-eu-eps/',\
                subdir = '')
    temp_subdir = 'raw_grib/run_{}{:02}{:02}{:02}'.format(
                   date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + temp_subdir):
        os.mkdir(path['base'] + temp_subdir)
    subdir_run = temp_subdir + '/'

    for var in var_list:
        if var[1] == 'sl':
            temp_subdir = subdir_run + var[0]
        else:
            temp_subdir = subdir_run + var[0] + '_' + var[1]

        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'

        for fcst_hour in fcst_hours_list:
            if var[0] == 'vmax_10m' and fcst_hour == 0:
                continue
            if var[1] == 'sl':
                filename = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                            date['year'], date['month'], date['day'], date['hour'], fcst_hour, var[0])
            else:
                level = var[1][:3]
                filename = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_{}_{}.grib2.bz2'\
                           .format( date['year'], date['month'], date['day'], date['hour'], fcst_hour, level, var[0])

            url = 'https://opendata.dwd.de/weather/nwp/icon-eu-eps/grib/{:02}/{}/'.format(
                   date['hour'], var[0])

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
