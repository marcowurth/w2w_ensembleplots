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
from w2w_ensembleplots.core.download_forecast import convert_gribfiles_to_one_netcdf, interpolate_icon_grib_to_latlon


def main():

    # make lists of forecast hours and variables #

    fcst_hours_list_prec_rate = list(range(0,78,1)) + list(range(78,180+1,3))
    fcst_hours_list_6h = list(range(0,180+1,6))


    # get latest run time #

    date = calc_latest_run_time('icon-global-det')


    # explicit download options #

   ###########################################################
    #date = dict(year = 2020, month = 5, day = 14, hour = 12)
   ###########################################################

    print('download run_{}{:02}{:02}{:02}'.format(
           date['year'], date['month'], date['day'], date['hour']))


    # list of dwd variable names #

    var_list = [['tot_prec','sl'],['pmsl','sl'],['relhum','850hPa'],['t','850hPa'],['fi','500hPa'],
                ['fi','300hPa'],['u','300hPa'],['v','300hPa'],
                ['t_2m','sl'],['u_10m','sl'],['v_10m','sl'],['clct','sl']]
    vars_to_interpolate = [['pmsl','sl'],['fi','500hPa'],['fi','300hPa']]


    # create paths if necessary #

    path = dict(base = '/')
    path['grid'] = 'data/model_data/icon-global-det/grid/'
    path['data'] = 'data/model_data/icon-global-det/forecasts/run_{}{:02}{:02}{:02}'.format(
                    date['year'], date['month'], date['day'], date['hour'])
    if not os.path.isdir(path['base'] + path['data']):
        os.mkdir(path['base'] + path['data'])
    path['data'] = path['data'] + '/'

    for var in var_list:
        if var[1] == 'sl':      # sl = single-level
            temp_subdir = path['data'] + var[0]
        else:
            temp_subdir = path['data'] + var[0] + '_' + var[1]

        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)
        path['subdir'] = temp_subdir + '/'


        # download all grib files from website #

        if var[0] == 'tot_prec':
            fcst_hours_list = fcst_hours_list_prec_rate
        else:
            fcst_hours_list = fcst_hours_list_6h

        for fcst_hour in fcst_hours_list:
            if var[1] == 'sl':
                filename = 'icon_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2.bz2'.format(
                            date['year'], date['month'], date['day'], date['hour'], fcst_hour, var[0].upper())
            else:
                level = var[1][:3]
                filename = 'icon_global_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_{}_{}.grib2.bz2'.format(
                            date['year'], date['month'], date['day'], date['hour'], fcst_hour, level, var[0].upper())

            url = 'https://opendata.dwd.de/weather/nwp/icon/grib/{:02}/{}/'.format(
                   date['hour'], var[0])

            if download(url, filename, path):
                filename = unzip(path, filename)

            if var in  vars_to_interpolate:
                if var[1] == 'sl':
                    latlon_filename = 'icon-global-det_latlon_0.1_single-level_{}{:02}{:02}{:02}_{:03}h_{}.nc'.format(
                                       date['year'], date['month'], date['day'], date['hour'], fcst_hour, var[0])
                else:
                    level = var[1][:3]
                    latlon_filename = 'icon-global-det_latlon_0.1_pressure-level_{}{:02}{:02}{:02}_{:03}h_{}_{}.nc'.format(
                                       date['year'], date['month'], date['day'], date['hour'], fcst_hour, level, var[0])
                interpolate_icon_grib_to_latlon(path, filename, latlon_filename, 'icon-global-det')


        # read in all grib files of variable and save as one combined netcdf file #

        if var[1] == 'sl':
            grib_filename = 'icon_global_icosahedral_single-level_{}{:02}{:02}{:02}_*_{}.grib2'.format(
                             date['year'], date['month'], date['day'], date['hour'], var[0].upper())
            netcdf_filename = 'icon-global-det_icosahedral_single-level_{}{:02}{:02}{:02}_{}.nc'.format(
                               date['year'], date['month'], date['day'], date['hour'], var[0])
        else:
            level = var[1][:3]
            grib_filename = 'icon_global_icosahedral_pressure-level_{}{:02}{:02}{:02}_*_{}_{}.grib2'.format(
                             date['year'], date['month'], date['day'], date['hour'], level, var[0].upper())
            netcdf_filename = 'icon-global-det_icosahedral_pressure-level_{}{:02}{:02}{:02}_{}_{}.nc'.format(
                               date['year'], date['month'], date['day'], date['hour'], level, var[0])
        convert_gribfiles_to_one_netcdf(path, grib_filename, netcdf_filename, 'icon-global-det')

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
