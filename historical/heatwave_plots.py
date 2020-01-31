
import numpy as np
import eccodes
import netCDF4 as nc
import Ngl
import os
import datetime
from contextlib import ExitStack

def main():

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                data = 'forecast_archive/pamore/heatwave_25.07.19/',
                grid = 'forecast_archive/icon-eu-eps/grid/',
                plots = 'plots/heatwave_25.07.19/',
                colorpalette = 'additional_data/colorpalettes/')

    for lead_days in [4]: #list(range(5)):
        run = dict(year = 2019, month = 7, day = 25 - lead_days, hour = 0)
        hours = [6,12,18,100]
        for i in range(len(hours)):
            hours[i] += lead_days * 100

        data_tmax_6h = np.empty((4, 40, 75948))

        filenames_all = []
        for hour in hours:
            filenames_all.append(['iefff0{:03d}0000.m0{:02d}'.format(hour, member) for member in range(1, 41)])
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/'.format(run['year'], run['month'], run['day'], run['hour'])

        with ExitStack() as stack:
            files_all = [[stack.enter_context(open(path['base'] + path['data'] + path['data_subfolder'] + filename,'rb'))\
              for filename in filenames_of_one_hour] for filenames_of_one_hour in filenames_all]

            for i, files_of_one_hour in enumerate(files_all):
                for j, file in enumerate(files_of_one_hour):
                    grib_id = eccodes.codes_grib_new_from_file(file)
                    data_tmax_6h[i, j, :] = eccodes.codes_get_array(grib_id, 'values')
                    eccodes.codes_release(grib_id)
        del files_all, files_of_one_hour, file

        data_tmax_6h -= 273.15
        data_tmax_24h = data_tmax_6h.max(axis=0)


        ##### settings for plotting #####

        #point = dict(lat = 49.01, lon =  8.40, name = 'Karlsruhe')
        #point = dict(lat = 50.82, lon =  8.92, name = 'Kirchhain')
        #domain = dict(method = 'deltalatlon', radius =    0, deltalat = 700, deltalon = 760,\
        #              lat = 48.7, lon =  5.4, name = 'france-germany')
        domain = dict(method = 'deltalatlon', radius =    0, deltalat = 850, deltalon = 680,\
                      lat = 48.4, lon =  5.0, name = 'france-germany')

        #stat_processing = dict(method = 'max')
        #stat_processing = dict(method = 'min')
        #stat_processing = dict(method = 'median')
        #stat_processing = dict(method = 'spread')
        #stat_processing = dict(method = 'member_extract', member = 1)

        thresholds = []
        #thresholds.append(30.0)
        thresholds.append(36.0)
        #thresholds.append(38.0)
        #thresholds.append(40.0)


        ##### call plotting function #####

        #for stat_processing['member'] in range(1,41):
        #plot_statistical_value_around_point(path, run, data_tmax_24h, point, stat_processing)

        for threshold in thresholds:
            plot_prob_of_exceedance_around_point(path, run, data_tmax_24h, domain, threshold)

    return

########################################################################
########################################################################
########################################################################

def plot_statistical_value_around_point(path, run, data_tmax_24h, point, stat_processing):

    if stat_processing['method'] == 'max':
        data_processed = data_tmax_24h.max(axis=0)
    elif stat_processing['method'] == 'min':
        data_processed = data_tmax_24h.min(axis=0)
    elif stat_processing['method'] == 'median':
        data_processed = np.percentile(data_tmax_24h, 50, axis=0)
    elif stat_processing['method'] == 'spread':
        data_processed = data_tmax_24h.std(axis=0)
    elif stat_processing['method'] == 'member_extract':
        data_processed = data_tmax_24h[stat_processing['member']-1, :]


    ########################################################################

    mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = mpi_file.variables['clat'][:].data * 180./np.pi
    clon = mpi_file.variables['clon'][:].data * 180./np.pi
    mpi_file.close()

    ########################################################################

    if stat_processing['method'] == 'max'\
     or stat_processing['method'] == 'min'\
     or stat_processing['method'] == 'spread'\
     or stat_processing['method'] == 'median':
        member_text_filename = stat_processing['method']
    elif stat_processing['method'] == 'member_extract':
        member_text_filename = 'm{:02d}'.format(stat_processing['member'])
    plot_name = 'iconeueps_tmax_24h_{}_run_{:02d}.{:02d}._{}'.format(\
                    member_text_filename, run['day'], run['month'], point['name'])

    ########################################################################

    x_resolution        = 800
    y_resolution        = 800
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
    resources   = Ngl.Resources()

    resources.mpProjection = 'Hammer'
    resources.mpCenterLonF = point['lon']
    resources.mpCenterLatF = point['lat']

    radius = 700    # image radius in km around centered point
    cutout_plot = dict(
                        lat_min = point['lat'] - radius / 111.2,
                        lat_max = point['lat'] + radius / 111.2,
                        lon_min = point['lon'] - radius / (111.2 * np.cos(point['lat']*np.pi/180)),
                        lon_max = point['lon'] + radius / (111.2 * np.cos(point['lat']*np.pi/180)),
                       )

    resources.mpLimitMode   = 'latlon'
    resources.mpMinLonF     = cutout_plot['lon_min']
    resources.mpMaxLonF     = cutout_plot['lon_max']
    resources.mpMinLatF     = cutout_plot['lat_min']
    resources.mpMaxLatF     = cutout_plot['lat_max']

    resources.nglMaximize   = False
    resources.vpXF          = 0.05
    resources.vpYF          = 0.95
    resources.vpWidthF      = 0.7
    resources.vpHeightF     = 0.7

    ########################################################################

    # Turn on filled map areas:
    resources.mpFillOn = True

    # Set colors for [FillValue, Ocean, Land , InlandWater]:
    resources.mpFillColors = ['pink','blue','white','blue']

    resources.mpDataBaseVersion         = 'MediumRes'
    resources.mpDataSetName             = 'Earth..4'
    resources.mpOutlineBoundarySets     = 'national'

    resources.mpGeophysicalLineThicknessF   = 7.0 * x_resolution / 1000
    resources.mpNationalLineThicknessF      = 7.0 * x_resolution / 1000
    #resources.mpGridAndLimbDrawOrder        = 'postdraw'

    resources.mpGridAndLimbOn               = False
    #resources.mpLimbLineColor               = 'black'
    #resources.mpLimbLineThicknessF          = 10
    #resources.mpGridLineColor               = 'black'
    #resources.mpGridLineThicknessF          = 1.0
    #resources.mpGridSpacingF                = 1

    resources.mpPerimOn                     = True
    resources.mpPerimLineColor              = 'black'
    resources.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000

    resources.tmXBOn = False
    resources.tmXTOn = False
    resources.tmYLOn = False
    resources.tmYROn = False

    resources.sfDataArray       = data_processed
    resources.sfXArray          = clon
    resources.sfYArray          = clat
    resources.sfXCellBounds     = vlon
    resources.sfYCellBounds     = vlat
    resources.sfMissingValueV   = 9999

    resources.cnFillOn              = True
    resources.cnFillMode            = 'CellFill'
    #resources.cnCellFillEdgeColor   = 'black'

    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = 'GMT_wysiwygcont'

    resources.cnLevelSelectionMode  = 'ManualLevels'
    minlevel                        = 0.0
    maxlevel                        = 45.0
    numberoflevels                  = 45
    resources.cnMinLevelValF        = minlevel
    resources.cnMaxLevelValF        = maxlevel
    resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

    if stat_processing['method'] == 'spread':
        resources.cnFillPalette         = 'WhiteYellowOrangeRed'
        minlevel                        = 0.0
        maxlevel                        = 4.0

    # Turn off contour lines and labels:
    resources.cnLinesOn         = False
    resources.cnLineLabelsOn    = False

    # Set resources for a nice label bar
    resources.lbLabelBarOn          = True
    resources.lbAutoManage          = False
    resources.lbOrientation         = 'vertical'
    resources.lbLabelOffsetF        = 0.05
    #resources.lbBoxMinorExtentF     = 0.2

    resources.lbLabelStride         = 5 #25
    resources.lbLabelFontHeightF    = 0.02
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleString         = 'K'
    resources.lbTitleFontHeightF    = 0.02
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    #resources.lbTitleAngleF         = 90.0
    resources.lbTitleExtentF        = 0.1
    resources.lbTitleOffsetF        = 0.0

    resources.nglFrame = False
    plot = Ngl.contour_map(wks, data_processed, resources)

    ########################################################################

    '''polymarker_res_1 = Ngl.Resources()
    polymarker_res_1.gsMarkerColor = 'black'
    polymarker_res_1.gsMarkerIndex = 16
    polymarker_res_1.gsMarkerSizeF = 0.012
    polymarker_res_1.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point['lon'], point['lat'], polymarker_res_1)

    ########################################################################

    polymarker_res_2 = Ngl.Resources()
    polymarker_res_2.gsMarkerColor = 'white'
    polymarker_res_2.gsMarkerIndex = 16
    polymarker_res_2.gsMarkerSizeF = 0.008
    polymarker_res_2.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point['lon'], point['lat'], polymarker_res_2)'''

    ########################################################################

    if stat_processing['method'] == 'max'\
     or stat_processing['method'] == 'min'\
     or stat_processing['method'] == 'spread'\
     or stat_processing['method'] == 'median':
        member_text = '{} of members'.format(stat_processing['method'])
    elif stat_processing['method'] == 'member_extract':
        member_text = 'member {:d}'.format(stat_processing['member'])

    text = 'tmax 00Z-00Z for 25.07.19, icon-eu-eps run {:02d}.{:02d}.19, {}'.format(\
                run['day'], run['month'], member_text)
    x = 0.1
    y = 0.95

    text_res_1 = Ngl.Resources()
    text_res_1.txFontHeightF    = 0.018
    text_res_1.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_1)

    Ngl.frame(wks)
    Ngl.destroy(wks)

    return

########################################################################
########################################################################
########################################################################

def plot_prob_of_exceedance_around_point(path, run, data_tmax_24h, domain, threshold):

    data_processed = np.where(data_tmax_24h >= threshold, 1, 0).sum(axis=0) / 40 * 100
    data_processed += 0.1

    ########################################################################

    mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = mpi_file.variables['clat'][:].data * 180./np.pi
    clon = mpi_file.variables['clon'][:].data * 180./np.pi
    mpi_file.close()

    ########################################################################

    color = 'heat'
    plot_name = 'iconeueps_tmax_24h_prob_over_{:.0f}C_run_{:02d}.{:02d}._{}_{}'.format(\
                    threshold, run['day'], run['month'], domain['name'], color)

    subfolder = 'prob_of_exceedance/{}'.format(domain['name'])
    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.mkdir(path['base'] + path['plots'] + subfolder)
    path['plots_subfolder'] = subfolder + '/'

    ########################################################################

    colorpalette_source = 'hclwizard'
    if colorpalette_source == 'tristenca':
        filename = 'colorscale_tristenca_tot_prec_monohue_blues.txt'
        with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
            line = f.read()

        hex_colors = []
        for i in range(40):
            start = i * 8 + 1
            end = start + 6
            hex_colors.append(line[start:end])

        custom_palette_list = [[255, 255, 255]]
        for hex_color in hex_colors[:]:
            rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
            custom_palette_list.append(rgb_color)
        custom_palette = np.array(custom_palette_list) / 255


    elif colorpalette_source == 'hclwizard':
        filename = 'colorscale_hclwizard_t2m_prob_{}.txt'.format(color)
        with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
            lines = f.readlines()

        hex_colors = []
        for line in lines:
            hex_colors.append(line[2:8])

        custom_palette_list = [[ 0, 255,  0]]           # extra color for correct LabelBar view
        custom_palette_list.append([255, 255, 255])     # color for 1% category
        for hex_color in hex_colors[:]:
            rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
            custom_palette_list.append(rgb_color)
        custom_palette_list.append([255,   0,   0])     # extra color for correct LabelBar view

        custom_palette = np.array(custom_palette_list)

    '''custom_palette = np.array([[255, 255, 255],\
                               [255, 255,   0],\
                               [250,   0,   0],\
                               [  0, 250,   0],\
                               [  0,   0, 250],\
                               [100,   0,   0],\
                               [  0, 100,   0],\
                               [  0,   0, 100],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [100, 100,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [  0,   0,   0],\
                               [250, 100, 100],\
                               [100, 250, 100],\
                               [100, 100, 250]])'''
    custom_palette = custom_palette / 255
    #print(custom_palette.shape)

    ########################################################################

    x_resolution        = 1200
    y_resolution        = 1200
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution
    wks_res.wkColorMap  = custom_palette

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + path['plots_subfolder'] + plot_name, wks_res)
    resources   = Ngl.Resources()

    if domain['method'] == 'centerpoint':
        resources.mpProjection = 'Hammer'
        resources.mpCenterLonF = domain['lon']
        resources.mpCenterLatF = domain['lat']

        cutout_plot = dict(
                            lat_min = domain['lat'] - domain['radius'] / 111.2,
                            lat_max = domain['lat'] + domain['radius'] / 111.2,
                            lon_min = domain['lon'] - domain['radius'] / (111.2 * np.cos(domain['lat']*np.pi/180)),
                            lon_max = domain['lon'] + domain['radius'] / (111.2 * np.cos(domain['lat']*np.pi/180)),
                           )

        resources.mpLimitMode   = 'latlon'
        resources.mpMinLonF     = cutout_plot['lon_min']
        resources.mpMaxLonF     = cutout_plot['lon_max']
        resources.mpMinLatF     = cutout_plot['lat_min']
        resources.mpMaxLatF     = cutout_plot['lat_max']

    elif domain['method'] == 'deltalatlon':
        resources.mpProjection = 'Hammer'
        resources.mpCenterLonF = domain['lon']
        resources.mpCenterLatF = domain['lat']

        cutout_plot = dict(
                            lat_min = domain['lat'] - domain['deltalat'] / 111.2,
                            lat_max = domain['lat'] + domain['deltalat'] / 111.2,
                            lon_min = domain['lon'] - domain['deltalon'] / (111.2 * np.cos(domain['lat']*np.pi/180)),
                            lon_max = domain['lon'] + domain['deltalon'] / (111.2 * np.cos(domain['lat']*np.pi/180)),
                           )

        resources.mpLimitMode   = 'latlon'
        resources.mpMinLonF     = cutout_plot['lon_min']
        resources.mpMaxLonF     = cutout_plot['lon_max']
        resources.mpMinLatF     = cutout_plot['lat_min']
        resources.mpMaxLatF     = cutout_plot['lat_max']
    else:
        print('domain method "{}" not implemented!'.format(domain['method']))
        exit()

    resources.nglMaximize   = False
    resources.vpXF          = 0.02
    resources.vpYF          = 0.92
    resources.vpWidthF      = 0.82
    resources.vpHeightF     = 0.70

########################################################################

    # Turn on filled map areas:
    resources.mpFillOn = True

    # Set colors for [FillValue, Ocean, Land , InlandWater]:
    resources.mpFillColors = ['pink','blue','white','blue']

    resources.mpDataBaseVersion         = 'MediumRes'
    resources.mpDataSetName             = 'Earth..4'
    resources.mpOutlineBoundarySets     = 'national'

    resources.mpGeophysicalLineThicknessF   = 3.0 * x_resolution / 1000
    resources.mpNationalLineThicknessF      = 3.0 * x_resolution / 1000
    #resources.mpGridAndLimbDrawOrder        = 'postdraw'

    resources.mpGridAndLimbOn               = False
    #resources.mpLimbLineColor               = 'black'
    #resources.mpLimbLineThicknessF          = 10
    #resources.mpGridLineColor               = 'black'
    #resources.mpGridLineThicknessF          = 1.0
    #resources.mpGridSpacingF                = 1

    resources.mpPerimOn                     = True
    resources.mpPerimLineColor              = 'black'
    resources.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000

    resources.tmXBOn = False
    resources.tmXTOn = False
    resources.tmYLOn = False
    resources.tmYROn = False

    resources.sfDataArray       = data_processed
    resources.sfXArray          = clon
    resources.sfYArray          = clat
    resources.sfXCellBounds     = vlon
    resources.sfYCellBounds     = vlat
    resources.sfMissingValueV   = 9999

    resources.cnFillOn              = True
    resources.cnFillMode            = 'CellFill'
    #resources.cnCellFillEdgeColor   = 'black'

    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = custom_palette
    resources.cnLevelSelectionMode  = 'ExplicitLevels'
    resources.cnLevels              = np.arange(0, 103, 2.5)

    minlevel                        = 0.0
    maxlevel                        = 100.0
    numberoflevels                  = 40
    resources.cnMinLevelValF        = minlevel
    resources.cnMaxLevelValF        = maxlevel
    resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

    # Turn off contour lines and labels:
    resources.cnLinesOn         = False
    resources.cnLineLabelsOn    = False

    # Set resources for a nice label bar
    resources.lbLabelBarOn          = True
    resources.lbAutoManage          = False
    resources.lbOrientation         = 'vertical'
    resources.lbLabelOffsetF        = 0.05
    #resources.lbBoxMinorExtentF     = 0.2

    #label_str_list = ['{:d}'.format(int(x)) for x in list(range(0, 101, 10))]

    resources.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
    #resources.cnExplicitLabelBarLabelsOn = True
    #resources.pmLabelBarDisplayMode =  'Always'
    resources.pmLabelBarWidthF      = 0.10
    #resources.lbLabelStrings        = label_str_list
    resources.lbLabelStride         = 4
    resources.lbLabelFontHeightF    = 0.018
    #resources.lbBoxCount            = 40
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleString         = '%'
    resources.lbTitleFontHeightF    = 0.018
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    #resources.lbTitleAngleF         = 90.0
    resources.lbTitleExtentF        = 0.1
    resources.lbTitleOffsetF        = 0.0

    resources.nglFrame = False
    plot = Ngl.contour_map(wks, data_processed, resources)

    ########################################################################

    '''polymarker_res_1 = Ngl.Resources()
    polymarker_res_1.gsMarkerColor = 'black'
    polymarker_res_1.gsMarkerIndex = 16
    polymarker_res_1.gsMarkerSizeF = 0.012
    polymarker_res_1.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point['lon'], point['lat'], polymarker_res_1)

    ########################################################################

    polymarker_res_2 = Ngl.Resources()
    polymarker_res_2.gsMarkerColor = 'white'
    polymarker_res_2.gsMarkerIndex = 16
    polymarker_res_2.gsMarkerSizeF = 0.008
    polymarker_res_2.gsMarkerThicknessF = 1
    Ngl.polymarker(wks, plot, point['lon'], point['lat'], polymarker_res_2)'''

    ########################################################################

    run_time = datetime.datetime(run['year'], run['month'], run['day'], run['hour'])
    timeshift = 2
    if timeshift == 1:
        time_code = 'CET'                           # UTC+1
    elif timeshift == 2:
        time_code = 'CEST'                          # UTC+2
    run_time = run_time + datetime.timedelta(0, 3600 * int(timeshift))
    valid_time = run_time + datetime.timedelta(0, 3600 * int(4*24 + 12))
    text1 = '4-Tages-Vorhersage der Maximaltemperatur vom 21.07.19: \
 Wahrscheinlichkeit, dass am 25.07.19 Temperaturen von \
36 ~S~o~N~C, 38 ~S~o~N~C, 40 ~S~o~N~C u~H-13V2F35~H~FV-2H3~berschritten werden'
    text1 = 'Vorhersage der Hitzewelle '
    text1 = 'Modell: ICON-EU-EPS, Bildautor: Marco Wurth, IMK-TRO (KIT)'
    #text2 = 'Wahrscheinlichkeit fu~H-13V2F35~H~FV-2H3~r u~H-13V2F35~H~FV-2H3~ber {:d} ~S~o~N~C'.format(int(threshold))

    text_res_1 = Ngl.Resources()
    text_res_1.txJust           = 'BottomLeft'

    text_res_1.txFontHeightF    = 0.009
    x = 0.01
    y = 0.01
    Ngl.text_ndc(wks, text1, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.018
    x = 0.25
    y = 0.94
    #Ngl.text_ndc(wks, text2, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.014
    x = 0.575
    y = 0.93
    #Ngl.text_ndc(wks, text3, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.014
    x = 0.025
    y = 0.192
    #Ngl.text_ndc(wks, text4, x, y, text_res_1)


    Ngl.frame(wks)
    Ngl.destroy(wks)

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.1f}s'.format(t2-t1))
