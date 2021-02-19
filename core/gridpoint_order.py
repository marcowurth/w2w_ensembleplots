
import os
import datetime

import numpy as np
import Ngl
from PIL import Image

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_grid_coordinates


def grid_order_contourplot(model, grid, first_varying_var, cut_domain):

    # define paths #

    path = dict(base = '/',
                plots = 'data/plots/experimental/gridpoint_order/')
    print('plotting model: {}'.format(model))


    # load icosahedral grid information #

    if grid == 'icosahedral':
        clat, clon, vlat, vlon = read_grid_coordinates(model, grid)
        data_array1 = np.arange(clat.shape[0], dtype='float32')
    else:
        clat, clon = read_grid_coordinates(model, grid)
        clon = clon - 180
        if first_varying_var == 'lon':
            data_array1 = np.arange(clat.shape[0]*clon.shape[0], dtype='float32').reshape((clat.shape[0],
                                                                                           clon.shape[0]))
        elif first_varying_var == 'lat':
            data_array1 = np.arange(clat.shape[0]*clon.shape[0], dtype='float32').reshape((clon.shape[0],
                                                                                           clat.shape[0])).T


    print('data_array1:', data_array1.shape, 'clat:', clat.shape, 'clon:', clon.shape)
    if grid == 'icosahedral':
        print('vlat:', vlat.shape, 'vlon:', vlon.shape)
    print('data_array1 min,max:', data_array1.min(), data_array1.max())
    print('clat min,max:', clat.min(), clat.max())
    print('clon min,max:', clon.min(), clon.max())
    if grid == 'icosahedral':
        print('vlat min,max:', vlat.min(), vlat.max())
        print('vlon min,max:', vlon.min(), vlon.max())
    print('------------------------------------------')

    if cut_domain['name'] == 'uncut':
        data_array1_cut = data_array1
    else:
        margin_deg = 0
        if grid == 'icosahedral':
            data_array1_cut, clat, clon, vlat, vlon \
              = cut_by_domain(cut_domain, grid, data_array1, clat, clon, vlat, vlon, margin_deg)
        else:
            data_array1_cut, clat, clon \
              = cut_by_domain(cut_domain, grid, data_array1, clat, clon, None, None, margin_deg)

    print('data_array1:', data_array1_cut.shape, 'clat:', clat.shape, 'clon:', clon.shape)
    if grid == 'icosahedral':
        print('vlat:', vlat.shape, 'vlon:', vlon.shape)
    print('data_array1_cut min,max:', data_array1_cut.min(), data_array1_cut.max())
    print('clat min,max:', clat.min(), clat.max())
    print('clon min,max:', clon.min(), clon.max())
    if grid == 'icosahedral':
        print('vlat min,max:', vlat.min(), vlat.max())
        print('vlon min,max:', vlon.min(), vlon.max())


    if grid == 'icosahedral':
        plot_name = 'gridpoint_order_{}_{}_global_{}'.format(model, grid, cut_domain['name'])
    else:
        plot_name = 'gridpoint_order_{}_{}_{}-varying-first_global_{}'.format(model, grid,
                                                                              first_varying_var, cut_domain['name'])


    # plot basic map with borders #

    wks_res             = Ngl.Resources()
    x_resolution        = 800
    y_resolution        = 800
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution

    wks_res.wkColorMap = 'BkBlAqGrYeOrReViWh200'
    levels1 = np.linspace(data_array1.min(), data_array1.max(), 200)

    wks_type = 'png'
    wks = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)


    mpres   = Ngl.Resources()
    mpres.mpProjection = 'CylindricalEquidistant'
    mpres.mpLimitMode  = 'LatLon'
    mpres.mpCenterLonF = 0.0
    mpres.mpCenterLatF = 0.0
    mpres.mpMinLonF    = -180.
    mpres.mpMaxLonF    = 180.
    mpres.mpMinLatF    = -90.
    mpres.mpMaxLatF    = 90.

    mpres.nglMaximize   = False
    mpres.vpXF          = 0.003
    mpres.vpYF          = 1.00
    mpres.vpWidthF      = 0.86
    mpres.vpHeightF     = 1.00
    mpres.mpMonoFillColor = 'True'
    mpres.mpFillColor = -1

    #Ngl.set_values(wks,mpres)
    mpres.mpFillOn       = True
    #resources.cnFillDrawOrder   = 'Predraw'     # draw contours first
    mpres.mpGridAndLimbOn       = False
    mpres.mpGreatCircleLinesOn  = False

    #mpres.mpOutlineDrawOrder       = 'PreDraw'
    mpres.mpDataBaseVersion         = 'LowRes'
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

    basic_map = Ngl.map(wks, mpres)


    # plot variable1 in shading/contours #

    v1res = Ngl.Resources()
    v1res.sfDataArray       = data_array1_cut
    v1res.sfXArray          = clon
    v1res.sfYArray          = clat
    if grid == 'icosahedral':
        v1res.cnFillMode            = 'CellFill'
        v1res.sfXCellBounds     = vlon
        v1res.sfYCellBounds     = vlat
    else:
        v1res.cnFillMode = 'RasterFill'
    v1res.sfMissingValueV   = 9999

    v1res.cnLinesOn             = False   # Turn off contour lines.
    v1res.cnFillOn              = True
    #v1res.cnFillOpacityF        = 0.5   
    #v1res.cnFillDrawOrder       = 'Predraw'
    v1res.cnLineLabelsOn = False
    v1res.cnLevelSelectionMode = 'ExplicitLevels' 
    v1res.cnLevels      = levels1


    # set resources for a nice label bar #

    v1res.lbLabelBarOn          = True
    v1res.lbAutoManage          = False
    v1res.lbOrientation         = 'vertical'
    v1res.lbLabelOffsetF        = 0.04      # minor axis fraction: the distance between colorbar and numbers
    v1res.lbBoxMinorExtentF     = 0.20      # minor axis fraction: width of the color boxes when labelbar down
    v1res.lbTopMarginF          = 0.05      # make a little more space at top for the unit label
    v1res.lbRightMarginF        = 0.0
    v1res.lbBottomMarginF       = 0.0
    v1res.lbLeftMarginF         = -0.35

    v1res.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
    #v1res.cnLabelBarEndStyle    = 'IncludeOuterBoxes'
    #v1res.cnExplicitLabelBarLabelsOn = True
    #v1res.pmLabelBarDisplayMode =  'Always'
    v1res.pmLabelBarWidthF      = 0.10
    #v1res.lbLabelStrings        = label_str_list
    v1res.lbLabelFontHeightF    = 0.010
    #v1res.lbBoxCount            = 40
    v1res.lbBoxSeparatorLinesOn = False
    v1res.lbBoxLineThicknessF   = 4
    #v1res.lbBoxEndCapStyle     = 'TriangleBothEnds'
    v1res.lbLabelAlignment      = 'InteriorEdges'
    v1res.lbLabelStride         = 1

    v1res.nglFrame = False
    v1res.nglDraw  = False

    v1plot = Ngl.contour(wks, data_array1_cut, v1res)


    # plot label bar unit #

    text_str = 'Index'
    text_res_1 = Ngl.Resources()
    text_res_1.txFontColor      = 'black'
    text_x = 0.975
    text_y = 0.72
    text_res_1.txFontHeightF = 0.012


    Ngl.overlay(basic_map, v1plot)

    Ngl.draw(basic_map)
    Ngl.text_ndc(wks, text_str, text_x, text_y, text_res_1)
    Ngl.frame(wks)
    Ngl.destroy(wks)
    #Ngl.end()


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


    del data_array1, data_array1_cut, clat, clon
    if grid == 'icosahedral':
        del vlat, vlon

    return



def cut_by_domain(cut_domain, grid, data_array_dims , data_array_list, clat, clon, vlat, vlon, margin_deg):

    if cut_domain['limits_type'] == 'deltalatlon':
        lat_min = cut_domain['centerlat'] - cut_domain['deltalat_deg'] - margin_deg
        lat_max = cut_domain['centerlat'] + cut_domain['deltalat_deg'] + margin_deg
        lon_min = cut_domain['centerlon'] - cut_domain['deltalon_deg'] - margin_deg
        lon_max = cut_domain['centerlon'] + cut_domain['deltalon_deg'] + margin_deg

    elif cut_domain['limits_type'] == 'radius':
        lat_min = float(np.where(cut_domain['centerlat'] - cut_domain['radius'] / 111.2 - margin_deg < -90, -90,
                                 cut_domain['centerlat'] - cut_domain['radius'] / 111.2 - margin_deg))
        lat_max = float(np.where(cut_domain['centerlat'] + cut_domain['radius'] / 111.2 + margin_deg > 90, 90,
                                 cut_domain['centerlat'] + cut_domain['radius'] / 111.2 + margin_deg))
        lon_min = float(np.where(lat_min <= -90 or lat_max >= 90, -180.1,
                                 cut_domain['centerlon'] - cut_domain['radius'] \
                                  / (111.2 * np.cos(cut_domain['centerlat']*np.pi/180)) - margin_deg))
        lon_max = float(np.where(lat_min <= -90 or lat_max >= 90, 180,
                                 cut_domain['centerlon'] + cut_domain['radius'] \
                                  / (111.2 * np.cos(cut_domain['centerlat']*np.pi/180)) + margin_deg))

    elif cut_domain['limits_type'] == 'angle':
        lat_min = float(np.where(cut_domain['centerlat'] - cut_domain['angle'] - margin_deg < -90, -90,
                                 cut_domain['centerlat'] - cut_domain['angle'] - margin_deg))
        lat_max = float(np.where(cut_domain['centerlat'] + cut_domain['angle'] + margin_deg > 90, 90,
                                 cut_domain['centerlat'] + cut_domain['angle'] + margin_deg))
        lon_min = -180.1
        lon_max = 180

    else:
        print('cut_domain limits_type "{}" not supported!'.format(cut_domain['limits_type']))
        exit()
    #print(lat_min, lat_max, lon_min, lon_max)

    if grid == 'icosahedral':
        filter_lat_high = list(np.where(clat < lat_max)[0])
        filter_lat_low = list(np.where(clat > lat_min)[0])
        if lon_min < -180:
            filter_lon1_high = list(np.where(clon < lon_max)[0])
            filter_lon1_low = list(np.where(clon > -180)[0])
            filter_lon2_high = list(np.where(clon < 180)[0])
            filter_lon2_low = list(np.where(clon > lon_min + 360)[0])
            filter_total1 = list(set(filter_lat_high).intersection(filter_lat_low))
            filter_total1 = list(set(filter_total1).intersection(filter_lon1_high))
            filter_total1 = list(set(filter_total1).intersection(filter_lon1_low))
            filter_total2 = list(set(filter_lat_high).intersection(filter_lat_low))
            filter_total2 = list(set(filter_total2).intersection(filter_lon2_high))
            filter_total2 = list(set(filter_total2).intersection(filter_lon2_low))
            filter_total = filter_total1 + filter_total2
        elif lon_max > 180:
            filter_lon1_high = list(np.where(clon < lon_max - 360)[0])
            filter_lon1_low = list(np.where(clon > -180)[0])
            filter_lon2_high = list(np.where(clon < 180)[0])
            filter_lon2_low = list(np.where(clon > lon_min)[0])
            filter_total1 = list(set(filter_lat_high).intersection(filter_lat_low))
            filter_total1 = list(set(filter_total1).intersection(filter_lon1_high))
            filter_total1 = list(set(filter_total1).intersection(filter_lon1_low))
            filter_total2 = list(set(filter_lat_high).intersection(filter_lat_low))
            filter_total2 = list(set(filter_total2).intersection(filter_lon2_high))
            filter_total2 = list(set(filter_total2).intersection(filter_lon2_low))
            filter_total = filter_total1 + filter_total2
        else:
            filter_lon_high = list(np.where(clon < lon_max)[0])
            filter_lon_low = list(np.where(clon > lon_min)[0])
            filter_total = list(set(filter_lat_high).intersection(filter_lat_low))
            filter_total = list(set(filter_total).intersection(filter_lon_high))
            filter_total = list(set(filter_total).intersection(filter_lon_low))

        filter_total.sort()
        #filter_total_array = np.array(filter_total)
        #print('filter_total shape:', filter_total_array.shape)
        #print('filter_total min,max:', filter_total_array.min(), filter_total_array.max())

        data_array_list_cut = []
        for data_array in data_array_list:
            data_array_list_cut.append(data_array[filter_total])
        clat_cut = clat[filter_total]
        clon_cut = clon[filter_total]
        vlat_cut = vlat[filter_total]
        vlon_cut = vlon[filter_total]
        del data_array_list, clat, clon, vlat, vlon, filter_lat_high, filter_lat_low
        if lon_min < -180 or lon_max > 180:
            del filter_lon1_high, filter_lon1_low, filter_lon2_high, filter_lon2_low
            del filter_total1, filter_total2, filter_total
        else:
            del filter_lon_high, filter_lon_low, filter_total

        return data_array_list_cut, clat_cut, clon_cut, vlat_cut, vlon_cut


    elif grid == 'latlon_0.25' or grid == 'latlon_0.1':
        filter_lat_high = list(np.where(clat < lat_max)[0])
        filter_lat_low = list(np.where(clat > lat_min)[0])
        filter_lon_high = list(np.where(clon < lon_max)[0])
        filter_lon_low = list(np.where(clon > lon_min)[0])
        filter_total_lat = list(set(filter_lat_high).intersection(filter_lat_low))
        filter_total_lon = list(set(filter_lon_high).intersection(filter_lon_low))
        filter_total_lat.sort()
        filter_total_lon.sort()

        data_array_list_cut = []
        for data_array in data_array_list:
            if data_array_dims == '2d':
                data_array_list_cut.append(data_array[filter_total_lat, :][:, filter_total_lon])
            elif data_array_dims == '3d':
                data_array_list_cut.append(data_array[:, filter_total_lat, :][:, :, filter_total_lon])
        clat_cut = clat[filter_total_lat]
        clon_cut = clon[filter_total_lon]
        del data_array_list, clat, clon, filter_lat_high, filter_lat_low, filter_lon_high, filter_lon_low
        del filter_total_lat, filter_total_lon

        return data_array_list_cut, clat_cut, clon_cut

    else:
        print('grid "{}" not supported!'.format(grid))
        exit()

