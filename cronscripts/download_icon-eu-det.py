############################################################################
###  script for downloading data from icon-eu                            ###
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

    # make lists of forecast hours and variables #

    fcst_hours_list_6h = list(range(0,120+1,6))
    fcst_hours_list_1h3h = list(range(0,78,1)) + list(range(78,120+1,3))


    # get latest run time #

    date = calc_latest_run_time('icon-eu-det')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2019, month = 4, day = 10, hour = 12)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names #

    if date['hour'] == 0 or date['hour'] == 12:
        var_list = ['synmsg_bt_cl_ir10.8','tot_prec','vmax_10m','t_2m','u_10m','v_10m','pmsl','clct',
                    'aswdir_s','aswdifd_s']
    else:
        var_list = ['tot_prec','t_2m','u_10m','v_10m','pmsl','clct','aswdir_s','aswdifd_s','vmax_10m']


    # create paths if necessary

    path = dict(base = '/')
    path['data'] = 'data/model_data/icon-eu-det/forecasts/run_{}{:02}{:02}{:02}'.format(
                    date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + path['data']):
        os.mkdir(path['base'] + path['data'])
    path['data'] = path['data'] + '/'

    for var in var_list:
        temp_subdir = path['data'] + var
        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'


        # download all grib files from website

        if var == 'synmsg_bt_cl_ir10.8':
            fcst_hours_list = fcst_hours_list_6h
        else:
            fcst_hours_list = fcst_hours_list_1h3h

        for fcst_hour in fcst_hours_list:
            filename = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                        date['year'], date['month'], date['day'], date['hour'], fcst_hour, var.upper())
            url = 'https://opendata.dwd.de/weather/nwp/icon-eu/grib/{:02}/{}/'.format(
                   date['hour'], var)

            if download(url, filename, path):
                filename = unzip(path, filename)


        # read in all grib files of variable and save as one combined netcdf file #

        grib_filename = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_*_{}.grib2'.format(
                         date['year'], date['month'], date['day'], date['hour'], var.upper())
        netcdf_filename = 'icon-eu-det_latlon_0.0625_single-level_{}{:02}{:02}{:02}_{}.nc'.format(
                           date['year'], date['month'], date['day'], date['hour'], var)
        convert_gribfiles_to_one_netcdf(path, grib_filename, netcdf_filename, 'icon-eu-det')

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.1f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
