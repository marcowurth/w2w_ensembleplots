##############################################
###  module for making meteogram boxplots  ###
##############################################

import os
import datetime

import numpy as np
import astropy.table
import astropy.io
import Magics.macro as magics

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time, get_timeshift
from w2w_ensembleplots.core.read_data import read_forecast_data, get_fcst_hours_list, get_all_available_vars


########################################################################
########################################################################
########################################################################

def boxplot_forecast(models, date, var, point, plot_type, save_point_data, verbose):

    # determine date and lead_times list #

    making_comparison_plots = False
    if date == 'latest':
        if models == 'both-eps':
            date = calc_latest_run_time('icon-eu-eps')
        elif models == 'icon-global-eps':
            date = calc_latest_run_time('icon-global-eps')
    if date == 'comparison':
        making_comparison_plots = True
        date = calc_latest_run_time('icon-global-eps')

    if verbose:
        if 'lat' in point:
            print('----- next point is {}, {:.2f}°N, {:.2f}°E -----'.format(point['name'], point['lat'], point['lon']))
        else:
            print('----- next point is {} -----'.format(point['name']))
        print('-- Initial time of run: {}{:02}{:02}-{:02}UTC --'.format(\
              date['year'], date['month'], date['day'], date['hour']))

    if making_comparison_plots:
        lead_times = [0,12,24,36,48]
    else:
        lead_times = [0]


    # determine var_list #

    if var == 'all_available':
        var_list = get_all_available_vars(models, date)
        if making_comparison_plots:
            var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad']
    else:
        var_list = [var]


    # main loop 1 in this function, every iteration makes several plots, one for every lead time #

    for var in var_list:
        if verbose:
            print('----- next variable is {} -----'.format(var))

        if models == 'both-eps':
            if (date['hour'] == 0 or date['hour'] == 12)\
             and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'clct'): 
                extend_with_global = True
            else:
                extend_with_global = False
        elif models == 'icon-global-eps':
            extend_with_global = False


        if models == 'both-eps':
            if var == 'prec_rate' or var == 'snow_rate' or var == 'direct_rad' or var == 'diffuse_rad':
                point_values_eu_eps = np.empty((len(lead_times), 64, 40), dtype='float32')
            elif var == 'vmax_10m':
                point_values_eu_eps = np.empty((len(lead_times), 65, 40), dtype='float32')
                point_values_eu_eps[:, 0 , :] = np.nan
            elif var == 'wind_10m':
                point_values_eu_eps = np.empty((len(lead_times), 65, 40, 2), dtype='float32')
                point_values_eu_eps[:, 0 , :, 1] = np.nan
            elif var == 'wind_3pl':
                point_values_eu_eps = np.empty((len(lead_times), 65, 40, 3), dtype='float32')
            else:
                point_values_eu_eps = np.empty((len(lead_times), 65, 40), dtype='float32')
        if extend_with_global:
            point_values_global_eps = np.empty((len(lead_times), 5, 40), dtype='float32')
        if models == 'icon-global-eps':
            if var == 'prec_rate':
                point_values_global_eps = np.empty((len(lead_times), 69, 40), dtype='float32')
            else:
                point_values_global_eps = np.empty((len(lead_times), 70, 40), dtype='float32')

        y_axis_range = dict()
        for i, lead_time in enumerate(lead_times):
            if making_comparison_plots:
                print('----- read lead time -{}h -----'.format(lead_time))

            time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
            time -= datetime.timedelta(0, 3600 * lead_time)
            old_run_date = dict(year = time.year, month = time.month, day = time.day, hour = time.hour)


            # get forecast data from icon-eu-eps #

            first_run_not_found = False
            if models == 'both-eps':
                try:
                    if var == 'wind_10m':
                        point_values_eu_eps[i, :, :, 0] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                              old_run_date, 'wind_mean_10m',
                                                                              point = point)
                        point_values_eu_eps[i, 1:, :, 1] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                               old_run_date, 'vmax_10m',
                                                                               point = point)
                    elif var == 'vmax_10m':
                        point_values_eu_eps[i, 1:, :] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                            old_run_date, var,
                                                                            point = point)
                    elif var == 'wind_3pl':
                        point_values_eu_eps[i, :, :, 0] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                              old_run_date, 'wind_850hPa',
                                                                              point = point)
                        point_values_eu_eps[i, :, :, 1] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                              old_run_date, 'wind_500hPa',
                                                                              point = point)
                        point_values_eu_eps[i, :, :, 2] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                              old_run_date, 'wind_300hPa',
                                                                              point = point)
                    else:
                        point_values_eu_eps[i, :, :] = read_forecast_data('icon-eu-eps', 'icosahedral',
                                                                           old_run_date, var,
                                                                           point = point)
                except FileNotFoundError:
                    point_values_eu_eps[i, :, :] = -100
                    print('-- icon-eu-eps forecast not found --')


            # get forecast data from icon-global-eps #

            if extend_with_global:
                try:
                    point_values_global_eps[i, :, :] = read_forecast_data('icon-global-eps', 'icosahedral',
                                                                           old_run_date, var,
                                                                           point = point)[-5:, :]
                except FileNotFoundError:
                    point_values_global_eps[i, :, :] = -100
                    print('-- icon-global-eps forecast not found --')

            if models == 'icon-global-eps':
                try:
                    point_values_global_eps[i, :, :] = read_forecast_data('icon-global-eps', 'icosahedral',
                                                                           old_run_date, var,
                                                                           point = point)
                except FileNotFoundError:
                    point_values_global_eps[i, :, :] = -100
                    print('-- icon-global-eps forecast not found --')


        # calculate y axis limits #

        if models == 'both-eps':
            y_axis_range['min'] = np.nanmin(point_values_eu_eps)
            y_axis_range['max'] = np.nanmax(point_values_eu_eps)
        if extend_with_global:
            if np.nanmin(point_values_global_eps) < y_axis_range['min']:
                y_axis_range['min'] = np.nanmin(point_values_global_eps)
            if np.nanmax(point_values_global_eps) > y_axis_range['max']:
                y_axis_range['max'] = np.nanmax(point_values_global_eps)
        if models == 'icon-global-eps':
            y_axis_range['min'] = np.nanmin(point_values_global_eps)
            y_axis_range['max'] = np.nanmax(point_values_global_eps)

        y_axis_range = fit_y_axis_to_data(var, y_axis_range, point['name'])


        # main loop 2 in this function, every iteration makes one plot #

        path = dict(base = '/')
        for i, lead_time in enumerate(lead_times):
            if models == 'both-eps':
                fcst_hours_list_eu = get_fcst_hours_list('icon-eu-eps')
                if extend_with_global:
                    fcst_hours_list_global = get_fcst_hours_list('icon-global-eps_eu-extension')
                else:
                    fcst_hours_list_global = None
            elif models == 'icon-global-eps':
                fcst_hours_list_eu = None
                fcst_hours_list_global = get_fcst_hours_list('icon-global-eps')

            time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
            time -= datetime.timedelta(0, 3600 * lead_time)
            date_run = dict(year = time.year, month = time.month, day = time.day, hour = time.hour)


            # define plot path and filename #

            ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
            if making_comparison_plots:
                temp_subdir = 'data/plots/{}/meteogram_boxplot/forecast/comparison/{:03}h_ago/'.format(
                               ex_op_str,lead_time)
                filename = 'meteogram_boxplot_{:03}h_ago_{}_{}'.format(lead_time, var, point['name'])
            elif plot_type == 'w2w_city':
                temp_subdir = 'data/plots/{}/meteogram_boxplot/forecast/w2w_cities/'.format(ex_op_str)
                filename = 'meteogram_boxplot_{}_latest_{}'.format(point['name'], var)
            elif plot_type == 'user_point':
                temp_subdir = 'data/plots/{}/meteogram_boxplot/forecast/user_points/'.format(ex_op_str)
                filename = 'meteogram_boxplot_{}_{}{:02}{:02}{:02}_{}'.format(
                            point['name'], date['year'], date['month'], date['day'], date['hour'], var)

            temp_subdir = temp_subdir + point['name']
            if not os.path.isdir(path['base'] + temp_subdir):
                os.mkdir(path['base'] + temp_subdir)
            path['plots'] = temp_subdir + '/'


            ##### save icon-eu-eps point data to textfile #####

            if save_point_data \
             and var in ['t_2m','prec_rate','snow_rate','prec_sum','wind_10m','mslp','clct','direct_rad', 'diffuse_rad']:
                if var == 'wind_10m':
                    vars_to_save = ['wind_mean_10m', 'vmax_10m']
                else:
                    vars_to_save = [var]

                for var_to_save in vars_to_save:
                    if var_to_save in ['prec_rate', 'snow_rate', 'vmax_10m', 'direct_rad', 'diffuse_rad']:
                        fcst_hours_list_save = fcst_hours_list_eu[1:]
                    else:
                        fcst_hours_list_save = fcst_hours_list_eu


                    # print data values to string matrix #

                    data_to_save = []
                    data_to_save.append(fcst_hours_list_save)

                    for column in range(40):
                        data_column = []
                        for row in range(len(fcst_hours_list_save)):
                            if var_to_save == 'wind_mean_10m':
                                value = point_values_eu_eps[0, row, column, 0]
                            elif var_to_save == 'vmax_10m':
                                value = point_values_eu_eps[0, row + 1, column, 1]
                            else:
                                value = point_values_eu_eps[0, row, column]

                            if abs(value) < 0.01:
                                value_str = '{:.0f}'.format(value)
                            else:
                                value_str = '{:.2f}'.format(value)
                            data_column.append(value_str)
                        data_to_save.append(data_column)


                        # make  header #

                        header = [str(x) for x in range(1,41)]
                        header.insert(0, 'fcst_hour')


                    # make astropy table and add meta data #

                    t = astropy.table.Table(data_to_save, names = header)
                    meta = get_meta_data(var_to_save)
                    str1 = 'variable: {}'.format(meta['var'])
                    str2 = 'units: {}'.format(meta['units'])
                    t.meta['comments'] = [str1, str2, '']


                    # write table to file #

                    path['benedikt_latest'] = 'data/model_data/icon-eu-eps/point-forecasts/benedikt_post_processing/'
                    path['benedikt_latest'] += 'latest_run/' + point['name']
                    if not os.path.isdir(path['base'] + path['benedikt_latest']):
                        os.mkdir(path['base'] + path['benedikt_latest'])
                    path['benedikt_latest'] += '/'


                    path['benedikt'] = 'data/model_data/icon-eu-eps/point-forecasts/benedikt_post_processing/'
                    path['benedikt'] += 'run_{}{:02}{:02}{:02}'.format(
                                         date['year'], date['month'], date['day'], date['hour'])
                    if not os.path.isdir(path['base'] + path['benedikt']):
                        os.mkdir(path['base'] + path['benedikt'])
                    path['benedikt'] += '/' + point['name']
                    if not os.path.isdir(path['base'] + path['benedikt']):
                        os.mkdir(path['base'] + path['benedikt'])
                    path['benedikt'] += '/'

                    filename_textfile_latest = 'icon-eu-eps_latest_run_{}_{}.txt'.format(
                                                var_to_save, point['name'])
                    filename_textfile = 'icon-eu-eps_{}{:02}{:02}{:02}_{}_{}.txt'.format(
                                         date['year'], date['month'], date['day'], date['hour'],
                                         var_to_save, point['name'])

                    astropy.io.ascii.write(t, output = path['base'] + path['benedikt_latest'] \
                                                      + filename_textfile_latest,
                                           overwrite = True, Writer = astropy.io.ascii.FixedWidth)
                    astropy.io.ascii.write(t, output = path['base'] + path['benedikt'] + filename_textfile,
                                           overwrite = True, Writer = astropy.io.ascii.FixedWidth)

                ##### save icon-global-eps point data to textfile #####

                if extend_with_global:

                    # print data values to string matrix #

                    var_to_save = var
                    data_to_save = []
                    data_to_save.append(fcst_hours_list_global)

                    for column in range(40):
                        data_column = []
                        for row in range(len(fcst_hours_list_global)):
                            value = point_values_global_eps[0, row, column]

                            if abs(value) < 0.01:
                                value_str = '{:.0f}'.format(value)
                            else:
                                value_str = '{:.2f}'.format(value)
                            data_column.append(value_str)
                        data_to_save.append(data_column)


                        # make  header #

                        header = [str(x) for x in range(1,41)]
                        header.insert(0, 'fcst_hour')


                    # make astropy table and add meta data #

                    t = astropy.table.Table(data_to_save, names = header)
                    meta = get_meta_data(var_to_save)
                    str1 = 'variable: {}'.format(meta['var'])
                    str2 = 'units: {}'.format(meta['units'])
                    t.meta['comments'] = [str1, str2, '']


                    # write table to file #

                    path['benedikt_latest'] = 'data/model_data/icon-global-eps/point-forecasts/'
                    path['benedikt_latest'] += 'benedikt_post_processing/latest_run/' + point['name']
                    if not os.path.isdir(path['base'] + path['benedikt_latest']):
                        os.mkdir(path['base'] + path['benedikt_latest'])
                    path['benedikt_latest'] += '/'


                    path['benedikt'] = 'data/model_data/icon-global-eps/point-forecasts/benedikt_post_processing/'
                    path['benedikt'] += 'run_{}{:02}{:02}{:02}'.format(
                                         date['year'], date['month'], date['day'], date['hour'])
                    if not os.path.isdir(path['base'] + path['benedikt']):
                        os.mkdir(path['base'] + path['benedikt'])
                    path['benedikt'] += '/' + point['name']
                    if not os.path.isdir(path['base'] + path['benedikt']):
                        os.mkdir(path['base'] + path['benedikt'])
                    path['benedikt'] += '/'

                    filename_textfile_latest = 'icon-global-eps_latest_run_{}_{}.txt'.format(
                                                var_to_save, point['name'])
                    filename_textfile = 'icon-global-eps_{}{:02}{:02}{:02}_{}_{}.txt'.format(
                                         date['year'], date['month'], date['day'], date['hour'],
                                         var_to_save, point['name'])

                    astropy.io.ascii.write(t, output = path['base'] + path['benedikt_latest'] \
                                                      + filename_textfile_latest,
                                           overwrite = True, Writer = astropy.io.ascii.FixedWidth)
                    astropy.io.ascii.write(t, output = path['base'] + path['benedikt'] + filename_textfile,
                                           overwrite = True, Writer = astropy.io.ascii.FixedWidth)


            # calculate percentiles #

            # data_percentiles_eu: 65 timesteps x 7 percentiles
            # data_percentiles_global: 70/5 timesteps x 7 percentiles
            if models == 'both-eps':
                data_percentiles_eu_eps = np.percentile(point_values_eu_eps[i, :, :],
                                                        [0,10,25,50,75,90,100], axis = 1).T
                if var == 'wind_10m':
                    data_percentiles_eu_eps = np.moveaxis(data_percentiles_eu_eps, 0, 2)
                elif var == 'wind_3pl':
                    data_percentiles_eu_eps = np.moveaxis(data_percentiles_eu_eps, 0, 2)
            else:
                data_percentiles_eu_eps = None
            if extend_with_global:
                data_percentiles_global_eps = np.percentile(point_values_global_eps[i, :, :], 
                                                            [0,10,25,50,75,90,100], axis = 1).T
            elif models == 'icon-global-eps':
                data_percentiles_global_eps = np.percentile(point_values_global_eps[i, :, :], 
                                                            [0,10,25,50,75,90,100], axis = 1).T
            else:
                data_percentiles_global_eps = None


            meta = get_variable_title_unit(var)


            # plotting #

            plot_in_magics_boxplot(path, date_run, point, var, meta, y_axis_range, filename,
                                   fcst_hours_list_eu, fcst_hours_list_global,
                                   data_percentiles_eu_eps, data_percentiles_global_eps,
                                   models, extend_with_global, making_comparison_plots, lead_time, plot_type)
        del y_axis_range

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def plot_in_magics_boxplot(path, date, point, var, meta, y_axis_range, filename,
                           fcst_hours_list_eu, fcst_hours_list_global,
                           data_percentiles_eu, data_percentiles_global,
                           models, extend_with_global, making_comparison_plots, lead_time, plot_type):

    run_time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
    if models == 'both-eps':
        timeshift = get_timeshift()
    elif models == 'icon-global-eps':
        timeshift = 0

    time_start = run_time + datetime.timedelta(0, 3600 * int(-1 + timeshift))
    time_end   = run_time + datetime.timedelta(0, 3600 * (183 + timeshift))

    if not extend_with_global:
        shading_area_time = [str(run_time + datetime.timedelta(0,3600 * int(183 - 24*1.25 + timeshift)))]

    if var == 't_2m':
        if timeshift == 0:
            t2m_6h_times_str = '0,6,12,18 UTC'
            if models == 'icon-global-eps':
                t2m_0_12UTC_times_str = '0,12 UTC'
                t2m_6_18UTC_times_str = '6,18 UTC'
        if timeshift == 1:
            t2m_6h_times_str = '1,7,13,19 CET'
        if timeshift == 2:
            t2m_6h_times_str = '2,8,14,20 CEST'

    if models == 'both-eps':
        if var == 't_2m':
            fcst_hours_list_eu_6h = [x for x in fcst_hours_list_eu if x % 6 == 0]
            fcst_hours_list_eu_1h = [x for x in fcst_hours_list_eu if x not in fcst_hours_list_eu_6h]

            dates_eu_6h = []
            for time_step in fcst_hours_list_eu_6h:
                dates_eu_6h.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))
            dates_eu_1h = []
            for time_step in fcst_hours_list_eu_1h:
                dates_eu_1h.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))            

            data_percentiles_eu_6h = data_percentiles_eu[[list(fcst_hours_list_eu).index(x)\
                                                          for x in fcst_hours_list_eu_6h]]
            data_percentiles_eu_1h = data_percentiles_eu[[list(fcst_hours_list_eu).index(x)\
                                                          for x in fcst_hours_list_eu_1h]]

        elif var == 'prec_rate' or var == 'snow_rate' or var == 'direct_rad' or var == 'diffuse_rad':
            dates_eu_all = []
            for i in range(len(fcst_hours_list_eu)-1):
                dates_eu_all.append(str(run_time + datetime.timedelta(0,\
                    3600 * ((fcst_hours_list_eu[i] + fcst_hours_list_eu[i+1]) / 2 + timeshift) )))
            #for time_step in range(1,120+1,1):
            #    dates_eu_1h.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift - 0.5))))

        elif var == 'wind_10m':
            data_percentiles_eu[0,:,1] = -100
            dates_eu_mean = []
            dates_eu_gust = []
            for time_step in fcst_hours_list_eu:
                dates_eu_mean.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift + 0.1))))
                dates_eu_gust.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift - 0.6))))

        else:
            if var == 'vmax_10m':
                timerangeshift = -0.5
                data_percentiles_eu[0,:] = -100
            else:
                # a lot of icon-eu-eps variables fall into this category #
                timerangeshift = 0.0
            dates_eu_all = []
            for time_step in fcst_hours_list_eu:
                dates_eu_all.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift\
                                                                                     + timerangeshift))))

    if extend_with_global:
        dates_global = []
        if var == 'prec_rate':
            #for time_step in range(121,180+1,1):
            #    dates_global.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift - 0.5))))
            for time_step in fcst_hours_list_global:
                dates_global.append(str(run_time + datetime.timedelta(0, 3600 * (time_step - 6 + timeshift))))
        else:
            # t_2m, prec_sum, clct #
            for time_step in fcst_hours_list_global:
                dates_global.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))

    if models == 'icon-global-eps':
        if var == 't_2m':
            fcst_hours_list_global_6h = [x for x in fcst_hours_list_global if x % 6 == 0]
            fcst_hours_list_global_0_12UTC = [x for x in fcst_hours_list_global_6h if x % 12 == 0]
            fcst_hours_list_global_6_18UTC = [x for x in fcst_hours_list_global_6h if x % 12 == 6]
            fcst_hours_list_global_1h = [x for x in fcst_hours_list_global if x not in fcst_hours_list_global_6h]

            dates_global_0_12UTC = []
            for time_step in fcst_hours_list_global_0_12UTC:
                dates_global_0_12UTC.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))
            dates_global_6_18UTC = []
            for time_step in fcst_hours_list_global_6_18UTC:
                dates_global_6_18UTC.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))
            dates_global_1h = []
            for time_step in fcst_hours_list_global_1h:
                dates_global_1h.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))            

            data_percentiles_global_0_12UTC = data_percentiles_global[[list(fcst_hours_list_global).index(x)\
                                                                       for x in fcst_hours_list_global_0_12UTC]]
            data_percentiles_global_6_18UTC = data_percentiles_global[[list(fcst_hours_list_global).index(x)\
                                                                       for x in fcst_hours_list_global_6_18UTC]]
            data_percentiles_global_1h = data_percentiles_global[[list(fcst_hours_list_global).index(x)\
                                                                  for x in fcst_hours_list_global_1h]]

        elif var == 'prec_rate':
            dates_global = []
            for i in range(len(fcst_hours_list_global)-1):
                dates_global.append(str(run_time + datetime.timedelta(0,\
                    3600 * ((fcst_hours_list_global[i] + fcst_hours_list_global[i+1]) / 2 + timeshift) )))
            #for time_step in range(1,180+1,1):
            #    dates_global.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift - 0.5))))

        else:
            # prec_sum, wind_mean_10m, clct #
            dates_global = []
            for time_step in fcst_hours_list_global:
                dates_global.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))


    output_layout = magics.output(
            output_formats = ['png'],
            output_name = path['base'] + path['plots'] + filename,
            output_name_first_page_number = 'off',
            output_width = 1500,
            super_page_x_length = 15.0,
            super_page_y_length = 6.0,
        )

    page_layout = magics.page(
            layout = 'positional',
            page_x_position = 0.0,
            page_y_position = 0.0,
            page_x_length = 15.0,
            page_y_length = 6.0,
            page_id_line='off',
        )

    coord_system = magics.mmap(
            subpage_map_projection = 'cartesian',
            subpage_x_axis_type = 'date',
            subpage_x_date_min = str(time_start),
            subpage_x_date_max = str(time_end),
            subpage_y_min = y_axis_range['min'],
            subpage_y_max = y_axis_range['max'],
            subpage_y_axis_type = 'regular',
            subpage_x_position = 1.55,
            subpage_y_position = 0.48,
            subpage_x_length = 13.25,
            subpage_y_length = 5.0,
        )

    vertical_axis = magics.maxis(
            axis_orientation = 'vertical',
            axis_grid = 'on',
            axis_type = 'regular',
            axis_tick_label_height = 0.7,
            axis_grid_colour = 'charcoal',
            axis_grid_thickness = 1,
            axis_grid_line_style='dash',
            axis_tick_interval = y_axis_range['interval'],
        )
    horizontal_axis = magics.maxis(
            axis_type = 'date',
            axis_years_label  = 'off',
            axis_months_label = 'off',
            axis_days_label = 'off',
            axis_hours_label = 'off',
            axis_tick_thickness = 4,
            axis_minor_tick = 'on',
            axis_grid = 'on',
            axis_grid_colour = 'charcoal',
            axis_grid_thickness = 1,
            axis_grid_line_style = 'dash',
            axis_title = 'off',
        )

    ########################################################################

    width_1h = 0.8
    if models == 'both-eps':

        if var == 't_2m':
            bar_minmax_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_6h,
                    input_y_values = data_percentiles_eu_6h[:,0],
                    input_y2_values = data_percentiles_eu_6h[:,6],
                )

            bar_p1090_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_6h,
                    input_y_values = data_percentiles_eu_6h[:,1],
                    input_y2_values = data_percentiles_eu_6h[:,5],
                )

            bar_p2575_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): {}</font>'.format(t2m_6h_times_str)
                )
            data_p2575_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_6h,
                    input_y_values = data_percentiles_eu_6h[:,2],
                    input_y2_values = data_percentiles_eu_6h[:,4],
                )

            bar_median_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_6h,
                    input_y_values  = data_percentiles_eu_6h[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu_6h[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_1h,
                    input_y_values = data_percentiles_eu_1h[:,0],
                    input_y2_values = data_percentiles_eu_1h[:,6],
                )

            bar_p1090_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_1h,
                    input_y_values = data_percentiles_eu_1h[:,1],
                    input_y2_values = data_percentiles_eu_1h[:,5],
                )

            bar_p2575_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): Other times</font>'
                )
            data_p2575_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_1h,
                    input_y_values = data_percentiles_eu_1h[:,2],
                    input_y2_values = data_percentiles_eu_1h[:,4],
                )

            bar_median_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_1h,
                    input_y_values = data_percentiles_eu_1h[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu_1h[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        elif var == 'prec_rate' or var == 'snow_rate' or var == 'direct_rad' or var == 'diffuse_rad':
            bar_minmax_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[:48],
                    input_y_values = data_percentiles_eu[:48,0],
                    input_y2_values = data_percentiles_eu[:48,6],
                )

            bar_p1090_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[:48],
                    input_y_values = data_percentiles_eu[:48,1],
                    input_y2_values = data_percentiles_eu[:48,5],
                )

            bar_p2575_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.8,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km)</font>'
                )
            data_p2575_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[:48],
                    input_y_values = data_percentiles_eu[:48,2],
                    input_y2_values = data_percentiles_eu[:48,4],
                )

            bar_median_eu_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.8,
                )
            data_median_eu_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[:48],
                    input_y_values = data_percentiles_eu[:48,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:48,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.15,
                )
            data_minmax_eu_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[48:56],
                    input_y_values = data_percentiles_eu[48:56,0],
                    input_y2_values = data_percentiles_eu[48:56,6],
                )

            bar_p1090_eu_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 1.75,
                )
            data_p1090_eu_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[48:56],
                    input_y_values = data_percentiles_eu[48:56,1],
                    input_y2_values = data_percentiles_eu[48:56,5],
                )

            bar_p2575_eu_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 2.8,
                )
            data_p2575_eu_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[48:56],
                    input_y_values = data_percentiles_eu[48:56,2],
                    input_y2_values = data_percentiles_eu[48:56,4],
                )

            bar_median_eu_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 2.8,
                )
            data_median_eu_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[48:56],
                    input_y_values = data_percentiles_eu[48:56,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[48:56,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.30,
                )
            data_minmax_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[56:64],
                    input_y_values = data_percentiles_eu[56:64,0],
                    input_y2_values = data_percentiles_eu[56:64,6],
                )

            bar_p1090_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 3.6,
                )
            data_p1090_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[56:64],
                    input_y_values = data_percentiles_eu[56:64,1],
                    input_y2_values = data_percentiles_eu[56:64,5],
                )

            bar_p2575_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 5.8,
                )
            data_p2575_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[56:64],
                    input_y_values = data_percentiles_eu[56:64,2],
                    input_y2_values = data_percentiles_eu[56:64,4],
                )

            bar_median_eu_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 5.8,
                )
            data_median_eu_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all[56:64],
                    input_y_values = data_percentiles_eu[56:64,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[56:64,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        elif var == 'wind_10m':
            bar_minmax_eu_mean = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_mean = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_mean,
                    input_y_values = data_percentiles_eu[:,0,0],
                    input_y2_values = data_percentiles_eu[:,6,0],
                )

            bar_p1090_eu_mean = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_mean = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_mean,
                    input_y_values = data_percentiles_eu[:,1,0],
                    input_y2_values = data_percentiles_eu[:,5,0],
                )

            bar_p2575_eu_mean = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): mean wind</font>'
                )
            data_p2575_eu_mean = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_mean,
                    input_y_values = data_percentiles_eu[:,2,0],
                    input_y2_values = data_percentiles_eu[:,4,0],
                )

            bar_median_eu_mean = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_mean = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_mean,
                    input_y_values = data_percentiles_eu[:,3,0] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3,0] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_gust = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_gust = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_gust,
                    input_y_values = data_percentiles_eu[:,0,1],
                    input_y2_values = data_percentiles_eu[:,6,1],
                )

            bar_p1090_eu_gust = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_gust = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_gust,
                    input_y_values = data_percentiles_eu[:,1,1],
                    input_y2_values = data_percentiles_eu[:,5,1],
                )

            bar_p2575_eu_gust = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): gust</font>'
                )
            data_p2575_eu_gust = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_gust,
                    input_y_values = data_percentiles_eu[:,2,1],
                    input_y2_values = data_percentiles_eu[:,4,1],
                )

            bar_median_eu_gust = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_gust = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_gust,
                    input_y_values = data_percentiles_eu[:,3,1] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3,1] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        elif var == 'wind_3pl':
            bar_minmax_eu_850hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_850hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,0,0],
                    input_y2_values = data_percentiles_eu[:,6,0],
                )

            bar_p1090_eu_850hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_850hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,1,0],
                    input_y2_values = data_percentiles_eu[:,5,0],
                )

            bar_p2575_eu_850hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): 850hPa</font>'
                )
            data_p2575_eu_850hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,2,0],
                    input_y2_values = data_percentiles_eu[:,4,0],
                )

            bar_median_eu_850hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_850hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,3,0] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3,0] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_500hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_500hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,0,1],
                    input_y2_values = data_percentiles_eu[:,6,1],
                )

            bar_p1090_eu_500hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_500hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,1,1],
                    input_y2_values = data_percentiles_eu[:,5,1],
                )

            bar_p2575_eu_500hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): 500hPa</font>'
                )
            data_p2575_eu_500hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,2,1],
                    input_y2_values = data_percentiles_eu[:,4,1],
                )

            bar_median_eu_500hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_500hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,3,1] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3,1] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_eu_300hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_300hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,0,2],
                    input_y2_values = data_percentiles_eu[:,6,2],
                )

            bar_p1090_eu_300hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_300hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,1,2],
                    input_y2_values = data_percentiles_eu[:,5,2],
                )

            bar_p2575_eu_300hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): 300hPa</font>'
                )
            data_p2575_eu_300hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,2,2],
                    input_y2_values = data_percentiles_eu[:,4,2],
                )

            bar_median_eu_300hPa = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_300hPa = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,3,2] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3,2] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        else:
            bar_minmax_eu_all = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_eu_all = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,0],
                    input_y2_values = data_percentiles_eu[:,6],
                )

            bar_p1090_eu_all = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_eu_all = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,1],
                    input_y2_values = data_percentiles_eu[:,5],
                )

            bar_p2575_eu_all = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-EU-EPS (20km)</font>'
                )
            data_p2575_eu_all = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,2],
                    input_y2_values = data_percentiles_eu[:,4],
                )

            bar_median_eu_all = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_eu_all = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_eu_all,
                    input_y_values = data_percentiles_eu[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_eu[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

    if extend_with_global:
        if var == 'prec_rate':
            bar_minmax_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.40,
                )
            data_minmax_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,0],
                    input_y2_values = data_percentiles_global[:,6],
                )

            bar_p1090_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * 7.4,
                )
            data_p1090_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,1],
                    input_y2_values = data_percentiles_global[:,5],
                )

            bar_p2575_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * 11.8,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km)</font>'
                )
            data_p2575_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,2],
                    input_y2_values = data_percentiles_global[:,4],
                )

            bar_median_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 11.8,
                )
            data_median_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        else:
            bar_minmax_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,0],
                    input_y2_values = data_percentiles_global[:,6],
                )

            bar_p1090_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,1],
                    input_y2_values = data_percentiles_global[:,5],
                )

            bar_p2575_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km)</font>'
                )
            data_p2575_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values = data_percentiles_global[:,2],
                    input_y2_values = data_percentiles_global[:,4],
                )

            bar_median_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

    if models == 'icon-global-eps':
        if var == 't_2m':
            bar_minmax_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_1h,
                    input_y_values  = data_percentiles_global_1h[:,0],
                    input_y2_values = data_percentiles_global_1h[:,6],
                )
            bar_p1090_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_1h,
                    input_y_values  = data_percentiles_global_1h[:,1],
                    input_y2_values = data_percentiles_global_1h[:,5],
                )
            bar_p2575_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km): Other times</font>'
                )
            data_p2575_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_1h,
                    input_y_values  = data_percentiles_global_1h[:,2],
                    input_y2_values = data_percentiles_global_1h[:,4],
                )
            bar_median_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_1h,
                    input_y_values  = data_percentiles_global_1h[:,3]\
                                      - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global_1h[:,3]\
                                      + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_global_0_12UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global_0_12UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_0_12UTC,
                    input_y_values  = data_percentiles_global_0_12UTC[:,0],
                    input_y2_values = data_percentiles_global_0_12UTC[:,6],
                )
            bar_p1090_global_0_12UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global_0_12UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_0_12UTC,
                    input_y_values  = data_percentiles_global_0_12UTC[:,1],
                    input_y2_values = data_percentiles_global_0_12UTC[:,5],
                )
            bar_p2575_global_0_12UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 242, 209)', # bright turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km): {}</font>'.format(
                                        t2m_0_12UTC_times_str)
                )
            data_p2575_global_0_12UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_0_12UTC,
                    input_y_values  = data_percentiles_global_0_12UTC[:,2],
                    input_y2_values = data_percentiles_global_0_12UTC[:,4],
                )
            bar_median_global_0_12UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_global_0_12UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_0_12UTC,
                    input_y_values  = data_percentiles_global_0_12UTC[:,3]\
                                      - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global_0_12UTC[:,3]\
                                      + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_global_6_18UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global_6_18UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_6_18UTC,
                    input_y_values  = data_percentiles_global_6_18UTC[:,0],
                    input_y2_values = data_percentiles_global_6_18UTC[:,6],
                )
            bar_p1090_global_6_18UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global_6_18UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_6_18UTC,
                    input_y_values  = data_percentiles_global_6_18UTC[:,1],
                    input_y2_values = data_percentiles_global_6_18UTC[:,5],
                )
            bar_p2575_global_6_18UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(88, 217, 34)', # green
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km): {}</font>'.format(
                                        t2m_6_18UTC_times_str)
                )
            data_p2575_global_6_18UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_6_18UTC,
                    input_y_values  = data_percentiles_global_6_18UTC[:,2],
                    input_y2_values = data_percentiles_global_6_18UTC[:,4],
                )
            bar_median_global_6_18UTC = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_global_6_18UTC = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global_6_18UTC,
                    input_y_values  = data_percentiles_global_6_18UTC[:,3]\
                                      - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global_6_18UTC[:,3]\
                                      + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        elif var == 'prec_rate':
            bar_minmax_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[:48],
                    input_y_values = data_percentiles_global[:48,0],
                    input_y2_values = data_percentiles_global[:48,6],
                )

            bar_p1090_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[:48],
                    input_y_values = data_percentiles_global[:48,1],
                    input_y2_values = data_percentiles_global[:48,5],
                )

            bar_p2575_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.8,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km)</font>'
                )
            data_p2575_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[:48],
                    input_y_values = data_percentiles_global[:48,2],
                    input_y2_values = data_percentiles_global[:48,4],
                )

            bar_median_global_1h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.8,
                )
            data_median_global_1h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[:48],
                    input_y_values = data_percentiles_global[:48,3] \
                                    - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[:48,3] \
                                    + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_global_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.15,
                )
            data_minmax_global_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[48:56],
                    input_y_values = data_percentiles_global[48:56,0],
                    input_y2_values = data_percentiles_global[48:56,6],
                )

            bar_p1090_global_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 1.75,
                )
            data_p1090_global_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[48:56],
                    input_y_values = data_percentiles_global[48:56,1],
                    input_y2_values = data_percentiles_global[48:56,5],
                )

            bar_p2575_global_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 2.8,
                )
            data_p2575_global_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[48:56],
                    input_y_values = data_percentiles_global[48:56,2],
                    input_y2_values = data_percentiles_global[48:56,4],
                )

            bar_median_global_3h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 2.8,
                )
            data_median_global_3h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[48:56],
                    input_y_values = data_percentiles_global[48:56,3] \
                                    - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[48:56,3] \
                                    + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_global_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.30,
                )
            data_minmax_global_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[56:64],
                    input_y_values = data_percentiles_global[56:64,0],
                    input_y2_values = data_percentiles_global[56:64,6],
                )

            bar_p1090_global_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 3.6,
                )
            data_p1090_global_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[56:64],
                    input_y_values = data_percentiles_global[56:64,1],
                    input_y2_values = data_percentiles_global[56:64,5],
                )

            bar_p2575_global_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 5.8,
                )
            data_p2575_global_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[56:64],
                    input_y_values = data_percentiles_global[56:64,2],
                    input_y2_values = data_percentiles_global[56:64,4],
                )

            bar_median_global_6h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 5.8,
                )
            data_median_global_6h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[56:64],
                    input_y_values = data_percentiles_global[56:64,3] \
                                    - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[56:64,3] \
                                    + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

            bar_minmax_global_12h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.40,
                )
            data_minmax_global_12h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[64:],
                    input_y_values = data_percentiles_global[64:,0],
                    input_y2_values = data_percentiles_global[64:,6],
                )

            bar_p1090_global_12h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 7.4,
                )
            data_p1090_global_12h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[64:],
                    input_y_values = data_percentiles_global[64:,1],
                    input_y2_values = data_percentiles_global[64:,5],
                )

            bar_p2575_global_12h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 11.8,
                )
            data_p2575_global_12h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[64:],
                    input_y_values = data_percentiles_global[64:,2],
                    input_y2_values = data_percentiles_global[64:,4],
                )

            bar_median_global_12h = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 11.8,
                )
            data_median_global_12h = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global[64:],
                    input_y_values  = data_percentiles_global[64:,3] \
                                     - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[64:,3] \
                                     + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

        else:
            bar_minmax_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * 0.05,
                )
            data_minmax_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,0],
                    input_y2_values = data_percentiles_global[:,6],
                )
            bar_p1090_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * 0.5,
                )
            data_p1090_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,1],
                    input_y2_values = data_percentiles_global[:,5],
                )
            bar_p2575_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                    graph_bar_width = 3600 * width_1h,
                    legend = 'on',
                    legend_user_text = '<font colour="black"> ICON-Global-EPS (40km)</font>'
                )
            data_p2575_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,2],
                    input_y2_values = data_percentiles_global[:,4],
                )
            bar_median_global = magics.mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'black',
                    graph_bar_width = 3600 * width_1h,
                )
            data_median_global = magics.minput(
                    input_x_type = 'date',
                    input_date_x_values = dates_global,
                    input_y_values  = data_percentiles_global[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                    input_y2_values = data_percentiles_global[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
                )

    ########################################################################

    if models == 'both-eps' and not extend_with_global:
        bar_shading_area = magics.mgraph(
                graph_type = 'bar',
                graph_shade = 'on',
                graph_shade_style = 'hatch',
                graph_shade_colour = 'grey',
                graph_shade_hatch_index = 6,
                graph_bar_width = 3600 * 24 * 2.5,
            )
        data_shading_area = magics.minput(
                input_x_type = 'date',
                input_date_x_values = shading_area_time,
                input_y_values  = [y_axis_range['min']], #[max(y_axis_range['min'],0.0)]
                input_y2_values = [y_axis_range['max'] - (y_axis_range['max'] - y_axis_range['min']) / 12.],
            )

    ########################################################################

    if var == 't_2m' or var == 't_850hPa' or var == 'lapse_rate_850hPa-500hPa':
        ref_th = 5
    else:
        ref_th = 0
    ref_level_line = magics.mgraph(
            graph_line_colour = 'black',
            graph_line_thickness = ref_th,
        )
    ref_level_value = magics.minput(
            input_x_type = 'date',
            input_date_x_values = [str(time_start), str(time_end)],
            input_y_values = [y_axis_range['ref'], y_axis_range['ref']]
        )

    ########################################################################

    if lead_time > 0:
        init_timeline_th = 5
    else:
        init_timeline_th = 0

    #if making_comparison_plots:
    time_init = time_start + datetime.timedelta(0, 3600 * int(lead_time + 1))

    init_timeline_line = magics.mgraph(
            graph_line_colour = 'red',
            graph_line_thickness = init_timeline_th,
        )
    init_timeline_value = magics.minput(
            input_x_type = 'date',
            input_date_x_values = [str(time_init), str(time_init)],
            input_y_values = [y_axis_range['min'], y_axis_range['max']]
        )

    ########################################################################

    if plot_type == 'w2w_city':
        title_str = '<b>{} in {}</b>'.format(meta['var'], point['name'].replace('_',' '))
    elif plot_type == 'user_point':
        if point['lat'] >= 0.0 and point['lon'] >= 0.0:
            coord_str = '{:.2f}°N, {:.2f}°E'.format(abs(point['lat']), abs(point['lon']))
        elif point['lat'] >= 0.0 and point['lon'] < 0.0:
            coord_str = '{:.2f}°N, {:.2f}°W'.format(abs(point['lat']), abs(point['lon']))
        elif point['lat'] < 0.0 and point['lon'] >= 0.0:
            coord_str = '{:.2f}°S, {:.2f}°E'.format(abs(point['lat']), abs(point['lon']))
        elif point['lat'] < 0.0 and point['lon'] < 0.0:
            coord_str = '{:.2f}°S, {:.2f}°W'.format(abs(point['lat']), abs(point['lon']))
        title_str = '<b>{} in {}</b> ({})'.format(meta['var'], point['name'], coord_str)

    title = magics.mtext(
            text_line_1 = title_str,
            text_font_size = 1.0,
            text_colour = 'black',
            text_justification = 'left',
            text_mode = 'positional',
            text_box_x_position = 5.85,
            text_box_y_position = 5.45,
            text_box_x_length = 8.0,
            text_box_y_length = 0.7,
        )

    ########################################################################

    initial_time = run_time.hour + timeshift
    if timeshift == 0:
        time_code = 'UTC'                           # UTC+1
    if timeshift == 1:
        time_code = 'CET'                           # UTC+1
    elif timeshift == 2:
        time_code = 'CEST'                          # UTC+2

    init_time_str = 'Initial time: {}, {:02}{}'.format(\
                        run_time.strftime('%a., %d %b. %Y'), initial_time, time_code)
    init_time = magics.mtext(
            text_line_1 = init_time_str,
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'left',
            text_mode = 'positional',
            text_box_x_position = 1.55,
            text_box_y_position = 5.45,
            text_box_x_length = 1.5,
            text_box_y_length = 0.5,
        )

    shading_area_text_str1 = 'ICON-Global-EPS forecasts for day 5-7.5'
    shading_area_text_str2 = 'not available for {:02}{} initial time'.format(initial_time, time_code)
    shading_area_text1 = magics.mtext(
            text_line_count = 2,
            text_line_1 = shading_area_text_str1,
            text_line_2 = shading_area_text_str2,
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = 10.65,
            text_box_y_position = 2.3,
            text_box_x_length = 4.0,
            text_box_y_length = 1.3,
            text_border = 'off',
            text_box_blanking = 'on',
        )

    ########################################################################

    unit_str = meta['units']
    unit = magics.mtext(
            text_line_1 = unit_str,
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'right',
            text_mode = 'positional',
            text_box_x_position = 0.86,
            text_box_y_position = 5.51,
            text_box_x_length = 0.5,
            text_box_y_length = 0.5,
        )

    if var == 't_2m' or var == 't_850hPa':
        unit_special_str = 'o'
        correction = -0.12
    elif var == 'direct_rad' or var == 'diffuse_rad':
        unit_special_str = '2'
        correction = 0.06
    else:
        unit_special_str = ''
        correction = 0
    unit_special = magics.mtext(
            text_line_1 = unit_special_str,
            text_font_size = 0.4,
            text_colour = 'black',
            text_justification = 'right',
            text_mode = 'positional',
            text_box_x_position = 0.86 + correction,
            text_box_y_position = 5.51+0.14,
            text_box_x_length = 0.5,
            text_box_y_length = 0.5,
        )

    ########################################################################

    logo_percentiles = magics.mimport(
                    import_file_name = path['base'] + 'data/plots/additional/' + 'percentiles_description.png',
                    import_x_position = 0.18,
                    import_y_position = 1.5,
                    import_height = 3.340,
                    import_width =  0.720,
                )

    logo_w2w = magics.mimport(
                    import_file_name = path['base'] + 'data/plots/additional/' + 'w2w_icon.png',
                    import_x_position = 13.95,
                    import_y_position = 5.52,
                    import_height = 0.474,
                    import_width =  1.000,
                )

    ########################################################################

    if models == 'both-eps':
        if var == 't_2m':
            if extend_with_global:
                legend = magics.mlegend(
                        legend_text_font_size = 0.7,
                        legend_box_mode = 'positional',
                        legend_box_x_position = 4.49,
                        legend_box_y_position = 5.07,
                        legend_box_x_length = 12.0,
                        legend_box_y_length = 0.5,
                        legend_entry_text_width = 90,
                    )
            else:
                legend = magics.mlegend(
                        legend_text_font_size = 0.7,
                        legend_box_mode = 'positional',
                        legend_box_x_position = 7.5,
                        legend_box_y_position = 5.07,
                        legend_box_x_length = 8.0,
                        legend_box_y_length = 0.5,
                        legend_entry_text_width = 90,
                    )
        elif var == 'wind_10m':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 8.4,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 7.5,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        elif var == 'wind_3pl':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 5.45,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 10.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        elif extend_with_global:
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 9.9,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 5.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        else:
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 12.55,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 3.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )

    elif models == 'icon-global-eps':
        if var == 't_2m':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 3.55,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 11.8,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        else:
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 12.2,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 3.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )

    ########################################################################

    date1 = time_start - datetime.timedelta(0,3600 * time_start.hour)
    if time_start.hour - timeshift + 1 <= 6:
        date1 += datetime.timedelta(0,3600 * 12)
    else:
        date1 += datetime.timedelta(1,3600 * 12)

    correction_start = 0
    correction_end = 0
    if date['hour'] == 0:
        factor = 2
    elif date['hour'] == 6:
        factor = 1
        correction_start = 0.2
    elif date['hour'] == 12:
        factor = 4
        correction_end = 0.0
    elif date['hour'] == 18:
        factor = 3
    else:
        print(time_start.hour, timeshift)

    spacing = 1.73
    left_pos = 0.92 - timeshift * 0.11 + factor * spacing / 4
    date1_label = magics.mtext(
            text_line_1 = date1.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 0 * spacing + correction_start,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date2 = date1 + datetime.timedelta(1)
    date2_label = magics.mtext(
            text_line_1 = date2.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 1 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date3 = date1 + datetime.timedelta(2)
    date3_label = magics.mtext(
            text_line_1 = date3.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 2 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date4 = date1 + datetime.timedelta(3)
    date4_label = magics.mtext(
            text_line_1 = date4.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 3 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date5 = date1 + datetime.timedelta(4)
    date5_label = magics.mtext(
            text_line_1 = date5.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 4 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date6 = date1 + datetime.timedelta(5)
    date6_label = magics.mtext(
            text_line_1 = date6.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 5 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date7 = date1 + datetime.timedelta(6)
    date7_label = magics.mtext(
            text_line_1 = date7.strftime('%a., %d %b.'),
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 6 * spacing + correction_end,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    magics.context.silent = True

    if models == 'both-eps':
        if not extend_with_global:
            if var == 't_2m':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_6h,
                        bar_minmax_eu_6h,
                        data_p1090_eu_6h,
                        bar_p1090_eu_6h,
                        data_p2575_eu_6h,
                        bar_p2575_eu_6h,
                        data_median_eu_6h,
                        bar_median_eu_6h,
                        data_minmax_eu_1h,
                        bar_minmax_eu_1h,
                        data_p1090_eu_1h,
                        bar_p1090_eu_1h,
                        data_p2575_eu_1h,
                        bar_p2575_eu_1h,
                        data_median_eu_1h,
                        bar_median_eu_1h,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            elif var == 'prec_rate' or var == 'snow_rate' or var == 'direct_rad' or var == 'diffuse_rad':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_1h,
                        bar_minmax_eu_1h,
                        data_p1090_eu_1h,
                        bar_p1090_eu_1h,
                        data_p2575_eu_1h,
                        bar_p2575_eu_1h,
                        data_median_eu_1h,
                        bar_median_eu_1h,
                        data_minmax_eu_3h,
                        bar_minmax_eu_3h,
                        data_p1090_eu_3h,
                        bar_p1090_eu_3h,
                        data_p2575_eu_3h,
                        bar_p2575_eu_3h,
                        data_median_eu_3h,
                        bar_median_eu_3h,
                        data_minmax_eu_6h,
                        bar_minmax_eu_6h,
                        data_p1090_eu_6h,
                        bar_p1090_eu_6h,
                        data_p2575_eu_6h,
                        bar_p2575_eu_6h,
                        data_median_eu_6h,
                        bar_median_eu_6h,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            elif var == 'wind_10m':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_mean,
                        bar_minmax_eu_mean,
                        data_p1090_eu_mean,
                        bar_p1090_eu_mean,
                        data_p2575_eu_mean,
                        bar_p2575_eu_mean,
                        data_median_eu_mean,
                        bar_median_eu_mean,
                        data_minmax_eu_gust,
                        bar_minmax_eu_gust,
                        data_p1090_eu_gust,
                        bar_p1090_eu_gust,
                        data_p2575_eu_gust,
                        bar_p2575_eu_gust,
                        data_median_eu_gust,
                        bar_median_eu_gust,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            elif var == 'wind_3pl':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_300hPa,
                        bar_minmax_eu_300hPa,
                        data_p1090_eu_300hPa,
                        bar_p1090_eu_300hPa,
                        data_p2575_eu_300hPa,
                        bar_p2575_eu_300hPa,
                        data_median_eu_300hPa,
                        bar_median_eu_300hPa,
                        data_minmax_eu_500hPa,
                        bar_minmax_eu_500hPa,
                        data_p1090_eu_500hPa,
                        bar_p1090_eu_500hPa,
                        data_p2575_eu_500hPa,
                        bar_p2575_eu_500hPa,
                        data_median_eu_500hPa,
                        bar_median_eu_500hPa,
                        data_minmax_eu_850hPa,
                        bar_minmax_eu_850hPa,
                        data_p1090_eu_850hPa,
                        bar_p1090_eu_850hPa,
                        data_p2575_eu_850hPa,
                        bar_p2575_eu_850hPa,
                        data_median_eu_850hPa,
                        bar_median_eu_850hPa,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            else:
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_all,
                        bar_minmax_eu_all,
                        data_p1090_eu_all,
                        bar_p1090_eu_all,
                        data_p2575_eu_all,
                        bar_p2575_eu_all,
                        data_median_eu_all,
                        bar_median_eu_all,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        else:
            if var == 't_2m':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_6h,
                        bar_minmax_eu_6h,
                        data_p1090_eu_6h,
                        bar_p1090_eu_6h,
                        data_p2575_eu_6h,
                        bar_p2575_eu_6h,
                        data_median_eu_6h,
                        bar_median_eu_6h,
                        data_minmax_eu_1h,
                        bar_minmax_eu_1h,
                        data_p1090_eu_1h,
                        bar_p1090_eu_1h,
                        data_p2575_eu_1h,
                        bar_p2575_eu_1h,
                        data_median_eu_1h,
                        bar_median_eu_1h,
                        data_minmax_global,
                        bar_minmax_global,
                        data_p1090_global,
                        bar_p1090_global,
                        data_p2575_global,
                        bar_p2575_global,
                        data_median_global,
                        bar_median_global,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            elif var == 'prec_rate':
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_1h,
                        bar_minmax_eu_1h,
                        data_p1090_eu_1h,
                        bar_p1090_eu_1h,
                        data_p2575_eu_1h,
                        bar_p2575_eu_1h,
                        data_median_eu_1h,
                        bar_median_eu_1h,
                        data_minmax_eu_3h,
                        bar_minmax_eu_3h,
                        data_p1090_eu_3h,
                        bar_p1090_eu_3h,
                        data_p2575_eu_3h,
                        bar_p2575_eu_3h,
                        data_median_eu_3h,
                        bar_median_eu_3h,
                        data_minmax_eu_6h,
                        bar_minmax_eu_6h,
                        data_p1090_eu_6h,
                        bar_p1090_eu_6h,
                        data_p2575_eu_6h,
                        bar_p2575_eu_6h,
                        data_median_eu_6h,
                        bar_median_eu_6h,
                        data_minmax_global,
                        bar_minmax_global,
                        data_p1090_global,
                        bar_p1090_global,
                        data_p2575_global,
                        bar_p2575_global,
                        data_median_global,
                        bar_median_global,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
            else:
                magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_eu_all,
                        bar_minmax_eu_all,
                        data_p1090_eu_all,
                        bar_p1090_eu_all,
                        data_p2575_eu_all,
                        bar_p2575_eu_all,
                        data_median_eu_all,
                        bar_median_eu_all,
                        data_minmax_global,
                        bar_minmax_global,
                        data_p1090_global,
                        bar_p1090_global,
                        data_p2575_global,
                        bar_p2575_global,
                        data_median_global,
                        bar_median_global,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
    elif models == 'icon-global-eps':
        if var == 't_2m':
            magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_global_0_12UTC,
                        bar_minmax_global_0_12UTC,
                        data_p1090_global_0_12UTC,
                        bar_p1090_global_0_12UTC,
                        data_p2575_global_0_12UTC,
                        bar_p2575_global_0_12UTC,
                        data_median_global_0_12UTC,
                        bar_median_global_0_12UTC,
                        data_minmax_global_6_18UTC,
                        bar_minmax_global_6_18UTC,
                        data_p1090_global_6_18UTC,
                        bar_p1090_global_6_18UTC,
                        data_p2575_global_6_18UTC,
                        bar_p2575_global_6_18UTC,
                        data_median_global_6_18UTC,
                        bar_median_global_6_18UTC,
                        data_minmax_global_1h,
                        bar_minmax_global_1h,
                        data_p1090_global_1h,
                        bar_p1090_global_1h,
                        data_p2575_global_1h,
                        bar_p2575_global_1h,
                        data_median_global_1h,
                        bar_median_global_1h,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        elif var == 'prec_rate':
            magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_global_1h,
                        bar_minmax_global_1h,
                        data_p1090_global_1h,
                        bar_p1090_global_1h,
                        data_p2575_global_1h,
                        bar_p2575_global_1h,
                        data_median_global_1h,
                        bar_median_global_1h,
                        data_minmax_global_3h,
                        bar_minmax_global_3h,
                        data_p1090_global_3h,
                        bar_p1090_global_3h,
                        data_p2575_global_3h,
                        bar_p2575_global_3h,
                        data_median_global_3h,
                        bar_median_global_3h,
                        data_minmax_global_6h,
                        bar_minmax_global_6h,
                        data_p1090_global_6h,
                        bar_p1090_global_6h,
                        data_p2575_global_6h,
                        bar_p2575_global_6h,
                        data_median_global_6h,
                        bar_median_global_6h,
                        data_minmax_global_12h,
                        bar_minmax_global_12h,
                        data_p1090_global_12h,
                        bar_p1090_global_12h,
                        data_p2575_global_12h,
                        bar_p2575_global_12h,
                        data_median_global_12h,
                        bar_median_global_12h,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        else:
            magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
                        ref_level_value,
                        ref_level_line,
                        data_minmax_global,
                        bar_minmax_global,
                        data_p1090_global,
                        bar_p1090_global,
                        data_p2575_global,
                        bar_p2575_global,
                        data_median_global,
                        bar_median_global,
                        title,
                        init_time,
                        unit,
                        unit_special,
                        logo_w2w,
                        logo_percentiles,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )

    return

########################################################################################################################
########################################################################################################################
########################################################################################################################

def get_variable_title_unit(var):
    if var == 't_2m':
        meta = dict(var = '2-m temperature', units = 'C')
    elif var == 'prec_rate':
        meta = dict(var = 'Precipitation rate', units = 'mm/h')
    elif var == 'snow_rate':
        meta = dict(var = 'Snow rate (water equivalent)', units = 'mm/h')
    elif var == 'prec_sum':
        meta = dict(var = 'Accumulated precipitation', units = 'mm')
    elif var == 'wind_10m':
        meta = dict(var = '10-m wind', units = 'km/h')
    elif var == 'wind_mean_10m':
        meta = dict(var = '10-m mean wind', units = 'km/h')
    elif var == 'vmax_10m':
        meta = dict(var = '10-m wind gust', units = 'km/h')
    elif var == 'mslp':
        meta = dict(var = 'Mean sea level pressure', units = 'hPa')
    elif var == 'clct':
        meta = dict(var = 'Total cloud cover', units = '%')
    elif var == 'direct_rad':
        meta = dict(var = 'Direct downward sw radiation', units = 'W/m')
    elif var == 'diffuse_rad':
        meta = dict(var = 'Diffuse downward sw radiation', units = 'W/m')
    elif var == 'tqv':
        meta = dict(var = 'Integrated water vapour', units = 'mm')
    elif var == 'gph_500hPa':
        meta = dict(var = '500hPa geopotential height', units = 'gpdm')
    elif var == 't_850hPa':
        meta = dict(var = '850hPa temperature', units = 'C')
    elif var == 'wind_3pl':
        meta = dict(var = 'Wind speed on pressure levels', units = 'km/h')
    elif var == 'shear_0-6km':
        meta = dict(var = '0-6km wind shear', units = 'm/s')
    elif var == 'lapse_rate_850hPa-500hPa':
        meta = dict(var = '850hPa-500hPa mean lapse rate', units = 'K/km')
    elif var == 'cape_ml':
        meta = dict(var = 'Mixed Layer CAPE', units = 'J/kg')

    return meta

########################################################################
########################################################################
########################################################################

def get_meta_data(var):

    if var == 't_2m':
        meta = dict(var = 'Temperature at 2m', units = 'degree celsius')
    elif var == 'prec_rate':
        meta = dict(var = 'Total Precipitation Rate, Average of Time Interval before fcst_hour',
                    units = 'mm/h')
    elif var == 'snow_rate':
        meta = dict(var = 'Snow Rate (Water Equivalent), Average of Time Interval before fcst_hour',
                    units = 'mm/h')
    elif var == 'prec_sum':
        meta = dict(var = 'Total Precipitation Sum', units = 'mm')
    elif var == 'wind_mean_10m':
        meta = dict(var = 'Momentary Wind Speed at 10m', units = 'km/h')
    elif var == 'mslp':
        meta = dict(var = 'Mean Sea Level Pressure', units = 'hPa')
    elif var == 'clct':
        meta = dict(var = 'Total Cloud Cover', units = 'percent')
    elif var == 'direct_rad':
        meta = dict(var = 'Direct Downward Shortwave Radiation, Average of Time Interval before fcst_hour',
                    units = 'W/m^2')
    elif var == 'diffuse_rad':
        meta = dict(var = 'Diffuse Downward Shortwave Radiation, Average of Time Interval before fcst_hour',
                    units = 'W/m^2')
    elif var == 'vmax_10m':
        meta = dict(var = 'Wind Gust at 10m, Maximum of Time Interval before fcst_hour', units = 'km/h')
    elif var == 'tqv':
        meta = dict(var = 'Total Column Integrated Water Vapour', units = 'mm')
    elif var == 't_850hPa':
        meta = dict(var = 'Temperature at 850hPa', units = 'degree celsius')
    elif var == 'wind_850hPa':
        meta = dict(var = 'Momentary Wind Speed at 850hPa', units = 'km/h')
    elif var == 'wind_300hPa':
        meta = dict(var = 'Momentary Wind Speed at 300hPa', units = 'km/h')
    elif var == 'gph_500hPa':
        meta = dict(var = 'Geopotential Height at 500hPa', units = 'gpdm')
    elif var == 'gph_300hPa':
        meta = dict(var = 'Geopotential Height at 300hPa', units = 'gpdm')
    elif var == 'shear_0-6km':
        meta = dict(var = 'Momentary Vertical Wind Shear 0-6km (Difference of 10m and 500hPa Wind Vector)',
                    units = 'm/s')
    elif var == 'lapse_rate_850hPa-500hPa':
        meta = dict(var = 'Mean Lapse Rate 850hPa-500hPa', units = 'K/km')


    return meta

########################################################################
########################################################################
########################################################################

def fit_y_axis_to_data(var, y_axis_range, pointname):

    if var == 't_2m':
        mean = (y_axis_range['max'] + y_axis_range['min']) / 2
        if y_axis_range['min'] < mean - 9.0:
            y_axis_range['min'] -= 1.0
        else:
            y_axis_range['min'] = mean - 10.0
        if y_axis_range['max'] > mean + 8.0:
            y_axis_range['max'] += 2.0
        else:
            y_axis_range['max'] = mean + 10.0
        y_axis_range['interval'] = 5.0
        y_axis_range['ref'] = 0.0

    elif var == 'prec_rate' or var == 'snow_rate':
        y_axis_range['min'] = -0.1
        if y_axis_range['max'] < 2.75:
            y_axis_range['max'] = 3.0
            y_axis_range['interval'] = 0.5
        elif y_axis_range['max'] < 6.0:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 1.0
        elif y_axis_range['max'] < 12.0:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 2.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 3.0
        y_axis_range['ref'] = 0.0

    elif var == 'prec_sum':
        y_axis_range['min'] = -0.8
        if y_axis_range['max'] < 8.0:
            y_axis_range['max'] = 10.0
            y_axis_range['interval'] = 2.0
        elif y_axis_range['max'] < 20.0:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 3.0
        elif y_axis_range['max'] < 40.0:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 5.0
        elif y_axis_range['max'] < 80.0:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 10.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 20.0
        y_axis_range['ref'] = 0.0

    elif var == 'wind_10m':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 30.0:
            y_axis_range['max'] = 30.0
            y_axis_range['interval'] = 5.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'wind_mean_10m':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 27.5:
            y_axis_range['max'] = 30.0
            y_axis_range['interval'] = 5.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'vmax_10m':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 30.0:
            y_axis_range['max'] = 30.0
            y_axis_range['interval'] = 5.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'mslp':
        if y_axis_range['min'] < 990.0:
            y_axis_range['min'] -= 5.0
        else:
            y_axis_range['min'] = 990.0
        if y_axis_range['max'] > 1037.0:
            y_axis_range['max'] += 5.0
        else:
            y_axis_range['max'] = 1040.0
        y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'clct':
        y_axis_range['min'] = -6.0
        y_axis_range['max'] = 110.0
        y_axis_range['interval'] = 20.0
        y_axis_range['ref'] = 0.0

    elif var == 'direct_rad':
        y_axis_range['min'] = -20.0
        if y_axis_range['max'] < 280.0:
            y_axis_range['max'] = 300.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
        y_axis_range['interval'] = 100.0
        y_axis_range['ref'] = 0.0

    elif var == 'diffuse_rad':
        y_axis_range['min'] = -20.0
        if y_axis_range['max'] < 280.0:
            y_axis_range['max'] = 300.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
        y_axis_range['interval'] = 100.0
        y_axis_range['ref'] = 0.0

    elif var == 'tqv':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 30.0:
            y_axis_range['max'] = 30.0
            y_axis_range['interval'] = 5.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
            y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 't_850hPa':
        if False: #pointname == 'Karlsruhe' or pointname == 'Mainz' or pointname == 'Munich':
            ##### hard axis with extension if over borders #####
            if y_axis_range['min'] < 0.0:
                y_axis_range['min'] -= 2.5
            else:
                y_axis_range['min'] = 0.0
            if y_axis_range['max'] > 25.0:
                y_axis_range['max'] += 2.5
            else:
                y_axis_range['max'] = 25.0
            y_axis_range['interval'] = 5.0
            y_axis_range['ref'] = 0.0
        else:
            ##### dynamical axis with plot in the middle #####
            mean = (y_axis_range['max'] + y_axis_range['min']) / 2
            if y_axis_range['min'] < mean - 9.0:
                y_axis_range['min'] -= 1.0
            else:
                y_axis_range['min'] = mean - 10.0
            if y_axis_range['max'] > mean + 9.0:
                y_axis_range['max'] += 1.0
            else:
                y_axis_range['max'] = mean + 10.0
            y_axis_range['interval'] = 5.0
            y_axis_range['ref'] = 0.0

    elif var == 'gph_500hPa':
        if y_axis_range['min'] < 530.0:
            y_axis_range['min'] -= 5.0
        else:
            y_axis_range['min'] = 530.0
        if y_axis_range['max'] > 595.0:
            y_axis_range['max'] += 5.0
        else:
            y_axis_range['max'] = 595.0
        y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'wind_3pl':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 100.0:
            y_axis_range['max'] = 100.0
            y_axis_range['interval'] = 20.0
        else:
            y_axis_range['max'] += 0.08 * y_axis_range['max']
            y_axis_range['interval'] = 20.0
        y_axis_range['ref'] = 0.0

    elif var == 'shear_0-6km':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 30.0:
            y_axis_range['max'] = 30.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
        y_axis_range['interval'] = 10.0
        y_axis_range['ref'] = 0.0

    elif var == 'lapse_rate_850hPa-500hPa':
        if y_axis_range['min'] < 0.0:
            y_axis_range['min'] -= 1.0
        else:
            y_axis_range['min'] = 0.0
        y_axis_range['max'] = 11.0
        y_axis_range['interval'] = 2.0
        y_axis_range['ref'] = 9.8

    elif var == 'cape_ml':
        y_axis_range['min'] = 0.0
        if y_axis_range['max'] < 500.0:
            y_axis_range['max'] = 500.0
        else:
            y_axis_range['max'] += 0.1 * y_axis_range['max']
        y_axis_range['interval'] = 100.0
        y_axis_range['ref'] = 0.0

    return y_axis_range

########################################################################
########################################################################
########################################################################

def expand_time_avg_data(model, fcst_hours_list_old, data_percentiles_old):
    if model == 'icon-global-eps_eu-extension':
        fcst_hours_list_new = list(range(121, fcst_hours_list_old[-1]+1, 1))
        iteration_length = len(fcst_hours_list_old)
    else:
        fcst_hours_list_new = list(range(fcst_hours_list_old[0]+1, fcst_hours_list_old[-1]+1, 1))
        iteration_length = len(fcst_hours_list_old)-1
    data_percentiles_new = np.zeros((len(fcst_hours_list_new), 7), dtype='float32')

    for i in range(iteration_length):
        if model == 'icon-global-eps_eu-extension':
            delta_t = 12
        else:
            delta_t = fcst_hours_list_old[i+1] - fcst_hours_list_old[i]
        for j in range(delta_t):
            #print(i, j, fcst_hours_list_old[0], fcst_hours_list_old[i] + j - fcst_hours_list_old[0], data_percentiles_new.shape)
            data_percentiles_new[fcst_hours_list_old[i] + j - fcst_hours_list_old[0], :] = data_percentiles_old[i, :]
    data_percentiles_new = np.where(data_percentiles_new >= 0., data_percentiles_new, 0.)
    data_percentiles_new = np.around(data_percentiles_new, 2)

    return fcst_hours_list_new, data_percentiles_new

########################################################################
########################################################################
########################################################################
