#########################################
###  container for various functions  ###
#########################################

import numpy as np
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
from w2w_ensembleplots.core.extract_point_from_grib import read_data


########################################################################
########################################################################
########################################################################

def plot_in_magics_boxplot(path, date, pointname, var, meta, y_axis_range, filename,
                            fcst_hours_list_eu, fcst_hours_list_global,
                            data_percentiles_eu, data_percentiles_global,
                            include_global, with_long_time_axis, lead_time):

    run_time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
    timeshift = get_timeshift()

    time_start = run_time + datetime.timedelta(0, 3600 * int(fcst_hours_list_eu[0] - 1 + timeshift))
    if with_long_time_axis:
        time_end   = run_time + datetime.timedelta(0, 3600 * int(fcst_hours_list_global[-1] + 3 + timeshift))
    else:
        time_end   = run_time + datetime.timedelta(0, 3600 * int(fcst_hours_list_eu[-1] + 3 + timeshift))

    if not include_global and with_long_time_axis:
        shading_area_time = [str(run_time + datetime.timedelta(0,3600 * int(fcst_hours_list_global[-1] + 3 - 24*1.25\
                                                                            + timeshift)))]

    if var == 'vmax_10m':
        fcst_hours_list_eu = fcst_hours_list_eu[1:]

    if var == 't_2m':
        fcst_hours_list_eu_6h = [x for x in fcst_hours_list_eu if x % 6 == 0]
        fcst_hours_list_eu_1h = [x for x in fcst_hours_list_eu if x not in fcst_hours_list_eu_6h]

        dates_eu_6h = []
        for time_step in fcst_hours_list_eu_6h:
            dates_eu_6h.append(str(run_time + datetime.timedelta(0, 3600 * int(time_step + timeshift))))
        dates_eu_1h = []
        for time_step in fcst_hours_list_eu_1h:
            dates_eu_1h.append(str(run_time + datetime.timedelta(0, 3600 * int(time_step + timeshift))))            

        data_percentiles_eu_6h = data_percentiles_eu[[list(fcst_hours_list_eu).index(x) for x in fcst_hours_list_eu_6h]]
        data_percentiles_eu_1h = data_percentiles_eu[[list(fcst_hours_list_eu).index(x) for x in fcst_hours_list_eu_1h]]

    elif var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum' or var == 'vmax_10m' or var == 'tqv'\
     or var == 't_850hPa' or var == 'gph_500hPa' or var == 'wind_850hPa' or var == 'shear_0-6km'\
     or var == 'lapse_rate_850hPa-500hPa':
        if var == 'vmax_10m':
            timerangeshift = 0.5
        else:
            timerangeshift = 0.0
        dates_eu_all = []
        for time_step in fcst_hours_list_eu:
            dates_eu_all.append(str(run_time + datetime.timedelta(0, int(3600 * (time_step + timeshift\
                                                                                 + timerangeshift)))))

    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        dates_eu_all = []
        for i in range(len(fcst_hours_list_eu)-1):
            dates_eu_all.append(str(run_time + datetime.timedelta(0,\
                int(3600 * ((fcst_hours_list_eu[i] + fcst_hours_list_eu[i+1]) / 2 + timeshift) ))))

    if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m'\
     or var == 'clct'):
        dates_global = []
        if var == 't_2m' or var == 'wind_10m' or var == 'clct' or var == 'prec_sum':
            for time_step in fcst_hours_list_global:
                dates_global.append(str(run_time + datetime.timedelta(0, 3600 * int(time_step + timeshift))))
        elif var == 'prec_rate':
            for time_step in fcst_hours_list_global:
                dates_global.append(str(run_time + datetime.timedelta(0, 3600 * int(time_step - 6 + timeshift))))


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
            subpage_x_position = 1.0,
            subpage_y_position = 0.48,
            subpage_x_length = 13.7,
            subpage_y_length = 5.0,
        )

    vertical_axis = magics.maxis(
            axis_orientation = 'vertical',
            axis_grid = 'on',
            axis_type = 'regular',
            axis_tick_label_height = 0.7,
            axis_tick_label_colour = 'charcoal',
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
                legend_user_text = '<font colour="black"> ICON-EU-EPS (20km): 2,8,14,20 CEST</font>'
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

    if var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum' or var == 'vmax_10m' or var == 'tqv'\
     or var == 't_850hPa' or var == 'gph_500hPa' or var == 'wind_850hPa' or var == 'shear_0-6km' or var == 'lapse_rate_850hPa-500hPa':
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

    if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m' or var == 'clct'):
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
                graph_bar_width = 3600 * 0.6,
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
                graph_bar_width = 3600 * 1.0,
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
                graph_bar_width = 3600 * 1.0,
            )
        data_median_global = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_global,
                input_y_values  = data_percentiles_global[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                input_y2_values = data_percentiles_global[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
            )

    ########################################################################
    ########################################################################

    if var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        bar_minmax_eu_1h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'black',
                graph_bar_width = 3600 * 0.15,
            )
        data_minmax_eu_1h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[:48],
                input_y_values  = data_percentiles_eu[:48,0],
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
                graph_bar_width = 3600 * 1.0,
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
                graph_bar_width = 3600 * 1.0,
            )
        data_median_eu_1h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[:48],
                input_y_values  = data_percentiles_eu[:48,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
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
                input_y_values  = data_percentiles_eu[48:56,0],
                input_y2_values = data_percentiles_eu[48:56,6],
            )
        bar_p1090_eu_3h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                graph_bar_width = 3600 * 1.5,
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
                graph_bar_width = 3600 * 3.0,
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
                graph_bar_width = 3600 * 3.0,
            )
        data_median_eu_3h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[48:56],
                input_y_values  = data_percentiles_eu[48:56,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                input_y2_values = data_percentiles_eu[48:56,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
            )

    ########################################################################

        bar_minmax_eu_6h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'black',
                graph_bar_width = 3600 * 0.15,
            )
        data_minmax_eu_6h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[56:],
                input_y_values  = data_percentiles_eu[56:,0],
                input_y2_values = data_percentiles_eu[56:,6],
            )
        bar_p1090_eu_6h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                graph_bar_width = 3600 * 3.0,
            )
        data_p1090_eu_6h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[56:],
                input_y_values = data_percentiles_eu[56:,1],
                input_y2_values = data_percentiles_eu[56:,5],
            )
        bar_p2575_eu_6h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'rgb(0, 150, 130)', # KIT turquoise
                graph_bar_width = 3600 * 6.0,
                legend = 'on',
                legend_user_text = '<font colour="black"> ICON-EU-EPS (20km)</font>'
            )
        data_p2575_eu_6h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[56:],
                input_y_values = data_percentiles_eu[56:,2],
                input_y2_values = data_percentiles_eu[56:,4],
            )
        bar_median_eu_6h = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'black',
                graph_bar_width = 3600 * 6.0,
            )
        data_median_eu_6h = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_eu_all[56:],
                input_y_values  = data_percentiles_eu[56:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                input_y2_values = data_percentiles_eu[56:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
            )

    ########################################################################

    if include_global and var == 'prec_rate':
        bar_minmax_global = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'black',
                graph_bar_width = 3600 * 0.15,
            )
        data_minmax_global = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_global,
                input_y_values  = data_percentiles_global[:,0],
                input_y2_values = data_percentiles_global[:,6],
            )
        bar_p1090_global = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'rgb(88, 217, 34)', # green
                graph_bar_width = 3600 * 6.0,
            )
        data_p1090_global = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_global,
                input_y_values  = data_percentiles_global[:,1],
                input_y2_values = data_percentiles_global[:,5],
            )
        bar_p2575_global = magics.mgraph(
                graph_type = 'bar',
                graph_bar_colour = 'rgb(88, 217, 34)', # green
                graph_bar_width = 3600 * 12.0,
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
                graph_bar_width = 3600 * 12.0,
            )
        data_median_global = magics.minput(
                input_x_type = 'date',
                input_date_x_values = dates_global,
                input_y_values  = data_percentiles_global[:,3] - (y_axis_range['max'] - y_axis_range['min']) / 400.,
                input_y2_values = data_percentiles_global[:,3] + (y_axis_range['max'] - y_axis_range['min']) / 400.,
            )

    ########################################################################

    if not include_global and with_long_time_axis:
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

    if var == 't_2m' or var == 'mslp' or var == 't_850hPa' or var == 'lapse_rate_850hPa-500hPa':
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

    title_str = '{} in {}'.format(meta['var'], pointname)
    title = magics.mtext(
            text_line_1 = title_str,
            text_font_size = 1.0,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = 5.3,
            text_box_y_position = 5.45,
            text_box_x_length = 5.0,
            text_box_y_length = 0.7,
        )

    ########################################################################

    initial_time = run_time.hour + timeshift
    if timeshift == 1:
        time_code = 'CET'                           # UTC+1
    elif timeshift == 2:
        time_code = 'CEST'                          # UTC+2

    init_time_str = 'Initial time: {}, {:02}{}'.format(\
                        time_start.strftime('%a., %d %b. %Y'), initial_time, time_code)
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
            text_box_x_position = 10.5,
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
            text_box_x_position = 0.31,
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
            text_box_x_position = 0.31 + correction,
            text_box_y_position = 5.51+0.14,
            text_box_x_length = 0.5,
            text_box_y_length = 0.5,
        )

    ########################################################################

    logo = magics.mimport(
                    import_file_name = path['base'] + 'plots/logo/' + 'w2w_icon.png',
                    import_x_position = 13.74,
                    import_y_position = 5.52,
                    import_height = 0.474,
                    import_width =  1.000,
                )

    ########################################################################

    if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m' or var == 'clct'):
        if var == 't_2m':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 4.2,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 12.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        elif var == 'wind_10m' or var == 'clct' or var == 'prec_sum' or var == 'prec_rate':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 9.7,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 5.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
    else:
        if var == 't_2m':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 7.15,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 8.3,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )
        elif var == 'wind_10m' or var == 'clct' or var == 'prec_sum' or var == 'mslp'\
         or var == 'direct_rad' or var == 'diffuse_rad' or var == 'prec_rate' or var == 'vmax_10m'\
         or var == 'tqv' or var == 't_850hPa' or var == 'gph_500hPa' or var == 'wind_850hPa'\
         or var == 'shear_0-6km' or var == 'lapse_rate_850hPa-500hPa':
            legend = magics.mlegend(
                    legend_text_font_size = 0.7,
                    legend_box_mode = 'positional',
                    legend_box_x_position = 12.3,
                    legend_box_y_position = 5.07,
                    legend_box_x_length = 3.0,
                    legend_box_y_length = 0.5,
                    legend_entry_text_width = 90,
                )

    ########################################################################

    if with_long_time_axis:
        date1 = time_start - datetime.timedelta(0,3600 * time_start.hour)
        if time_start.hour - timeshift + 1 <= 6:
            date1 += datetime.timedelta(0,3600 * 12)
        else:
            date1 += datetime.timedelta(1,3600 * 12)

        correction_start = 0
        correction_end = 0
        if time_start.hour - timeshift + 1 == 0:
            factor = 2
        elif time_start.hour - timeshift + 1 == 6:
            factor = 1
            correction_start = 0.2
        elif time_start.hour - timeshift + 1 == 12:
            factor = 4
            correction_end = -0.4
        elif time_start.hour - timeshift + 1 == 18:
            factor = 3
        else:
            print(time_start.hour, timeshift)

        spacing = 1.78
        left_pos = 0.40 - timeshift * 0.11 + factor * spacing / 4
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
    else:
        date1 = time_start - datetime.timedelta(0,3600 * time_start.hour)
        if time_start.hour - timeshift + 1 <= 6:
            date1 += datetime.timedelta(0,3600 * 12)
        else:
            date1 += datetime.timedelta(1,3600 * 12)

        correction_end = 0
        if time_start.hour - timeshift + 1 == 0:
            factor = 2
        elif time_start.hour - timeshift + 1 == 6:
            factor = 1
        elif time_start.hour - timeshift + 1 == 12:
            factor = 4
            correction_end = -0.4
        elif time_start.hour - timeshift + 1 == 18:
            factor = 3

        spacing = 2.65
        left_pos = 0.40 - timeshift * 0.11 + factor * spacing / 4
        date1_label = magics.mtext(
                text_line_1 = date1.strftime('%a., %d %b.'),
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
                text_box_x_position = left_pos + 4 * spacing + correction_end,
                text_box_y_position = 0.0,
                text_box_x_length = 1.5,
                text_box_y_length = 0.3,
                text_border = 'off',
            )

    magics.context.silent = True
    if var == 't_2m':
        if include_global:
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        elif not include_global and with_long_time_axis:
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
                        data_shading_area,
                        bar_shading_area,
                        title,
                        init_time,
                        shading_area_text1,
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        )
    if var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum' or var == 'vmax_10m' or var == 'tqv'\
     or var == 't_850hPa' or var == 'gph_500hPa' or var == 'wind_850hPa' or var == 'shear_0-6km' or var == 'lapse_rate_850hPa-500hPa':
        if include_global and (var == 'wind_10m' or var == 'clct' or var == 'prec_sum'):
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        elif not include_global and with_long_time_axis:
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
                        data_shading_area,
                        bar_shading_area,
                        title,
                        init_time,
                        shading_area_text1,
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        )

    if include_global:
        if var == 'prec_rate':
            magics.plot(
                        output_layout,
                        page_layout,
                        coord_system,
                        vertical_axis,
                        horizontal_axis,
                        init_timeline_value,
                        init_timeline_line,
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
        elif var == 'direct_rad' or var == 'diffuse_rad':
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                        date6_label,
                        date7_label,
                        )
    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        if not include_global and with_long_time_axis:
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
                        data_shading_area,
                        bar_shading_area,
                        title,
                        init_time,
                        shading_area_text1,
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
                        logo,
                        legend,
                        date1_label,
                        date2_label,
                        date3_label,
                        date4_label,
                        date5_label,
                    )

    return

############################################################################
############################################################################
############################################################################

def boxplot_forecast(pointnames, date_user, include_global, latest_fcst, verbose):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list_eu = np.concatenate((np.arange(0,48,1),\
                                        np.arange(48,72,3),\
                                        np.arange(72,120+1,6)))
    fcst_hours_list_global = np.arange(132,180+1,12)

    if include_global:
        model = 'icon-global-eps'
    else:
        model = 'icon-eu-eps'

    date = calc_latest_run_time(model)
    if date_user is not None:
        date = date_user

    print('-- Forecast time: {}{:02}{:02}-{:02}UTC --'.format(\
          date['year'], date['month'], date['day'], date['hour']))

    if date['hour'] == 0 or date['hour'] == 12:
        #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m',\
        #            'tqv','gph_500hPa','t_850hPa','wind_850hPa','shear_0-6km','lapse_rate_850hPa-500hPa']
        var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad','t_850hPa']
        with_long_time_axis = True

    elif date['hour'] == 6 or date['hour'] == 18:
        #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m']
        var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad']
        with_long_time_axis = False

    with_long_time_axis = True


    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                points_eu_eps = '',
                points_global_eps = '',
                plots = '')

    ##### main loop #####

    for var in var_list:
        if var == 't_2m':
            meta = dict(var = '2-m temperature', units = 'C')
            var_str = var
        elif var == 'prec_rate':
            meta = dict(var = 'Precipitation rate', units = 'mm/h')
            var_str = var
        elif var == 'prec_sum':
            meta = dict(var = 'Precipitation sum', units = 'mm')
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
            meta = dict(var = 'Direct downward sw radiation', units = 'W/m')
            var_str = 'aswdir_s'
        elif var == 'diffuse_rad':
            meta = dict(var = 'Diffuse downward sw radiation', units = 'W/m')
            var_str = 'aswdifd_s'
        elif var == 'vmax_10m':
            meta = dict(var = '10-m wind gust', units = 'km/h')
            var_str = var
        elif var == 'tqv':
            meta = dict(var = 'Integrated water vapour', units = 'mm')
            var_str = var
        elif var == 'gph_500hPa':
            meta = dict(var = '500hPa geopotential height', units = 'gpdm')
            var_str = var
        elif var == 't_850hPa':
            meta = dict(var = '850hPa temperature', units = 'C')
            var_str = var
        elif var == 'wind_850hPa':
            meta = dict(var = '850hPa wind speed', units = 'km/h')
            var_str = var
        elif var == 'shear_0-6km':
            meta = dict(var = '0-6km wind shear', units = 'm/s')
            var_str = var
        elif var == 'lapse_rate_850hPa-500hPa':
            meta = dict(var = '850hPa-500hPa mean lapse rate', units = 'K/km')
            var_str = var


        for pointname in pointnames:
            if verbose:
                print('----- next point is {} -----'.format(pointname))
                print('----- next variable is {} -----'.format(var))
            
            path_old = dict(base = path['base'],
                            points_eu_eps = path['points_eu_eps'],
                            points_global_eps = path['points_global_eps'],
                            plots = path['plots'])

            if latest_fcst:
                lead_times = [0]
            else:
                lead_times = [0,12,24,36,48,72,96,120,144,168]

            y_axis_range = dict()
            i = 0
            for lead_time in lead_times:
                time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
                time -= datetime.timedelta(0, 3600 * lead_time)
                old_run_date = dict(year = time.year, month = time.month, day = time.day, hour = time.hour)


                ##### get data from icon-eu-eps #####

                path_old['points_eu_eps'] = 'forecast_archive/icon-eu-eps/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                    old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str)

                first_run_not_found = False
                try:
                    point_values_old_eu_eps = read_data(path_old, old_run_date, var_str, pointname, 'icon-eu-eps')
                    if var == 'prec_sum':
                        point_values_old_eu_eps = reduce_prec_sum(point_values_old_eu_eps, fcst_hours_list_eu)
                    if i == 0:
                        y_axis_range['min'] = np.amin(point_values_old_eu_eps)
                        y_axis_range['max'] = np.amax(point_values_old_eu_eps)
                    else:
                        if np.amin(point_values_old_eu_eps) < y_axis_range['min']:
                            y_axis_range['min'] = np.amin(point_values_old_eu_eps)
                        if np.amax(point_values_old_eu_eps) > y_axis_range['max']:
                            y_axis_range['max'] = np.amax(point_values_old_eu_eps)
                except (FileNotFoundError, AssertionError):
                    print('-- no icon-eu-eps data found in minmax loop --')
                    first_run_not_found = True
                    if var == 'mslp':
                        y_axis_range['min'] = 980.0
                        y_axis_range['max'] = 1035.0
                    else:
                        y_axis_range['min'] = 0.0
                        y_axis_range['max'] = 1.0                        



                ##### get data from icon-eps #####

                if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m' or var == 'clct'):
                    path_old['points_global_eps'] = 'forecast_archive/icon-eps/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                        old_run_date['year'], old_run_date['month'], old_run_date['day'], old_run_date['hour'], var_str)
                    try:
                        point_values_old_global_eps = read_data(path_old, old_run_date, var_str, pointname, 'icon-global-eps')
                        if i == 0 and first_run_not_found:
                            y_axis_range['min'] = np.amin(point_values_old_global_eps)
                            y_axis_range['max'] = np.amax(point_values_old_global_eps)
                        else:
                            if np.amin(point_values_old_global_eps) < y_axis_range['min']:
                                y_axis_range['min'] = np.amin(point_values_old_global_eps)
                            if np.amax(point_values_old_global_eps) > y_axis_range['max']:
                                y_axis_range['max'] = np.amax(point_values_old_global_eps)
                    except (FileNotFoundError, AssertionError):
                        pass

                i += 1

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

            elif var == 'vmax_10m':
                y_axis_range['min'] = 0.0
                if y_axis_range['max'] < 30.0:
                    y_axis_range['max'] = 30.0
                    y_axis_range['interval'] = 5.0
                else:
                    y_axis_range['max'] += 0.1 * y_axis_range['max']
                    y_axis_range['interval'] = 10.0
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
                if pointname == 'Karlsruhe' or pointname == 'Mainz' or pointname == 'Munich':
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

            elif var == 'wind_850hPa':
                y_axis_range['min'] = 0.0
                if y_axis_range['max'] < 30.0:
                    y_axis_range['max'] = 30.0
                    y_axis_range['interval'] = 5.0
                else:
                    y_axis_range['max'] += 0.1 * y_axis_range['max']
                    y_axis_range['interval'] = 10.0
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


            if latest_fcst:
                lead_times = [0]
            else:
                lead_times = [0,12,24,36,48,72,96,120,144,168]

            for lead_time in lead_times:
                time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
                time -= datetime.timedelta(0, 3600 * lead_time)
                date_run = dict(year = time.year, month = time.month, day = time.day, hour = time.hour)

                ##### make path #####

                if latest_fcst:
                    temp_subdir = 'plots/operational/boxplots_forecast/latest_forecast/'
                else:
                    temp_subdir = 'plots/operational/boxplots_forecast/comparison_forecast/{:03}h_ago/'.format(lead_time)

                temp_subdir = temp_subdir + pointname
                if not os.path.isdir(path['base'] + temp_subdir):
                    os.mkdir(path['base'] + temp_subdir)
                path['plots'] = temp_subdir + '/'

                filename = 'boxplot_{:03}h_ago_{}_{}'.format(\
                            lead_time, var, pointname)


                ##### get data from icon-eu-eps #####

                try:
                    path['points_eu_eps'] = 'forecast_archive/icon-eu-eps/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                            date_run['year'], date_run['month'], date_run['day'], date_run['hour'], var_str)
                    point_values_eu_eps = read_data(path, date_run, var_str, pointname, 'icon-eu-eps')

                    #if var == 'prec_sum':
                    #    point_values_eu_eps = reduce_prec_sum(point_values_eu_eps, fcst_hours_list_eu)

                except (FileNotFoundError, AssertionError):
                    print('no icon-eu-eps data')
                    if var == 'vmax_10m':
                        point_values_eu_eps = np.ones((64, 40)) * -100   # will be out of plot
                    else:
                        point_values_eu_eps = np.ones((65, 40)) * -100   # will be out of plot


                ##### get data from icon-eps #####

                if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m' or var == 'clct'):
                    try:
                        path['points_global_eps'] = 'forecast_archive/icon-eps/extracted_points/run_{}{:02}{:02}{:02}/{}/'.format(\
                                                date_run['year'], date_run['month'], date_run['day'], date_run['hour'], var)
                        point_values_global_eps = read_data(path, date_run, var_str, pointname, 'icon-global-eps')

                    except (FileNotFoundError, AssertionError):
                        if var == 't_2m' or var == 'wind_10m' or var == 'clct' or var == 'prec_sum' or var == 'prec_rate':
                            print('no icon-global-eps data')
                        point_values_global_eps = np.ones((5, 40)) * -100   # will be out of plot


                ##### calculate percentiles #####

                # data_percentiles_eu: 65 timesteps x 7 percentiles
                # data_percentiles_global: 5 timesteps x 7 percentiles
                data_percentiles_eu_eps = np.percentile(point_values_eu_eps, [0,10,25,50,75,90,100], axis = 1).T
                if include_global and (var == 't_2m' or var == 'prec_rate' or var == 'prec_sum' or var == 'wind_10m' or var == 'clct'):
                    data_percentiles_global_eps = np.percentile(point_values_global_eps, [0,10,25,50,75,90,100], axis = 1).T
                else:
                    data_percentiles_global_eps = None


                ##### plotting #####

                plot_in_magics_boxplot(path, date_run, pointname, var, meta, y_axis_range, filename,
                                       fcst_hours_list_eu, fcst_hours_list_global,
                                       data_percentiles_eu_eps, data_percentiles_global_eps,
                                       include_global, with_long_time_axis, lead_time)
            del y_axis_range

    return

########################################################################
########################################################################
########################################################################

def reduce_prec_sum(point_values_eu_eps, fcst_hours_list_eu):
    timespan = 0
    old_mean = 0.0

    for i in range(1, len(fcst_hours_list_eu)):
        new_mean = np.nanmean(point_values_eu_eps[i,:])
        if abs(new_mean - old_mean) < 0.001:
            timespan += fcst_hours_list_eu[i] - fcst_hours_list_eu[i-1]
            if timespan >= 6:
                timespan = 0
                point_values_eu_eps[i:,:] -= point_values_eu_eps[i,:]
        old_mean = new_mean


    return point_values_eu_eps

########################################################################
########################################################################
########################################################################

