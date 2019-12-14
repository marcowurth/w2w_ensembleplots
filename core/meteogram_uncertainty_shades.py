#########################################
###  container for various functions  ###
#########################################

import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.neighbors.kde import KernelDensity

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time
from w2w_ensembleplots.core.extract_point_from_grib import read_data


########################################################################
########################################################################
########################################################################

def plot_tmax_uncertainty_shades(path, run, point, ens_points):

    colorpalette = Oranges_9.mpl_colormap

    ymin = 20
    ymax = 45

    image_height = 461
    image_width = 65
    #image_width = 124

    num_days = 5
    kde_width = 0.8
    kernel = 'epanechnikov'

    y_vec = np.linspace(ymin, ymax, image_height)
    ens_density = np.empty((image_height, num_days))
    for i in range(num_days):
        kde = KernelDensity(kernel=kernel, bandwidth=kde_width).fit(ens_points[i, :][:, None])
        ens_density[:, i] = np.exp(kde.score_samples(y_vec[:, None]))

        #plt.plot(y_vec, ens_density[:, i], 'o')
        #plt.show()


    image = np.empty((image_height, image_width, num_days))
    for i in range(num_days):
        image[:, :, i] = np.tile(ens_density[:, i],(image_width,1)).T
    background = np.zeros((image_height, 619))
    background[10, 10] = 1

    fig, ax = plt.subplots(figsize = [800 / 100, 600 / 100])
    fig.figimage(background, xo=101, yo=66,
                 cmap=colorpalette, origin='lower')
    for i in range(num_days):
        fig.figimage(image[:, :, i], xo=(101 + 62 + 124 * i - image_width / 2), yo=66, vmax=0.6,
                     cmap=colorpalette, origin='lower')

    ax.set(xlim=(0, 5), ylim=(ymin, ymax), yticks=np.arange(ymin, ymax+1, 5))
    ax.set(xticks=np.arange(0.5, 5, 1), xticklabels=['day {}'.format(i) for i in range(1, 6)])
    ax.set_xlabel('forecast time', labelpad=10)
    ax.set_ylabel(r'$^\circ$C', labelpad=20, rotation='horizontal')
    plt.title('tmax forecast for {}, icon-eu-eps run from 21.07.2019, 00UTC'.format(point['name']))


    #ax.plot(np.arange(0.5, 5, 1), point['measurements'], 'kx', zorder=15)

    filename = 'tmax_{}_run_{:02d}.{:02d}_{}.png'.format(point['name'], run['day'], run['month'], kernel)
    plt.savefig(path['base'] + path['plots'] + filename)

    return

########################################################################
########################################################################
########################################################################

def plot_t2m_uncertainty_shades(pointnames, date_user, mode, colorpalette_name, verbose):

    ##### make lists of forecast hours and variables #####

    fcst_hours_list_eu = np.concatenate((np.arange(0,48,1),\
                                        np.arange(48,72,3),\
                                        np.arange(72,120+1,6)))
    fcst_hours_list_global = np.arange(132,180+1,12)

    if mode == '180h_raw':
        model = 'icon-global-eps'
    else:
        model = 'icon-eu-eps'

    run = calc_latest_run_time(model)
    if date_user is not None:
        run = date_user

    print('-- Forecast time: {}{:02}{:02}-{:02}UTC --'.format(\
          run['year'], run['month'], run['day'], run['hour']))


    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                points_eu_eps = '',
                points_global_eps = '',
                plots = 'plots/experimental/uncertainty_shades/',
                cityfolder = '',
                colorpalette = 'additional_data/colorpalettes/')

    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])
    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.mkdir(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/'

    for pointname in pointnames:
        if verbose:
            print('----- next point is {} -----'.format(pointname))

        #subfolder = pointname
        #if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        #    os.mkdir(path['base'] + path['plots'] + subfolder)
        #path['cityfolder'] = subfolder + '/'


        ##### get data from icon-eu-eps #####

        try:
            pathstr = 'forecast_archive/icon-eu-eps/extracted_points/'
            path['points_eu_eps'] = '{}run_{}{:02}{:02}{:02}/t_2m/'.format(\
                                    pathstr, run['year'], run['month'], run['day'], run['hour'])
            point_values_eu_eps = read_data(path, run, 't_2m', pointname, 'icon-eu-eps')

        except (FileNotFoundError, AssertionError):
            print('no icon-eu-eps data')
            point_values_eu_eps = np.ones((65, 40)) * -100   # will be out of plot

        if mode == '48h_interpolated':
            point_values_eu_eps = point_values_eu_eps[:49]
            fcst_hours_list_eu = fcst_hours_list_eu[:49]

        ##### get data from icon-eps #####

        if mode == '180h_raw':
            try:
                pathstr = 'forecast_archive/icon-eps/extracted_points/'
                path['points_global_eps'] = '{}run_{}{:02}{:02}{:02}/t_2m/'.format(\
                                            pathstr, run['year'], run['month'], run['day'], run['hour'])
                point_values_global_eps = read_data(path, run, 't_2m', pointname, 'icon-global-eps')

            except (FileNotFoundError, AssertionError):
                print('no icon-global-eps data')
                point_values_global_eps = np.ones((5, 40)) * -100   # will be out of plot


        y_axis_range = dict()
        if mode == '180h_raw':
            y_axis_range['min'] = min(point_values_eu_eps.min(), point_values_global_eps.min())
            y_axis_range['max'] = max(point_values_eu_eps.max(), point_values_global_eps.max())
        else:
            y_axis_range['min'] = point_values_eu_eps.min()
            y_axis_range['max'] = point_values_eu_eps.max()

        mean = (y_axis_range['max'] + y_axis_range['min']) / 2

        if y_axis_range['min'] < mean - 9.0:
            y_axis_range['min'] -= 1.0
        else:
            y_axis_range['min'] = mean - 10.0

        if y_axis_range['max'] > mean + 9.0:
            y_axis_range['max'] += 1.0
        else:
            y_axis_range['max'] = mean + 10.0

        y_axis_range['min'] = np.around(y_axis_range['min'])
        y_axis_range['max'] = np.around(y_axis_range['max'])

########################################################################

        if mode == '120h_raw':
            data_values = point_values_eu_eps
        elif mode == '48h_interpolated':
            num_intersteps = 30
            data_values = np.zeros((48*num_intersteps+1, 40), dtype='float32')
            for member in range(40):
                for timestep in range(0, 48):
                    for n in range(num_intersteps):
                        data_values[timestep*num_intersteps+n, member] =\
                            (1-n/num_intersteps) * point_values_eu_eps[timestep, member]\
                            + (n/num_intersteps) * point_values_eu_eps[timestep+1, member]
                data_values[48*num_intersteps, member] = point_values_eu_eps[48, member]

########################################################################

        if colorpalette_name == 'palettable_orange':
            from palettable.colorbrewer.sequential import Oranges_9
            colorpalette = Oranges_9.mpl_colormap

        elif colorpalette_name == 'custom':
            colorpalette_source = 'tristenca'

            if colorpalette_source == 'tristenca':
                filename = 'colorscale_tristenca_t2m_monohue_blues_1.txt'
                with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
                    line = f.read()

                num_colors = int(len(line) / 8)
                inverse_colorpalette = True


                hex_colors = []
                for i in range(num_colors):
                    start = i * 8 + 1
                    end = start + 6
                    hex_colors.append(line[start:end])

                if not inverse_colorpalette:
                    custom_palette_list = [[255, 255, 255]]
                    for hex_color in hex_colors[:]:
                        rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
                        custom_palette_list.append(rgb_color)
                else:
                    custom_palette_list = []
                    for hex_color in hex_colors[:]:
                        rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
                        custom_palette_list.append(rgb_color)
                    custom_palette_list.append([255, 255, 255])
                    custom_palette_list = custom_palette_list[::-1]


            elif colorpalette_source == 'hclwizard':
                filename = 'colorscale_hclwizard_t2m_prob_plasma.txt'
                with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
                    lines = f.readlines()

                hex_colors = []
                for line in lines:
                    hex_colors.append(line[2:8])

                custom_palette_list = [[255, 255, 255]]           # extra white color
                for hex_color in hex_colors[:]:
                    rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
                    custom_palette_list.append(rgb_color)
                #custom_palette_list.append(custom_palette_list[-1])     # extra color for correct LabelBar view

            colorpalette = mpl.colors.ListedColormap(np.array(custom_palette_list) / 255)


########################################################################

        image_height = 539

        if mode == '120h_raw':
            image_width = 12
            num_times = 65
        elif mode == '48h_interpolated':
            image_width = 1
            num_times = 48*num_intersteps+1

        kernel = 'epanechnikov'
        kde_width = 0.8
        vmax = 0.6

        y_vec = np.linspace(y_axis_range['min'], y_axis_range['max'], image_height)
        ens_density = np.empty((image_height, num_times))
        for i in range(num_times):
            kde = KernelDensity(kernel=kernel, bandwidth=kde_width).fit(data_values[i, :][:, None])
            ens_density[:, i] = np.exp(kde.score_samples(y_vec[:, None]))

            #plt.plot(y_vec, ens_density[:, i], 'o')
            #plt.show()


        image = np.empty((image_height, image_width, num_times))
        for i in range(num_times):
            image[:, :, i] = np.tile(ens_density[:, i],(image_width,1)).T
        background = np.zeros((image_height, 1426))
        background[10, 10] = 1

        fig, ax = plt.subplots(figsize = [1500 / 100, 600 / 100])
        fig.tight_layout()
        #figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()

        y_axis_tick_min = ((y_axis_range['min'] + 204) // 5 - 40) * 5

        if mode == '120h_raw':
            fig.figimage(background, xo=48, yo=39,
                         cmap=colorpalette, origin='lower')
            for i in range(num_times):
                fig.figimage(image[:, :, i], xo=(81 + 272 / 24 * fcst_hours_list_eu[i] - image_width / 2),\
                             yo=39, vmax=vmax, cmap=colorpalette, origin='lower')

            ax.set(xlim=(-3, 120+3), ylim=(y_axis_range['min'], y_axis_range['max']),\
                   yticks=np.arange(y_axis_tick_min, y_axis_range['max'] + 0.1, 5))
            #ax.set(xticks=np.arange(0, 121, 24), xticklabels=['day {}'.format(i) for i in range(1, 6)])
            ax.set(xticks=np.arange(0, 121, 24))

        elif mode == '48h_interpolated':
            for i in range(num_times):
                fig.figimage(image[:, :, i], xo=(81 + 272 / 9.6 / num_intersteps * i - image_width / 2),\
                             yo=39, vmax=vmax, cmap=colorpalette, origin='lower')

            ax.set(xlim=(-1.2, 48+1.2), ylim=(y_axis_range['min'], y_axis_range['max']),\
                   yticks=np.arange(y_axis_tick_min, y_axis_range['max'] + 0.1, 5))
            ax.set(xticks=np.arange(0, 49, 6))

        ax.set_xlabel('forecast time', labelpad=10)
        ax.set_ylabel(r'$^\circ$C', labelpad=20, rotation='horizontal')
        plt.title('t2m forecast for {}, icon-eu-eps run from {:02d}.{:02d}.{:4d}, {:02d}UTC'.format(\
                    pointname, run['day'], run['month'], run['year'], run['hour']))


        #ax.plot(np.arange(0.5, 5, 1), point['measurements'], 'kx', zorder=15)

        filename = 'uncertainty_shades_{}_t2m_run_{:4d}{:02d}{:02d}{:02d}_{}.png'.format(\
                    mode, run['year'], run['month'], run['day'], run['hour'], pointname)
        plt.savefig(path['base'] + path['plots'] + filename)

        del fig, ax
        plt.close()

    return

########################################################################
########################################################################
########################################################################

