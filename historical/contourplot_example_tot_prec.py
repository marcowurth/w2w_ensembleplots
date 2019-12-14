
import numpy as np
import eccodes
import netCDF4 as nc
import Ngl

def main():

########################################################################
###  settings                                                        ###
########################################################################

    ##### set base path and subpaths of input data and output #####

    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                data = 'forecast_archive/icon-eu-eps/raw_grib/',
                grid = 'forecast_archive/icon-eu-eps/grid/',
                plots = 'plots/experimental/contourplots/europe/')


    ##### set date of forecast run, forecast hour and variable, statistical processing method #####

    date = dict(year = 2019, month = 8, day = 20, hour = 12)
    fcst_hours = [84, 108]
    variable = 'tot_prec'
    stat_processing_methods = ['min', '10p', '25p', '50p', '75p', '90p', 'max']

    plot_contourmap(path, date, fcst_hours, variable, stat_processing_methods)

    return


########################################################################
###  main plotting function                                          ###
########################################################################

def plot_contourmap(path, date, fcst_hours, variable, stat_processing_methods):

    ##### generate subpath and filename #####

    subpath = 'run_{}{:02}{:02}{:02}/{}/'.format(\
                    date['year'], date['month'], date['day'], date['hour'], variable)

    filename1 = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                    date['year'], date['month'], date['day'], date['hour'], fcst_hours[0], variable)

    filename2 = 'icon-eu-eps_europe_icosahedral_single-level_{}{:02}{:02}{:02}_{:03}_{}.grib2'.format(\
                    date['year'], date['month'], date['day'], date['hour'], fcst_hours[1], variable)


########################################################################
###  read data                                                       ###
########################################################################

    ##### create empty numpy arrays #####
    ##### 2 fcst_hours, 40 members, 75948 eu gridpoints #####

    data_raw = np.empty((2, 40, 75948))
    data_members = np.empty((40, 75948))


    ##### every time in loop open next grib msg from grib file #####
    ##### grib messages in dwd file are sorted by increasing member number #####

    with open(path['base'] + path['data'] + subpath + filename1,'rb') as file:
        for member in range(1,41):
            print('read data from member {}'.format(member))
            grib_msg_id = eccodes.codes_grib_new_from_file(file)
            data_raw[0, member - 1, :] = eccodes.codes_get_array(grib_msg_id, 'values')
            eccodes.codes_release(grib_msg_id)
    with open(path['base'] + path['data'] + subpath + filename2,'rb') as file:
        for member in range(1,41):
            print('read data from member {}'.format(member))
            grib_msg_id = eccodes.codes_grib_new_from_file(file)
            data_raw[1, member - 1, :] = eccodes.codes_get_array(grib_msg_id, 'values')
            eccodes.codes_release(grib_msg_id)


    ##### take the difference of the two accumulated total precipitation arrays #####

    data_members = data_raw[1, :, :] - data_raw[0, :, :]
    del data_raw


    ##### open icon-eps grid file #####

    icongrid_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    vlat = icongrid_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = icongrid_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = icongrid_file.variables['clat'][:].data * 180./np.pi
    clon = icongrid_file.variables['clon'][:].data * 180./np.pi
    icongrid_file.close()


    for stat_processing in stat_processing_methods:

########################################################################
###  statistically process data                                      ###
########################################################################

        if stat_processing == 'mean':
            data_processed = data_members.mean(axis=0)
        elif stat_processing == 'max':
            data_processed = data_members.max(axis=0)
        elif stat_processing == 'min':
            data_processed = data_members.min(axis=0)
        elif stat_processing == '90p':
            data_processed = np.percentile(data_members, 90, axis=0)
        elif stat_processing == '75p':
            data_processed = np.percentile(data_members, 75, axis=0)
        elif stat_processing == '50p':
            data_processed = np.percentile(data_members, 50, axis=0)
        elif stat_processing == '25p':
            data_processed = np.percentile(data_members, 25, axis=0)
        elif stat_processing == '10p':
            data_processed = np.percentile(data_members, 10, axis=0)

        #print('shape of data_members: {}'.format(np.shape(data_members)))
        #print('shape of data_processed: {}'.format(np.shape(data_processed)))


    ########################################################################
    ###  plot data on world map                                          ###
    ########################################################################

        ##### set domain due to center point and radius #####

        center_point = dict(lat = 48.5, lon =  9.0)
        radius = 1800    # domain radius in km around center_point

        domain = dict(
                        lat_min = center_point['lat'] - radius / 111.2,
                        lat_max = center_point['lat'] + radius / 111.2,
                        lon_min = center_point['lon'] - radius / (111.2 * np.cos(center_point['lat']*np.pi/180)),
                        lon_max = center_point['lon'] + radius / (111.2 * np.cos(center_point['lat']*np.pi/180)),
                        )


        ##### or set domain manually in deg N/E #####

        '''domain = dict(
                        lat_min = 0.0,
                        lat_max = 20.0,
                        lon_min = 0.0,
                        lon_max = 20.0,
                        )'''


        ##### set image size (should be squared) #####
        ##### plotting area in pyngl can not exceed squared area even if plotting on rectangular images #####
        ##### for obtaining rectangular plots on has to cut manually afterwards e.g. with pillow package #####

        x_resolution        = 800
        y_resolution        = 800
        wks_res             = Ngl.Resources()
        wks_res.wkWidth     = x_resolution
        wks_res.wkHeight    = y_resolution

        plot_name = 'contourplot_icon-eu-eps_tot_prec_{:02d}-{:02d}h_{}'.format(\
                        fcst_hours[0], fcst_hours[1], stat_processing)
        wks_type    = 'png'
        wks         = Ngl.open_wks(wks_type, path['base'] + path['plots'] + plot_name, wks_res)
        resources   = Ngl.Resources()   # create resources object containing all the plot settings

        resources.mpProjection = 'Hammer'   # projection type
        resources.mpCenterLonF = (domain['lon_max'] + domain['lon_min']) / 2    # projection center point
        resources.mpCenterLatF = (domain['lat_max'] + domain['lat_min']) / 2

        resources.mpLimitMode   = 'latlon'
        resources.mpMinLonF     = domain['lon_min']
        resources.mpMaxLonF     = domain['lon_max']
        resources.mpMinLatF     = domain['lat_min']
        resources.mpMaxLatF     = domain['lat_max']


        ##### set plot area #####

        resources.nglMaximize   = False
        resources.vpXF          = 0.05
        resources.vpYF          = 0.9
        resources.vpWidthF      = 0.7
        resources.vpHeightF     = 0.7


        ##### set all map plot settings #####

        resources.mpFillOn = True   # turn on filled map areas
        resources.mpFillColors = ['pink','blue','white','white'] # set colors for [FillValue, Ocean, Land , InlandWater]

        resources.mpDataBaseVersion         = 'MediumRes'   # quality of national borders
        resources.mpDataSetName             = 'Earth..4'
        resources.mpOutlineBoundarySets     = 'national'

        #resources.mpDataBaseVersion         = 'HighRes'
        #resources.mpDataResolution          = 'Fine'
        resources.mpGeophysicalLineThicknessF   = 7.0 * x_resolution / 1000     # keep borders thickness resolution-independent
        resources.mpNationalLineThicknessF      = 7.0 * x_resolution / 1000
        #resources.mpGridAndLimbDrawOrder        = 'postdraw'

        resources.mpGridAndLimbOn               = False     # turn off geographic coordinates grid
        #resources.mpLimbLineColor               = 'black'
        #resources.mpLimbLineThicknessF          = 10
        #resources.mpGridLineColor               = 'black'
        #resources.mpGridLineThicknessF          = 1.0
        #resources.mpGridSpacingF                = 1

        resources.mpPerimOn                     = True      # turn on perimeter around plot
        resources.mpPerimLineColor              = 'black'
        resources.mpPerimLineThicknessF         = 8.0 * x_resolution / 1000     # keep perimeter thickness resolution-independent

        resources.tmXBOn = False    # turn off location ticks around plot
        resources.tmXTOn = False
        resources.tmYLOn = False
        resources.tmYROn = False

        resources.sfDataArray       = data_processed    # data input file to plot
        resources.sfXArray          = clon              # array with cell center locations
        resources.sfYArray          = clat
        resources.sfXCellBounds     = vlon              # array with cell vertices locations
        resources.sfYCellBounds     = vlat
        resources.sfMissingValueV   = 9999              # in case you want to mask values

        resources.cnFillOn              = True
        resources.cnFillMode            = 'CellFill'
        #resources.cnCellFillEdgeColor   = 'black'      # uncomment this for plotting the cell edges

        resources.cnMissingValFillColor = 'black'
        resources.cnFillPalette         = 'WhiteBlueGreenYellowRed'     # color palette
        resources.cnLevelSelectionMode  = 'ManualLevels'

        minlevel                        = 0.0       # min level of colorbar
        maxlevel                        = 50.0      # max level of colorbar
        numberoflevels                  = 250       # number of levels of colorbar, max. 250 with this color palette
        resources.cnMinLevelValF        = minlevel
        resources.cnMaxLevelValF        = maxlevel
        resources.cnLevelSpacingF       = (maxlevel - minlevel) / numberoflevels

        resources.cnLinesOn         = False     # turn off contour lines
        resources.cnLineLabelsOn    = False     # turn off contour labels


        ##### set resources for a nice colorbar #####

        resources.lbLabelBarOn          = True
        resources.lbAutoManage          = False
        resources.lbOrientation         = 'vertical'
        resources.lbLabelOffsetF        = 0.05
        #resources.lbBoxMinorExtentF     = 0.2

        resources.lbLabelStride         = 25    # print a tick every 25 levels
        resources.lbLabelFontHeightF    = 0.016
        resources.lbBoxSeparatorLinesOn = False
        resources.lbBoxLineThicknessF   = 4.0
        #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
        resources.lbLabelAlignment      = 'BoxCenters'

        resources.lbTitleString         = 'mm'
        resources.lbTitleFontHeightF    = 0.016
        resources.lbTitlePosition       = 'Right'
        resources.lbTitleDirection      = 'Across'
        resources.lbTitleAngleF         = 90.0
        resources.lbTitleExtentF        = 0.1
        resources.lbTitleOffsetF        = -0.15


        resources.nglFrame = False      # hold on frame because will plot text afterwards on same plot
        Ngl.contour_map(wks, data_processed, resources)      # plot the actual plot


        ##### plot title text #####

        text = '{:02d}-{:02d}h Total Precipitation {}, ICON-EPS run {:02}.{:02}.{} {:02}Z'.format(\
                    fcst_hours[0], fcst_hours[1], stat_processing,\
                    date['day'], date['month'], date['year'], date['hour'])
        x = 0.5
        y = 0.95

        text_res_1 = Ngl.Resources()
        text_res_1.txFontHeightF    = 0.018
        text_res_1.txJust           = 'TopCenter'

        Ngl.text_ndc(wks, text, x, y, text_res_1)


        Ngl.frame(wks)      # advance frame
        Ngl.destroy(wks)    # delete workspace to free memory, relevant if plotting various plots in one script

        print('plotted "{}.png"'.format(plot_name))

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
