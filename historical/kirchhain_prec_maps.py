
import numpy as np
import eccodes
import netCDF4 as nc
import Ngl
import os
from contextlib import ExitStack

def main():

    #point = dict(lat = 49.014, lon =  8.404, name = 'Karlsruhe')
    point = dict(lat = 50.822, lon =  8.920, name = 'Kirchhain')
    #point = dict(lat = 65.661, lon =-18.718, name = 'Iceland')


    path = dict(base = '/lsdfos/kit/imk-tro/projects/MOD/Gruppe_Knippertz/nw5893/',
                data = 'forecast_archive/pamore/kirchhain/run_12Z/',
                grid = 'forecast_archive/icon-eu-eps/grid/',
                plots = 'plots/kirchhain/run_12Z/')

    data_rain_gsp_sum = np.empty((25, 40, 75948))
    data_rain_con_sum = np.empty((25, 40, 75948))
    hours = list(range(0, 12+1))

    filenames_all = []
    for hour in hours:
        filenames_all.append(['iefff0{:03d}0000.m0{:02d}'.format(hour, member) for member in range(1, 41)])

    with ExitStack() as stack:
        files_all = [[stack.enter_context(open(path['base'] + path['data'] + filename,'rb'))\
          for filename in filenames_of_one_hour] for filenames_of_one_hour in filenames_all]

        for i, files_of_one_hour in enumerate(files_all):
            for j, file in enumerate(files_of_one_hour):
                grib_id = eccodes.codes_grib_new_from_file(file)
                data_rain_gsp_sum[i - hours[0], j, :] = eccodes.codes_get_array(grib_id, 'values')
                grib_id = eccodes.codes_grib_new_from_file(file)
                data_rain_con_sum[i - hours[0], j, :] = eccodes.codes_get_array(grib_id, 'values')
                eccodes.codes_release(grib_id)
    data_rain_tot_sum = data_rain_gsp_sum + data_rain_con_sum
    del data_rain_gsp_sum, data_rain_con_sum, files_all

    print(data_rain_tot_sum.max(axis=1).max(axis=1))
    print('data_rain_tot_sum: {:.0f}MB'.format(data_rain_tot_sum.nbytes / 1e6))

    stat_processing = 'max'
    member = None
    plot_rain_around_point(path, data_rain_tot_sum, 0, 12, point, stat_processing, member)

    '''stat_processing = 'member_extract'
    for member in range(1,41):
        plot_rain_around_point(path, data_rain_tot_sum, 0, 24, point, stat_processing, member)'''

    return

########################################################################
########################################################################
########################################################################

def plot_rain_around_point(path, data_rain_tot_sum, hour_start, hour_end, point, stat_processing, member):

    if stat_processing == 'max':
        data_processed = (data_rain_tot_sum[hour_end, :, :] - data_rain_tot_sum[hour_start, :, :]).max(axis=0)
    elif stat_processing == 'member_extract':
        data_processed = data_rain_tot_sum[hour_end, member-1, :] - data_rain_tot_sum[hour_start, member-1, :]


    ########################################################################

    if stat_processing == 'max':
        member_text_filename = 'max'
    elif stat_processing == 'member_extract':
        member_text_filename = 'm{:02d}'.format(member)
    plot_name = 'iconeueps_rain_{}_{:02d}Z-{:02d}Z_{}'.format(\
                    point['name'], hour_start+12, hour_end+12, member_text_filename)

    mpi_file = nc.Dataset(path['base'] + path['grid'] + 'icon_grid_0028_R02B07_N02.nc', 'r')
    vlat = mpi_file.variables['clat_vertices'][:].data * 180./np.pi
    vlon = mpi_file.variables['clon_vertices'][:].data * 180./np.pi
    clat = mpi_file.variables['clat'][:].data * 180./np.pi
    clon = mpi_file.variables['clon'][:].data * 180./np.pi
    mpi_file.close()

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

    radius = 500    # image radius in km around centered point
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
    resources.cnCellFillEdgeColor   = 'black'

    resources.cnMissingValFillColor = 'black'
    resources.cnFillPalette         = 'WhiteBlueGreenYellowRed'
    resources.cnLevelSelectionMode  = 'ManualLevels'

    minlevel                        = 0.0
    maxlevel                        = 50.0
    numberoflevels                  = 250
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

    resources.lbLabelStride         = 25
    resources.lbLabelFontHeightF    = 0.02
    resources.lbBoxSeparatorLinesOn = False
    resources.lbBoxLineThicknessF   = 4.0
    #resources.lbBoxEndCapStyle     = 'TriangleBothEnds'
    resources.lbLabelAlignment      = 'BoxCenters'

    resources.lbTitleString         = 'mm'
    resources.lbTitleFontHeightF    = 0.02
    resources.lbTitlePosition       = 'Right'
    resources.lbTitleDirection      = 'Across'
    resources.lbTitleAngleF         = 90.0
    resources.lbTitleExtentF        = 0.1
    resources.lbTitleOffsetF        = 0.0

    resources.nglFrame = False
    plot = Ngl.contour_map(wks, data_processed, resources)

    ########################################################################

    polymarker_res_1 = Ngl.Resources()
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
    Ngl.polymarker(wks, plot, point['lon'], point['lat'], polymarker_res_2)

    ########################################################################

    if stat_processing == 'max':
        member_text = 'max member of each cell'
    elif stat_processing == 'member_extract':
        member_text = 'member {:d}'.format(member)
    text = 'rain_gsp + rain_con,  07.08.19  {}Z-{}Z, {}'.format(hour_start+12, hour_end+12, member_text)
    x = 0.1
    y = 0.95

    text_res_1 = Ngl.Resources()
    text_res_1.txFontHeightF    = 0.02
    text_res_1.txJust           = 'BottomLeft'

    Ngl.text_ndc(wks, text, x, y, text_res_1)

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
