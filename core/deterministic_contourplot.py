
import os
import datetime

import numpy as np
import Ngl

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_forecast_data, read_grid_coordinates
from w2w_ensembleplots.core.download_forecast import get_timeshift



#new function using read_forecast_data from read_data.py
def det_contourplot(domain, variable1, variable2, model, run):

    hours = list(range(0,180+1,12)) #maybe a more sophisticated solution for that
#    hours = list(range(0,12+1,12))
    var1var2 = variable1['name'] + '_' + variable2['name']

    #define pasthth bases:
    path = dict(base = '/',
                data1 = 'data/model_data/{}/forecasts/'.format(model),
                data2 = 'data/model_data/{}/forecasts/'.format(model),
                grid = 'data/model_data/{}/grid/'.format(model),
                plots = 'data/plots/operational/map_deterministic/{}/'.format(model), #use format to get variable1+2 names in as subdir
                #colorpalette # for now i would use one from pyngl
                #shapefiles = 'data/additional_data/shapefiles/', #this dir is still empty, brauch ich auch nicht
                topo = 'data/model_data/{}/invariant/'.format(model) #some grib files, dont know what they mean
                )   

    #finish the paths

    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])

    #if not os.path.isdir(path['base'] + path['data1'] + subfolder + '/' + variable1['name'] + '/'):
    #    os.mkdir(path['base'] + path['data1'] + subfolder + '/' + variable1['name'] + '/')
    #path['data1'] += subfolder + '/' + variable1['name'] + '/'

    #if not os.path.isdir(path['base'] + path['data2'] + subfolder + '/' + variable2['name'] + '/'):
    #    os.mkdir(path['base'] + path['data2'] + subfolder + '/' + variable2['name'] + '/')
    #path['data2'] += subfolder + '/' + variable2['name'] + '/'

    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.makedirs(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/' 

    if not os.path.isdir(path['base'] + path['plots'] + var1var2):
        os.makedirs(path['base'] + path['plots'] + var1var2)
    path['plots'] += var1var2 + '/'


    ##get filenames
    #if model == 'icon-global-det':
    #    filename_beginning = 'icon_global_icosahedral_single-level_'
    #elif model == 'icon-eu-det':
    #    filename_beginning = 'icon-eu_europe_regular-lat-lon_single-level_'
#
    #filename1 = []
    #filename1.append('{}_{:4d}{:02d}{:02d}{:02d}_{}.nc'.format(\
    #                            filename_beginning, run['year'], run['month'], run['day'], run['hour'],\
    #                            variable1['name']))
#
    #filename2 = []
    #filename2.append('{}_{:4d}{:02d}{:02d}{:02d}_{}.nc'.format(\
    #                            filename_beginning, run['year'], run['month'], run['day'], run['hour'],\
    #                            variable2['name']))
 

    # load icosahedral grid information only once #

    clat, clon, vlat, vlon = read_grid_coordinates(model, 'icosahedral')


    # start here the whole plotting routine #

    for hour in hours[:1]:
        print('forecast hour:', hour)

        ll_lat, ll_lon = read_grid_coordinates(model, 'latlon_0.25')
        data_array1 = read_forecast_data(model, variable1['grid'], run, variable1['name'], fcst_hour=hour)
        data_array2f = read_forecast_data(model, variable2['grid'], run, variable2['name'], fcst_hour=hour)

        if variable2['grid'] == 'latlon_0.25':
            data_array2, ll_lon = Ngl.add_cyclic(data_array2f, ll_lon)

        plot_name = '{}_{}_{}_{:03d}h'.format(
                     variable1['name'], variable2['name'], domain['name'], hour)

        #if variable1['name'] == 'tot_prec'
        #    varname1_cf = 'tp'

        #if variable2['name'] == 'mslp'
        #    varname2_cf = 'prmsl'

        #do array1 in shading

        wks_res             = Ngl.Resources()
        x_resolution        = 800
        y_resolution        = 800
        wks_res.wkWidth     = x_resolution
        wks_res.wkHeight    = y_resolution

        if variable1['name'] == 'prec_rate' :
            wks_res.wkColorMap = 'precip3_16lev'
            levels1 = ([0.1,0.2,0.5,1,2,5,10,20,50]) #hier vllt ein array mit definitiven leveln
        elif variable1['name'] == 't_850hPa' :
            wks_res.wkColorMap = 'BkBlAqGrYeOrReViWh200'
            levels1 = np.arange(-40,40,4)
        elif variable1['name'] == 'wind_300hPa' :
            wks_res.wkColorMap = 'wh-bl-gr-ye-re' #from 100 to 200
            levels1 = np.arange(150,300,25)
        #irgendwie so machen dass es erst bei grün anfängt
        wks_type = 'png'
        wks = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)



        mpres   = Ngl.Resources()

        if domain['method'] == 'centerpoint':
            mpres.mpProjection = 'Hammer'
            mpres.mpCenterLonF = domain['lon']
            mpres.mpCenterLatF = domain['lat']

            cutout_plot = dict(
                                lat_min = float(np.where(domain['lat'] - domain['radius'] / 111.2 < -90,
                                                   -90, domain['lat'] - domain['radius'] / 111.2)),
                                lat_max = float(np.where(domain['lat'] + domain['radius'] / 111.2 > 90,
                                                   90, domain['lat'] + domain['radius'] / 111.2)),
                               )
            cutout_plot['lon_min'] = float(np.where(cutout_plot['lat_min'] <= -90 or cutout_plot['lat_max'] >= 90,
                                           0,
                                           domain['lon'] - domain['radius'] \
                                            / (111.2 * np.cos(domain['lat']*np.pi/180))))
            cutout_plot['lon_max'] = float(np.where(cutout_plot['lat_min'] <= -90 or cutout_plot['lat_max'] >= 90,
                                           360,
                                           domain['lon'] + domain['radius'] \
                                            / (111.2 * np.cos(domain['lat']*np.pi/180))))
            #print('domain center point lat:', domain['lat'])
            #print('lat_min:', cutout_plot['lat_min'])
            #print('lat_max:', cutout_plot['lat_max'])
            #print('lon_min:', cutout_plot['lon_min'])
            #print('lon_max:', cutout_plot['lon_max'])

        mpres.mpLimitMode   = 'latlon'
        mpres.mpMinLonF     = cutout_plot['lon_min']
        mpres.mpMaxLonF     = cutout_plot['lon_max']
        mpres.mpMinLatF     = cutout_plot['lat_min']
        mpres.mpMaxLatF     = cutout_plot['lat_max']

        mpres.nglMaximize   = False
#       if plot_type == 'small_map_only':
#        mpres.vpXF          = 0.00
#        mpres.vpYF          = 1.00
#        mpres.vpWidthF      = 1.00
#        mpres.vpHeightF     = 1.00
        mpres.mpMonoFillColor = 'True'
        mpres.mpFillColor = -1
    
#        Ngl.set_values(wks,mpres)
        mpres.mpFillOn       = True    # Turn on map fill.   
        # Set colors for [FillValue, Ocean, Land , InlandWater]:
#        resources.cnFillDrawOrder       = 'Predraw'     # Draw contours first.
        mpres.mpGridAndLimbOn               = False
        mpres.mpGreatCircleLinesOn  = True

#        mpres.mpOutlineDrawOrder           = 'PreDraw'
        mpres.mpDataBaseVersion         = 'MediumRes'
        mpres.mpDataSetName             = 'Earth..4'
        mpres.mpOutlineBoundarySets     = 'national'
        mpres.mpGeophysicalLineColor        = 'black'
        mpres.mpNationalLineColor           = 'black'
        mpres.mpGeophysicalLineThicknessF   = 2. * x_resolution / 1000
        mpres.mpNationalLineThicknessF      = 2. * x_resolution / 1000

        mpres.mpPerimOn                     = True
        mpres.mpPerimLineColor              = 'black'
        mpres.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000
        mpres.tmXBOn = False
        mpres.tmXTOn = False
        mpres.tmYLOn = False
        mpres.tmYROn = False

        mpres.nglDraw        =  False              #-- don't draw plot
        mpres.nglFrame       =  False              #-- don't advance frame

        map = Ngl.map(wks, mpres)

        v1res = Ngl.Resources()
        v1res.sfDataArray       = data_array1   
        v1res.sfXArray          = clon             
        v1res.sfYArray          = clat
        v1res.sfXCellBounds     = vlon
        v1res.sfYCellBounds     = vlat
        v1res.sfMissingValueV   = 9999

        v1res.cnLinesOn      = False   # Turn off contour lines.
        v1res.cnFillOn              = True
        v1res.cnFillMode            = 'CellFill'
#        v1res.cnFillOpacityF        = 0.5   
#        v1res.cnFillDrawOrder       = 'Predraw'
        v1res.cnLevelSelectionMode = 'ExplicitLevels' 
        v1res.cnLevels      = levels1
        


        # set resources for a nice label bar #

        v1res.lbLabelBarOn          = True
        v1res.lbAutoManage          = False
        v1res.lbOrientation         = 'vertical'
        v1res.lbLabelOffsetF        = 0.05
        #v1res.lbBoxMinorExtentF     = 0.2

        v1res.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
        if variable1['name'] == 'prec_rate' :
            v1res.cnLabelBarEndStyle    = 'IncludeOuterBoxes'
        #v1res.cnExplicitLabelBarLabelsOn = True
        #v1res.pmLabelBarDisplayMode =  'Always'
        v1res.pmLabelBarWidthF      = 0.10
        #v1res.lbLabelStrings        = label_str_list
        v1res.lbLabelFontHeightF    = 0.016
        #v1res.lbBoxCount            = 40
        v1res.lbBoxSeparatorLinesOn = False
        v1res.lbBoxLineThicknessF   = 4.0
        #v1res.lbBoxEndCapStyle     = 'TriangleBothEnds'
        v1res.lbLabelAlignment      = 'InteriorEdges'
        v1res.lbLabelStride         = 2
        if variable1['name'] == 'prec_rate' :
            v1res.lbLabelStride     = 1


        # plot label bar unit #

        text_str = variable1['unit']
        text_res_1 = Ngl.Resources()
        text_res_1.txJust           = 'BottomLeft'
        text_res_1.txFontHeightF    = 0.016
        text_res_1.txFontColor      = 'black'
        text_x = 0.85
        text_y = 0.21


        v1res.nglFrame = False
        v1res.nglDraw  = False

        v1plot = Ngl.contour(wks, data_array1, v1res)

        #do array2 in contourlines
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
        v2res.cnLineThicknessF = 5.0
        v2res.cnInfoLabelOn = False
        #hier wird doch wieder cnLevels definiert werden müssen
        v2res.cnSmoothingOn = True
        v2res.cnSmoothingDistanceF = 0.01
        v2res.cnSmoothingTensionF = 0.1
        if variable2['name'] == 'mslp':
            spcng = 5
#           levesl2 = np.arange(850,1100,5)
        elif variable2['name'] == 'gph_500hPa':
            spcng = 4
        elif variable2['name'] == 'gph_300hPa':
            spcng = 4
        v2res.cnLevelSelectionMode = 'ManualLevels' 
        v2res.cnLevelSpacingF      =  spcng
#       v2res.cnLevels = levels2
#        v2res.cnRasterSmoothingOn = True

        v2res.nglFrame = False
        v2res.nglDraw  = False

        v2plot = Ngl.contour(wks, data_array2, v2res)


        Ngl.overlay(map, v1plot)
        Ngl.overlay(map, v2plot)
 
        print('hi')
        Ngl.draw(map)
        Ngl.text_ndc(wks, text_str, text_x, text_y, text_res_1)
        print('map done')
        Ngl.frame(wks)
        print('frame done')
        Ngl.destroy(wks)
#        Ngl.end()
        print('destroy done')

    del data_array1, data_array2, vlat, vlon, clat, clon

    return





##equivalent to triangle_contourplot from statistics_contourplot.py
#def triangle_det_contourplot(domain, variable1, variable2, model, run, plot_type):
#
#    hours = list(range(0,180+1,12)) #maybe a more sophisticated solution for that
#
#    #define pasth bases:
#    path = dict(base = '/'
#                data1 = '/data/model_data/{}/forecasts'.format(model)
#                data2 = '/data/model_data/{}/forecasts'.format(model)
#                grid = '/data/model_data/{}/grid'.format(model)
#                plots = '/data/plots/experimental/map_deterministic' #use format to get variable1+2 names in as subdir
#                #colorpalette # for now i would use one from pyngl
#                shapefiles = '/data/additional_data/shapefiles' #this dir is still empty
#                topo = '/data/model_data/{}/invariant'.format(model) #some grib files, dont know what they mean
#                )
#
#    # set basic plot path #
#
#    if plot_type == 'map_only' or plot_type == 'labelBar1' or plot_type == 'labelBar2' or plot_type == 'text':
#        if variable1['name'] + "_" + variable2['name'] == 'tot_prec_06h_pmsl':
#            path['plots'] = 'plots/operational/prob_of_exc/forecast/tot_prec_06h_pmsl/'        
#        #if variable1['name'] == 'pmsl':
#        #    path['plots'] = 'plots/operational/prob_of_exc/forecast/pmsl/'   
#        #if variable2['name'] == 'tot_prec_06h':
#        #    path['plots'] = 'plots/operational/prob_of_exc/forecast/tot_prec_06h/'        
#        #if variable2['name'] == 'pmsl':
#        #    path['plots'] = 'plots/operational/prob_of_exc/forecast/pmsl/'       
#
#    # create plot subfolders
#
#    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])
#    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
#        os.mkdir(path['base'] + path['plots'] + subfolder)
#    path['plots'] += subfolder + '/'
#
#    #set path and filenames for first grib files
#
#    return



#### write quivalent to plot_prob_of_exc from statistics_contourplot.py
#def plot_deterministic_contourplot(domain, variable1, variable2, model, run, plot_type):
#    
#    
#    #calclatestruntime
#    #variable1['name']=
#    #variable2['name']=
#    
#
#
#    #set path
#    path = dict(#base =     
#                data = data = 'data/model_data/icon-global-det/forecasts/run_{}{:02}{:02}{:02}'.format(
#                    date['year'], date['month'], date['day'], date['hour'])#run/variable    date=run?
#                plots = '~/data/plots/experimental/map_deterministic/'#run/variable
#                )
#    # set workstation
#    x_resolution        = 800
#    y_resolution        = 800
#    wks_res             = Ngl.Resources()
#    wks_res.wkWidth     = x_resolution
#    wks_res.wkHeight    = y_resolution
#    #wks_res.wkColorMap  = custom_palette
#
#    wks_type    = 'png'
#    wks         = Ngl.open_wks(wks_type, path['plots'] + plot_name, wks_res)
#    resources   = Ngl.Resources()
#    #get data_processed
#
#    #set ressources
#
#    resources.nglFrame = False
#    plot = Ngl.contour_map(wks, data_processed, resources)
#
#
#    del wks, data_processed, resources
#    return