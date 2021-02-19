
import os
import datetime
import json

import numpy as np
import Ngl
import Nio
import palettable
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
        hours = list(range(0, 180+1, 6))
        #hours = list(range(1, 48+1, 1))
        #hours = [120]
    elif model == 'icon-eu-det':
        hours = list(range(0, 120+1, 6))
        #hours = list(range(0, 72+1, 1))
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

    numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_outofloop.npz'.format(var1var2)

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

        if variable1['name'] == 'prec_24h_eu' or variable1['name'] == 'prec_24h_global':
            varname = 'prec_24h'
        else:
            varname = variable1['name']

        if variable1['load_global_field']:
            data_array1 = read_forecast_data(model, variable1['grid'], run, varname, fcst_hour=hour)

            if variable2['name'] != '':
                data_array2_non_cyclic \
                 = read_forecast_data(model, variable2['grid'], run, variable2['name'], fcst_hour=hour)

                if variable2['name'] == 'mslp':
                    lines_max_oro = 600
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
                    data_array2[:, 1799:] = data_array2_non_cyclic[:, :1801]  # flip around the data in lon direction to match
                    data_array2[:, :1799] = data_array2_non_cyclic[:, 1801:]  # positions in the ll_lon array
                elif variable2['grid'] == 'latlon_0.25':
                    data_array2[:, 719:] = data_array2_non_cyclic[:, :721]  # flip around the data in lon direction to match
                    data_array2[:, :719] = data_array2_non_cyclic[:, 721:]  # positions in the ll_lon array

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
            numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_withinloop.npz'.format(var1var2)
            with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
                if variable2['name'] == '':
                    np.savez(f, data_array1 = data_array1)
                else:
                    np.savez(f, data_array1 = data_array1, data_array2 = data_array2)


        for domain in domains:
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

            json_filename = 'deterministic_overview_maps_{}_dicts_strings.json'.format(var1var2)
            with open(path['base'] + path['temp'] + json_filename, 'w') as f:
                json.dump([path, domain, variable1, variable2, model, run, hour], f)


            # start new batch python script that will free its needed memory afterwards #

            scriptname = 'callfile_deterministic_overview_maps.py'
            command = 'python {}{}{} '.format(path['base'], path['callfiles'], scriptname)
            arguments = var1var2
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

def double_contourplot(var1var2):

    recoverpath = dict(base = '/',
                       temp = 'data/additional_data/temp/{}/'.format(ex_op_str))

    # load all dictionaries and strings from json file #

    json_filename = 'deterministic_overview_maps_{}_dicts_strings.json'.format(var1var2)
    with open(recoverpath['base'] + recoverpath['temp'] + json_filename, 'r') as f:
        path, domain, variable1, variable2, model, run, hour = json.load(f)


    # load numpy arrays #

    if variable1['load_global_field']:
        numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_outofloop.npz'.format(var1var2)

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

        numpyarrays_filename = 'deterministic_overview_maps_{}_ndarrays_withinloop.npz'.format(var1var2)
        with open(recoverpath['base'] + recoverpath['temp'] + numpyarrays_filename, 'rb') as f:
            with np.load(f) as loadedfile:
                data_array1 = loadedfile['data_array1']
                if variable2['name'] != '':
                    data_array2 = loadedfile['data_array2']

        print('loaded all vars')


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

    wks_res = Ngl.Resources()
    wks_res.wkWidth  = domain['plot_width']
    wks_res.wkHeight = domain['plot_width']     # the whitespace above and below the plot will be cut afterwards

    if variable1['name'] == 'prec_rate'\
     or variable1['name'] == 'prec_6h':
        filename_colorpalette = 'colorscale_prec_rate.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # placeholder for color for under the lowest value
        rgb_colors.append([1, 1, 1])    # first color
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors[2] = rgb_colors[3]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = ([0,0.1,0.2,0.3,0.5,1,2,3,5,10,20,30,50])
        lbStride_value = 1

    elif variable1['name'] == 't_850hPa':
        wks_res.wkColorMap = 'BkBlAqGrYeOrReViWh200'
        levels1 = np.arange(-40, 40, 4)
        lbStride_value = 1
    elif variable1['name'] == 'theta_e_850hPa':
        wks_res.wkColorMap = 'BkBlAqGrYeOrReViWh200'
        levels1 = np.arange(-20, 80+1, 5)
        lbStride_value = 1
    elif variable1['name'] == 'wind_300hPa':
        wks_res.wkColorMap = 'wh-bl-gr-ye-re'
        levels1 = np.arange(150,300,25)
        lbStride_value = 1
    elif variable1['name'] == 'cape_ml':
        rgb_colors = []
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # placeholder for color for under the lowest value
        for i in range(9):              # load colors from palettable
            rgb_colors.append(list(palettable.cmocean.sequential.Thermal_9.get_mpl_colormap(N=9)(i)[:3]))
        rgb_colors[2] = rgb_colors[3]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = np.arange(0, 3000+1, 100)
        levels1 = ([0,10,20,50,100,200,500,1000,2000,5000])
        lbStride_value = 1

    elif variable1['name'] == 'synth_bt_ir10.8':
        filename_colorpalette = 'rainbowIRsummer.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        for i, line in enumerate(lines):
            if i % 14 == 0 and i > 70:
                rgb_colors.append([float(line[:10]), float(line[11:21]), float(line[22:32])])
        num_bw_colors = 30
        for i in range(num_bw_colors+1):
            rgb_colors.append([1-i/num_bw_colors, 1-i/num_bw_colors, 1-i/num_bw_colors])
        rgb_colors.append([0, 0, 0])
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = (list(range(-90,-20,1)) + list(range(-20,40+1,2)))
        lbStride_value = 10

    elif variable1['name'] == 'prec_24h_eu'\
     or variable1['name'] == 'prec_24h_global'\
     or variable1['name'] == 'prec_sum':
        filename_colorpalette = 'colorscale_prec24h.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors.append([1, 1, 1])
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = ([0,1,2,5,10,15,20,30,40,50,60,80,100,120,150,200,250,300,350,400,450,500,1000])
        lbStride_value = 1

    elif variable1['name'] == 'vmax_10m':
        filename_colorpalette = 'colorscale_vmax.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors.append([0, 0, 1])
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = (list(range(0,90+1,5)) + list(range(100,160+1,10)) + list(range(180,260+1,20)))
        lbStride_value = 1

    elif variable1['name'] == 'shear_200-850hPa':
        filename_colorpalette = 'colorscale_shear_200-850hPa.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        rgb_colors.append([1, 1, 1])
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors.append([0, 0, 1])
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = (list(np.arange(0,30,2.5)) + list(range(30,50+1,5)) + [99])
        lbStride_value = 1

    elif variable1['name'][:2] == 'pv'\
     and variable1['name'][-1:] == 'K':
        filename_colorpalette = 'colorscale_ipv_eth.txt'
        with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
            lines = f.readlines()
        rgb_colors = []
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # placeholder for color for under the lowest value
        for i, line in enumerate(lines):
            rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
        rgb_colors[2] = rgb_colors[3]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = ([-1,-0.5,0.2,0.7,1,1.5,2,3,4,5,6,7,8,9,10])
        lbStride_value = 1

    elif variable1['name'][:5] == 'theta'\
     and variable1['name'][-3:] == 'PVU':
        rgb_colors = []
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # color not seen, needed for pyngl
        rgb_colors.append([0, 0, 0])    # placeholder for color for under the lowest value
        for i in range(30):              # load colors from palettable
            rgb_colors.append(list(palettable.colorbrewer.diverging.RdYlBu_10.get_mpl_colormap(N=30)(i)[:3]))
        rgb_colors[2] = rgb_colors[3]       # copy lowest loaded color to color for under the lowest value
        rgb_colors.append(rgb_colors[-1])   # add highest loaded color to color for over the highest value
        wks_res.wkColorMap = np.array(rgb_colors)
        levels1 = np.arange(270, 420+1, 5)
        #levels1 = np.arange(300, 360+1, 20)
        lbStride_value = 2


    wks_type = 'png'
    wks = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)


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
    mpres.mpMonoFillColor = 'True'
    if variable1['name'] == 't_850hPa':
        mpres.mpFillColors = ['transparent', 'transparent', 'transparent', 'transparent']
    elif variable1['name'] == 'theta_e_850hPa':
        mpres.mpFillColors = ['transparent', 'white', 'navajowhite1', 'transparent']
    elif variable1['name'] == 'wind_300hPa':
        mpres.mpFillColors = ['transparent', 'white', 'navajowhite1', 'transparent']
    else:
        mpres.mpFillColors = ['transparent', 'transparent', 'transparent', 'transparent']

    mpres.mpFillOn = True
    mpres.mpGridAndLimbOn = False
    mpres.mpGreatCircleLinesOn = False

    mpres.mpDataBaseVersion         = 'MediumRes'
    mpres.mpDataSetName             = 'Earth..4'
    mpres.mpOutlineBoundarySets     = 'national'
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
    v1res.cnFillBackgroundColor = 'white'
    v1res.cnMissingValFillColor = 'white'

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


    if variable1['name'] == 't_850hPa':
        v1res.lbBottomMarginF   = -0.07
    elif variable1['name'] == 'theta_e_850hPa':
        v1res.lbBottomMarginF   = -0.07
    elif variable1['name'] == 'wind_300hPa':
        v1res.lbBottomMarginF   = -0.35
    elif variable1['name'] == 'synth_bt_ir10.8'\
     or variable1['name'] == 'cape_ml'\
     or variable1['name'] == 'prec_rate'\
     or variable1['name'] == 'prec_24h_eu'\
     or variable1['name'] == 'prec_24h_global'\
     or variable1['name'] == 'prec_sum'\
     or variable1['name'] == 'vmax_10m'\
     or variable1['name'] == 'shear_200-850hPa'\
     or variable1['name'][:2] == 'pv':
        v1res.lbBottomMarginF   = 0.05

    v1res.lbLeftMarginF         = -0.35

    if domain['name'] == 'mediterranean':
        # very wide domain
        mpres.vpWidthF      = 0.94
        v1res.lbBottomMarginF += 0.15
        #v1res.lbBoxMinorExtentF = 0.13
        if variable1['name'] == 'prec_rate':
            v1res.lbLabelFontHeightF = 0.007
        elif variable1['name'] == 't_850hPa':
            v1res.lbLabelFontHeightF = 0.005
        elif variable1['name'] == 'theta_e_850hPa':
            v1res.lbLabelFontHeightF = 0.005
        elif variable1['name'] == 'wind_300hPa'\
         or variable1['name'] == 'shear_200-850hPa':
            v1res.lbLabelFontHeightF = 0.005
        elif variable1['name'] == 'synth_bt_ir10.8'\
         or variable1['name'] == 'prec_24h_eu'\
         or variable1['name'] == 'prec_sum'\
         or variable1['name'] == 'cape_ml'\
         or variable1['name'] == 'vmax_10m':
            v1res.lbLabelFontHeightF = 0.005
            v1res.lbTopMarginF = 0.35
        v1res.lbBottomMarginF   = 0.05
        v1res.pmLabelBarWidthF = 0.04
        v1res.lbLeftMarginF = -0.5


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
            v2res.cnLineLabelInterval = 2
            v3res.cnLevels = np.arange(900, 1100, 10)
            v3res.cnLineLabelInterval = 2

        elif variable2['name'] == 'gph_500hPa':
            v2res.cnLevels = np.arange(472, 633, 4)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(472, 633, 16)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'gph_300hPa':
            v2res.cnLevels = np.arange(780, 1000, 6)
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = np.arange(780, 1000, 24)
            v3res.cnLineLabelInterval = 1

        elif variable2['name'] == 'shear_0-6km':
            v2res.cnLevels = [15, 25, 35]
            v2res.cnLineLabelInterval = 1
            v3res.cnLevels = [10, 20, 30]
            v3res.cnLineLabelInterval = 1


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


    # override settings for specific cases #

    if domain['name'] == 'mediterranean':
        text_res_1.txFontHeightF = 0.010
        text_x = 0.980
        mpres.mpGeophysicalLineThicknessF = 1.0 * domain['plot_width'] / 1000
        mpres.mpNationalLineThicknessF    = 1.0 * domain['plot_width'] / 1000

    elif domain['name'] == 'north_pole' or domain['name'] == 'south_pole':
        if variable2['name'] == 'mslp':
            v2res.cnLevels = np.arange(900, 1100, 4)
            v3res.cnLevels = np.arange(900, 1100, 20)
        elif variable2['name'] == 'gph_500hPa':
            v2res.cnLevels = np.arange(472, 633, 8)
            v3res.cnLevels = np.arange(472, 633, 32)
        elif variable2['name'] == 'gph_300hPa':
            v2res.cnLevels = np.arange(780, 1000, 12)
            v3res.cnLevels = np.arange(780, 1000, 48)


    basic_map = Ngl.map(wks, mpres)

    # plot subnational borders for some domains #

    shp_filenames = []
    if domain['name'] == 'southern_south_america':
        shp_filenames.append(['gadm36_ARG_1.shp', 0.2])
        shp_filenames.append(['gadm36_BRA_1.shp', 0.2])
        shp_filenames.append(['gadm36_CHL_1.shp', 0.2])
    elif domain['name'] == 'usa':
        shp_filenames.append(['gadm36_USA_1.shp', 0.2])
        shp_filenames.append(['gadm36_CAN_1.shp', 0.2])
        shp_filenames.append(['gadm36_MEX_1.shp', 0.2])

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

    Ngl.overlay(basic_map, contourshades_plot)
    if variable2['name'] != '':
        Ngl.overlay(basic_map, contourlines_minor_plot)
        Ngl.overlay(basic_map, contourlines_major_plot)

    Ngl.draw(basic_map)
    Ngl.text_ndc(wks, text_str, text_x, text_y, text_res_1)

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
