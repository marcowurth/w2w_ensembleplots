#########################################
###  container for various functions  ###
#########################################

import os
import numpy as np
import eccodes
from astropy.table import Table
from astropy.io import ascii

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.grid_information_around_point import which_grid_point
from w2w_ensembleplots.core.grid_information_around_point import get_latlon_filter_distance


########################################################################
########################################################################
########################################################################

def point_savetofile_iconeudet(pointnames, date_user, var, pointname, one_run_one_city, verbose):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list = list(range(0,78,1)) + list(range(78,120+1,3))
    model = 'icon-eu-det'

    if one_run_one_city:
        var_list = [var]
        pointnames = [pointname]
        date = date_user
    else:
        var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','aswdir_s','aswdifd_s']

        date = calc_latest_run_time('icon-eu-det')

        if date_user is not None:
            date = date_user

        print('-- Run time: {}{:02}{:02}-{:02}UTC --'.format(\
              date['year'], date['month'], date['day'], date['hour']))


    ##### make path #####
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/forecast_archive/icon-eu/',\
                raw_data = '',\
                raw_data_u = '',\
                raw_data_v = '',\
                points = '',\
                grid = 'grid/')
    temp_subdir = 'extracted_points/run_{}{:02}{:02}{:02}'.format(\
                    date['year'], date['month'], date['day'], date['hour'])

    if not os.path.isdir(path['base'] + temp_subdir): #and pointnames[0] == 'Karlsruhe':
        os.mkdir(path['base'] + temp_subdir)
    subdir_run = temp_subdir + '/'

    filenames = dict(clat = '',\
                     clon = '',\
                     var = '',\
                     var_u = '',\
                     var_v = '')
    filenames['clat'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLAT.grib2'
    filenames['clon'] = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLON.grib2'


    ##### main loop #####

    for var in var_list:
        temp_subdir = subdir_run + var
        if len(pointnames) == 1:
            if not os.path.isdir(path['base'] + temp_subdir):
                os.mkdir(path['base'] + temp_subdir)
        else:
            if not os.path.isdir(path['base'] + temp_subdir) and pointnames[0] == 'Karlsruhe':
                os.mkdir(path['base'] + temp_subdir)

        path['points'] = temp_subdir + '/'

        for pointname in pointnames:
            if verbose and not one_run_one_city:
                print('----- variable is {} -----'.format(var))
                print('----- next point is {} -----'.format(pointname))

            point_index = get_point_index(path, filenames, pointname, model)

            data = np.zeros((len(fcst_hours_list)), dtype='float32')


            ##### main loop #####

            for i in range(len(fcst_hours_list)):
                #if verbose and not one_run_one_city:
                #    print('read {:03}h...'.format(fcst_hours_list[i]))

                if var == 't_2m':
                    meta = dict(var = 'Temperature at 2m', units = 'degree celsius')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_T_2M.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'prec_rate':
                    meta = dict(var = 'Total Precipitation Rate, Average of Time Interval before fcst_hour', units = 'mm/h')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_TOT_PREC.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'prec_sum':
                    meta = dict(var = 'Total Precipitation Sum', units = 'mm')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_TOT_PREC.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'wind_10m':
                    meta = dict(var = 'Momentary Wind Speed at 10m', units = 'km/h')
                    path['raw_data_u'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_u'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_U_10M.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_V_10M.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'mslp':
                    meta = dict(var = 'Mean Sea Level Pressure', units = 'hPa')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/pmsl/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_PMSL.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'clct':
                    meta = dict(var = 'Total Cloud Cover', units = 'percent')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_CLCT.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'aswdir_s':
                    meta = dict(var = 'Direct Downward Shortwave Radiation, Average of Time Interval before fcst_hour', units = 'W/m^2')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_ASWDIR_S.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'aswdifd_s':
                    meta = dict(var = 'Diffuse Downward Shortwave Radiation, Average of Time Interval before fcst_hour', units = 'W/m^2')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu_europe_regular-lat-lon_single-level_{}{:02}{:02}{:02}_{:03}_ASWDIFD_S.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                data[i] = get_value_eu_det(path, filenames, var, point_index)


            if var == 'aswdir_s' or var == 'aswdifd_s':
                save_values(calculate_inst_values_of_avg(data, fcst_hours_list, model),
                            fcst_hours_list[1:], path, date, pointname, var, meta, model)
            elif var == 'prec_rate':
                save_values(calculate_inst_values_of_sum(data, fcst_hours_list, var, model),
                            fcst_hours_list[1:], path, date, pointname, var, meta, model)
            else:
                save_values(data, fcst_hours_list, path, date, pointname, var, meta, model)

    return

########################################################################
########################################################################
########################################################################

def point_savetofile_iconeueps(pointnames, date_user, var, pointname, one_run_one_city, verbose):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
    model = 'icon-eu-eps'

    if one_run_one_city:
        var_list = [var]
        pointnames = [pointname]
        date = date_user
    else:
        date = calc_latest_run_time('icon-eu-eps')

        if date_user is not None:
            date = date_user

        print('-- Run time: {}{:02}{:02}-{:02}UTC --'.format(\
              date['year'], date['month'], date['day'], date['hour']))

        if date['hour'] == 0 or date['hour'] == 12:
            #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','aswdir_s','aswdifd_s','vmax_10m',\
            #            'tqv','gph_500hPa','t_850hPa','wind_850hPa','shear_0-6km','lapse_rate_850hPa-500hPa']
            var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','aswdir_s','aswdifd_s','t_850hPa']

        elif date['hour'] == 6 or date['hour'] == 18:
            #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','aswdir_s','aswdifd_s','vmax_10m']
            var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','aswdir_s','aswdifd_s']


    ##### make path #####
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/forecast_archive/icon-eu-eps/',\
                raw_data = '',\
                raw_data_u = '',\
                raw_data_v = '',\
                raw_data_t_red = '',\
                raw_data_u_10m = '',\
                raw_data_v_10m = '',\
                raw_data_u_500hPa = '',\
                raw_data_v_500hPa = '',\
                raw_data_t_850hPa = '',\
                raw_data_g_850hPa = '',\
                raw_data_t_500hPa = '',\
                raw_data_g_500hPa = '',\
                invariant = 'invariant/',\
                points = '',\
                grid = 'grid/')
    temp_subdir = 'extracted_points/run_{}{:02}{:02}{:02}'.format(\
                    date['year'], date['month'], date['day'], date['hour'])

    if not os.path.isdir(path['base'] + temp_subdir) and pointnames[0] == 'Karlsruhe':
        os.mkdir(path['base'] + temp_subdir)
    subdir_run = temp_subdir + '/'

    filenames = dict(clat = '',\
                     clon = '',\
                     var = '',\
                     var_u = '',\
                     var_v = '',\
                     var_t_red = '',\
                     var_u_10m = '',\
                     var_v_10m = '',\
                     var_u_500hPa = '',\
                     var_v_500hPa = '',\
                     var_t_850hPa = '',\
                     var_g_850hPa = '',\
                     var_t_500hPa = '',\
                     var_g_500hPa = '',\
                     topo = '')
    filenames['clat'] = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clat.grib2'
    filenames['clon'] = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clon.grib2'


    ##### main loop #####

    for var in var_list:
        temp_subdir = subdir_run + var
        if len(pointnames) == 1:
            if not os.path.isdir(path['base'] + temp_subdir) and pointnames[0] == 'Karlsruhe':
                os.mkdir(path['base'] + temp_subdir)
        else:
            if not os.path.isdir(path['base'] + temp_subdir) and pointnames[0] == 'Karlsruhe':
                os.mkdir(path['base'] + temp_subdir)
        path['points'] = temp_subdir + '/'

        for pointname in pointnames:
            if verbose:# and not one_run_one_city:
                print('----- variable is {} -----'.format(var))
                print('----- next point is {} -----'.format(pointname))

            point_index = get_point_index(path, filenames, pointname, model)

            data = np.zeros((len(fcst_hours_list),40), dtype='float32')


            ##### main loop #####

            for i in range(len(fcst_hours_list)):
                #if verbose and not one_run_one_city:
                #    print('read {:03}h...'.format(fcst_hours_list[i]))

                if var == 'vmax_10m' and fcst_hours_list[i] == 0:
                    continue

                if var == 't_2m':
                    meta = dict(var = 'Temperature at 2m', units = 'degree celsius')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'prec_rate':
                    meta = dict(var = 'Total Precipitation Rate, Average of Time Interval before fcst_hour', units = 'mm/h')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_tot_prec.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'prec_sum':
                    meta = dict(var = 'Total Precipitation Sum', units = 'mm')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_tot_prec.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'wind_10m':
                    meta = dict(var = 'Momentary Wind Speed at 10m', units = 'km/h')
                    path['raw_data_u'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_u'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_u_10m.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_v_10m.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'mslp':
                    meta = dict(var = 'Mean Sea Level Pressure', units = 'hPa')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/ps/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_t_red'] = 'raw_grib/run_{}{:02}{:02}{:02}/t_2m/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_ps.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_t_red'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_t_2m.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['topo'] = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121312_hsurf.grib2'

                elif var == 'clct':
                    meta = dict(var = 'Total Cloud Cover', units = 'percent')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'aswdir_s':
                    meta = dict(var = 'Direct Downward Shortwave Radiation, Average of Time Interval before fcst_hour', units = 'W/m^2')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'aswdifd_s':
                    meta = dict(var = 'Diffuse Downward Shortwave Radiation, Average of Time Interval before fcst_hour', units = 'W/m^2')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'vmax_10m':
                    meta = dict(var = 'Wind Gust at 10m, Maximum of Time Interval before fcst_hour', units = 'km/h')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'tqv':
                    meta = dict(var = 'Total Column Integrated Water Vapour', units = 'mm')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 't_850hPa':
                    meta = dict(var = 'Temperature at 850hPa', units = 'degree celsius')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_850_t.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'wind_850hPa':
                    meta = dict(var = 'Momentary Wind Speed at 850hPa', units = 'km/h')
                    path['raw_data_u'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_850hPa/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_850hPa/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_u'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_850_u.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_850_v.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'gph_500hPa':
                    meta = dict(var = 'Geopotential Height at 500hPa', units = 'gpdm')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/fi_500hPa/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_500_fi.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'shear_0-6km':
                    meta = dict(var = 'Momentary Vertical Wind Shear 0-6km (Difference of 10m and 500hPa Wind Vector)', units = 'm/s')
                    path['raw_data_u_10m'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_10m/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v_10m'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_10m/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_u_500hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_500hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v_500hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_500hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_u_10m'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_u_10m.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v_10m'] = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_v_10m.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_u_500hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_500_u.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v_500hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_500_v.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'lapse_rate_850hPa-500hPa':
                    meta = dict(var = 'Mean Lapse Rate 850hPa-500hPa', units = 'K/km')
                    path['raw_data_t_850hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/t_850hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_g_850hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/fi_850hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_t_500hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/t_500hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_g_500hPa'] = 'raw_grib/run_{}{:02}{:02}{:02}/fi_500hPa/'.format(\
                                                    date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_t_850hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_850_t.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_g_850hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_850_fi.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_t_500hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_500_t.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_g_500hPa'] = 'icon-eu-eps_europe_icosahedral_pressure-level_{}{:02}{:02}{:02}_{:03}_500_fi.grib2'.format(\
                                                date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])


                data[i,:] = get_value(path, filenames, var, point_index)

            if var == 'aswdir_s' or var == 'aswdifd_s':
                save_values(calculate_inst_values_of_avg(data, fcst_hours_list, model),
                            fcst_hours_list[1:], path, date, pointname, var, meta, model)
            elif var == 'prec_rate':
                save_values(calculate_inst_values_of_sum(data, fcst_hours_list, var, model),
                            fcst_hours_list[1:], path, date, pointname, var, meta, model)
            else:
                save_values(data, fcst_hours_list, path, date, pointname, var, meta, model)

    return
    
########################################################################
########################################################################
########################################################################

def point_savetofile_iconglobaleps(pointnames, date_user, var, pointname, one_run_one_city, verbose):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list = list(range(132,180+1,12))
    model = 'icon-global-eps'

    if one_run_one_city:
        var_list = [var]
        pointnames = [pointname]
        date = date_user
    else:
        var_list = ['t_2m','prec_sum','prec_rate','wind_10m','clct']

        date = calc_latest_run_time('icon-global-eps')

        if date_user is not None:
            date = date_user

        print('-- Run time: {}{:02}{:02}-{:02}UTC --'.format(\
              date['year'], date['month'], date['day'], date['hour']))


    ##### make path #####
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/forecast_archive/icon-eps/',\
                raw_data = '',
                raw_data_u = '',
                raw_data_v = '',
                points = '',
                grid = 'grid/')
    temp_subdir = 'extracted_points/run_{}{:02}{:02}{:02}'.format(\
                    date['year'], date['month'], date['day'], date['hour'])

    if not os.path.isdir(path['base'] + temp_subdir): #and pointnames[0] == 'Karlsruhe':
        os.mkdir(path['base'] + temp_subdir)
    subdir_run = temp_subdir + '/'

    filenames = dict(clat = '',
                     clon = '',
                     var = '',
                     var_u = '',
                     var_v = '')
    filenames['clat'] = 'icon-eps_global_icosahedral_time-invariant_2019010800_clat.grib2'
    filenames['clon'] = 'icon-eps_global_icosahedral_time-invariant_2019010800_clon.grib2'


    ##### main loop #####

    for var in var_list:
        temp_subdir = subdir_run + var
        if len(pointnames) == 1:
            if not os.path.isdir(path['base'] + temp_subdir):
                os.mkdir(path['base'] + temp_subdir)
        else:
            if not os.path.isdir(path['base'] + temp_subdir) and pointnames[0] == 'Karlsruhe':
                os.mkdir(path['base'] + temp_subdir)

        path['points'] = temp_subdir + '/'

        for pointname in pointnames:
            if verbose and not one_run_one_city:
                print('----- variable is {} -----'.format(var))
                print('----- next point is {} -----'.format(pointname))

            point_index = get_point_index(path, filenames, pointname, model)

            if var == 'prec_rate':
                data = np.zeros((len(fcst_hours_list)+1,40), dtype='float32')
            else:
                data = np.zeros((len(fcst_hours_list),40), dtype='float32')


            ##### main loop #####

            for i in range(len(fcst_hours_list)):
                #if verbose and not one_run_one_city:
                #    print('read {:03}h...'.format(fcst_hours_list[i]))

                if var == 't_2m':
                    meta = dict(var = 'Temperature at 2m', units = 'degree celsius')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                elif var == 'prec_rate':
                    meta = dict(var = 'Total Precipitation Rate, Average of Time Interval before fcst_hour', units = 'mm/h')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_tot_prec.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'prec_sum':
                    meta = dict(var = 'Total Precipitation Sum', units = 'mm')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'])
                    filenames['var'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_tot_prec.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'wind_10m':
                    meta = dict(var = 'Momentary Wind Speed at 10m', units = 'km/h')
                    path['raw_data_u'] = 'raw_grib/run_{}{:02}{:02}{:02}/u_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    path['raw_data_v'] = 'raw_grib/run_{}{:02}{:02}{:02}/v_10m/'.format(\
                                            date['year'], date['month'], date['day'], date['hour'])
                    filenames['var_u'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_u_10m.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])
                    filenames['var_v'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_v_10m.grib2'.format(\
                                            date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i])

                elif var == 'clct':
                    meta = dict(var = 'Total Cloud Cover', units = 'percent')
                    path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], var)
                    filenames['var'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                                        date['year'], date['month'], date['day'], date['hour'], fcst_hours_list[i], var)

                if var == 'prec_rate':
                    data[i+1,:] = get_value(path, filenames, var, point_index)
                else:
                    data[i,:] = get_value(path, filenames, var, point_index)


            ##### get initial prec_sum value for prec_rate calculation #####

            if var == 'prec_rate':
                path['raw_data'] = 'raw_grib/run_{}{:02}{:02}{:02}/tot_prec/'.format(\
                                    date['year'], date['month'], date['day'], date['hour'])
                filenames['var'] = 'icon-eps_global_icosahedral_single-level_{}{:02}{:02}{:02}_120_tot_prec.grib2'.format(\
                                    date['year'], date['month'], date['day'], date['hour'])
                data[0,:] = get_value(path, filenames, var, point_index)


            ##### save values and calculate prec_rate values of sum values #####

            if var == 'prec_rate':
                fcst_hours_list_prec_rate = [120] + fcst_hours_list
                save_values(calculate_inst_values_of_sum(data, fcst_hours_list_prec_rate, var, model),
                            fcst_hours_list_prec_rate[1:], path, date, pointname, var, meta, model)
            else:
                save_values(data, fcst_hours_list, path, date, pointname, var, meta, model)

    return

########################################################################
########################################################################
########################################################################

def calculate_inst_values_of_avg(data_avg, fcst_hours_list, model):
    # aswdir_s, aswdifd_s
    if model == 'icon-eu-eps' or model == 'icon-global-eps':
        data_inst = np.zeros((len(fcst_hours_list)-1,40), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i,:] = (fcst_hours_list[i+1]*data_avg[i+1,:] - fcst_hours_list[i]*data_avg[i,:])\
                                 / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    elif model == 'icon-eu-det':
        data_inst = np.zeros((len(fcst_hours_list)-1), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i] = (fcst_hours_list[i+1]*data_avg[i+1] - fcst_hours_list[i]*data_avg[i])\
                                 / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    data_inst = np.where(data_inst >= 0., data_inst, 0.)
    data_inst = np.around(data_inst, 1)

    return data_inst


def calculate_inst_values_of_sum(data_avg, fcst_hours_list, var, model):
    # prec_rate
    if model == 'icon-eu-eps' or model == 'icon-global-eps':
        data_inst = np.zeros((len(fcst_hours_list)-1,40), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i,:] = (data_avg[i+1,:] - data_avg[i,:]) / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    elif model == 'icon-eu-det':
        data_inst = np.zeros((len(fcst_hours_list)-1), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i] = (data_avg[i+1] - data_avg[i]) / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    if var == 'prec_rate':
        data_inst = np.where(data_inst >= 0.0, data_inst, 0.0)
    data_inst = np.around(data_inst, 2)

    return data_inst

########################################################################
########################################################################
########################################################################

def get_value_eu_det(path, filename_dict, var, index_nearest):

    # read data

    if var == 'wind_10m':
        with open(path['base'] + path['raw_data_u'] + filename_dict['var_u'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            data_u = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        with open(path['base'] + path['raw_data_v'] + filename_dict['var_v'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            data_v = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        value = np.sqrt(data_u[index_nearest]*data_u[index_nearest] + data_v[index_nearest]*data_v[index_nearest]) * 3.6

    else:
        with open(path['base'] + path['raw_data'] + filename_dict['var'],'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        value = data[index_nearest]

        if var == 't_2m':
            value -= 273.15
        if var == 'mslp':
            value = value * 0.01

    return value

########################################################################
########################################################################
########################################################################

def get_point_index(path, filename_dict, pointname, model):

    # get grid point location

    point = which_grid_point(pointname, model)


    # get clat and clon 1D arrays

    with open(path['base'] + path['grid'] + filename_dict['clat'],'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clat = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)
    with open(path['base'] + path['grid'] + filename_dict['clon'],'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clon = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)

    # read out index of native point

    filter_distance = get_latlon_filter_distance(model)
    lat_near = list(np.where(abs(clat - point['lat']) < filter_distance)[0])
    lon_near = list(np.where(abs(clon - point['lon']) < filter_distance)[0])
    id_near = list(set(lat_near).intersection(lon_near))
    id_near.sort()
    distances = np.sqrt( np.square(abs(clat[id_near] - point['lat']) * 111.2) \
                        + np.square(abs(clon[id_near] - point['lon']) * 111.2 \
                                                 * np.cos(point['lat']*np.pi/180)) )
    index_nearest = id_near[np.argmin(distances)]

    #print(id_near)
    #print(distances)
    #print(index_nearest)
    #print(clat[index_nearest], clon[index_nearest])

    return index_nearest

########################################################################
########################################################################
########################################################################

def get_value(path, filename_dict, var, index_nearest):

    # read data

    values = np.zeros((40), dtype='float32')
    for member in range(1,41):
        if var == 't_2m':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest] - 273.15

        elif var == 'prec_rate' or var == 'prec_sum':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest]

        elif var == 'wind_10m':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_u'] + filename_dict['var_u'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_u = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_v'] + filename_dict['var_v'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_v = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = np.sqrt(data_u[index_nearest]*data_u[index_nearest]\
                                       + data_v[index_nearest]*data_v[index_nearest]) * 3.6

        elif var == 'mslp':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_ps = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_t_red'] + filename_dict['var_t_red'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_t_2m = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            with open(path['base'] + path['invariant'] + filename_dict['topo'],'rb') as file:
                grib_id = eccodes.codes_grib_new_from_file(file)
                topo_hgt = eccodes.codes_get_array(grib_id, 'values')
                eccodes.codes_release(grib_id)

            # reduce surface pressure to sea level with DWD formula and height and t2m:
            values[member-1] = data_ps[index_nearest] * 0.01\
                                * np.exp(9.80665*topo_hgt[index_nearest]/(287.05*data_t_2m[index_nearest]))

        elif var == 'clct':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest]

        elif var == 'aswdir_s':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest]

        elif var == 'aswdifd_s':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest]

        elif var == 'vmax_10m':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest] * 3.6

        elif var == 'tqv':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest]

        elif var == 't_850hPa':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest] - 273.15

        elif var == 'wind_850hPa':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_u'] + filename_dict['var_u'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_u = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_v'] + filename_dict['var_v'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_v = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = np.sqrt(data_u[index_nearest]*data_u[index_nearest]\
                                       + data_v[index_nearest]*data_v[index_nearest]) * 3.6

        elif var == 'gph_500hPa':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data'] + filename_dict['var'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = data[index_nearest] / 98.0665

        elif var == 'shear_0-6km':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_u_10m'] + filename_dict['var_u_10m'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_u_10m = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_v_10m'] + filename_dict['var_v_10m'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_v_10m = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_u_500hPa'] + filename_dict['var_u_500hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_u_500hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_v_500hPa'] + filename_dict['var_v_500hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_v_500hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = np.sqrt((data_u_500hPa[index_nearest]-data_u_10m[index_nearest])**2\
                                       + (data_v_500hPa[index_nearest]-data_v_10m[index_nearest])**2)

        elif var == 'lapse_rate_850hPa-500hPa':
            index_list = ['perturbationNumber']
            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_t_850hPa'] + filename_dict['var_t_850hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_t_850hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_g_850hPa'] + filename_dict['var_g_850hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_g_850hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_t_500hPa'] + filename_dict['var_t_500hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_t_500hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            index_id = eccodes.codes_index_new_from_file(\
                path['base'] + path['raw_data_g_500hPa'] + filename_dict['var_g_500hPa'], index_list)
            eccodes.codes_index_select(index_id, 'perturbationNumber', member)
            grib_id = eccodes.codes_new_from_index(index_id)
            if grib_id is None:
                print('error: grib_id is None, msg selection failed')
                exit()
            data_g_500hPa = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_index_release(index_id)
            eccodes.codes_release(grib_id)

            values[member-1] = (data_t_850hPa[index_nearest]-data_t_500hPa[index_nearest])*9806.65\
                                / (data_g_500hPa[index_nearest]-data_g_850hPa[index_nearest])

    return values

############################################################################
############################################################################
############################################################################

def save_values(data_source, fcst_hours_list, path, date, pointname, variable, meta, model):

    # write forecast times

    data = []
    if variable == 'vmax_10m':
        data.append(fcst_hours_list[1:])
    else:
        data.append(fcst_hours_list)


    # print data values to string matrix

    if model == 'icon-eu-eps' or model == 'icon-global-eps':
        for column in range(40):
            data_column = []
            for row in range(len(fcst_hours_list)):
                if variable == 'vmax_10m' and row == 0:
                    continue
                value = data_source[row, column]
                if abs(value) < 0.01:
                    value_str = '{:.0f}'.format(value)
                else:
                    value_str = '{:.2f}'.format(value)
                data_column.append(value_str)
            data.append(data_column)

        # make  header

        header = [str(x) for x in range(1,41)]
        header.insert(0,'fcst_hour')

    elif model == 'icon-eu-det':
        data_column = []
        for row in range(len(fcst_hours_list)):
            value = data_source[row]
            if abs(value) < 0.01:
                value_str = '{:.0f}'.format(value)
            else:
                value_str = '{:.2f}'.format(value)
            data_column.append(value_str)
        data.append(data_column)

        # make  header

        header = ['fcst_hour','det']

    # make astropy table and add meta data

    t = Table(data, names=header)
    str1 = 'variable: {}'.format(meta['var'])
    str2 = 'units: {}'.format(meta['units'])
    t.meta['comments'] = [str1, str2, '']

    # write table to file
    if model == 'icon-global-eps':
        model_str = 'icon-eps'
    else:
        model_str = model
    filename = '{}_{}{:02}{:02}{:02}_{}_{}.txt'.format(\
            model_str, date['year'], date['month'], date['day'], date['hour'], variable, pointname)

    ascii.write(t, output=path['base'] + path['points'] + filename, overwrite=True,\
                Writer=ascii.FixedWidth)
    #print('------------------')
    return

############################################################################
############################################################################
############################################################################

def read_data(path, date, var_str, pointname, model):
    if model == 'icon-global-eps':
        model_str = 'icon-eps'
    else:
        model_str = model
    filename = '{}_{}{:02}{:02}{:02}_{}_{}.txt'.format(\
                model_str, date['year'], date['month'], date['day'], date['hour'], var_str, pointname)

    if model == 'icon-eu-eps':
        data_table = ascii.read(path['base'] + path['points_eu_eps'] + filename, format='fixed_width')
    elif model == 'icon-eu-det':
        data_table = ascii.read(path['base'] + path['points_eu_det'] + filename, format='fixed_width')
    elif model == 'icon-global-eps' or model == 'icon-eps':
        data_table = ascii.read(path['base'] + path['points_global_eps'] + filename, format='fixed_width')

    data = data_table.as_array()

    read_values = np.zeros((len(data), len(data[0])-1), dtype='float32')
    for i in range(len(data)):
        data_row = data[i]
        for j in range(1,len(data[0])):
            read_values[i][j-1] = data_row[j]

    return read_values

########################################################################
########################################################################
########################################################################

