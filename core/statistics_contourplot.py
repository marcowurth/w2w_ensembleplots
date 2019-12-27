
import numpy as np
import eccodes
import netCDF4 as nc
import Ngl
import os
import datetime
from contextlib import ExitStack

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('scripts')+8 : current_path.index('w2w_ensembleplots')-1]
sys.path.append('/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/scripts/{}'.format(ex_op_str))
from w2w_ensembleplots.core.download_forecast import get_timeshift


def triangle_contourplot(variable, run, domain, model, stat_processing, plot_type):

    # set data path and hours list #

    if model == 'icon-eu-eps':
        model_path_deprec = 'icon-eu-eps'
        hours = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
    elif model == 'icon-global-eps':
        model_path_deprec = 'icon-eps'
        hours = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120,6)) + list(range(120,180+1,12))

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                data = 'forecast_archive/{}/raw_grib/'.format(model_path_deprec),
                grid = 'forecast_archive/{}/grid/'.format(model_path_deprec),
                plots = 'plots/operational/triangle_contourplots/',
                colorpalette = 'additional_data/colorpalettes/',
                topo = 'forecast_archive/{}/invariant/'.format(model_path_deprec))


    # set basic plot path #

    if plot_type == 'small_map_only' or plot_type == 'labelBar1' or plot_type == 'labelBar2' or plot_type == 'text':
        if variable['name'] == 'tot_prec_24h':
            path['plots'] = 'plots/operational/prob_of_exc/tot_prec_24h/'
        elif variable['name'] == 'tot_prec_48h':
            path['plots'] = 'plots/operational/prob_of_exc/tot_prec_48h/'
        elif variable['name'] == 'acc_prec':
            path['plots'] = 'plots/operational/prob_of_exc/acc_prec/'
        elif variable['name'] == 't_850hpa':
            path['plots'] = 'plots/operational/prob_of_exc/t_850hpa/'
        elif variable['name'] == 'mslp':
            path['plots'] = 'plots/operational/prob_of_exc/mslp/'
        elif variable['name'] == 'wind_10m':
            path['plots'] = 'plots/operational/prob_of_exc/wind_10m/'
        elif variable['name'] == 'wind_300hpa':
            path['plots'] = 'plots/operational/prob_of_exc/wind_300hpa/'
        elif variable['name'] == 'gph_500hpa':
            path['plots'] = 'plots/operational/prob_of_exc/gph_500hpa/'
        elif variable['name'] == 'gph_300hpa':
            path['plots'] = 'plots/operational/prob_of_exc/gph_300hpa/'
        elif variable['name'] == 'tqv':
            path['plots'] = 'plots/operational/prob_of_exc/tqv/'
        else:
            print('error: variable unknown')


    # create plot subfolders #

    subfolder = 'run_{:4d}{:02d}{:02d}{:02d}'.format(run['year'], run['month'], run['day'], run['hour'])
    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.mkdir(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/'

    subfolder = domain['name']
    if not os.path.isdir(path['base'] + path['plots'] + subfolder):
        os.mkdir(path['base'] + path['plots'] + subfolder)
    path['plots'] += subfolder + '/'

    if plot_type != 'small_map_only' and plot_type != 'labelBar1' and plot_type != 'labelBar2' and plot_type != 'text':
        if stat_processing['method'] == 'prob_of_exc':
            subfolder = 'prob_of_exc'
        elif stat_processing['method'] == 'member_extract':
            subfolder = 'members'
        else:
            subfolder = 'statistical'
        if not os.path.isdir(path['base'] + path['plots'] + subfolder):
            os.mkdir(path['base'] + path['plots'] + subfolder)
        path['plots'] += subfolder + '/'


    # set path and filenames for first grib file variable #

    if variable['name'] == 'tot_prec_24h'\
     or variable['name'] == 'tot_prec_48h'\
     or variable['name'] == 'acc_prec':
        if model == 'icon-eu-eps':
            filename_beginning = 'icon-eu-eps_europe_icosahedral_single-level'
        elif model == 'icon-global-eps':
            filename_beginning = 'icon-eps_global_icosahedral_single-level'
        dwd_varname = 'tot_prec'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/tot_prec/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 't_850hpa':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_pressure-level'
        dwd_varname = '850_t'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/t_850hPa/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'mslp':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_single-level'
        dwd_varname = 'ps'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/ps/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'wind_10m':
        if model == 'icon-eu-eps':
            filename_beginning = 'icon-eu-eps_europe_icosahedral_single-level'
        elif model == 'icon-global-eps':
            filename_beginning = 'icon-eps_global_icosahedral_single-level'
        dwd_varname = 'u_10m'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/u_10m/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'wind_300hpa':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_pressure-level'
        dwd_varname = '300_u'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/u_300hPa/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'gph_500hpa':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_pressure-level'
        dwd_varname = '500_fi'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/fi_500hPa/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'gph_300hpa':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_pressure-level'
        dwd_varname = '300_fi'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/fi_300hPa/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])
    elif variable['name'] == 'tqv':
        filename_beginning = 'icon-eu-eps_europe_icosahedral_single-level'
        dwd_varname = 'tqv'
        path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/tqv/'.format(\
                                    run['year'], run['month'], run['day'], run['hour'])


    # load first grib file variable #

    filenames_all = []
    for hour in hours:
        filenames_all.append('{}_{:4d}{:02d}{:02d}{:02d}_{:03d}_{}.grib2'.format(\
                                filename_beginning, run['year'], run['month'], run['day'], run['hour'],\
                                hour, dwd_varname))

    if model == 'icon-eu-eps':
        data_array = np.empty((len(hours), 40, 75948), dtype='float32')
    elif model == 'icon-global-eps':
        data_array = np.empty((len(hours), 40, 327680), dtype='float32')
    with ExitStack() as stack:
        files_all = [stack.enter_context(open(path['base'] + path['data'] + path['data_subfolder'] + filename,'rb'))\
                     for filename in filenames_all]

        for i, file in enumerate(files_all):
            for j in range(40):
                grib_id = eccodes.codes_grib_new_from_file(file)
                data_array[i, j, :] = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
    del files_all, grib_id, stack


    # set path and filenames for second grib file variable #

    if variable['name'] == 'mslp' or variable['name'] == 'wind_10m' or variable['name'] == 'wind_300hpa':
        if variable['name'] == 'mslp':
            dwd_varname = 't_2m'
            path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/t_2m/'.format(\
                                      run['year'], run['month'], run['day'], run['hour'])
        elif variable['name'] == 'wind_10m':
            dwd_varname = 'v_10m'
            path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/v_10m/'.format(\
                                      run['year'], run['month'], run['day'], run['hour'])
        elif variable['name'] == 'wind_300hpa':
            dwd_varname = '300_v'
            path['data_subfolder'] = 'run_{:4d}{:02d}{:02d}{:02d}/v_300hPa/'.format(\
                                      run['year'], run['month'], run['day'], run['hour'])
        filenames_all = []
        for hour in hours:
            filenames_all.append('{}_{:4d}{:02d}{:02d}{:02d}_{:03d}_{}.grib2'.format(\
                                    filename_beginning, run['year'], run['month'], run['day'], run['hour'],\
                                    hour, dwd_varname))


        # load second grib file variable #

        if model == 'icon-eu-eps':
            data_array2 = np.empty((len(hours), 40, 75948), dtype='float32')
        elif model == 'icon-global-eps':
            data_array2 = np.empty((len(hours), 40, 327680), dtype='float32')
        with ExitStack() as stack:
            files_all = [stack.enter_context(open(path['base'] + path['data'] + path['data_subfolder']\
                                                  + filename,'rb')) for filename in filenames_all]

            for i, file in enumerate(files_all):
                for j in range(40):
                    grib_id = eccodes.codes_grib_new_from_file(file)
                    data_array2[i, j, :] = eccodes.codes_get_array(grib_id, 'values')
                eccodes.codes_release(grib_id)
        del files_all, grib_id, stack
    else:
        data_array2 = None


    # call plotting function #

    if stat_processing['method'] == 'member_extract':
        if stat_processing['member'] == 'all':
            for stat_processing['member'] in range(1,41):
                plot_statistical_value_around_point(path, run, data_array, variable, domain, stat_processing)
            return
        else:
            stat_processing['member'] = int(stat_processing['member'])

    if stat_processing['method'] == 'prob_of_exc':
        plot_prob_of_exc(path, run, hours, data_array, data_array2, variable, domain, model, stat_processing,
                         plot_type)
    else:
        plot_statistical_value_around_point(path, run, data_array, variable, domain, stat_processing)

    del data_array, data_array2

    return

########################################################################
########################################################################
########################################################################

def plot_statistical_value_around_point(path, run, data_tot_prec, variable, domain, stat_processing):

    hours = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
    data_tot_prec_timespan = data_tot_prec[hours.index(variable['hour_end']), :, :]\
                            - data_tot_prec[hours.index(variable['hour_start']), :, :]
    if stat_processing['method'] == 'max':
        data_processed = data_tot_prec_timespan.max(axis=0)
    elif stat_processing['method'] == 'min':
        data_processed = data_tot_prec_timespan.min(axis=0)
    elif stat_processing['method'] == 'median':
        data_processed = np.percentile(data_tot_prec_timespan, 50, axis=0)
    elif stat_processing['method'] == '10p':
        data_processed = np.percentile(data_tot_prec_timespan, 10, axis=0)
    elif stat_processing['method'] == '90p':
        data_processed = np.percentile(data_tot_prec_timespan, 90, axis=0)
    elif stat_processing['method'] == 'spread':
        data_processed = data_tot_prec_timespan.std(axis=0)
    elif stat_processing['method'] == 'member_extract':
        data_processed = data_tot_prec_timespan[stat_processing['member']-1, :]
    else:
        print('statistical method "{}" not implemented!'.format(stat_processing['method']))
        exit()

    ########################################################################

    mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = mpi_file.variables['clat'][:].data * 180./np.pi
    clon = mpi_file.variables['clon'][:].data * 180./np.pi
    mpi_file.close()

    ########################################################################

    if stat_processing['method'] == 'member_extract':
        plot_name = 'iconeueps_{}_{:03d}-{:03d}h_{}_m{:02d}'.format(\
                    variable['name'], variable['hour_start'], variable['hour_end'], domain['name'],\
                    stat_processing['member'])
    else:
        plot_name = 'iconeueps_{}_stats_{}_{:03d}-{:03d}h_{}'.format(\
                    variable['name'], stat_processing['method'], variable['hour_start'], variable['hour_end'],\
                    domain['name'])

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


    elif colorpalette_source == 'hclwizard':
        filename = 'colorscale_hclwizard_tot_prec_stat_YlBl.txt'
        with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
            lines = f.readlines()

        hex_colors = []
        for line in lines:
            hex_colors.append(line[2:8])

        custom_palette_list = [[255, 255, 255]]           # extra color for correct LabelBar view
        custom_palette_list.append([255, 255, 255])     # color for 1% category
        for hex_color in hex_colors[:]:
            rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
            custom_palette_list.append(rgb_color)
        custom_palette_list.append(custom_palette_list[-1])     # extra color for correct LabelBar view

    custom_palette = np.array(custom_palette_list) / 255

    ########################################################################

    x_resolution        = 800
    y_resolution        = 800
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution
    wks_res.wkColorMap  = custom_palette

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
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
    resources.cnMissingValFillColor = 'black'

    if variable['name'] == 'tot_prec_24h':
        resources.cnFillPalette         = custom_palette
        resources.cnLevelSelectionMode  = 'ExplicitLevels'
        resources.cnLevels              = np.arange(0, 21, 0.5)

        resources.lbLabelStride         = 4
        resources.lbTitleString         = 'mm'

        if stat_processing['method'] == 'spread':
            resources.cnFillPalette         = 'WhiteYellowOrangeRed'
            minlevel                        = 0.0
            maxlevel                        = 10.0
            resources.lbLabelStride         = 25
            resources.lbTitleString         = 'mm'

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

    resources.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
    #resources.cnExplicitLabelBarLabelsOn = True
    #resources.pmLabelBarDisplayMode =  'Always'
    resources.pmLabelBarWidthF      = 0.10
    #resources.lbLabelStrings        = label_str_list
    resources.lbLabelFontHeightF    = 0.012
    #resources.lbBoxCount            = 40
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleFontHeightF    = 0.012
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    resources.lbTitleAngleF         = 90.0
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

    if stat_processing['method'] == 'member_extract':
        member_text = 'member {:d}'.format(stat_processing['member'])
    elif stat_processing['method'] == 'max':
        member_text = 'maximum of all 40 members per gridpoint'
    elif stat_processing['method'] == 'min':
        member_text = 'minimum of all 40 members per gridpoint'
    elif stat_processing['method'] == 'median':
        member_text = 'median of all 40 members per gridpoint'
    elif stat_processing['method'] == '10p':
        member_text = '10-percentile of all 40 members per gridpoint'
    elif stat_processing['method'] == '90p':
        member_text = '90-percentile of all 40 members per gridpoint'

    if variable['name'] == 'tot_prec_24h':
        run_time = datetime.datetime(run['year'], run['month'], run['day'], run['hour'])
        timeshift = get_timeshift()
        if timeshift == 1:
            time_code = 'CET'                           # UTC+1
        elif timeshift == 2:
            time_code = 'CEST'                          # UTC+2
        run_time = run_time + datetime.timedelta(0, 3600 * int(timeshift))
        valid_time = run_time + datetime.timedelta(0, 3600 * int(variable['hour_start'] + 12))

        text1 = '24h-precipitation, {}'.format(member_text)
        text2 = 'Initial time: {}, {:02}{}'.format(run_time.strftime('%a., %d %b. %Y'), run_time.hour, time_code)
        text3 = 'Valid time: {}'.format(valid_time.strftime('%a., %d %b. %Y'))
        text4 = 'Model: ICON-EU-EPS, Forecast time: {}-{}h'.format(variable['hour_start'], variable['hour_end'])

    text_res_1 = Ngl.Resources()
    text_res_1.txJust           = 'BottomLeft'

    text_res_1.txFontHeightF    = 0.016
    if stat_processing['method'] == 'member_extract':
        x = 0.30
    else:
        x = 0.13
    y = 0.965
    Ngl.text_ndc(wks, text1, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.014
    x = 0.025
    y = 0.93
    Ngl.text_ndc(wks, text2, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.014
    x = 0.575
    y = 0.93
    Ngl.text_ndc(wks, text3, x, y, text_res_1)

    text_res_1.txFontHeightF    = 0.014
    x = 0.025
    y = 0.192
    Ngl.text_ndc(wks, text4, x, y, text_res_1)


    Ngl.frame(wks)
    Ngl.destroy(wks)

    del data_tot_prec, data_tot_prec_timespan, data_processed, vlat, vlon, clat, clon

    return

########################################################################
########################################################################
########################################################################

def plot_prob_of_exc(path, run, hours, data_array, data_array2, variable, domain, model, stat_processing, plot_type):

    # calculated probabilities of variables #

    if variable['name'] == 'tot_prec_24h' or variable['name'] == 'tot_prec_48h':
        data_tot_prec_timespan = data_array[hours.index(variable['hour_end']), :, :]\
                                - data_array[hours.index(variable['hour_start']), :, :]
        data_processed = np.where(data_tot_prec_timespan >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'acc_prec':
        data_tot_prec_timespan = data_array[hours.index(variable['hour']), :, :]\
                                - data_array[0, :, :]
        data_processed = np.where(data_tot_prec_timespan >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 't_850hpa':
        data_t_850hpa_hour = data_array[hours.index(variable['hour']), :, :] - 273.15
        data_processed = np.where(data_t_850hpa_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'mslp':
        filename_topo = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121312_hsurf.grib2'
        with open(path['base'] + path['topo'] + filename_topo,'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            topo_hgt_field = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        topo_hgt = np.tile(topo_hgt_field,(40,1))
        data_mslp_hour = data_array[hours.index(variable['hour']), :, :] * 0.01\
                         * np.exp(9.80665*topo_hgt/(287.05*data_array2[hours.index(variable['hour']), :, :]))
        data_processed = np.where(data_mslp_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'wind_10m':
        data_wind10m_hour = np.sqrt(data_array[hours.index(variable['hour']), :, :]**2\
                                    + data_array2[hours.index(variable['hour']), :, :]**2) * 3.6
        data_processed = np.where(data_wind10m_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'wind_300hpa':
        data_wind10m_hour = np.sqrt(data_array[hours.index(variable['hour']), :, :]**2\
                                    + data_array2[hours.index(variable['hour']), :, :]**2) * 3.6
        data_processed = np.where(data_wind10m_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'gph_500hpa':
        data_gph_500hpa_hour = data_array[hours.index(variable['hour']), :, :] / 98.0665
        data_processed = np.where(data_gph_500hpa_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'gph_300hpa':
        data_gph_500hpa_hour = data_array[hours.index(variable['hour']), :, :] / 98.0665
        data_processed = np.where(data_gph_500hpa_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if variable['name'] == 'tqv':
        data_tqv_hour = data_array[hours.index(variable['hour']), :, :]
        data_processed = np.where(data_tqv_hour >= stat_processing['threshold'], 1, 0).sum(axis=0) / 40 * 100

    if plot_type == 'labelBar1':
        data_processed *= (40 / 100)    # plot number of members, not percentage
    data_processed += 0.1


    # load grid information #

    if model == 'icon-eu-eps':
        mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    elif model == 'icon-global-eps':
        mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0024_R02B06_G.nc', 'r')

    vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = mpi_file.variables['clat'][:].data * 180./np.pi
    clon = mpi_file.variables['clon'][:].data * 180./np.pi
    mpi_file.close()


    # set plotname #

    if model == 'icon-eu-eps':
        model_acr = 'iconeueps'
    elif model == 'icon-global-eps':
        model_acr = 'iconglobaleps'

    if variable['name'] == 'tot_prec_24h'\
     or variable['name'] == 'tot_prec_48h':
        if stat_processing['threshold'] >= 1.0:
            threshold_str = '{:03d}'.format(int(stat_processing['threshold']))
        else:
            threshold_str = '{:.1f}'.format(stat_processing['threshold'])
        plot_name = '{}_{}_{}_{}{}_{:03d}-{:03d}h_{}_{}'.format(
                     model_acr, stat_processing['method'], variable['name'], threshold_str, variable['unit'],
                     variable['hour_start'], variable['hour_end'], domain['name'], plot_type)
    elif variable['name'] == 'acc_prec':
        if stat_processing['threshold'] >= 1.0:
            threshold_str = '{:03d}'.format(int(stat_processing['threshold']))
        else:
            threshold_str = '{:.1f}'.format(stat_processing['threshold'])
        plot_name = '{}_{}_{}_{:.0f}{}_{:03d}h_{}_{}'.format(
                     model_acr, stat_processing['method'], variable['name'], stat_processing['threshold'],
                     variable['unit'], variable['hour'], domain['name'], plot_type)
    else:
        plot_name = '{}_{}_{}_{:.0f}{}_{:03d}h_{}_{}'.format(
                     model_acr, stat_processing['method'], variable['name'], threshold_str,
                     variable['unit'], variable['hour'], domain['name'], plot_type)


    # load colormap #

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
        filename = 'colorscale_hclwizard_tot_prec_prob_4.txt'
        with open(path['base'] + path['colorpalette'] + filename, 'r') as f:
            lines = f.readlines()

        hex_colors = []
        for line in lines:
            hex_colors.append(line[2:8])

        custom_palette_list = [[ 0, 255,  0]]           # extra color for correct LabelBar view
        custom_palette_list.append([255, 255, 255])     # color for 0% category
        for hex_color in hex_colors[:]:
            rgb_color = [int(hex_str, 16) for hex_str in [hex_color[:2], hex_color[2:4], hex_color[4:]]]
            custom_palette_list.append(rgb_color)
        custom_palette_list.append([255,   0,   0])     # extra color for correct LabelBar view

        custom_palette = np.array(custom_palette_list)

    custom_palette = custom_palette / 255
    #print(custom_palette.shape)


    # begin plot settings #

    if plot_type == 'small_map_only':
        x_resolution        = 360
        y_resolution        = 360
    else:
        x_resolution        = 800
        y_resolution        = 800
    wks_res             = Ngl.Resources()
    wks_res.wkWidth     = x_resolution
    wks_res.wkHeight    = y_resolution
    wks_res.wkColorMap  = custom_palette

    wks_type    = 'png'
    wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
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
    if plot_type == 'small_map_only':
        resources.vpXF          = 0.00
        resources.vpYF          = 1.00
        resources.vpWidthF      = 1.00
        resources.vpHeightF     = 1.00
    elif plot_type == 'labelBar1' or plot_type == 'labelBar2':
        resources.vpXF          = 0.00
        resources.vpYF          = 1.00
        resources.vpWidthF      = 1.00
        resources.vpHeightF     = 0.70
    else:
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

    resources.cnConstFEnableFill    = True
    resources.cnConstFLabelOn       = False
    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = custom_palette
    resources.cnLevelSelectionMode  = 'ExplicitLevels'
    if plot_type == 'labelBar1':
        resources.cnLevels              = np.arange(0, 41.5, 1.0)
    elif plot_type == 'labelBar2':
        resources.cnLevels              = np.arange(0, 103, 2.5)
    else:
        resources.cnLevels              = np.arange(0, 103, 2.5)

    #minlevel                        = 0.0
    #maxlevel                        = 100.0
    #numberoflevels                  = 40
    #resources.cnMinLevelValF        = minlevel
    #resources.cnMaxLevelValF        = maxlevel
    #resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

    # Turn off contour lines and labels:
    resources.cnLinesOn         = False
    resources.cnLineLabelsOn    = False

    # Set resources for a nice label bar
    if plot_type == 'small_map_only' or plot_type == 'text':
        resources.lbLabelBarOn          = False
    elif plot_type == 'labelBar1':
        resources.lbLabelBarOn          = True
        resources.lbAutoManage          = False
        resources.lbOrientation         = 'horizontal'
        resources.lbLeftMarginF         = -0.03     # def: 0.05, fraction of length of the minor labelbar axis
        resources.lbRightMarginF        = 0.03      # def: 0.05, fraction of length of the minor labelbar axis

        resources.lbLabelOffsetF        = 0.10      # def: 0.01, fraction of length of the minor labelbar axis
        resources.lbBoxMinorExtentF     = 0.35      # def: 0.33, fraction of length of the minor labelbar axis
        resources.pmLabelBarWidthF      = 0.66      # def: 0.60 if horizontal
        resources.pmLabelBarHeightF     = 0.08      # def: 0.15 if horizontal
 
        resources.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
        resources.lbLabelStride         = 5
        resources.lbLabelFontHeightF    = 0.012     # def: 0.02
        resources.lbBoxSeparatorLinesOn = False
        resources.lbBoxLineThicknessF   = 4.0
        resources.lbLabelAlignment      = 'BoxCenters'

        resources.lbTitleString         = 'Number of Members'
        resources.lbTitleFontHeightF    = 0.012     # def: 0.025
        resources.lbTitlePosition       = 'Bottom'
        #resources.lbTitleDirection      = 'Across'
        #resources.lbTitleAngleF         = 90.0
        #resources.lbTitleExtentF        = 0.1
        #resources.lbTitleOffsetF        = 0.0
    elif plot_type == 'labelBar2':
        resources.lbLabelBarOn          = True
        resources.lbAutoManage          = False
        resources.lbOrientation         = 'horizontal'
        resources.lbLeftMarginF         = 0.0       # def: 0.05, fraction of length of the minor labelbar axis
        resources.lbRightMarginF        = 0.0       # def: 0.05, fraction of length of the minor labelbar axis

        resources.lbLabelOffsetF        = 0.10      # def: 0.01, fraction of length of the minor labelbar axis
        resources.lbBoxMinorExtentF     = 0.35      # def: 0.33, fraction of length of the minor labelbar axis
        resources.pmLabelBarWidthF      = 0.66      # def: 0.60 if horizontal
        resources.pmLabelBarHeightF     = 0.08      # def: 0.15 if horizontal
 
        resources.cnLabelBarEndStyle    = 'ExcludeOuterBoxes'
        resources.lbLabelStride         = 4
        resources.lbLabelFontHeightF    = 0.012     # def: 0.02
        resources.lbBoxSeparatorLinesOn = False
        resources.lbBoxLineThicknessF   = 4.0
        resources.lbLabelAlignment      = 'BoxCenters'

        resources.lbTitleString         = '% of Members'
        resources.lbTitleFontHeightF    = 0.012     # def: 0.025
        resources.lbTitlePosition       = 'Bottom'
        #resources.lbTitleDirection      = 'Across'
        #resources.lbTitleAngleF         = 90.0
        #resources.lbTitleExtentF        = 0.1      # def: 0.15
        resources.lbTitleOffsetF        = 0.05      # def: 0.03
    else:
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
        resources.lbLabelFontHeightF    = 0.012
        #resources.lbBoxCount            = 40
        resources.lbBoxSeparatorLinesOn = False
        resources.lbBoxLineThicknessF   = 4.0
        #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
        resources.lbLabelAlignment      = 'BoxCenters'

        resources.lbTitleString         = '%'
        resources.lbTitleFontHeightF    = 0.012
        resources.lbTitlePosition       = 'Right'
        resources.lbTitleDirection      = 'Across'
        #resources.lbTitleAngleF         = 90.0
        resources.lbTitleExtentF        = 0.1
        resources.lbTitleOffsetF        = 0.0


    resources.nglFrame = False
    #Ngl.draw_colormap(wks)
    plot = Ngl.contour_map(wks, data_processed, resources)


    # plot texts #

    if plot_type == 'small_map_only':

        # map thresholds #

        if variable['name'] == 'tot_prec_24h'\
         or variable['name'] == 'tot_prec_48h'\
         or variable['name'] == 'acc_prec':
            if stat_processing['threshold'] >= 1.0:
                threshold_str = '{:d}'.format(int(stat_processing['threshold']))
            else:
                threshold_str = '{:.1f}'.format(stat_processing['threshold'])
            unit_str = 'mm'
        elif variable['name'] == 't_850hpa':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = '~S~o~N~C'
        elif variable['name'] == 'mslp':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'hPa'
        elif variable['name'] == 'wind_10m':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'km/h'
        elif variable['name'] == 'wind_300hpa':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'km/h'
        elif variable['name'] == 'gph_500hpa':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'gpdm'
        elif variable['name'] == 'gph_300hpa':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'gpdm'
        elif variable['name'] == 'tqv':
            threshold_str = '{:.0f}'.format(stat_processing['threshold'])
            unit_str = 'mm'

        text1 = 'More than {}{}'.format(threshold_str, unit_str)

        text_res_1 = Ngl.Resources()
        text_res_1.txJust           = 'BottomLeft'

        text_res_1.txFontHeightF    = 0.032
        if stat_processing['threshold'] == 0.1:
            x = 0.33
        else:
            if variable['name'] == 'mslp'\
             or variable['name'] == 'wind_10m'\
             or variable['name'] == 'wind_300hpa'\
             or variable['name'] == 'gph_500hpa'\
             or variable['name'] == 'gph_300hpa':
                x = 0.31
            else:
                x = 0.36
        y = 0.95
        Ngl.text_ndc(wks, text1, x, y, text_res_1)

    elif plot_type == 'labelBar1' or plot_type == 'labelBar2':
        pass

    elif plot_type == 'text':

        # 2x2 plot title #

        if variable['name'] == 'tot_prec_24h':
                text1 = 'Probability of exceedance: 24h-precipitation'
        elif variable['name'] == 'tot_prec_48h':
                text1 = 'Probability of exceedance: 48h-precipitation'
        elif variable['name'] == 'acc_prec':
                text1 = 'Probability of exceedance: accumulated precipitation'
        elif variable['name'] == 't_850hpa':
            text1 = 'Probability of exceedance: 850hPa-temperature'
        elif variable['name'] == 'mslp':
            text1 = 'Probability of exceedance: mean sea level pressure'
        elif variable['name'] == 'wind_10m':
            text1 = 'Probability of exceedance: 10m-wind speed'
        elif variable['name'] == 'wind_300hpa':
            text1 = 'Probability of exceedance: 300hPa-wind speed'
        elif variable['name'] == 'gph_500hpa':
            text1 = 'Probability of exceedance: 500hPa-geopotential height'
        elif variable['name'] == 'gph_300hpa':
            text1 = 'Probability of exceedance: 300hPa-geopotential height'
        elif variable['name'] == 'tqv':
            text1 = 'Probability of exceedance: total column water vapour'


        # initial, valid and forecast time texts #

        run_time = datetime.datetime(run['year'], run['month'], run['day'], run['hour'])

        if domain['name'] == 'central_argentina':
            time_code = 'UTC'
        else:
            timeshift = get_timeshift()
            if timeshift == 1:
                time_code = 'CET'                           # UTC+1
            elif timeshift == 2:
                time_code = 'CEST'                          # UTC+2
            run_time = run_time + datetime.timedelta(0, 3600 * int(timeshift))

        text2 = 'Initial time: {}, {:02}{}'.format(
                 run_time.strftime('%a., %d %b. %Y'), run_time.hour, time_code)

        if model == 'icon-eu-eps':
            model_text = 'ICON-EU-EPS'
        elif model == 'icon-global-eps':
            model_text = 'ICON-Global-EPS'

        if variable['name'] == 'tot_prec_24h'\
         or variable['name'] == 'tot_prec_48h':
            valid_time_start = run_time + datetime.timedelta(0, 3600 * int(variable['hour_start']))
            valid_time_end = run_time + datetime.timedelta(0, 3600 * int(variable['hour_end']))
            text3 = 'Valid:   From {}, {:02}{}'.format(
                     valid_time_start.strftime('%a., %d %b. %Y'), valid_time_start.hour, time_code)
            text5 = 'To {}, {:02}{}'.format(
                     valid_time_end.strftime('%a., %d %b. %Y'), valid_time_end.hour, time_code)
            text4 = 'Model: {} from DWD (40 Members), Forecast time: {}-{}h'.format(
                     model_text, variable['hour_start'], variable['hour_end'])

        elif variable['name'] == 'acc_prec'\
         or variable['name'] == 't_850hpa'\
         or variable['name'] == 'mslp'\
         or variable['name'] == 'wind_10m'\
         or variable['name'] == 'wind_300hpa'\
         or variable['name'] == 'gph_500hpa'\
         or variable['name'] == 'gph_300hpa'\
         or variable['name'] == 'tqv':
            valid_time = run_time + datetime.timedelta(0, 3600 * int(variable['hour']))
            text3 = 'Valid time: {}, {:02}{}'.format(
                     valid_time.strftime('%a., %d %b. %Y'), valid_time.hour, time_code)
            text4 = 'Model: {} from DWD (40 Members), Forecast time: {}h'.format(
                     model_text, variable['hour'])

        text_res_1 = Ngl.Resources()
        text_res_1.txJust           = 'BottomLeft'

        text_res_1.txFontHeightF    = 0.016
        x = 0.16
        y = 0.965
        Ngl.text_ndc(wks, text1, x, y, text_res_1)

        text_res_1.txFontHeightF    = 0.014
        x = 0.025
        y = 0.93
        Ngl.text_ndc(wks, text2, x, y, text_res_1)

        x = 0.575
        y = 0.93
        Ngl.text_ndc(wks, text3, x, y, text_res_1)

        x = 0.025
        y = 0.192
        Ngl.text_ndc(wks, text4, x, y, text_res_1)

        if variable['name'] == 'tot_prec_24h'\
         or variable['name'] == 'tot_prec_48h':
            x = 0.70
            y = 0.192
            Ngl.text_ndc(wks, text5, x, y, text_res_1)

        del text_res_1

    else:
        run_time = datetime.datetime(run['year'], run['month'], run['day'], run['hour'])
        timeshift = get_timeshift()
        if timeshift == 1:
            time_code = 'CET'                           # UTC+1
        elif timeshift == 2:
            time_code = 'CEST'                          # UTC+2
        run_time = run_time + datetime.timedelta(0, 3600 * int(timeshift))

        if stat_processing['threshold'] >= 1.0:
            threshold_str = '{:d}'.format(int(stat_processing['threshold']))
        else:
            threshold_str = '{:.1f}'.format(stat_processing['threshold'])
        text1 = 'Probability of exceedance: 24h-precipitation over {}mm'.format(threshold_str)

        text2 = 'Initial time: {}, {:02}{}'.format(run_time.strftime('%a., %d %b. %Y'), run_time.hour, time_code)
        if variable['name'] == 'tot_prec_24h':
            valid_time = run_time + datetime.timedelta(0, 3600 * int(variable['hour_start'] + 12))
            text3 = 'Valid time: {}'.format(valid_time.strftime('%a., %d %b. %Y'))
            text4 = 'Model: ICON-EU-EPS (40 Members), Forecast time: {}-{}h'.format(
                     variable['hour_start'], variable['hour_end'])
        if variable['name'] == 't_850hpa' or variable['name'] == 'mslp' or variable['name'] == 'wind_10m' :
            valid_time = run_time + datetime.timedelta(0, 3600 * int(variable['hour']))
            text3 = 'Valid time: {}, {:02}{}'.format(valid_time.strftime('%a., %d %b. %Y'), valid_time.hour, time_code)
            text4 = 'Model: ICON-EU-EPS (40 Members), Forecast time: {}h'.format(variable['hour'])

        text_res_1 = Ngl.Resources()
        text_res_1.txJust           = 'BottomLeft'

        text_res_1.txFontHeightF    = 0.016
        x = 0.16
        y = 0.965
        Ngl.text_ndc(wks, text1, x, y, text_res_1)

        text_res_1.txFontHeightF    = 0.014
        x = 0.025
        y = 0.93
        Ngl.text_ndc(wks, text2, x, y, text_res_1)

        text_res_1.txFontHeightF    = 0.014
        x = 0.575
        y = 0.93
        Ngl.text_ndc(wks, text3, x, y, text_res_1)

        text_res_1.txFontHeightF    = 0.014
        x = 0.025
        y = 0.192
        Ngl.text_ndc(wks, text4, x, y, text_res_1)
        del text_res_1


    Ngl.frame(wks)
    Ngl.destroy(wks)

    del data_array, data_processed, vlat, vlon, clat, clon

    return
