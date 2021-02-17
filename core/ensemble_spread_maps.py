
import os
import datetime
import json

import numpy as np
import Ngl
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_forecast_data, read_grid_coordinates


def ens_spread_contourplot(domains, variable1, variable2, model, run):

    hours = list(range(0, 120+1, 6))
    #hours = [0]

    var1var2 = variable1['name'] + '_mean_spread'


    # define paths and create folders #

    ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
    # ex_op_str equals either 'experimental' or 'operational' depending on where this script is

    path = dict(base = '/',
                plots = 'data/plots/{}/ensemble_spread_maps/'.format(ex_op_str),
                temp = 'data/additional_data/temp/{}/'.format(ex_op_str),
                callfiles = 'progs/{}/w2w_ensembleplots/callfiles/'.format(ex_op_str),
                colorpalette = 'data/additional_data/colorpalettes/')

    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])

    if variable1['name'] == 't_850hPa':
        filename_latest_run = 'latest_run_ens_spread_map.txt'
        with open(path['base'] + path['plots'] + filename_latest_run, 'w') as file:
            file.write(subfolder[4:])

    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.makedirs(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/' 

    if not os.path.isdir(path['base'] + path['plots'] + var1var2):
        os.makedirs(path['base'] + path['plots'] + var1var2)
    path['plots'] += var1var2 + '/'


    # load icosahedral grid information and save as npz file #
 
    clat, clon, vlat, vlon = read_grid_coordinates(model, variable1['grid'])
    ll_lat, ll_lon = read_grid_coordinates(model, variable2['grid'])

    numpyarrays_filename = 'ensemble_spread_maps_{}_ndarrays_outofloop.npz'.format(var1var2)
    with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
        np.savez(f, clat = clat, clon = clon, vlat = vlat, vlon = vlon, ll_lat = ll_lat, ll_lon = ll_lon)


    # start plotting loop #

    print('plotting model: {}, run: {:02d}.{:02d}.{:4d}, {:02d}UTC, vars: {}'.format(
          model, run['day'], run['month'], run['year'], run['hour'], var1var2))

    for hour in hours:
        print('forecast hour:', hour)

        data_array1 = read_forecast_data(model, variable1['grid'], run, variable1['name'], fcst_hour=hour)
        data_array2 = read_forecast_data(model, variable2['grid'], run, variable2['name'], fcst_hour=hour)
        data_array1 = np.std(data_array1, axis=0)
        data_array2 = np.mean(data_array2, axis=0)


        # mask the too high areas > plotted grey + without lines #

        if variable1['name'] == 'gph_500hPa':
            lines_max_oro = 5000    # metres
        elif variable1['name'] == 'mslp':
            lines_max_oro = 600
        elif variable1['name'] == 't_850hPa':
            lines_max_oro = 1400

        data_oro_icosahedral = read_forecast_data(model, variable1['grid'], run, 'orography', fcst_hour=hour)
        data_oro_latlon = read_forecast_data(model, variable2['grid'], run, 'orography', fcst_hour=hour)
        data_array1 = np.where(data_oro_icosahedral > lines_max_oro, np.ones_like(data_array1)*9999, data_array1)
        data_array2 = np.where(data_oro_latlon > lines_max_oro, np.ones_like(data_array2)*9999, data_array2)


        # save all numpy arrays to npz file #

        numpyarrays_filename = 'ensemble_spread_maps_{}_ndarrays_withinloop.npz'.format(var1var2)
        with open(path['base'] + path['temp'] + numpyarrays_filename, 'wb') as f:
            np.savez(f, data_array1 = data_array1, data_array2 = data_array2)


        for domain in domains:
            print('domain:', domain['name'])

            # save all dictionaries and strings to a json file #

            json_filename = 'ensemble_spread_maps_{}_dicts_strings.json'.format(var1var2)
            with open(path['base'] + path['temp'] + json_filename, 'w') as f:
                json.dump([path, domain, variable1, variable2, model, run, hour], f)


            # start new batch python script that will free its needed memory afterwards #

            scriptname = 'callfile_ensemble_spread_maps.py'
            command = 'python {}{}{} '.format(path['base'], path['callfiles'], scriptname)
            arguments = var1var2
            os.system(command + arguments)


    # copy all plots and .txt-file to imk-tss-web server #

    subfolder_name = 'ensemble_spread_maps'
    path_webserver = '/home/iconeps/Data3/plots/icon/{}/{}'.format(subfolder_name, var1var2)
    os.system('scp ' + path['base'] + path['plots'] + '*.png '\
              + 'iconeps@imk-tss-web.imk-tro.kit.edu:' + path_webserver)

    if variable1['name'] == 't_850hPa':
        path_webserver = '/home/iconeps/Data3/plots/icon/{}'.format(subfolder_name)
        path_latest_run_files = 'data/plots/{}/{}/'.format(ex_op_str, subfolder_name)
        os.system('scp ' + path['base'] + path_latest_run_files + filename_latest_run\
                  + ' iconeps@imk-tss-web.imk-tro.kit.edu:' + path_webserver)

    return

########################################################################
########################################################################
########################################################################

def ens_spread_map(var1var2):

    recoverpath = dict(base = '/',
                       temp = 'data/additional_data/temp/{}/'.format(ex_op_str))

    # load all dictionaries and strings from json file #

    json_filename = 'ensemble_spread_maps_{}_dicts_strings.json'.format(var1var2)
    with open(recoverpath['base'] + recoverpath['temp'] + json_filename, 'r') as f:
        path, domain, variable1, variable2, model, run, hour = json.load(f)


    # load numpy arrays #

    numpyarrays_filename = 'ensemble_spread_maps_{}_ndarrays_outofloop.npz'.format(var1var2)
    with open(path['base'] + path['temp'] + numpyarrays_filename, 'rb') as f:
        with np.load(f) as loadedfile:
            clat = loadedfile['clat']
            clon = loadedfile['clon']
            vlat = loadedfile['vlat']
            vlon = loadedfile['vlon']
            ll_lat = loadedfile['ll_lat']
            ll_lon = loadedfile['ll_lon']

    numpyarrays_filename = 'ensemble_spread_maps_{}_ndarrays_withinloop.npz'.format(var1var2)
    with open(recoverpath['base'] + recoverpath['temp'] + numpyarrays_filename, 'rb') as f:
        with np.load(f) as loadedfile:
            data_array1 = loadedfile['data_array1']
            data_array2 = loadedfile['data_array2']

    #print('loaded all vars')


    # example plot_name: icon-eu-eps_2020070512_mslp_mean_spread_europe_000h
    plot_name = '{}_{:4d}{:02d}{:02d}{:02d}_{}_{}_{:03d}h'.format(
                 model, run['year'], run['month'], run['day'], run['hour'],
                 var1var2, domain['name'], hour)


    # plot basic map with borders #

    wks_res          = Ngl.Resources()
    wks_res.wkWidth  = domain['plot_width']
    wks_res.wkHeight = domain['plot_width']     # the whitespace above and below the plot will be cut afterwards

    filename_colorpalette = 'colormap_WhiteBeigeGreenBlue_12.txt'
    with open(path['base'] + path['colorpalette'] + filename_colorpalette, 'r') as f:
        lines = f.readlines()
    rgb_colors = []
    rgb_colors.append([1, 1, 1])
    rgb_colors.append([0, 0, 0])
    rgb_colors.append([.5, .5, .5])
    for line in lines:
        rgb_colors.append([float(line[0:3])/255, float(line[4:7])/255, float(line[8:11])/255])
    rgb_colors.append(rgb_colors[-1])
    wks_res.wkColorMap = np.array(rgb_colors)

    if variable1['name'] == 'gph_500hPa' :
        levels1 = np.arange(0, 12.1, 1)
    elif variable1['name'] == 'mslp' :
        levels1 = np.arange(0, 12.1, 1)
    elif variable1['name'] == 't_850hPa' :
        levels1 = np.arange(0, 6.1, 0.5)


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
    mpres.mpFillColor = -1
    mpres.mpFillOn = True
    mpres.mpGridAndLimbOn = False
    mpres.mpGreatCircleLinesOn = False

    mpres.mpDataBaseVersion         = 'MediumRes'
    mpres.mpDataSetName             = 'Earth..4'
    mpres.mpOutlineBoundarySets     = 'national'
    mpres.mpGeophysicalLineColor        = 'black'
    mpres.mpNationalLineColor           = 'black'
    mpres.mpGeophysicalLineThicknessF   = 1.0 * domain['plot_width'] / 1000
    mpres.mpNationalLineThicknessF      = 1.0 * domain['plot_width'] / 1000

    mpres.mpPerimOn                     = True
    mpres.mpPerimLineColor              = 'black'
    mpres.mpPerimLineThicknessF         = 6.0 * domain['plot_width'] / 1000
    mpres.tmXBOn = False
    mpres.tmXTOn = False
    mpres.tmYLOn = False
    mpres.tmYROn = False

    mpres.nglDraw        =  False              # don't draw plot
    mpres.nglFrame       =  False              # don't advance frame


    # settings for variable1 / shading #

    v1res = Ngl.Resources()
    v1res.sfDataArray       = data_array1
    v1res.sfXArray          = clon             
    v1res.sfYArray          = clat
    v1res.sfXCellBounds     = vlon
    v1res.sfYCellBounds     = vlat
    v1res.sfMissingValueV   = 9999
    v1res.cnMissingValFillColor = 'Gray80'

    v1res.cnLinesOn         = False   # Turn off contour lines.
    v1res.cnFillOn          = True
    v1res.cnFillMode        = 'CellFill'
    #v1res.cnFillOpacityF    = 0.5   
    #v1res.cnFillDrawOrder   = 'Predraw'
    v1res.cnLevelSelectionMode = 'ExplicitLevels' 
    v1res.cnLevels          = levels1


    # set resources for a nice label bar #

    v1res.lbLabelBarOn          = True
    v1res.lbAutoManage          = False
    v1res.lbOrientation         = 'vertical'
    v1res.lbLabelOffsetF        = 0.04      # minor axis fraction: the distance between colorbar and numbers
    v1res.lbBoxMinorExtentF     = 0.20      # minor axis fraction: width of the color boxes when labelbar down
    v1res.lbTopMarginF          = 0.14      # make a little more space at top for the unit label
    v1res.lbRightMarginF        = 0.0
    v1res.lbBottomMarginF       = 0.0
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
    if variable2['name'] == 'mslp':
        v1res.lbLabelStride = 1
    elif variable2['name'] == 'gph_500hPa':
        v1res.lbLabelStride = 1
    elif variable2['name'] == 't_850hPa':
        v1res.lbLabelStride = 2

    v1res.nglFrame = False
    v1res.nglDraw  = False


    # settings for variable2 / thin contourlines #

    v2res = Ngl.Resources()
    v2res.sfDataArray       = data_array2
    v2res.sfXArray          = ll_lon
    v2res.sfYArray          = ll_lat
    v2res.sfMissingValueV   = 9999  
    #v2res.trGridType        = 'TriangularMesh'
    v2res.cnFillOn       = False
    v2res.cnLinesOn      = True
    v2res.cnLineLabelsOn = True
    v2res.cnLineLabelInterval = 1
    v2res.cnLineLabelPlacementMode = 'Constant'
    v2res.cnLineDashSegLenF = 0.25
    v2res.cnLabelDrawOrder = 'PostDraw' # necessary to make everything visible
    v2res.cnLineThicknessF = 3.0 * domain['plot_width'] / 1000
    v2res.cnInfoLabelOn = False
 
    v2res.cnSmoothingOn = False
    v2res.cnSmoothingDistanceF = 0.01
    v2res.cnSmoothingTensionF = 0.1            
    if variable2['name'] == 'mslp':
        v2res.cnLevelSpacingF = 2
        v2res.cnLineLabelFontHeightF = 0.008
    elif variable2['name'] == 'gph_500hPa':
        v2res.cnLevelSpacingF = 4
        v2res.cnLineLabelFontHeightF = 0.008
    elif variable2['name'] == 't_850hPa':
        v2res.cnLevelSpacingF = 2
        v2res.cnLineLabelFontHeightF = 0.009
        v2res.cnLineDashSegLenF = 0.18

    v2res.cnLevelSelectionMode = 'ManualLevels' 
    #v2res.cnLevels = levels2
    #v2res.cnRasterSmoothingOn = True

    v2res.nglFrame = False
    v2res.nglDraw  = False


    # settings for variable2 / thick contourlines #

    v3res = Ngl.Resources()
    v3res.sfDataArray       = data_array2
    v3res.sfXArray          = ll_lon
    v3res.sfYArray          = ll_lat
    v3res.sfMissingValueV   = 9999  
    #v3res.trGridType        = 'TriangularMesh'
    v3res.cnFillOn       = False
    v3res.cnLinesOn      = True
    v3res.cnLineLabelsOn = True
    v3res.cnLineLabelInterval = 1
    v3res.cnLineLabelPlacementMode = 'Constant'
    v3res.cnLineDashSegLenF = 0.25
    v3res.cnLabelDrawOrder = 'PostDraw' # necessary to make everything visible
    v3res.cnLineThicknessF = 5.0 * domain['plot_width'] / 1000
    v3res.cnLineLabelFontHeightF = 0.010
    v3res.cnInfoLabelOn = False
 
    v3res.cnSmoothingOn = False
    #v3res.cnSmoothingDistanceF = 0.01
    #v3res.cnSmoothingTensionF = 0.1            
    v3res.cnLevelSelectionMode = 'ManualLevels' 
    #v3res.cnLevels = levels2
    #v3res.cnRasterSmoothingOn = True

    if variable2['name'] == 'mslp':
        v3res.cnLevelSpacingF = 10
        v3res.cnLineLabelFontHeightF = 0.008
    elif variable2['name'] == 'gph_500hPa':
        v3res.cnLevelSpacingF = 16
        v3res.cnLineLabelFontHeightF = 0.008
        v3res.cnLevelSelectionMode = 'ExplicitLevels' 
        v3res.cnLevels = np.arange(520, 600, 16)
    elif variable2['name'] == 't_850hPa':
        v3res.cnLevelSpacingF = 6
        v3res.cnLineLabelFontHeightF = 0.009
        v3res.cnLineDashSegLenF = 0.18

    v3res.nglFrame = False
    v3res.nglDraw  = False


    # settings for unit text #

    text_str = variable1['unit']
    text_res_1 = Ngl.Resources()
    text_res_1.txFontColor      = 'black'
    text_res_1.txFontHeightF = 0.013
    #text_x = 0.965
    text_x = 0.972
    text_y = 0.837 #0.865


    # put everything together # 

    basic_map = Ngl.map(wks, mpres)
    v1plot = Ngl.contour(wks, data_array1, v1res)
    v2plot = Ngl.contour(wks, data_array2, v2res)
    v3plot = Ngl.contour(wks, data_array2, v3res)
    Ngl.overlay(basic_map, v1plot)
    Ngl.overlay(basic_map, v2plot)
    Ngl.overlay(basic_map, v3plot)

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
