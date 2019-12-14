#########################################
###  container for various functions  ###
#########################################

import numpy as np
import eccodes
import os
import datetime
import Magics.macro as magics
from astropy.io import ascii

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.download_forecast import get_timeshift
from w2w_ensembleplots.core.extract_point_from_grib import point_savetofile_iconeueps
from w2w_ensembleplots.core.extract_point_from_grib import point_savetofile_iconeudet
from w2w_ensembleplots.core.extract_point_from_grib import read_data


########################################################################
########################################################################
########################################################################

def plot_in_magics_boxplot(path, date, pointname, var, meta, y_axis_range, filename, lead_times,\
                           data_percentiles_eu_eps, point_values_eu_det):

    run_time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])

    if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct':
        lead_times = [-1.0*x for x in lead_times]
    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        lead_times = [-1.0*x for x in lead_times]

    time_start = -123.
    time_end   =    3.

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
            subpage_x_min = time_start,
            subpage_x_max = time_end,
            subpage_y_min = y_axis_range['min'],
            subpage_y_max = y_axis_range['max'],
            subpage_x_position = 1.0,
            subpage_y_position = 0.48,
            subpage_x_length = 13.7,
            subpage_y_length = 5.0,
        )

    vertical_axis = magics.maxis(
            axis_orientation = 'vertical',
            axis_grid = 'on',
            axis_tick_label_height = 0.7,
            axis_grid_thickness = 1,
            axis_grid_line_style='dash',
            axis_tick_interval = y_axis_range['interval'],
        )
    horizontal_axis = magics.maxis(
            axis_tick_interval = 24,
            axis_tick_label = 'off',
            axis_title = 'off',
        )

    ########################################################################

    ##### icon-eu-eps #####
    bar_minmax_eu = magics.mgraph(
            graph_type = 'bar',
            graph_bar_colour = 'black',
            graph_bar_width = 0.05,
        )
    data_minmax_eu = magics.minput(
            input_x_values = lead_times,
            input_y_values = data_percentiles_eu_eps[:,0],
            input_y2_values = data_percentiles_eu_eps[:,6],
        )

    bar1090_eu = magics.mgraph(
            graph_type = 'bar',
            graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
            graph_bar_width = 0.5,
        )
    data1090_eu = magics.minput(
            input_x_values = lead_times,
            input_y_values = data_percentiles_eu_eps[:,1],
            input_y2_values = data_percentiles_eu_eps[:,5],
        )

    bar2575_eu = magics.mgraph(
            graph_type = 'bar',
            graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
            graph_bar_width = 1.0,
            legend = 'on',
            legend_user_text = '<font colour="black"> ICON-EU-EPS (20km)</font>'
        )
    data2575_eu = magics.minput(
            input_x_values = lead_times,
            input_y_values = data_percentiles_eu_eps[:,2],
            input_y2_values = data_percentiles_eu_eps[:,4],
        )

    bar_median_eu = magics.mgraph(
            graph_type = 'bar',
            graph_bar_colour = 'black',
            graph_bar_width = 1.0,
        )
    data_median_eu = magics.minput(
            input_x_values = lead_times,
            input_y_values  = data_percentiles_eu_eps[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
            input_y2_values = data_percentiles_eu_eps[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
        )

    ##### icon-eu #####
    bar_eu_det = magics.mgraph(
            graph_line = 'off',
            graph_symbol = 'on',
            graph_symbol_marker_index = 15,
            graph_symbol_height = 0.2,
            graph_symbol_colour = 'white',
            graph_symbol_outline = 'on',
            graph_symbol_outline_colour = 'black',
            graph_symbol_outline_thickness = 3,
            legend = 'on',
            legend_user_text = '<font colour="black"> ICON-EU-DET (6.5km)</font>'
        )
    data_eu_det = magics.minput(
            input_x_values = lead_times,
            input_y_values = point_values_eu_det[:],
        )

    ########################################################################

    analysis_line = magics.mgraph(
            graph_line_colour = 'rgb(0, 242, 209)', # bright turquoise
            graph_line_thickness = 3,
            legend = 'on',
            legend_user_text = '<font colour="black"> ICON-EU-DET (6.5km), 0h-Forecast</font>'
        )
    analysis_value = magics.minput(
            input_x_values = [time_start, time_end],
            input_y_values = [y_axis_range['analysis'], y_axis_range['analysis']]
        )

    if var == 't_2m' or var == 'mslp':
        ref_th = 5
    else:
        ref_th = 0
    ref_level_line = magics.mgraph(
            graph_line_colour = 'black',
            graph_line_thickness = ref_th,
        )
    ref_level_value = magics.minput(
            input_x_values = [time_start, time_end],
            input_y_values = [y_axis_range['ref'], y_axis_range['ref']]
        )

    ########################################################################

    if var == 'direct_rad' or var == 'diffuse_rad':
        long_title_adjustment = 0.7
    else:
        long_title_adjustment = 0.0

    title_str = '{} in {}'.format(meta['var'], pointname)
    title = magics.mtext(
            text_line_1 = title_str,
            text_font_size = 1.0,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = 5.3 + long_title_adjustment,
            text_box_y_position = 5.45,
            text_box_x_length = 5.0,
            text_box_y_length = 0.7,
        )

    ########################################################################

    timeshift = get_timeshift()
    initial_time = run_time.hour + timeshift

    if timeshift == 1:
        time_code = 'CET'                           # UTC+1
    elif timeshift == 2:
        time_code = 'CEST'                          # UTC+2

    if var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        initial_time2 = initial_time + 6
        if initial_time2 == 26:
            initial_time2 = 2
        init_time_str = 'Forecast time: {}, {:02}-{:02}{}'.format(\
                            run_time.strftime('%a., %d %b. %Y'), initial_time, initial_time2, time_code)
    else:
        init_time_str = 'Forecast time: {}, {:02}{}'.format(\
                            run_time.strftime('%a., %d %b. %Y'), initial_time, time_code)

    init_time = magics.mtext(
            text_line_1 = init_time_str,
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'left',
            text_mode = 'positional',
            text_box_x_position = 1.0,
            text_box_y_position = 5.45,
            text_box_x_length = 1.5,
            text_box_y_length = 0.5,
        )

    unit_str = meta['units']
    unit = magics.mtext(
            text_line_1 = unit_str,
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'right',
            text_mode = 'positional',
            text_box_x_position = 0.31,
            text_box_y_position = 5.55,
            text_box_x_length = 0.5,
            text_box_y_length = 0.5,
        )

    if var == 't_2m':
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
            text_box_x_position = 0.31 + correction,
            text_box_y_position = 5.55+0.14,
            text_box_x_length = 0.5,
            text_box_y_length = 0.5,
        )

    logo = magics.mimport(
                    import_file_name = path['base'] + 'plots/logo/' + 'w2w_icon.png',
                    import_x_position = 13.74,
                    import_y_position = 5.52,
                    import_height = 0.474,
                    import_width =  1.000,
                )

    legend = magics.mlegend(
            legend_text_font_size = 0.8,
            legend_box_mode = 'positional',
            legend_box_x_position = 5.0,
            legend_box_y_position = 5.03,
            legend_box_x_length = 9.0,
            legend_box_y_length = 0.5,
            legend_entry_text_width = 90,
        )

    time_labels = ['-120h','-96h','-72h','-48h','-24h','0h']
    spacing = 2.61
    left_pos = 0.58
    date1_label = magics.mtext(
            text_line_1 = time_labels[0],
            text_font_size = 0.8,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = left_pos + 0 * spacing,
            text_box_y_position = 0.0,
            text_box_x_length = 1.5,
            text_box_y_length = 0.3,
            text_border = 'off',
        )

    date2_label = magics.mtext(
            text_line_1 = time_labels[1],
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

    date3_label = magics.mtext(
            text_line_1 = time_labels[2],
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

    date4_label = magics.mtext(
            text_line_1 = time_labels[3],
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

    date5_label = magics.mtext(
            text_line_1 = time_labels[4],
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

    date6_label = magics.mtext(
            text_line_1 = time_labels[5],
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

    magics.context.silent = True
    magics.plot(
                output_layout,
                page_layout,
                coord_system,
                vertical_axis,
                horizontal_axis,
                ref_level_value,
                ref_level_line,
                data_minmax_eu,
                bar_minmax_eu,
                data1090_eu,
                bar1090_eu,
                data2575_eu,
                bar2575_eu,
                data_median_eu,
                bar_median_eu,
                data_eu_det,
                bar_eu_det,
                analysis_value,
                analysis_line,
                title,
                init_time,
                unit,
                unit_special,
                logo,
                legend,
                date1_label,
                date2_label,
                date3_label,
                date4_label,
                date5_label,
                date6_label,
            )

    return

############################################################################
############################################################################
############################################################################

def boxplot_leadtime(pointnames, date_user, verbose):

    ##### variables #####

    var_list = ['t_2m','wind_10m','mslp','clct','prec_rate','direct_rad','diffuse_rad']
    #var_list = []

    date_fcst = calc_latest_run_time('icon-eu-eps')

    if date_user is not None:
        date_fcst = date_user

    
    print('-- Forecast time: {}{:02}{:02}-{:02}UTC --'.format(\
          date_fcst['year'], date_fcst['month'], date_fcst['day'], date_fcst['hour']))

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                points_eu_eps = '',
                points_eu_det = '',
                plots = '')

    ##### main loop #####

    for var in var_list:
        if var == 't_2m':
            meta = dict(var = '2-m temperature', units = 'C')
            var_str = var
        elif var == 'prec_rate':
            meta = dict(var = 'Precipitation rate', units = 'mm/h')
            var_str = var
        elif var == 'wind_10m':
            meta = dict(var = '10-m wind speed', units = 'km/h')
            var_str = var
        elif var == 'mslp':
            meta = dict(var = 'Mean sea level pressure', units = 'hPa')
            var_str = var
        elif var == 'clct':
            meta = dict(var = 'Total cloud cover', units = '%')
            var_str = var
        elif var == 'direct_rad':
            meta = dict(var = 'Direct downward shortwave radiation', units = 'W/m')
            var_str = 'aswdir_s'
        elif var == 'diffuse_rad':
            meta = dict(var = 'Diffuse downward shortwave radiation', units = 'W/m')
            var_str = 'aswdifd_s'


        ##### make list of lead times #####

        if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct':
            max_lead_time = 120
            fcst_hours_list_eu_eps = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
            fcst_hours_list_eu_det = list(range(0,78,1)) + list(range(78,120+1,3))

            date = date_fcst

        elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
            max_lead_time = 120 - 6
            fcst_hours_list_eu_eps = list(range(1,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
            fcst_hours_list_eu_det = list(range(1,78,1)) + list(range(78,120+1,3))

            date_holder = datetime.datetime(date_fcst['year'], date_fcst['month'], date_fcst['day'], date_fcst['hour'])
            date_holder -= datetime.timedelta(0, 3600 * 6)
            date = dict(year = date_holder.year, month = date_holder.month, day = date_holder.day, hour = date_holder.hour)

        lead_times = list(range(max_lead_time,0-1,-6))


        for pointname in pointnames:
            if verbose:
                print('----- next point is {} -----'.format(pointname))
                print('----- next variable is {} -----'.format(var))
            
            path_old = dict(base = path['base'],
                            points_eu_eps = path['points_eu_eps'],
                            points_eu_det = path['points_eu_det'],
                            plots = path['plots'])

            point_values_eu_eps = np.zeros((len(lead_times), 40), dtype='float32')
            point_values_eu_det = np.zeros((len(lead_times)), dtype='float32')
            i = 0
            for lead_time in lead_times:
                time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
                time -= datetime.timedelta(0, 3600 * lead_time)
                old_run_date = dict(year = time.year, month = time.month, day = time.day, hour = time.hour)

                ##### get data from icon-eu-eps #####

                path_old['points_eu_eps'] = 'forecast_archive/icon-eu-eps/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                    old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str)
                filename = 'icon-eu-eps_{}{:02}{:02}{:02}_{}_{}.txt'.format(\
                    old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str, pointname)

                try:
                    if not os.path.isdir(path_old['base'] + path_old['points_eu_eps']):
                        print('----- extracting data from eps run {}{:02}{:02}-{:02}UTC --'.format(\
                            old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                        point_savetofile_iconeueps(None, old_run_date, var_str, pointname, True, True)

                    elif not os.path.isfile(path_old['base'] + path_old['points_eu_eps'] + filename):
                        print('----- extracting data from eps run {}{:02}{:02}-{:02}UTC --'.format(\
                            old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                        point_savetofile_iconeueps(None, old_run_date, var_str, pointname, True, True)

                    else:
                        print('----- reading data from eps run {}{:02}{:02}-{:02}UTC -----'.format(\
                              old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                    point_values_eu_eps_one_run = read_data(path_old, old_run_date, var_str, pointname, 'icon-eu-eps')
                    if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct':
                        point_values_eu_eps[i,:] = point_values_eu_eps_one_run[fcst_hours_list_eu_eps.index(lead_time),:]
                    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
                        n = fcst_hours_list_eu_eps.index(lead_time + 6)
                        if lead_time + 6 > 72:
                            timestep = 6
                        elif lead_time + 6 > 48:
                            timestep = 3
                        else:
                            timestep = 1
                        k = int(6 / timestep)
                        point_values_eu_eps[i,:] = np.nanmean(point_values_eu_eps_one_run[n-k+1:n+1,:], 0)

                except (FileNotFoundError, AssertionError, eccodes.CodesInternalError):
                    print('----- -> missing eps raw grib file --------------------')
                    point_values_eu_eps[i,:] = np.ones((40)) * -100   # NaN, will be out of plot


                ##### get data from icon-eu #####

                path_old['points_eu_det'] = 'forecast_archive/icon-eu/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                    old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str)
                filename = 'icon-eu-det_{}{:02}{:02}{:02}_{}_{}.txt'.format(\
                    old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str, pointname)

                try:
                    if not os.path.isdir(path_old['base'] + path_old['points_eu_det']):
                        print('----- extracting data from det run {}{:02}{:02}-{:02}UTC --'.format(\
                            old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                        point_savetofile_iconeudet(None, old_run_date, var_str, pointname, True, True)

                    elif not os.path.isfile(path_old['base'] + path_old['points_eu_det'] + filename):
                        print('----- extracting data from det run {}{:02}{:02}-{:02}UTC --'.format(\
                            old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                        point_savetofile_iconeudet(None, old_run_date, var_str, pointname, True, True)

                    else:
                        print('----- reading data from det run {}{:02}{:02}-{:02}UTC -----'.format(\
                              old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour']))

                    point_values_eu_det_one_run = read_data(path_old, old_run_date, var_str, pointname, 'icon-eu-det')
                    if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct':
                        point_values_eu_det[i] = point_values_eu_det_one_run[fcst_hours_list_eu_det.index(lead_time)]
                    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
                        n = fcst_hours_list_eu_det.index(lead_time + 6)
                        if lead_time + 6 > 78:
                            timestep = 3
                        else:
                            timestep = 1
                        k = int(6 / timestep)
                        point_values_eu_det[i] = np.nanmean(point_values_eu_det_one_run[n-k+1:n+1])

                except (FileNotFoundError, AssertionError, eccodes.CodesInternalError):
                    print('----- -> missing det raw grib file --------------------')
                    point_values_eu_det[i] = -100   # NaN, will be out of plot

                i += 1


            ##### calculate total value range #####

            point_values_eu_eps[np.where(point_values_eu_eps==-100)] = np.nan
            point_values_eu_det[np.where(point_values_eu_det==-100)] = np.nan

            y_axis_range = dict(min = np.nanmin(point_values_eu_eps[:]), max = np.nanmax(point_values_eu_eps[:]))
            if np.nanmin(point_values_eu_det[:]) < y_axis_range['min']:
                y_axis_range['min'] = np.nanmin(point_values_eu_det[:])
            if np.nanmax(point_values_eu_det[:]) > y_axis_range['max']:
                y_axis_range['max'] = np.nanmax(point_values_eu_det[:])

            point_values_eu_eps[np.isnan(point_values_eu_eps)] = -100
            point_values_eu_det[np.isnan(point_values_eu_det)] = -100


            ##### set y-axis limits, tick interval and ref value #####

            y_axis_range['analysis'] = point_values_eu_det[-1]

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

            elif var == 'prec_rate':
                y_axis_range['min'] = -0.2
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

            elif var == 'wind_10m':
                y_axis_range['min'] = 0.0
                if y_axis_range['max'] < 27.5:
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


            ##### make path #####

            temp_subdir = 'plots/operational/boxplots_leadtime/run_{}{:02}{:02}{:02}'.format(\
                            date_fcst['year'], date_fcst['month'], date_fcst['day'], date_fcst['hour'])

            if not os.path.isdir(path['base'] + temp_subdir): #and pointname == 'Karlsruhe':
                os.mkdir(path['base'] + temp_subdir)

            temp_subdir = temp_subdir + '/' + pointname
            if not os.path.isdir(path['base'] + temp_subdir):
                os.mkdir(path['base'] + temp_subdir)
            path['plots'] = temp_subdir + '/'

            filename = 'boxplot_leadtime_{}{:02}{:02}{:02}_{}_{}'.format(\
                        date_fcst['year'], date_fcst['month'], date_fcst['day'], date_fcst['hour'], var, pointname)


            ##### calculate percentiles #####

            # data_percentiles_eu: 65 timesteps x 7 percentiles
            data_percentiles_eu_eps = np.percentile(point_values_eu_eps, [0,10,25,50,75,90,100], axis = 1).T


            ##### plotting #####

            plot_in_magics_boxplot(path, date, pointname, var, meta, y_axis_range, filename, lead_times,\
                                   data_percentiles_eu_eps, point_values_eu_det)

            print('------------------------------------------------')

    return

########################################################################
########################################################################
########################################################################

def interpolate_data(point_values, time_steps):
    #time_steps = list(range(72,120+1,6))

    data_interpolated = np.zeros((121, 40), dtype='float32')
    for member in range(40):
        # 1st part: 1h-data:
        data_interpolated[:48+1,member] = point_values[:48+1,member]

        # 2nd part: 3h-data:
        for hour in range(48,72,3):
            data_interpolated[hour,member] = point_values[np.where(time_steps == hour),member][0,0]
            data_interpolated[hour+1,member] = (2./3) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (1./3) * point_values[np.where(time_steps == hour+3),member][0,0]
            data_interpolated[hour+2,member] = (1./3) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (2./3) * point_values[np.where(time_steps == hour+3),member][0,0]

        # 3rd part: 6h-data:
        for hour in range(72,120,6):
            data_interpolated[hour,member] = point_values[np.where(time_steps == hour),member][0,0]
            data_interpolated[hour+1,member] = (5./6) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (1./6) * point_values[np.where(time_steps == hour+6),member][0,0]
            data_interpolated[hour+2,member] = (4./6) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (2./6) * point_values[np.where(time_steps == hour+6),member][0,0]
            data_interpolated[hour+3,member] = (3./6) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (3./6) * point_values[np.where(time_steps == hour+6),member][0,0]
            data_interpolated[hour+4,member] = (2./6) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (4./6) * point_values[np.where(time_steps == hour+6),member][0,0]
            data_interpolated[hour+5,member] = (1./6) * point_values[np.where(time_steps == hour),member][0,0]\
                                             + (5./6) * point_values[np.where(time_steps == hour+6),member][0,0]
        data_interpolated[120,member] = point_values[np.where(time_steps == 120),member][0,0]
    
    return data_interpolated

########################################################################
########################################################################
########################################################################

