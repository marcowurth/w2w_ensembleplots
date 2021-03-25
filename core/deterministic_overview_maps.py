
import os
import datetime
import json

import numpy as np
import Ngl
import Nio
import palettable
import cmasher
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_forecast_data, read_grid_coordinates
from w2w_ensembleplots.core.gridpoint_order import cut_by_domain
#from w2w_ensembleplots.core.calc_icon_pv import calc_pv_on_theta, calc_theta_on_pv


def det_contourplot(domains, variable1, variable2, model, run):

    transfer_to_webserver = True
    #transfer_to_webserver = False

    if model == 'icon-global-det':
        if variable1['name'] == 'prec_sum':
            hours = list(range(6, 180+1, 6))
        elif variable1['name'] == 'prec_24h':
            hours = list(range(24, 180+1, 6))
        else:
            hours = list(range(0, 180+1, 6))
    elif model == 'icon-eu-det':
        if variable1['name'] == 'prec_24h':
            hours = list(range(24, 120+1, 6))
        else:
            hours = list(range(0, 120+1, 6))


    # hours for manual override for testing #

    #hours = list(range(0, 72+1, 1))
    #hours = list(range(0, 78+1, 6))
    #hours = [0]
    #hours = [24]


    if variable2['name'] == '':
        var1var2 = variable1['name']
    else:
        var1var2 = variable1['name'] + '_' + variable2['name']


    # define paths and create folders #

    ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
    # ex_op_str equals either 'experimental' or 'operational' depending on where this script is

    path = dict(base = '/',
                temp = 'data/additional_data/temp/{}/'.format(ex_op_str),
                callfiles = 'progs/{}/w2w_ensembleplots/callfiles/'.format(ex_op_str),
                colorpalette = 'data/additional_data/colorpalettes/',
                shapefiles = 'data/additional_data/shapefiles/')

    path['plots'] = 'data/plots/{}/deterministic_overview_maps/'.format(ex_op_str)
    filename_latest_run = 'latest_run_det_overview_map.txt'

    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])

    if variable1['name'] == 'wind_300hPa':
        with open(path['base'] + path['plots'] + filename_latest_run, 'w') as file:
            file.write(subfolder[4:])

    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.makedirs(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/' 

    if not os.path.isdir(path['base'] + path['plots'] + var1var2):
        os.makedirs(path['base'] + path['plots'] + var1var2)
    path['plots'] += var1var2 + '/'
 

    # load icosahedral grid information and save as npz file #

    numpyarrays_filename = 'deterministic_overview_maps_{}_{}_ndarrays_outofloop.npz'.format(model, var1var2)

    if variable1['load_global_field']:
        if model == 'icon-eu-det':
            clat, clon = read_grid_coordinates(model, variable1['grid'])
            with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                np.savez(f, clat = clat, clon = clon)

        elif model == 'icon-global-det':   
            clat, clon, vlat, vlon = read_grid_coordinates(model, variable1['grid']) 

            if variable2['name'] == '':
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                    np.savez(f, clat = clat, clon = clon, vlat = vlat, vlon = vlon)
            else:
                ll_lat, ll_lon = read_grid_coordinates(model, variable2['grid'])
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                    np.savez(f, clat = clat, clon = clon, vlat = vlat, vlon = vlon, ll_lat = ll_lat, ll_lon = ll_lon)


    # start plotting loop #

    print('plotting model: {}, run: {:02d}.{:02d}.{:4d}, {:02d}UTC, vars: {} {}'.format(
          model, run['day'], run['month'], run['year'], run['hour'],
          variable1['name'], variable2['name']))

    for hour in hours:
        print('forecast hour:', hour)

        if variable1['load_global_field']:
            data_array1 = read_forecast_data(model, variable1['grid'], run, variable1['name'], fcst_hour=hour)

            if variable1['name'] == 't_850hPa'\
             or variable1['name'] == 'theta_e_850hPa':
                contours_max_oro = 1400
                data_oro_icosahedral = read_forecast_data(model, variable1['grid'], run, 'orography', fcst_hour=hour)
                data_array1 = np.where(data_oro_icosahedral > contours_max_oro,
                                       np.ones_like(data_array1) * 9999, data_array1)


            if variable2['name'] != '':
                data_array2_non_cyclic \
                 = read_forecast_data(model, variable2['grid'], run, variable2['name'], fcst_hour=hour)

                if variable2['name'] == 'mslp':
                    lines_max_oro = 1000
                    data_oro_latlon = read_forecast_data(model, variable2['grid'], run, 'orography', fcst_hour=hour)
                    data_array2_non_cyclic = np.where(data_oro_latlon > lines_max_oro,
                                                      np.ones_like(data_array2_non_cyclic) * 9999,
                                                      data_array2_non_cyclic)
                elif variable2['name'] == 'gph_850hPa':
                    lines_max_oro = 1400
                    data_oro_latlon = read_forecast_data(model, variable2['grid'], run, 'orography', fcst_hour=hour)
                    data_array2_non_cyclic = np.where(data_oro_latlon > lines_max_oro,
                                                      np.ones_like(data_array2_non_cyclic) * 9999,
                                                      data_array2_non_cyclic)
                elif variable2['name'] == 'shear_0-6km':
                    lines_max_oro = 1000
                    data_oro_latlon = read_forecast_data(model, variable2['grid'], run, 'orography', fcst_hour=hour)
                    data_array2_non_cyclic = np.where(data_oro_latlon > lines_max_oro,
                                                      np.ones_like(data_array2_non_cyclic) * 9999,
                                                      data_array2_non_cyclic)

                data_array2 = np.empty_like(data_array2_non_cyclic)
                if variable2['grid'] == 'latlon_0.1':
                    data_array2[:, 1799:] = data_array2_non_cyclic[:, :1801]  # flip around the data in lon direction
                    data_array2[:, :1799] = data_array2_non_cyclic[:, 1801:]  # to match positions in the ll_lon array
                elif variable2['grid'] == 'latlon_0.25':
                    data_array2[:, 719:] = data_array2_non_cyclic[:, :721]  # flip around the data in lon direction
                    data_array2[:, :719] = data_array2_non_cyclic[:, 721:]  # to match positions in the ll_lon array

                ''' code for manual add_cyclic: add last lon row before the first lon
                ll_lon = np.empty((ll_lon_non_cyclic.shape[0]+1))
                ll_lon[1:] = ll_lon_non_cyclic[:]
                ll_lon[0] = -180.0
                data_array2 = np.empty((data_array2_non_cyclic.shape[0], data_array2_non_cyclic.shape[1]+1))
                data_array2[:, 720:] = data_array2_non_cyclic[:, :721]
                data_array2[:, 1:720] = data_array2_non_cyclic[:, 721:]
                data_array2[:, 0] = data_array2_non_cyclic[:, -1]'''


        # for non-pv vars: save all global/eu numpy arrays to npz file #

        if variable1['load_global_field']:
            numpyarrays_filename = 'deterministic_overview_maps_{}_{}_ndarrays_withinloop.npz'.format(model, var1var2)
            with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                if variable2['name'] == '':
                    np.savez(f, data_array1 = data_array1)
                else:
                    np.savez(f, data_array1 = data_array1, data_array2 = data_array2)

        for domain in domains:
            if model == 'icon-global-det' \
             and (variable1['name'] == 'prec_24h' or variable1['name'] == 'vmax_10m') \
             and (domain['name'] == 'europe' or domain['name'] == 'mediterranean') \
             and hour <= 120:
                continue

            print('domain:', domain['name'])

            # for pv vars: read and save all domain-cut numpy arrays to npz file #

            '''if not variable1['load_global_field']:
                if variable1['name'][:2] == 'pv':
                    iso_theta_value = float(variable1['name'][3:6])
                    print(iso_theta_value, 'K')
                    data_array1, ll_lat, ll_lon \
                     = calc_pv_on_theta(model, domain, variable1['grid'], run, hour, iso_theta_value)

                numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_outofloop.npz'.format(var1var2)
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                    np.savez(f, ll_lat = ll_lat, ll_lon = ll_lon)

                numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_withinloop.npz'.format(var1var2)
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                    if variable2['name'] == '':
                        np.savez(f, data_array1 = data_array1)
                    else:
                        print('variable2 not implemented yet for variable1==pv...')
                        exit()
                        #np.savez(f, data_array1 = data_array1, data_array2 = data_array2)'''


            # save all dictionaries and strings to a json file #

            json_filename = 'deterministic_overview_maps_{}_{}_dicts_strings.json'.format(model, var1var2)
            with open(path['base'] + path['temp'] + json_filename, 'w') as f:
                json.dump([path, domain, variable1, variable2, run, hour], f)


            # start new batch python script that will free its needed memory afterwards #

            scriptname = 'callfile_deterministic_overview_maps.py'
            command = 'python {}{}{} '.format(path['base'], path['callfiles'], scriptname)
            arguments = '{} {}'.format(var1var2, model)
            os.system(command + arguments)


    # copy all plots and .txt-file to imk-tss-web server #

    if transfer_to_webserver:
        subfolder_name = 'deterministic_overview_maps'
        path_webserver = '/home/iconeps/Data3/plots/icon/{}/{}'.format(subfolder_name, var1var2)
        os.system('scp ' + path['base'] + path['plots'] + '*.png '\
                  + 'iconeps@imk-tss-web.imk-tro.kit.edu:' + path_webserver)

        if variable1['name'] == 'wind_300hPa':
            path_webserver = '/home/iconeps/Data3/plots/icon/{}'.format(subfolder_name)
            path_latest_run_files = 'data/plots/{}/{}/'.format(ex_op_str, subfolder_name)
            os.system('scp ' + path['base'] + path_latest_run_files + filename_latest_run\
                      + ' iconeps@imk-tss-web.imk-tro.kit.edu:' + path_webserver)

    return

########################################################################
########################################################################
########################################################################

def double_contourplot(var1var2, model):

    recoverpath = dict(base = '/',
                       temp = 'data/additional_data/temp/{}/'.format(ex_op_str))

    # load all dictionaries and strings from json file #

    json_filename = 'deterministic_overview_maps_{}_{}_dicts_strings.json'.format(model, var1var2)
    with open(recoverpath['base'] + recoverpath['temp'] + json_filename, 'r') as f:
        path, domain, variable1, variable2, run, hour = json.load(f)


    # load numpy arrays #

    if variable1['load_global_field']:
        numpyarrays_filename = 'deterministic_overview_maps_{}_{}_ndarrays_outofloop.npz'.format(model, var1var2)

        if model == 'icon-eu-det':
            with open(path['base'] + path['temp'] + numpyarrays_filename, 'rb') as f:
                with np.load(f) as loadedfile:
                    clat = loadedfile['clat']
                    clon = loadedfile['clon']

        elif model == 'icon-global-det':
            if not variable1['load_global_field']:
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'rb') as f:
                    with np.load(f) as loadedfile:
                        ll_lat = loadedfile['ll_lat']
                        ll_lon = loadedfile['ll_lon']
            elif variable2['name'] == '':
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'rb') as f:
                    with np.load(f) as loadedfile:
                        clat = loadedfile['clat']
                        clon = loadedfile['clon']
                        vlat = loadedfile['vlat']
                        vlon = loadedfile['vlon']
            else:
                with open(path['base'] + path['temp'] + numpyarrays_filename, 'rb') as f:
                    with np.load(f) as loadedfile:
                        clat = loadedfile['clat']
                        clon = loadedfile['clon']
                        vlat = loadedfile['vlat']
                        vlon = loadedfile['vlon']
                        ll_lat = loadedfile['ll_lat']
                        ll_lon = loadedfile['ll_lon']

        numpyarrays_filename = 'deterministic_overview_maps_{}_{}_ndarrays_withinloop.npz'.format(model, var1var2)
        with open(recoverpath['base'] + recoverpath['temp'] + numpyarrays_filename, 'rb') as f:
            with np.load(f) as loadedfile:
                data_array1 = loadedfile['data_array1']
                if variable2['name'] != '':
                    data_array2 = loadedfile['data_array2']

        #print('loaded all vars')


        if domain['limits_type'] == 'radius':
            margin_deg = 20
        elif domain['limits_type'] == 'deltalatlon' or domain['limits_type'] == 'angle':
            margin_deg = 20

        if model == 'icon-eu-det':
            data_array1_cut, clat_cut, clon_cut, vlat_cut, vlon_cut = data_array1, clat, clon, None, None
        elif model == 'icon-global-det':
            data_array_dims = '2d'
            [data_array1_cut], clat_cut, clon_cut, vlat_cut, vlon_cut = \
              cut_by_domain(domain, variable1['grid'], data_array_dims,
                            [data_array1], clat, clon, vlat, vlon, margin_deg)
            if variable2['name'] != '':
                [data_array2_cut], ll_lat_cut, ll_lon_cut = \
                  cut_by_domain(domain, variable2['grid'], data_array_dims,
                                [data_array2], ll_lat, ll_lon, None, None, margin_deg)
                #data_array2_cut, ll_lat_cut, ll_lon_cut = data_array2, ll_lat, ll_lon
    else:
        # if load_global_field == False
        if variable1['name'][:2] == 'pv'\
         and variable1['name'][-1:] == 'K':
            iso_theta_value = float(variable1['name'][3:6])
            data_array1_cut, clat_cut, clon_cut \
             = calc_pv_on_theta(model, domain, variable1['grid'], run, hour, iso_theta_value)
        elif variable1['name'][:5] == 'theta'\
         and variable1['name'][-3:] == 'PVU':
            iso_pv_value = float(variable1['name'][6:9])
            data_array1_cut, clat_cut, clon_cut \
             = calc_theta_on_pv(model, domain, variable1['grid'], run, hour, iso_pv_value)


    # example plot_name: icon-global-det_2020070512_prec_rate_mslp_europe_000h.png
    plot_name = '{}_{:4d}{:02d}{:02d}{:02d}_{}_{}_{:03d}h'.format(
                 model, run['year'], run['month'], run['day'], run['hour'],
                 var1var2, domain['name'], hour)


    # plot basic map with borders #

    if variable1['name'] == 'prec_rate'\
     or variable1['name'] == 'prec_6h':
        filename_colorpalette = 'colorscale_prec_rate.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0, 0])     # color for under the lowest value, transparent
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255, 1])
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = ([0.1,0.2,0.3,0.5,1,2,3,5,10,20,30,50])
        lbStride_value = 1

    elif variable1['name'] == 't_850hPa':
        rgb_colors = []
        rgb_colors.append([0, 0, 0])        # placeholder for color for under the lowest value
        for i in range(10):
            rgb_colors.append(list(cmasher.take_cmap_colors('cmr.flamingo', 10, cmap_range=(0.45, 0.88))[i]))
        for i in range(2,12):
            rgb_colors.append(list(palettable.colorbrewer.sequential.Purples_9.get_mpl_colormap(N=14)(i)[:3]))
        rgb_colors.append(list(np.array([60, 53, 139])/255))
        rgb_colors.append(list(np.array([65, 69, 171])/255))
        rgb_colors.append(list(np.array([68, 86, 199])/255))
        for i in range(2,19):
            rgb_colors.append(list(palettable.colorbrewer.diverging.Spectral_10.get_mpl_colormap(N=19).reversed()(i)[:3]))
        for i in range(1,11):
            rgb_colors.append(list(palettable.cartocolors.sequential.Burg_7.get_mpl_colormap(N=11).reversed()(i)[:3]))
        rgb_colors[0] = rgb_colors[1]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        rgb_colors[31] = list(np.array([255, 255, 160])/255)
        rgb_colors[32] = list(np.array([247, 230, 128])/255)
        levels1 = np.arange(-25, 25+1, 1)
        lbStride_value = 5

    elif variable1['name'] == 'theta_e_850hPa':
        rgb_colors = []
        rgb_colors.append([0, 0, 0])        # placeholder for color for under the lowest value
        for i in range(5):
            rgb_colors.append(list(cmasher.take_cmap_colors('cmr.flamingo', 5, cmap_range=(0.65, 0.93))[i]))
        for i in range(4,13):
            rgb_colors.append(list(palettable.colorbrewer.sequential.Purples_9.get_mpl_colormap(N=16)(i)[:3]))
        for i in range(26):
            rgb_colors.append(list(palettable.colorbrewer.diverging.Spectral_10.get_mpl_colormap(N=26).reversed()(i)[:3]))
        for i in range(1,11):
            rgb_colors.append(list(palettable.cartocolors.sequential.Burg_7.get_mpl_colormap(N=11).reversed()(i)[:3]))
        for i in range(2,2+5):
            rgb_colors.append(list(palettable.scientific.sequential.Turku_10.get_mpl_colormap(N=12).reversed()(i)[:3]))
        rgb_colors[0] = rgb_colors[1]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        rgb_colors[27] = list(np.array([255, 255, 160])/255)
        rgb_colors[28] = list(np.array([247, 237, 128])/255)
        levels1 = np.arange(-20, 90+1, 2)
        lbStride_value = 5

    elif variable1['name'] == 'wind_300hPa':
        rgb_colors = []
        rgb_colors.append([0, 0, 0, 0])     # color for under the lowest value, transparent
        for i in range(1,8):
            rgb_colors.append(list(palettable.cmocean.sequential.Ice_10.get_mpl_colormap(N=10).reversed()(i)[:3]) + [1])
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = (list(range(120,330+1,30)))
        lbStride_value = 1

    elif variable1['name'] == 'cape_ml':
        rgb_colors = []
        rgb_colors.append([0, 0, 0, 0])     # color for under the lowest value, transparent
        for i in range(2,7):
            rgb_colors.append(list(palettable.scientific.sequential.Tokyo_7.get_mpl_colormap(N=7)(i)[:3]) + [1])
        for i in range(1,17,3):
            rgb_colors.append(list(palettable.cmocean.sequential.Thermal_20.get_mpl_colormap(N=22).reversed()(i)[:3]) + [1])
        for i in range(9,18,4):
            rgb_colors.append(list(palettable.cmocean.sequential.Ice_20.get_mpl_colormap(N=20)(i)[:3]) + [1])
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        rgb_colors[1] = list(np.array([138, 98, 110])/255) + [1]
        rgb_colors[10] = list(np.array([142, 69, 139])/255) + [1]
        #levels1 = ([0,100,200,350,530,750,1000,1300,1630,2000,2400,2850,3330,3850,4400,5000])  # follows (wmax)**2
        levels1 = ([100,200,350,500,750,1000,1300,1600,2000,2400,2800,3300,3800,4400,5000])   # rounded to be pretty
        lbStride_value = 1

        #rgb_arr = np.array(rgb_colors)
        #np.savetxt("colorpalette_marco_cape_ml.txt", np.around(rgb_arr[3:-1]*255,0), fmt='%2d', delimiter = ",")

    elif variable1['name'] == 'synth_bt_ir10.8':
        filename_colorpalette = 'rainbowIRsummer.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append(list(np.array([118, 39, 118])/255))
        for i, line in enumerate(lines):
            if i % 14 == 0 and i > 70:
                rgb_colors.append([float(line[:10]), float(line[11:21]), float(line[22:32])])
        rgb_colors.append(list(np.array([35, 244, 255])/255))
        num_bw_colors = 30
        for i in range(num_bw_colors+1):
            rgb_colors.append([1-i/num_bw_colors, 1-i/num_bw_colors, 1-i/num_bw_colors])
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = (list(range(-90,-20,1)) + list(range(-20,40+1,2)))
        lbStride_value = 10

    elif variable1['name'] == 'prec_24h'\
     or variable1['name'] == 'prec_sum':
        filename_colorpalette = 'colorscale_prec24h.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0, 0])     # color for under the lowest value, transparent
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255, 1])
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value

        levels1 = ([1,10,20,40,60,80,100,120,140,160,180,200,250,300,400])
        lbStride_value = 1

    elif variable1['name'] == 'vmax_10m':
        filename_colorpalette = 'colorscale_vmax.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0])        # placeholder for color for under the lowest value
        for i in range(0,11):               # load colors from palettable
            rgb_colors.append(list(cmasher.take_cmap_colors('cmr.chroma', 11, cmap_range=(0.20, 0.95))[::-1][i]))
        for i in range(0,3):                # load colors from palettable
            rgb_colors.append(list(cmasher.take_cmap_colors('cmr.freeze', 3, cmap_range=(0.40, 0.90))[i]))
        for i in range(0,2):                # load colors from palettable
            rgb_colors.append(list(cmasher.take_cmap_colors('cmr.flamingo', 2, cmap_range=(0.55, 0.80))[::-1][i]))
        rgb_colors[0] = rgb_colors[1]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = ([0,6,12,20,29,39,50,62,75,89,103,118,154,178,209,251,300])
        lbStride_value = 1

    elif variable1['name'] == 'shear_200-850hPa':
        filename_colorpalette = 'colorscale_shear_200-850hPa.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([1, 1, 1])
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors.append([0, 0, 1])
        levels1 = (list(np.arange(0,30,2.5)) + list(range(30,50+1,5)) + [99])
        lbStride_value = 1

    elif variable1['name'][:2] == 'pv'\
     and variable1['name'][-1:] == 'K':
        filename_colorpalette = 'colorscale_ipv_eth.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0])        # placeholder for color for under the lowest value
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors[0] = rgb_colors[1]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = ([-1,-0.5,0.2,0.7,1,1.5,2,3,4,5,6,7,8,9,10])
        lbStride_value = 1

    elif variable1['name'][:5] == 'theta'\
     and variable1['name'][-3:] == 'PVU':
        rgb_colors = []
        rgb_colors.append([0, 0, 0])        # placeholder for color for under the lowest value
        for i in range(30):
            rgb_colors.append(list(palettable.colorbrewer.diverging.RdYlBu_10.get_mpl_colormap(N=30)(i)[:3]))
        rgb_colors[0] = rgb_colors[1]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        levels1 = np.arange(270, 420+1, 5)
        #levels1 = np.arange(300, 360+1, 20)
        lbStride_value = 2


    mpres   = Ngl.Resources()
    mpres.mpProjection = domain['projection']

    if domain['limits_type'] == 'radius':
        mpres.mpLimitMode  = 'LatLon'
        mpres.mpCenterLonF = domain['centerlon']
        mpres.mpCenterLatF = domain['centerlat']
        cutout_plot = dict(
                            lat_min = float(np.where(domain['centerlat'] - domain['radius'] / 111.2 < -90,
                                               -90, domain['centerlat'] - domain['radius'] / 111.2)),
                            lat_max = float(np.where(domain['centerlat'] + domain['radius'] / 111.2 > 90,
                                               90, domain['centerlat'] + domain['radius'] / 111.2)),
                           )
        cutout_plot['lon_min'] = float(np.where(cutout_plot['lat_min'] <= -90 or cutout_plot['lat_max'] >= 90,
                                       0,
                                       domain['centerlon'] - domain['radius'] \
                                        / (111.2 * np.cos(domain['centerlat']*np.pi/180))))
        cutout_plot['lon_max'] = float(np.where(cutout_plot['lat_min'] <= -90 or cutout_plot['lat_max'] >= 90,
                                       360,
                                       domain['centerlon'] + domain['radius'] \
                                        / (111.2 * np.cos(domain['centerlat']*np.pi/180))))
        mpres.mpMinLonF     = cutout_plot['lon_min']
        mpres.mpMaxLonF     = cutout_plot['lon_max']
        mpres.mpMinLatF     = cutout_plot['lat_min']
        mpres.mpMaxLatF     = cutout_plot['lat_max']

    elif domain['limits_type'] == 'deltalatlon':
        mpres.mpLimitMode  = 'LatLon'
        mpres.mpCenterLonF = 0
        mpres.mpCenterLatF = 0
        mpres.mpMinLonF    = domain['centerlon'] - domain['deltalon_deg']
        mpres.mpMaxLonF    = domain['centerlon'] + domain['deltalon_deg']
        mpres.mpMinLatF    = domain['centerlat'] - domain['deltalat_deg']
        mpres.mpMaxLatF    = domain['centerlat'] + domain['deltalat_deg']

    elif domain['limits_type'] == 'angle':
        mpres.mpLimitMode    = 'Angles'
        mpres.mpCenterLonF   = domain['centerlon']
        mpres.mpCenterLatF   = domain['centerlat']
        mpres.mpLeftAngleF   = domain['angle']
        mpres.mpRightAngleF  = domain['angle']
        mpres.mpTopAngleF    = domain['angle']
        mpres.mpBottomAngleF = domain['angle']

    mpres.nglMaximize   = False
    mpres.vpXF          = 0.001
    mpres.vpYF          = 1.00
    mpres.vpWidthF      = 0.88
    mpres.vpHeightF     = 1.00

    mpres.mpLandFillColor        = list(np.array([255, 225, 171])/255)
    mpres.mpOceanFillColor       = [1, 1, 1]
    mpres.mpInlandWaterFillColor = [1, 1, 1]

    mpres.mpFillOn                     = True
    mpres.mpGridAndLimbOn              = False
    mpres.mpGreatCircleLinesOn         = False

    mpres.mpDataBaseVersion             = 'MediumRes'
    mpres.mpDataSetName                 = 'Earth..4'
    mpres.mpOutlineBoundarySets         = 'national'
    mpres.mpGeophysicalLineColor        = 'black'
    mpres.mpNationalLineColor           = 'black'
    mpres.mpGeophysicalLineThicknessF   = 1.5 * domain['plot_width'] / 1000
    mpres.mpNationalLineThicknessF      = 1.5 * domain['plot_width'] / 1000

    mpres.mpPerimOn                     = True
    mpres.mpPerimLineColor              = 'black'
    mpres.mpPerimLineThicknessF         = 8.0 * domain['plot_width'] / 1000
    mpres.tmXBOn = False
    mpres.tmXTOn = False
    mpres.tmYLOn = False
    mpres.tmYROn = False

    mpres.nglDraw        =  False              #-- don't draw plot
    mpres.nglFrame       =  False              #-- don't advance frame


    # settings for variable1 / shading #

    v1res = Ngl.Resources()
    v1res.nglFrame = False
    v1res.nglDraw  = False
    v1res.sfDataArray       = data_array1_cut
    v1res.sfXArray          = clon_cut
    v1res.sfYArray          = clat_cut
    v1res.sfMissingValueV   = 9999
    #v1res.cnFillBackgroundColor = 'transparent'
    v1res.cnMissingValFillColor = 'Gray80'
    v1res.cnFillColors          = np.array(rgb_colors)

    v1res.cnLinesOn = False
    v1res.cnFillOn  = True
    v1res.cnLineLabelsOn = False
    if not variable1['load_global_field']:
        v1res.cnFillMode = 'RasterFill'
    elif model == 'icon-eu-det':
        v1res.cnFillMode = 'RasterFill'
    elif model == 'icon-global-det':
        v1res.cnFillMode = 'CellFill'
        v1res.sfXCellBounds = vlon_cut
        v1res.sfYCellBounds = vlat_cut
    #v1res.cnFillOpacityF        = 0.5
    #v1res.cnFillDrawOrder       = 'Predraw'
    v1res.cnLevelSelectionMode = 'ExplicitLevels' 
    v1res.cnLevels = levels1

    v1res.lbLabelBarOn          = True
    v1res.lbAutoManage          = False
    v1res.lbOrientation         = 'vertical'
    v1res.lbLabelOffsetF        = 0.04      # minor axis fraction: the distance between colorbar and numbers
    v1res.lbBoxMinorExtentF     = 0.20      # minor axis fraction: width of the color boxes when labelbar down
    v1res.lbTopMarginF          = 0.2       # make a little more space at top for the unit label
    v1res.lbRightMarginF        = 0.0
    v1res.lbBottomMarginF       = 0.05
    v1res.lbLeftMarginF         = -0.35

    v1res.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
    #if variable1['name'] == 'prec_rate' :
    #    v1res.cnLabelBarEndStyle    = 'IncludeOuterBoxes'
    #v1res.cnExplicitLabelBarLabelsOn = True
    #v1res.pmLabelBarDisplayMode =  'Always'
    v1res.pmLabelBarWidthF      = 0.10
    #v1res.lbLabelStrings        = label_str_list
    v1res.lbLabelFontHeightF    = 0.010
    #v1res.lbBoxCount            = 40
    v1res.lbBoxSeparatorLinesOn = False
    v1res.lbBoxLineThicknessF   = 4
    #v1res.lbBoxEndCapStyle     = 'TriangleBothEnds'
    v1res.lbLabelAlignment      = 'ExternalEdges'
    v1res.lbLabelStride         = lbStride_value


    # settings for variable2 / contourlines #

    if variable2['name'] != '':
        v2res = Ngl.Resources()
        v2res.nglFrame = False
        v2res.nglDraw  = False
        v2res.sfDataArray       = data_array2_cut
        v2res.sfXArray          = ll_lon_cut #ll_lon_cyclic
        v2res.sfYArray          = ll_lat_cut
        v2res.sfMissingValueV   = 9999  
        #v2res.trGridType        = 'TriangularMesh'
        v2res.cnFillOn          = False
        v2res.cnLinesOn         = True
        v2res.cnLineLabelsOn    = True
        v2res.cnLineLabelPlacementMode = 'Constant'
        v2res.cnLabelDrawOrder = 'PostDraw'
        v2res.cnInfoLabelOn = False
        v2res.cnSmoothingOn = False
        v2res.cnLevelSelectionMode = 'ExplicitLevels'
        v2res.cnLineThicknessF = 3.0 * domain['plot_width'] / 1000
        v2res.cnLineLabelFontHeightF = 0.008
        v2res.cnLineDashSegLenF = 0.25

        v3res = Ngl.Resources()
        v3res.nglFrame = False
        v3res.nglDraw  = False
        v3res.sfDataArray       = data_array2_cut
        v3res.sfXArray          = ll_lon_cut #ll_lon_cyclic
        v3res.sfYArray          = ll_lat_cut
        v3res.sfMissingValueV   = 9999  
        #v3res.trGridType        = 'TriangularMesh'
        v3res.cnFillOn          = False
        v3res.cnLinesOn         = True
        v3res.cnLineLabelsOn    = True
        v3res.cnLineLabelPlacementMode = 'Constant'
        v3res.cnLabelDrawOrder = 'PostDraw'
        v3res.cnInfoLabelOn = False
        v3res.cnSmoothingOn = False
        v3res.cnLevelSelectionMode = 'ExplicitLevels'
        v3res.cnLineThicknessF = 5.0 * domain['plot_width'] / 1000
        v3res.cnLineLabelFontHeightF = 0.008
        v3res.cnLineDashSegLenF = 0.25

        if variable2['name'] == 'mslp':
            v2res.cnLevels = np.arange(900, 1100, 2)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(900, 1100, 10)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'gph_300hPa':
            v2res.cnLevels = np.arange(780, 1000, 6)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(780, 1000, 24)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'gph_850hPa':
            v2res.cnLevels = np.arange(100, 180, 2)
            v2res.cnLineLabelInterval = 2
            v3res.cnLevels = np.arange(100, 180, 10)
            v3res.cnLineLabelInterval = 2

        elif variable2['name'] == 'gph_700hPa':
            v2res.cnLevels = np.arange(472, 633, 2)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(472, 633, 8)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'gph_500hPa':
            v2res.cnLevels = np.arange(472, 633, 4)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(472, 633, 16)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'shear_0-6km':
            v4res = Ngl.Resources()
            v4res.nglFrame = False
            v4res.nglDraw  = False
            v4res.sfDataArray       = data_array2_cut
            v4res.sfXArray          = ll_lon_cut #ll_lon_cyclic
            v4res.sfYArray          = ll_lat_cut
            v4res.sfMissingValueV   = 9999  
            #v4res.trGridType        = 'TriangularMesh'
            v4res.cnFillOn          = False
            v4res.cnLinesOn         = True
            v4res.cnLineLabelsOn    = True
            v4res.cnLineLabelPlacementMode = 'Constant'
            v4res.cnLabelDrawOrder = 'PostDraw'
            v4res.cnInfoLabelOn = False
            v4res.cnSmoothingOn = False
            v4res.cnLevelSelectionMode = 'ExplicitLevels'
            v4res.cnLineLabelFontHeightF = 0.008
            v4res.cnLineDashSegLenF = 0.25
            v5res = Ngl.Resources()
            v5res.nglFrame = False
            v5res.nglDraw  = False
            v5res.sfDataArray       = data_array2_cut
            v5res.sfXArray          = ll_lon_cut #ll_lon_cyclic
            v5res.sfYArray          = ll_lat_cut
            v5res.sfMissingValueV   = 9999  
            #54res.trGridType        = 'TriangularMesh'
            v5res.cnFillOn          = False
            v5res.cnLinesOn         = True
            v5res.cnLineLabelsOn    = True
            v5res.cnLineLabelPlacementMode = 'Constant'
            v5res.cnLabelDrawOrder = 'PostDraw'
            v5res.cnInfoLabelOn = False
            v5res.cnSmoothingOn = False
            v5res.cnLevelSelectionMode = 'ExplicitLevels'
            v5res.cnLineLabelFontHeightF = 0.008
            v5res.cnLineDashSegLenF = 0.25

            v2res.cnLevels = [10]
            v2res.cnLineLabelInterval = 1
            v2res.cnLineDashSegLenF = 0.15
            v2res.cnLineThicknessF = 2.4 * domain['plot_width'] / 1000
            v3res.cnLevels = [15]
            v3res.cnLineLabelInterval = 1
            v3res.cnLineThicknessF = 4.5 * domain['plot_width'] / 1000
            v3res.cnLineDashSegLenF = 0.15
            v3res.cnLineThicknessF = 3.6 * domain['plot_width'] / 1000
            v4res.cnLevels = [20]
            v4res.cnLineLabelInterval = 1
            v4res.cnLineDashSegLenF = 0.15
            v4res.cnLineThicknessF = 5.4 * domain['plot_width'] / 1000
            v5res.cnLevels = [25]
            v5res.cnLineLabelInterval = 1
            v5res.cnLineDashSegLenF = 0.15
            v5res.cnLineThicknessF = 8.0 * domain['plot_width'] / 1000


    ''' these are settings for some experiment with lows/highs min/max pressure labels:
    v2res.cnLineLabelsOn = True
    v2res.cnLabelDrawOrder = 'PostDraw'
    v2res.cnLineLabelPerimOn = False
    v2res.cnLineLabelBackgroundColor = 'transparent'
    v2res.cnLineLabelPlacementMode = 'Computed'
    v2res.cnLineLabelDensityF = 0.2
    v2res.cnLineLabelFontHeightF = 0.010
    #v2res.cnLineDashSegLenF = 0.25

    v2res.cnLowLabelsOn = True
    #v2res.cnLowLabelPerimOn = False
    v2res.cnLowLabelString = '$ZDV$hPa'
    #v2res.cnLowLabelFontColor = 'black'
    v2res.cnLowLabelBackgroundColor = 'white'''


    # settings for unit text #

    if variable1['name'][:2] == 'pv'\
    and (domain['name'] == 'southern_south_america'\
          or domain['name'] == 'south_pole'):
        text_str = variable1['unit'] + ' * -1'
    else:
        text_str = variable1['unit']
    text_res_1 = Ngl.Resources()
    text_res_1.txFontColor      = 'black'
    text_res_1.txFontHeightF = 0.013
    text_x = 0.965
    text_y = domain['text_y']


    # settings for description label #

    res_text_descr = Ngl.Resources()
    res_text_descr.txJust           = 'CenterLeft'
    res_text_descr.txFontHeightF    = 0.01
    res_text_descr.txFontColor      = 'black'
    res_text_descr.txBackgroundFillColor = 'white'
    res_text_descr.txPerimOn = True
    res_text_descr.txPerimColor = 'black'

    text_descr_str1 = 'ICON-Global-Deterministic from {:02d}.{:02d}.{:4d} {:02d}UTC +{:d}h, '.format(
                       run['day'], run['month'], run['year'], run['hour'], hour)
    if variable2['name'] == '':
        text_descr_str2 = 'Contours: {} in {}'.format(
                           variable1['name'], variable1['unit'])
    else:
        text_descr_str2 = 'Contours: {} in {}, Lines: {} in {}'.format(
                           variable1['name'], variable1['unit'], variable2['name'], variable2['unit'])
    text_descr_x = 0.02
    text_descr_y = domain['text_y'] - 0.005


    # override settings for specific cases #

    if domain['name'] == 'mediterranean':
        mpres.mpPerimLineThicknessF /= 1.5
        mpres.mpGeophysicalLineThicknessF /= 1.5
        mpres.mpNationalLineThicknessF /= 1.5
        mpres.vpWidthF              = 0.94
        v1res.lbLabelFontHeightF    = 0.005
        v1res.pmLabelBarWidthF      = 0.04
        v1res.lbLeftMarginF         = -0.50
        if variable2['name'] != '':
            v2res.cnLineThicknessF /= 1.5
            v2res.cnLineLabelFontHeightF /= 1.5
            v3res.cnLineThicknessF /= 1.5
            v3res.cnLineLabelFontHeightF /= 1.5
            v2res.cnLineDashSegLenF = 0.12
            v3res.cnLineDashSegLenF = 0.12
        text_res_1.txFontHeightF = 0.007
        text_x = 0.980
        res_text_descr.txFontHeightF = 0.007
        text_descr_x = 0.005

    elif domain['name'] == 'north_pole' or domain['name'] == 'south_pole':
        if variable2['name'] == 'mslp':
            v2res.cnLevels = np.arange(900, 1100, 4)
            v3res.cnLevels = np.arange(900, 1100, 20)
        elif variable2['name'] == 'gph_300hPa':
            v2res.cnLevels = np.arange(780, 1000, 12)
            v3res.cnLevels = np.arange(780, 1000, 48)
        elif variable2['name'] == 'gph_500hPa':
            v2res.cnLevels = np.arange(472, 633, 8)
            v3res.cnLevels = np.arange(472, 633, 32)
        elif variable2['name'] == 'gph_700hPa':
            v2res.cnLevels = np.arange(472, 633, 8)
            v3res.cnLevels = np.arange(472, 633, 32)
        elif variable2['name'] == 'gph_850hPa':
            v2res.cnLevels = np.arange(102, 180, 4)
            v3res.cnLevels = np.arange(102, 180, 20)
    elif domain['name'] == 'Argentina_Central' or domain['name'] == 'Argentina_Central_cerca':
        if variable2['name'] == 'gph_850hPa':
            v2res.cnLevels = np.arange(100, 180, 1)
            v3res.cnLevels = np.arange(100, 180, 5)
            v2res.cnLineLabelInterval = 1


    wks_res = Ngl.Resources()
    wks_res.wkWidth  = domain['plot_width']
    wks_res.wkHeight = domain['plot_width']     # the whitespace above and below the plot will be cut afterwards
    #wks_res.wkColorMap = np.array(rgb_colors)
    wks_type = 'png'
    wks = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)

    basic_map = Ngl.map(wks, mpres)


    # plot subnational borders for some domains #

    shp_filenames = []
    if domain['name'] == 'southern_south_america'\
     or domain['name'] == 'arg_uru_braz'\
     or domain['name'] == 'argentina_central'\
     or domain['name'] == 'argentina_central_cerca':
        shp_filenames.append(['gadm36_ARG_1.shp', 0.3])
        shp_filenames.append(['gadm36_BRA_1.shp', 0.3])
        shp_filenames.append(['gadm36_CHL_1.shp', 0.3])
    elif domain['name'] == 'north_america':
        shp_filenames.append(['gadm36_USA_1.shp', 0.3])
        shp_filenames.append(['gadm36_CAN_1.shp', 0.3])
        shp_filenames.append(['gadm36_MEX_1.shp', 0.3])
    elif domain['name'] == 'eastern_asia':
        shp_filenames.append(['gadm36_CHN_1.shp', 0.3])

    for shp_filename, lineThickness in shp_filenames:
        shpf = Nio.open_file(path['base'] + path['shapefiles'] + shp_filename, 'r')
        shpf_lon = np.ravel(shpf.variables['x'][:])
        shpf_lat = np.ravel(shpf.variables['y'][:])
        shpf_segments = shpf.variables['segments'][:, 0]

        plres = Ngl.Resources()
        plres.gsLineColor = 'black'
        plres.gsLineThicknessF = lineThickness
        plres.gsSegments = shpf_segments
        Ngl.add_polyline(wks, basic_map, shpf_lon, shpf_lat, plres)


    # put everything together # 

    contourshades_plot = Ngl.contour(wks, data_array1_cut, v1res)
    if variable2['name'] != '':
        contourlines_minor_plot = Ngl.contour(wks, data_array2_cut, v2res)
        contourlines_major_plot = Ngl.contour(wks, data_array2_cut, v3res)
        if variable2['name'] == 'shear_0-6km':
            contourlines_major2_plot = Ngl.contour(wks, data_array2_cut, v4res)
            contourlines_major3_plot = Ngl.contour(wks, data_array2_cut, v5res)

    Ngl.overlay(basic_map, contourshades_plot)
    if variable2['name'] != '':
        Ngl.overlay(basic_map, contourlines_minor_plot)
        Ngl.overlay(basic_map, contourlines_major_plot)
        if variable2['name'] == 'shear_0-6km':
            Ngl.overlay(basic_map, contourlines_major2_plot)
            Ngl.overlay(basic_map, contourlines_major3_plot)

    Ngl.draw(basic_map)
    Ngl.text_ndc(wks, text_str, text_x, text_y, text_res_1)
    #Ngl.text_ndc(wks, text_descr_str1 + text_descr_str2, text_descr_x, text_descr_y, res_text_descr)

    Ngl.frame(wks)
    Ngl.delete_wks(wks)


    # cut top and bottom whitespace of plot #

    im = Image.open(path['base'] + path['plots'] + plot_name + '.png')
    image_array = np.asarray(im.convert('L'))
    image_array = np.where(image_array < 255, 1, 0)
    image_filter = np.amax(image_array, axis=1)
    vmargins = [np.nonzero(image_filter)[0][0], np.nonzero(image_filter[::-1])[0][0]]
    #print(vmargins)
    #print(im.size)

    im_cropped = Image.new('RGB',(im.size[0], im.size[1] - vmargins[0] - vmargins[1]), (255,255,255))
    im_cropped.paste(im.crop((0, vmargins[0], im.size[0], im.size[1] - vmargins[1])), (0, 0))
    #print(im_cropped.size)
    im.close()
    im_cropped.save(path['base'] + path['plots'] + plot_name + '.png', 'png')
    im_cropped.close()

    return
