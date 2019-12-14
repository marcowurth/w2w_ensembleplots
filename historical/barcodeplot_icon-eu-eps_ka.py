###############################################################################
###  script for plotting barcode meteograms of point data of icon-eu-eps    ###
###  processes latest run if not explicitly specified                       ###
###############################################################################

import numpy as np
import datetime
import time
import sys
from astropy.io import ascii
from Magics.macro import *
from PIL import Image

def main():

    points =   [dict(lat = 49.014, lon =  8.350, name = 'Karlsruhe')]
    mode = 'ka'

    barcodeplot(points, mode)

    return

########################################################################
########################################################################
########################################################################

def barcodeplot(points, mode):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list = np.concatenate((np.arange(0,48,1),\
                                     np.arange(48,72,3),\
                                     np.arange(72,120+1,6)))

    var_list = ['t_2m','prec_sum','wind_10m','mslp','clct']


    ##### calc latest run time #####

    timeshift = 1.0    # MEZ
    datenow  = datetime.datetime.now().date()
    timenow  = datetime.datetime.now().time()
    run_year  = datenow.year
    run_month = datenow.month
    run_day   = datenow.day
    run_time_float = timenow.hour + timenow.minute / 60.

    update_times = np.array([4.5, 9.8, 16.5, 21.8]) + timeshift
    if   run_time_float >= update_times[0] and run_time_float < update_times[1]: run_hour = 0
    elif run_time_float >= update_times[1] and run_time_float < update_times[2]: run_hour = 6
    elif run_time_float >= update_times[2] and run_time_float < update_times[3]: run_hour = 12
    elif run_time_float >= update_times[3]  or run_time_float < update_times[0]: run_hour = 18
    else: exit()

    if run_time_float < update_times[0]:
        run_year, run_month, run_day = go_back_one_day(run_year, run_month, run_day)

    date = dict(year = run_year, month = run_month, day = run_day, hour = run_hour)


    ##### explicit options #####

  ###########################################################
    #date = dict(year = 2019, month = 1, day = 21, hour = 12)
    #point = dict(lat = 49.013, lon =  8.411, name = 'Karlsruhe')
    time_steps_mode = 'original'
    #time_steps_mode = '6h-selected'
    #time_steps_mode = '1h-interpolated'
    model_bias = 0.0
  ###########################################################


    ##### make path #####
    
    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',\
                points = '',\
                plots = '')
    temp_subdir = 'plots/icon-eu-eps/run_%4d%02d%02d%02d'\
     % (date['year'], date['month'], date['day'], date['hour'])

    if not os.path.isdir(path['base'] + temp_subdir):
        os.mkdir(path['base'] + temp_subdir)
    subdir_run = temp_subdir + '/'
    if mode == 'ka':
        temp_subdir = subdir_run + '_sorted_by_cities'
        if not os.path.isdir(path['base'] + temp_subdir):
            os.mkdir(path['base'] + temp_subdir)

    
    ##### main loop #####

    for var in var_list:
        #print '----- next variable is %s -----' % var
        if var == 't_2m':
            meta = dict(var = 'Temperature 2m', units = 'C')
            var_str = var
        elif var == 'prec_rate':
            meta = dict(var = 'Time-Average Precipitation Rate', units = 'mm/h')
            var_str = var
        elif var == 'prec_sum':
            meta = dict(var = 'Precipitation Sum', units = 'mm')
            var_str = var
        elif var == 'wind_10m':
            meta = dict(var = 'Momentary Wind Speed at 10m', units = 'km/h')
            var_str = var
        elif var == 'mslp':
            meta = dict(var = 'Mean Sea Level Pressure', units = 'hPa')
            var_str = var
        elif var == 'clct':
            meta = dict(var = 'Total Cloud Cover', units = '%')
            var_str = var
        elif var == 'direct_rad':
            meta = dict(var = 'Time-Average Direct Downward Shortwave Radiation', units = 'W/m^2')
            var_str = 'aswdir_s'
        elif var == 'diffuse_rad':
            meta = dict(var = 'Time-Average Diffuse Downward Shortwave Radiation', units = 'W/m^2')
            var_str = 'aswdifd_s'

        for point in points:
            if mode == 'ka':
                temp_subdir = subdir_run + '_sorted_by_cities/' + point['name']
                if not os.path.isdir(path['base'] + temp_subdir):
                    os.mkdir(path['base'] + temp_subdir)
                path['plots'] = temp_subdir + '/'
                path['points'] = 'forecast_archive/icon-eu-eps/point_data/run_%4d%02d%02d%02d/%s/'\
                 % (date['year'], date['month'], date['day'], date['hour'], var_str)
            elif mode == 'non-ka':
                temp_subdir = subdir_run + var
                if not os.path.isdir(path['base'] + temp_subdir):
                    os.mkdir(path['base'] + temp_subdir)
                path['plots'] = temp_subdir + '/'
                path['points'] = 'forecast_archive/icon-eu-eps/point_data/run_%4d%02d%02d%02d/%s/'\
                 % (date['year'], date['month'], date['day'], date['hour'], var_str)

            #print '----- next point is %s -----' % point['name']
            point_values = read_data(path, date, var_str, point)
            #print 'input data shape: %dx%d' % (point_values.shape[0], point_values.shape[1])


            ##### select timesteps #####

            # selected_time_steps: 65/21/121 timesteps
            if time_steps_mode == 'original':
                selected_time_steps = fcst_hours_list
            elif time_steps_mode == 'original-wide':
                selected_time_steps = fcst_hours_list
            elif time_steps_mode == '6h-selected':
                selected_time_steps = np.float32(fcst_hours_list[np.where(fcst_hours_list % 6 == 0)])
            elif time_steps_mode == '1h-interpolated':
                selected_time_steps = np.arange(0,120+1,1)

            # data_all_members: 65/21/121 timesteps x 40 ens members
            if time_steps_mode == 'original':
                data_all_members = point_values
            if time_steps_mode == 'original-wide':
                data_all_members = point_values
            elif time_steps_mode == '6h-selected':
                data_all_members = point_values[np.where(fcst_hours_list % 6 == 0),:][0,:,:]
            elif time_steps_mode == '1h-interpolated':
                data_all_members = interpolate_data(point_values, fcst_hours_list)


            ##### correct bias #####

            data_all_members += model_bias


            ##### calculate percentiles #####

            # data_percentiles: 21/65 timesteps x 7 percentiles
            data_percentiles = np.percentile(data_all_members, [0,10,25,50,75,90,100], axis = 1).T

            #print 'plotted data shape: %dx%d' % (data_percentiles.shape[0], data_percentiles.shape[1])
            #print '-----'


            ##### plotting #####

            epsboxplot(path, date, point, var, meta, selected_time_steps, time_steps_mode, data_all_members)

    return

############################################################################
############################################################################
############################################################################

def epsboxplot(path, date, point, var, meta, selected_time_steps, time_steps_mode, data_all_members):

    run_time = datetime.datetime(date['year'], date['month'], date['day'], date['hour'])
    timeshift = 1   # MEZ = UTC+1
    dates = []
    if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum':
        for time_step in selected_time_steps:
            dates.append(str(run_time + datetime.timedelta(0, 3600 * (time_step + timeshift))))
    elif var == 'prec_rate' or var == 'direct_rad' or var == 'diffuse_rad':
        for i in range(len(selected_time_steps)-1):
            dates.append(str(run_time + datetime.timedelta(0,\
                3600 * ((selected_time_steps[i] + selected_time_steps[i+1]) / 2. + timeshift))))

    time_start = str(run_time + datetime.timedelta(0, 3600 * (selected_time_steps[0] - 1 + timeshift)))
    time_end   = str(run_time + datetime.timedelta(0, 3600 * (selected_time_steps[-1] + 3 + timeshift)))

    if time_steps_mode == '6h-selected':
        width_factor = 2.0
    else:
        width_factor = 1.0

    page_layout = page(
            layout = 'positional',
            page_x_position = 0.0,
            page_y_position = 0.0,
            page_x_length = 18.0,
            page_y_length = 9.5,
            page_id_line='off',
        )

    if var == 't_2m':
        ymin = -10.0
        ymax =  20.0
        y_interval = 5.0
        y_ref = 0.0
    elif var == 'prec_rate':
        ymin =  0.0
        ymax = 5.0
        y_interval = 1.0
    elif var == 'prec_sum':
        ymin =  0.0
        ymax = 30.0
        y_interval = 5.0
        y_ref = 0.0
    elif var == 'wind_10m':
        ymin =  0.0
        ymax = 80.0
        y_interval = 20.0
        y_ref = 0.0
    elif var == 'mslp':
        ymin =  970.0
        ymax = 1050.0
        y_interval = 10.0
        y_ref = 1013.25
    elif var == 'clct':
        ymin =   0.0
        ymax = 100.0
        y_interval = 20.0
        y_ref = 0.0
    elif var == 'direct_rad':
        ymin =   0.0
        ymax = 600.0
        y_interval = 100.0
    elif var == 'diffuse_rad':
        ymin =   0.0
        ymax = 600.0
        y_interval = 100.0

    coord_system = mmap(
            subpage_map_projection = 'cartesian',
            subpage_x_axis_type = 'date',
            subpage_x_date_min = time_start,
            subpage_x_date_max = time_end,
            subpage_y_min = ymin,
            subpage_y_max = ymax,
            subpage_y_axis_type = 'regular',
            subpage_x_position = 2.0,
            subpage_y_position = 1.5,
            subpage_x_length = 17.0,
            subpage_y_length = 9.0,
            subpage_vertical_axis_width = 0.3,
        )


    ##### background #####
    filename = 'barcodeplot_icon-eu-eps_%4d%02d%02d%02d_%s_%s_bg'\
             % (date['year'], date['month'], date['day'],\
                date['hour'], var, point['name'])
    output_layout = output(
            output_formats = ['png'],
            output_name = path['base'] + path['plots'] + filename,
            output_name_first_page_number = 'off',
            output_width = 1400,
            super_page_y_length = 12.0,
            super_page_x_length = 20.0,
        )
    vertical_axis = maxis(
            axis_orientation = 'vertical',
            axis_grid = 'on',
            axis_type = 'regular',
            axis_tick_label_height = 0.6,
            axis_tick_label_colour = 'black',
            axis_grid_colour = 'black',
            axis_grid_thickness = 1,
            axis_grid_line_style='dash',
            axis_tick_interval = y_interval,
        )
    horizontal_axis = maxis(
            axis_type = 'date',
            axis_years_label  = 'off',
            axis_months_label_height = 0.60,
            axis_days_label_height = 0.60,
            axis_tick_thickness = 4,
            axis_minor_tick = 'on',
            axis_grid = 'on',
            axis_grid_colour = 'black',
            axis_grid_thickness = 1,
            axis_grid_line_style = 'dash',
        )

    if var == 't_2m' or var == 'mslp': l_th = 5
    else: l_th = 1
    ref_level_line = mgraph(
            graph_line_colour = 'black',
            graph_line_thickness = l_th,
        )
    ref_level_value = minput(
            input_x_type = 'date',
            input_date_x_values = [time_start, time_end],
            input_y_values = [y_ref, y_ref],
        )

    title_str = '%s in %s' % (meta['var'], point['name'])
    title = mtext(
            text_line_1 = title_str,
            text_font_size = 1.0,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'title',
        )

    unit_str = meta['units']
    unit = mtext(
            text_line_1 = unit_str,
            text_font_size = 0.7,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = 0.9,
            text_box_y_position = 10.8,
            text_box_x_length = 1.5,
            text_box_y_length = 0.5,
        )

    if var == 't_2m': unit_special_str = 'o'
    else: unit_special_str = ''
    unit_special = mtext(
            text_line_1 = unit_special_str,
            text_font_size = 0.4,
            text_colour = 'black',
            text_justification = 'centre',
            text_mode = 'positional',
            text_box_x_position = 0.78,
            text_box_y_position = 10.94,
            text_box_x_length = 1.5,
            text_box_y_length = 0.5,
        )

    if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum':
        plot(
                output_layout,
                page_layout,
                coord_system,
                vertical_axis,
                horizontal_axis,
                ref_level_value,
                ref_level_line,
                title,
                unit,
                unit_special,
            )

    ##### barcode plots #####
    for j in range(40):
        filename = 'barcodeplot_icon-eu-eps_%4d%02d%02d%02d_%s_%s_m%02d'\
                 % (date['year'], date['month'], date['day'],\
                    date['hour'], var, point['name'], j+1)
        output_layout = output(
                output_formats = ['png'],
                output_name = path['base'] + path['plots'] + filename,
                output_name_first_page_number = 'off',
                output_width = 1400,
                super_page_y_length = 12.0,
                super_page_x_length = 20.0,
                output_cairo_transparent_background = 'on',
            )
        vertical_axis = maxis(
                axis_orientation = 'vertical',
                axis_type = 'regular',
                axis_tick_label_height = 0.0,
                axis_tick_label_colour = 'black',
                axis_tick_interval = y_interval,
            )
        horizontal_axis = maxis(
                axis_type = 'date',
                axis_years_label  = 'off',
                axis_months_label_height = 0.0,
                axis_days_label_height = 0.0,
            )

        if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum':
            y_delta = (ymax - ymin) / 750.

            line_member = mgraph(
                    graph_type = 'bar',
                    graph_bar_colour = 'rgba(0.,0.4,1.,1.)',
                    graph_bar_width = 3600 * 0.9,
                    graph_bar_line_colour = 'rgba(1.,1.,1.,0.)',
                )
            data_member = minput(
                    input_x_type = 'date',
                    input_date_x_values = dates,
                    input_y_values = data_all_members[:,j] - y_delta / 2.,
                    input_y2_values = data_all_members[:,j] + y_delta / 2.,
                )

        if var == 't_2m' or var == 'wind_10m' or var == 'mslp' or var == 'clct' or var == 'prec_sum':
            plot(
                    output_layout,
                    page_layout,
                    coord_system,
                    vertical_axis,
                    horizontal_axis,
                    data_member,
                    line_member,
                )

    #clear_warning(18)

    filename_final = 'barcodeplot_icon-eu-eps_%4d%02d%02d%02d_%s_%s.png'\
             % (date['year'], date['month'], date['day'],\
                date['hour'], var, point['name'])

    filename = 'barcodeplot_icon-eu-eps_%4d%02d%02d%02d_%s_%s_bg.png'\
             % (date['year'], date['month'], date['day'],\
                date['hour'], var, point['name'])
    bg = Image.open(path['base'] + path['plots'] + filename)
    os.remove(path['base'] + path['plots'] + filename)

    for j in range(40):
        filename = 'barcodeplot_icon-eu-eps_%4d%02d%02d%02d_%s_%s_m%02d.png'\
                 % (date['year'], date['month'], date['day'],\
                    date['hour'], var, point['name'], j+1)
        member = Image.open(path['base'] + path['plots'] + filename)
        bg.paste(member, (0, 0), member)
        os.remove(path['base'] + path['plots'] + filename)
    bg.save(path['base'] + path['plots'] + filename_final,'png')


    return

############################################################################
############################################################################
############################################################################

def interpolate_data(point_values, time_steps):
    #time_steps = range(72,120+1,6)

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

############################################################################
############################################################################
############################################################################

def read_data(path, date, var, point):
    filename = 'icon-eu-eps_%4d%02d%02d%02d_%s_%s.txt' % (date['year'],\
                 date['month'], date['day'], date['hour'], var, point['name'])

    data_table = ascii.read(path['base'] + path['points'] + filename, format='fixed_width')
    #print data_table
    data = data_table.as_array()

    point_values = np.zeros((len(data), len(data[0])-1), dtype='float32')
    for i in range(len(data)):
        data_row = data[i]
        for j in range(1,len(data[0])):
            point_values[i][j-1] = data_row[j]

    #print 'read %s' % filename

    return point_values
    
########################################################################
########################################################################
########################################################################

def go_back_one_day(run_year, run_month, run_day):
    if run_day >= 2: run_day -= 1
    else:
        # run_day is 1
        if run_year % 4 == 0:
            days_of_month = [31,29,31,30,31,30,31,31,30,31,30,31]
        else:
            days_of_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        if run_month >= 2:
            run_month -= 1
            run_day = days_of_month[run_month-1]
        else:
            # run_month is 1
            run_year -= 1
            run_month = 12
            run_day = days_of_month[run_month-1]

    return run_year, run_month, run_day
    
########################################################################
########################################################################
########################################################################

def clear_warning(num_lines):
    CURSOR_UP_ONE = '\x1b[1A'
    ERASE_LINE = '\x1b[2K'
    for i in range(num_lines):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)
    return

############################################################################
############################################################################

if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print 'total script time:  %0.1fs' % float(t2-t1)
