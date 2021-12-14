#########################################
###  container for various functions  ###
#########################################

import numpy as np
import xarray as xr
import eccodes
from astropy.io import ascii

from w2w_ensembleplots.core.grid_information_around_point import which_grid_point
from w2w_ensembleplots.core.grid_information_around_point import get_latlon_filter_distance
from w2w_ensembleplots.core.python_module_julian import calc_the_from_relhum


########################################################################
########################################################################
########################################################################

def read_forecast_data(model, grid, date, var, **kwargs):

    if var == 't_2m':
        varname1_lvtype = 'sl'
        varname1_folder = 't_2m'
        varname1_grib = 't_2m'
        if model == 'icon-eu-eps' and grid == 'latlon_0.2':
            varname1_cf = '2t'
        else:
            varname1_cf = 't2m'
    elif var == 'prec_rate':
        varname1_lvtype = 'sl'
        varname1_folder = 'tot_prec'
        varname1_grib = 'tot_prec'
        varname1_cf = 'tp'
    elif var == 'snow_rate':
        varname1_lvtype = 'sl'
        varname1_folder = 'snow_con'
        varname1_grib = 'snow_con'
        varname1_cf = 'csrwe'
        varname2_lvtype = 'sl'
        varname2_folder = 'snow_gsp'
        varname2_grib = 'snow_gsp'
        varname2_cf = 'lssrwe'
    elif var == 'prec_6h':
        varname1_lvtype = 'sl'
        varname1_folder = 'tot_prec'
        varname1_grib = 'tot_prec'
        varname1_cf = 'tp'
    elif var == 'prec_24h':
        varname1_lvtype = 'sl'
        varname1_folder = 'tot_prec'
        varname1_grib = 'tot_prec'
        varname1_cf = 'tp'
    elif var == 'prec_sum':
        varname1_lvtype = 'sl'
        varname1_folder = 'tot_prec'
        varname1_grib = 'tot_prec'
        varname1_cf = 'tp'
    elif var == 'wind_mean_10m':
        varname1_lvtype = 'sl'
        varname1_folder = 'u_10m'
        varname1_grib = 'u_10m'
        varname1_cf = 'u10'
        varname2_lvtype = 'sl'
        varname2_folder = 'v_10m'
        varname2_grib = 'v_10m'
        varname2_cf = 'v10'
    elif var == 'mslp':
        if model == 'icon-eu-eps':
            varname1_lvtype = 'sl'
            varname1_folder = 'ps'
            varname1_grib = 'ps'
            varname1_cf = 'sp'
            varname2_lvtype = 'sl'
            varname2_folder = 't_2m'
            varname2_grib = 't_2m'
            if grid == 'latlon_0.2':
                varname2_cf = '2t'
                filename_inv = 'icon-eu-eps_latlon_0.2_time-invariant_hsurf.nc'
            else:
                varname2_cf = 't2m'
                filename_inv = 'icon-eu-eps_europe_icosahedral_time-invariant_2021021700_hsurf.grib2'
        elif model == 'icon-eu-det' or model == 'icon-global-det':
            varname1_lvtype = 'sl'
            varname1_folder = 'pmsl'
            varname1_grib = 'pmsl'
            varname1_cf = 'prmsl'
    elif var == 'cape_ml':
        varname1_lvtype = 'sl'
        varname1_folder = 'cape_ml'
        varname1_grib = 'cape_ml'
        varname1_cf = 'CAPE_ML'
    elif var == 'clct':
        varname1_lvtype = 'sl'
        varname1_folder = 'clct'
        varname1_grib = 'clct'
        varname1_cf = 'CLCT'
    elif var == 'direct_rad':
        varname1_lvtype = 'sl'
        varname1_folder = 'aswdir_s'
        varname1_grib = 'aswdir_s'
        varname1_cf = 'ASWDIR_S'
    elif var == 'diffuse_rad':
        varname1_lvtype = 'sl'
        varname1_folder = 'aswdifd_s'
        varname1_grib = 'aswdifd_s'
        varname1_cf = 'ASWDIFD_S'
    elif var == 'vmax_10m':
        varname1_lvtype = 'sl'
        varname1_folder = 'vmax_10m'
        varname1_grib = 'vmax_10m'
        varname1_cf = 'gust'
    elif var == 'tqv':
        varname1_lvtype = 'sl'
        varname1_folder = 'tqv'
        varname1_grib = 'tqv'
        varname1_cf = 'tciwv'
    elif var == 'gph_300hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'fi_300hPa'
        varname1_grib = '300_fi'
        varname1_cf = 'z'
    elif var == 'gph_500hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'fi_500hPa'
        varname1_grib = '500_fi'
        varname1_cf = 'z'
    elif var == 'gph_700hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'fi_700hPa'
        varname1_grib = '700_fi'
        varname1_cf = 'z'
    elif var == 'gph_850hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'fi_850hPa'
        varname1_grib = '850_fi'
        varname1_cf = 'z'
    elif var == 't_850hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 't_850hPa'
        varname1_grib = '850_t'
        varname1_cf = 't'
    elif var == 'theta_e_850hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 't_850hPa'
        varname1_grib = '850_t'
        varname1_cf = 't'
        varname2_lvtype = 'pl'
        varname2_folder = 'relhum_850hPa'
        varname2_grib = '850_relhum'
        varname2_cf = 'r'
    elif var == 'wind_850hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'u_850hPa'
        varname1_grib = '850_u'
        varname1_cf = 'u'
        varname2_lvtype = 'pl'
        varname2_folder = 'v_850hPa'
        varname2_grib = '850_v'
        varname2_cf = 'v'
    elif var == 'wind_500hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'u_500hPa'
        varname1_grib = '500_u'
        varname1_cf = 'u'
        varname2_lvtype = 'pl'
        varname2_folder = 'v_500hPa'
        varname2_grib = '500_v'
        varname2_cf = 'v'
    elif var == 'wind_300hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'u_300hPa'
        varname1_grib = '300_u'
        varname1_cf = 'u'
        varname2_lvtype = 'pl'
        varname2_folder = 'v_300hPa'
        varname2_grib = '300_v'
        varname2_cf = 'v'
    elif var == 'shear_0-6km':
        varname1_lvtype = 'sl'
        varname1_folder = 'u_10m'
        varname1_grib = 'u_10m'
        varname1_cf = 'u10'
        varname2_lvtype = 'sl'
        varname2_folder = 'v_10m'
        varname2_grib = 'v_10m'
        varname2_cf = 'v10'
        varname3_lvtype = 'pl'
        varname3_folder = 'u_500hPa'
        varname3_grib = '500_u'
        varname3_cf = 'u'
        varname4_lvtype = 'pl'
        varname4_folder = 'v_500hPa'
        varname4_grib = '500_v'
        varname4_cf = 'v'
        if grid == 'latlon_0.1':
            varname1_cf = '10u'
            varname2_cf = '10v'
    elif var == 'shear_200-850hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 'u_200hPa'
        varname1_grib = '200_u'
        varname1_cf = 'u'
        varname2_lvtype = 'pl'
        varname2_folder = 'v_200hPa'
        varname2_grib = '200_v'
        varname2_cf = 'v'
        varname3_lvtype = 'pl'
        varname3_folder = 'u_850hPa'
        varname3_grib = '850_u'
        varname3_cf = 'u'
        varname4_lvtype = 'pl'
        varname4_folder = 'v_850hPa'
        varname4_grib = '850_v'
        varname4_cf = 'v'
    elif var == 'lapse_rate_850hPa-500hPa':
        varname1_lvtype = 'pl'
        varname1_folder = 't_850hPa'
        varname1_grib = '850_t'
        varname1_cf = 't'
        varname2_lvtype = 'pl'
        varname2_folder = 'fi_850hPa'
        varname2_grib = '850_fi'
        varname2_cf = 'z'
        varname3_lvtype = 'pl'
        varname3_folder = 't_500hPa'
        varname3_grib = '500_t'
        varname3_cf = 't'
        varname4_lvtype = 'pl'
        varname4_folder = 'fi_500hPa'
        varname4_grib = '500_fi'
        varname4_cf = 'z'
    elif var == 'synth_bt_ir10.8':
        varname1_lvtype = 'sl'
        varname1_folder = 'synmsg_bt_cl_ir10.8'
        varname1_grib = 'synmsg_bt_cl_ir10.8'
        varname1_cf = 'clbt'
    elif var == 'orography':
        varname1_grib = None
        if model == 'icon-eu-eps':
            if grid == 'latlon_0.2':
                filename_inv = 'icon-eu-eps_latlon_0.2_time-invariant_hsurf.nc'
            else:
                filename_inv = 'icon-eu-eps_europe_icosahedral_time-invariant_2021021700_hsurf.grib2'
        elif model == 'icon-global-det':
            if grid == 'latlon_0.1':
                filename_inv = 'icon-global-det_latlon_0.1_time-invariant_hsurf.nc'
            else:
                filename_inv = 'icon_global_icosahedral_time-invariant_2021021700_HSURF.grib2'


    path = dict(base = '/')

    if 'point' in kwargs:
        # structure: icon-eu-det: point_index = [latitude, longitude], other models: point_index = [index]
        point_index = get_point_index(model, kwargs['point'])
        if model == 'icon-eu-eps':
            values_chunksize = 19000
        elif model == 'icon-global-eps':
            values_chunksize = 82000
    elif 'fcst_hour' in kwargs:
        fcst_hours_list = get_fcst_hours_list_var_grid(model, varname1_grib, grid)
        fcst_hour_index = fcst_hours_list.index(kwargs['fcst_hour'])
        if var == 'prec_6h':
            fcst_hour_start = kwargs['fcst_hour'] - 6
            if fcst_hour_start < 0:
                fcst_hour_start = 0
            fcst_hour_index_start = fcst_hours_list.index(fcst_hour_start)
        if var == 'prec_24h':
            fcst_hour_start = kwargs['fcst_hour'] - 24
            if fcst_hour_start < 0:
                fcst_hour_start = 0
            fcst_hour_index_start = fcst_hours_list.index(fcst_hour_start)

    model_grib_str = model + '_' + grid


    if 'varname1_folder' in locals():
        if varname1_lvtype == 'sl':
            level_str = 'single-level'
        elif varname1_lvtype == 'pl':
            level_str = 'pressure-level'
        path['subdir'] = 'data/model_data/{}/forecasts/run_{}{:02}{:02}{:02}/{}/'.format(
                          model, date['year'], date['month'], date['day'], date['hour'], varname1_folder)
        if grid == 'icosahedral':
            if 'point' in kwargs:
                if model == 'icon-eu-eps' or model == 'icon-global-eps':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}_{:04d}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname1_grib, point_index[0] // values_chunksize)
                elif model == 'icon-eu-det' or model == 'icon-global-det':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname1_grib)
            elif 'fcst_hour' in kwargs:
                filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                            model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                            varname1_grib)
        elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
            filename = '{}_{}_{}{:02}{:02}{:02}_{:03d}h_{}.nc'.format(
                        model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                        kwargs['fcst_hour'], varname1_grib)
        elif grid == 'latlon_0.0625':
            filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                        model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                        varname1_grib)

        ds = xr.open_dataset(path['base'] + path['subdir'] + filename)

        if 'point' in kwargs:
            if model == 'icon-eu-eps' or model == 'icon-global-eps':
                data_var1 = ds[varname1_cf].loc[dict(values = point_index[0] % values_chunksize)].values
            elif model == 'icon-eu-det':
                data_var1 = ds[varname1_cf][dict(latitude = point_index[0], longitude = point_index[1])].values
            elif 'icon-global-det':
                data_var1 = ds[varname1_cf].loc[dict(values = point_index[0])].values

        elif 'fcst_hour' in kwargs:
            if var == 'prec_rate':
                if fcst_hour_index == 0:
                    fcst_hour_index = 1
                data_var1 = (ds[varname1_cf][dict(step = fcst_hour_index)].values \
                            - ds[varname1_cf][dict(step = fcst_hour_index - 1)].values) \
                            / float(fcst_hours_list[fcst_hour_index] - fcst_hours_list[fcst_hour_index - 1])
                print(fcst_hours_list[fcst_hour_index - 1], fcst_hours_list[fcst_hour_index])
                data_var1 = np.where(data_var1 >= 0.0, data_var1, 0.0)
                data_var1 = np.around(data_var1, 2)
            elif var == 'prec_6h':
                data_var1 = ds[varname1_cf][dict(step = fcst_hour_index)].values \
                            - ds[varname1_cf][dict(step = fcst_hour_index_start)].values
                data_var1 = np.where(data_var1 >= 0.0, data_var1, 0.0)
                data_var1 = np.around(data_var1, 2)
            elif var == 'prec_24h':
                data_var1 = ds[varname1_cf][dict(step = fcst_hour_index)].values \
                            - ds[varname1_cf][dict(step = fcst_hour_index_start)].values
                data_var1 = np.where(data_var1 >= 0.0, data_var1, 0.0)
                data_var1 = np.around(data_var1, 2)
            else:
                if grid == 'icosahedral':
                    data_var1 = ds[varname1_cf][dict(step = fcst_hour_index)].values

                elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
                    if model == 'icon-eu-eps':
                        if varname1_lvtype == 'sl':
                            if varname1_cf == '2t':
                                filter_vars_dict = dict(time = 0, height = 0)
                            else:
                                filter_vars_dict = dict(time = 0)
                        elif varname1_lvtype == 'pl':
                            filter_vars_dict = dict(time = 0, plev = 0)

                        new_data_shape = ds[varname1_cf][filter_vars_dict].values.shape
                        data_var1 = np.empty((40, new_data_shape[0], new_data_shape[1]))

                        for i in range(1, 40+1):
                            if i == 1:
                                varname_str = varname1_cf
                            else:
                                varname_str = varname1_cf + '_{:d}'.format(i)
                            data_var1[i-1, :, :] = ds[varname_str][filter_vars_dict].values

                    elif model == 'icon-global-det':
                        if varname1_lvtype == 'sl':
                            if varname1_cf == '10u':
                                data_var1 = ds[varname1_cf][dict(time = 0, height = 0)].values
                            else:
                                data_var1 = ds[varname1_cf][dict(time = 0)].values
                        elif varname1_lvtype == 'pl':
                            data_var1 = ds[varname1_cf][dict(time = 0, plev = 0)].values

                elif grid == 'latlon_0.0625':
                    data_var1 = ds[varname1_cf][dict(step = fcst_hour_index)].values
        ds.close()
        del ds


    if 'varname2_folder' in locals():
        if varname2_lvtype == 'sl':
            level_str = 'single-level'
        elif varname2_lvtype == 'pl':
            level_str = 'pressure-level'
        path['subdir'] = 'data/model_data/{}/forecasts/run_{}{:02}{:02}{:02}/{}/'.format(
                          model, date['year'], date['month'], date['day'], date['hour'], varname2_folder)
        if grid == 'icosahedral':
            if 'point' in kwargs:
                if model == 'icon-eu-eps' or model == 'icon-global-eps':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}_{:04d}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname2_grib, point_index[0] // values_chunksize)
                elif model == 'icon-eu-det' or model == 'icon-global-det':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname2_grib)
            elif 'fcst_hour' in kwargs:
                filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                            model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                            varname2_grib)
        elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
            filename = '{}_{}_{}{:02}{:02}{:02}_{:03d}h_{}.nc'.format(
                        model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                        kwargs['fcst_hour'], varname2_grib)

        ds = xr.open_dataset(path['base'] + path['subdir'] + filename)

        if 'point' in kwargs:
            if model == 'icon-eu-eps' or model == 'icon-global-eps':
                data_var2 = ds[varname2_cf].loc[dict(values = point_index[0] % values_chunksize)].values
            elif model == 'icon-eu-det':
                data_var2 = ds[varname2_cf][dict(latitude = point_index[0], longitude = point_index[1])].values
            elif 'icon-global-det':
                data_var2 = ds[varname2_cf].loc[dict(values = point_index[0])].values

        elif 'fcst_hour' in kwargs:
            if grid == 'icosahedral':
                data_var2 = ds[varname2_cf][dict(step = fcst_hour_index)].values

            elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
                if model == 'icon-eu-eps':
                    if varname2_lvtype == 'sl':
                        if varname2_cf == '2t':
                            filter_vars_dict = dict(time = 0, height = 0)
                        else:
                            filter_vars_dict = dict(time = 0)
                    elif varname2_lvtype == 'pl':
                        filter_vars_dict = dict(time = 0, plev = 0)

                    new_data_shape = ds[varname2_cf][filter_vars_dict].values.shape
                    data_var2 = np.empty((40, new_data_shape[0], new_data_shape[1]))

                    for i in range(1, 40+1):
                        if i == 1:
                            varname_str = varname2_cf
                        else:
                            varname_str = varname2_cf + '_{:d}'.format(i)
                        data_var2[i-1, :, :] = ds[varname_str][filter_vars_dict].values

                elif model == 'icon-global-det':
                    if varname2_lvtype == 'sl':
                        if varname2_cf == '10v':
                            data_var2 = ds[varname2_cf][dict(time = 0, height = 0)].values
                        else:
                            data_var2 = ds[varname2_cf][dict(time = 0)].values
                    elif varname2_lvtype == 'pl':
                        data_var2 = ds[varname2_cf][dict(time = 0, plev = 0)].values
        ds.close()
        del ds


    if 'varname3_folder' in locals():
        if varname3_lvtype == 'sl':
            level_str = 'single-level'
        elif varname3_lvtype == 'pl':
            level_str = 'pressure-level'
        path['subdir'] = 'data/model_data/{}/forecasts/run_{}{:02}{:02}{:02}/{}/'.format(
                          model, date['year'], date['month'], date['day'], date['hour'], varname3_folder)
        if grid == 'icosahedral':
            if 'point' in kwargs:
                if model == 'icon-eu-eps' or model == 'icon-global-eps':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}_{:04d}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname3_grib, point_index[0] // values_chunksize)
                elif model == 'icon-eu-det' or model == 'icon-global-det':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname3_grib)
            elif 'fcst_hour' in kwargs:
                filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                            model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                            varname3_grib)
        elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
            filename = '{}_{}_{}{:02}{:02}{:02}_{:03d}h_{}.nc'.format(
                        model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                        kwargs['fcst_hour'], varname3_grib)

        ds = xr.open_dataset(path['base'] + path['subdir'] + filename)

        if 'point' in kwargs:
            if model == 'icon-eu-eps' or model == 'icon-global-eps':
                data_var3 = ds[varname3_cf].loc[dict(values = point_index[0] % values_chunksize)].values
            elif model == 'icon-eu-det':
                data_var3 = ds[varname3_cf][dict(latitude = point_index[0], longitude = point_index[1])].values
            elif 'icon-global-det':
                data_var3 = ds[varname3_cf].loc[dict(values = point_index[0])].values

        elif 'fcst_hour' in kwargs:
            if grid == 'icosahedral':
                data_var3 = ds[varname3_cf][dict(step = fcst_hour_index)].values

            elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
                if model == 'icon-eu-eps':
                    if varname3_lvtype == 'sl':
                        if varname3_cf == '2t':
                            filter_vars_dict = dict(time = 0, height = 0)
                        else:
                            filter_vars_dict = dict(time = 0)
                    elif varname3_lvtype == 'pl':
                        filter_vars_dict = dict(time = 0, plev = 0)

                    new_data_shape = ds[varname3_cf][filter_vars_dict].values.shape
                    data_var3 = np.empty((40, new_data_shape[0], new_data_shape[1]))

                    for i in range(1, 40+1):
                        if i == 1:
                            varname_str = varname3_cf
                        else:
                            varname_str = varname3_cf + '_{:d}'.format(i)
                        data_var3[i-1, :, :] = ds[varname_str][filter_vars_dict].values

                elif model == 'icon-global-det':
                    if varname3_lvtype == 'sl':
                        data_var3 = ds[varname3_cf][dict(time = 0)].values
                    elif varname3_lvtype == 'pl':
                        data_var3 = ds[varname3_cf][dict(time = 0, plev = 0)].values
        ds.close()
        del ds


    if 'varname4_folder' in locals():
        if varname4_lvtype == 'sl':
            level_str = 'single-level'
        elif varname4_lvtype == 'pl':
            level_str = 'pressure-level'
        path['subdir'] = 'data/model_data/{}/forecasts/run_{}{:02}{:02}{:02}/{}/'.format(
                          model, date['year'], date['month'], date['day'], date['hour'], varname4_folder)
        if grid == 'icosahedral':
            if 'point' in kwargs:
                if model == 'icon-eu-eps' or model == 'icon-global-eps':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}_{:04d}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname4_grib, point_index[0] // values_chunksize)
                elif model == 'icon-eu-det' or model == 'icon-global-det':
                    filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                                model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                                varname4_grib)
            elif 'fcst_hour' in kwargs:
                filename = '{}_{}_{}{:02}{:02}{:02}_{}.nc'.format(
                            model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                            varname4_grib)
        elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
            filename = '{}_{}_{}{:02}{:02}{:02}_{:03d}h_{}.nc'.format(
                        model_grib_str, level_str, date['year'], date['month'], date['day'], date['hour'],
                        kwargs['fcst_hour'], varname4_grib)

        ds = xr.open_dataset(path['base'] + path['subdir'] + filename)

        if 'point' in kwargs:
            if model == 'icon-eu-eps' or model == 'icon-global-eps':
                data_var4 = ds[varname4_cf].loc[dict(values = point_index[0] % values_chunksize)].values
            elif model == 'icon-eu-det':
                data_var4 = ds[varname4_cf][dict(latitude = point_index[0], longitude = point_index[1])].values
            elif 'icon-global-det':
                data_var4 = ds[varname4_cf].loc[dict(values = point_index[0])].values

        elif 'fcst_hour' in kwargs:
            if grid == 'icosahedral':
                data_var4 = ds[varname4_cf][dict(step = fcst_hour_index)].values

            elif grid == 'latlon_0.2' or grid == 'latlon_0.1':
                if model == 'icon-eu-eps':
                    if varname4_lvtype == 'sl':
                        if varname4_cf == '2t':
                            filter_vars_dict = dict(time = 0, height = 0)
                        else:
                            filter_vars_dict = dict(time = 0)
                    elif varname4_lvtype == 'pl':
                        filter_vars_dict = dict(time = 0, plev = 0)

                    new_data_shape = ds[varname4_cf][filter_vars_dict].values.shape
                    data_var4 = np.empty((40, new_data_shape[0], new_data_shape[1]))

                    for i in range(1, 40+1):
                        if i == 1:
                            varname_str = varname4_cf
                        else:
                            varname_str = varname4_cf + '_{:d}'.format(i)
                        data_var4[i-1, :, :] = ds[varname_str][filter_vars_dict].values

                elif model == 'icon-global-det':
                    if varname4_lvtype == 'sl':
                        data_var4 = ds[varname4_cf][dict(time = 0)].values
                    elif varname4_lvtype == 'pl':
                        data_var4 = ds[varname4_cf][dict(time = 0, plev = 0)].values
        ds.close()
        del ds


    if 'filename_inv' in locals():
        path['subdir'] = 'data/model_data/{}/invariant/'.format(model)
        if grid == 'latlon_0.2'\
         or grid == 'latlon_0.1':
            ds = xr.open_dataset(path['base'] + path['subdir'] + filename_inv)
            data_var_inv = ds['HSURF'][dict(time = 0)].values
            ds.close()
            del ds
        else:
            ds = xr.open_dataset(path['base'] + path['subdir'] + filename_inv, engine='cfgrib', backend_kwargs={'errors': 'ignore'})
            if 'point' in kwargs:
                data_var_inv = float(ds['h'][point_index[0]].values)
            elif 'fcst_hour' in kwargs:
                data_var_inv = ds['h'].values
            ds.close()
            del ds


    # calculate final variables out of the read data arrays #

    if var == 't_2m':           # in deg C
        data_final = data_var1 - 273.15
    elif var == 'prec_rate':    # in mm/h
        if 'point' in kwargs:
            data_final = calculate_inst_values_of_sum(data_var1, model)
        elif 'fcst_hour' in kwargs:
            data_final = data_var1
    elif var == 'snow_rate':    # in mm/h (water equivalent)
        if 'point' in kwargs:
            data_final = calculate_inst_values_of_sum(data_var1, model) \
                       + calculate_inst_values_of_sum(data_var2, model)
    elif var == 'prec_6h':     # in mm
        data_final = data_var1
    elif var == 'prec_24h':     # in mm
        data_final = data_var1
    elif var == 'prec_sum':     # in mm
        data_final = data_var1
    elif var == 'wind_mean_10m':    # in km/h
        data_final = np.sqrt(data_var1**2 + data_var2**2) * 3.6
    elif var == 'mslp':         # in hPa
        if model == 'icon-eu-eps':
            # reduce surface pressure to mslp with DWD formula and height and t2m #
            data_final = data_var1 * 1e-2 * np.exp(9.80665 * data_var_inv / (287.05 * data_var2))
        elif model == 'icon-eu-det' or model == 'icon-global-det':
            data_final = data_var1 * 1e-2
    elif var == 'cape_ml':      # in J/kg
        data_final = data_var1
    elif var == 'clct':         # in %
        data_final = data_var1
    elif var == 'direct_rad':
        data_final = calculate_inst_values_of_avg(data_var1, model)
    elif var == 'diffuse_rad':
        data_final = calculate_inst_values_of_avg(data_var1, model)
    elif var == 'vmax_10m':     # in km/h
        data_final = data_var1 * 3.6
    elif var == 'tqv':          # in mm
        data_final = data_var1
    elif var == 'gph_300hPa':   # in gpdm
        data_final = data_var1 / 98.0665
    elif var == 'gph_500hPa':   # in gpdm
        data_final = data_var1 / 98.0665
    elif var == 'gph_700hPa':   # in gpdm
        data_final = data_var1 / 98.0665
    elif var == 'gph_850hPa':   # in gpdm
        data_final = data_var1 / 98.0665
    elif var == 't_850hPa':     # in deg C
        data_final = data_var1 - 273.15
    elif var == 'theta_e_850hPa':
        data_final = calc_the_from_relhum(data_var2, data_var1, 850) - 273.15
    elif var == 'wind_850hPa':  # in km/h
        data_final = np.sqrt(data_var1**2 + data_var2**2) * 3.6
    elif var == 'wind_500hPa':  # in km/h
        data_final = np.sqrt(data_var1**2 + data_var2**2) * 3.6
    elif var == 'wind_300hPa':  # in km/h
        data_final = np.sqrt(data_var1**2 + data_var2**2) * 3.6
    elif var == 'windvector_300hPa':  # in km/h
        print(data_var1.shape)
        data_final = np.stack((data_var1, data_var2)) #feld mit u,v,lat,
        print(data_final.shape)
    elif var == 'u_300hPa':
        data_final = data_var1
    elif var == 'v_300hPa':
        data_final = data_var1    
    elif var[:5] == 'u_div' and var[-1:] == 'K':
        data_final = data_var1 
    elif var[:5] == 'v_div' and var[-1:] == 'K':
        data_final = data_var1 
    elif var == 'shear_0-6km':  # in m/s
        data_final = np.sqrt((data_var3 - data_var1)**2 + (data_var4 - data_var2)**2)
    elif var == 'shear_200-850hPa':  # in knots
        data_final = np.sqrt((data_var1 - data_var3)**2 + (data_var2 - data_var4)**2) * 1.943844
    elif var == 'lapse_rate_850hPa-500hPa':     # in k/km
        data_final = 9806.65 * (data_var1 - data_var3) / (data_var4 - data_var2)
    elif var == 'synth_bt_ir10.8':      # in deg C
        data_final = data_var1 - 273.15
    elif var == 'orography':            # in m
        data_final = data_var_inv
    elif var[:2] == 'pv' and var[-1:] == 'K':       # in PVU
        data_final = data_var1
    elif var[:10] == 'pv_adv_div' and var[-1:] == 'K':
        data_final = data_var1
    elif var[:5] == 'theta' and var[-3:] == 'PVU':  # in K
        data_final = data_var1
    elif var == 'ivt':            # in kg /m / s
        data_final = data_var1
    elif var[:6] == 'w_mean':     # in m / s
        data_final = data_var1
    elif var == 'qvec_div_850hPa':
        data_final = data_var1
    elif var == 'qvec_div_700-900hPa':
        data_final = data_var1
    elif var == 'qvec_x_700-900hPa':
        data_final = data_var1
    elif var == 'qvec_y_700-900hPa':
        data_final = data_var1


    #print(var + ', shape:', data_final.shape)
    return data_final

########################################################################
########################################################################
########################################################################

def read_forecast_pp_data(model, date, var, pointname):
    path = dict(base = '/',
                textfiles_pp_eu = 'data/model_data/icon-eu-eps/point-forecasts/benedikt_post_processing/',
                textfiles_pp_global = 'data/model_data/icon-global-eps/point-forecasts/benedikt_post_processing/')
    subfolder = 'latest_run_pp/{}/'.format(pointname)

    filename = '{}_latest_run_pp_{}_{}.txt'.format(model, var, pointname)

    if model == 'icon-eu-eps':
        data_table = ascii.read(path['base'] + path['textfiles_pp_eu'] + subfolder + filename)
    elif model == 'icon-global-eps':
        data_table = ascii.read(path['base'] + path['textfiles_pp_global'] + subfolder + filename)

    data = data_table.as_array()

    read_values = np.zeros((len(data), len(data[0])-1), dtype='float32')
    for i in range(len(data)):
        data_row = data.data[i]
        for j in range(1,len(data[0])):
            read_values[i][j-1] = data_row[j]

    return read_values[1:, :-1]

########################################################################
########################################################################
########################################################################

def get_point_index(model, point):

    # if known named point get grid point location #

    if not 'lat' in point:
        #print('pointname is known: {}'.format(point['name']))
        point = which_grid_point(point['name'], model)


    path = dict(base = '/')
    path['subdir'] = 'data/model_data/{}/grid/'.format(model)

    if model == 'icon-eu-eps':
        filename_clat = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clat.grib2'
        filename_clon = 'icon-eu-eps_europe_icosahedral_time-invariant_2018121000_clon.grib2'
    elif model == 'icon-global-eps':
        filename_clat = 'icon-eps_global_icosahedral_time-invariant_2019010800_clat.grib2'
        filename_clon = 'icon-eps_global_icosahedral_time-invariant_2019010800_clon.grib2'
    elif model == 'icon-eu-det':
        filename_clat = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLAT.grib2'
        filename_clon = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLON.grib2'
    elif model == 'icon-global-det':
        filename_clat = 'icon_global_icosahedral_time-invariant_2020020700_CLAT.grib2'
        filename_clon = 'icon_global_icosahedral_time-invariant_2020020700_CLON.grib2'


    # get clat and clon 1D arrays #

    with open(path['base'] + path['subdir'] + filename_clat,'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clat = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)
    with open(path['base'] + path['subdir'] + filename_clon,'rb') as file:
        grib_id = eccodes.codes_grib_new_from_file(file)
        clon = eccodes.codes_get_array(grib_id, 'values')
        eccodes.codes_release(grib_id)


    # read out index of nearest icosahedral point #

    filter_distance = get_latlon_filter_distance(model)
    lat_near = list(np.where(abs(clat - point['lat']) < filter_distance)[0])
    lon_near = list(np.where(abs(clon - point['lon']) < filter_distance)[0])
    id_near = list(set(lat_near).intersection(lon_near))
    id_near.sort()
    distances = np.sqrt( np.square(abs(clat[id_near] - point['lat']) * 111.2) \
                        + np.square(abs(clon[id_near] - point['lon']) * 111.2 \
                                                 * np.cos(point['lat']*np.pi/180)) )
    index_nearest = id_near[np.argmin(distances)]

    #print(id_near)
    #print(distances)
    #print(index_nearest)
    #print(clat[index_nearest], clon[index_nearest])

    if model == 'icon-eu-det':
        # this model data is on regular lat-lon-grid #
        lat_index = int((clat[index_nearest] - 29.5) / 0.0625)
        lon_index = int((clon[index_nearest] + 23.5) / 0.0625)
        point_index = [lat_index, lon_index]
    else:
        # all other model data is on icosahedral grid with single index #
        point_index = [index_nearest]


    return point_index

########################################################################
########################################################################
########################################################################

def calculate_inst_values_of_avg(data_avg, model):

    # calculate aswdir_s, aswdifd_s #

    fcst_hours_list = get_fcst_hours_list(model)
    if model == 'icon-eu-eps' or model == 'icon-global-eps':
        data_inst = np.zeros((len(fcst_hours_list)-1, 40), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i,:] = (fcst_hours_list[i+1]*data_avg[i+1,:] - fcst_hours_list[i]*data_avg[i,:])\
                                 / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    elif model == 'icon-eu-det' or model == 'icon-global-det':
        data_inst = np.zeros((len(fcst_hours_list)-1), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i] = (fcst_hours_list[i+1]*data_avg[i+1] - fcst_hours_list[i]*data_avg[i])\
                                 / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    data_inst = np.where(data_inst >= 0., data_inst, 0.)
    data_inst = np.around(data_inst, 1)

    return data_inst


def calculate_inst_values_of_sum(data_sum, model):

    # calculate prec_rate #

    fcst_hours_list = get_fcst_hours_list(model)
    if model == 'icon-eu-eps' or model == 'icon-global-eps' or model == 'pamore_icon-global-eps':
        data_inst = np.zeros((len(fcst_hours_list)-1, 40), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i,:] = (data_sum[i+1,:] - data_sum[i,:]) / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    elif model == 'icon-eu-det' or model == 'icon-global-det':
        data_inst = np.zeros((len(fcst_hours_list)-1), dtype='float32')
        for i in range(len(fcst_hours_list)-1):
            data_inst[i] = (data_sum[i+1] - data_sum[i]) / float(fcst_hours_list[i+1] - fcst_hours_list[i])
    data_inst = np.where(data_inst >= 0.0, data_inst, 0.0)
    data_inst = np.around(data_inst, 2)

    return data_inst

########################################################################
########################################################################
########################################################################

def get_fcst_hours_list(model):
    if model == 'icon-eu-eps':
        fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
    elif model == 'icon-global-eps':
        fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120,6)) +list(range(120,180+1,12))
    elif model == 'icon-global-eps_eu-extension':
        fcst_hours_list = list(range(132,180+1,12))
    elif model == 'icon-eu-det':
        fcst_hours_list = list(range(0,78,1)) + list(range(78,120+1,3))
    elif model == 'icon-global-det':
        fcst_hours_list = list(range(0,78,1)) + list(range(78,180+1,3))
    elif model == 'pamore_icon-global-eps':
        fcst_hours_list = list(range(0,75,1)) + list(range(75,180+1,3))

    return fcst_hours_list

########################################################################
########################################################################
########################################################################

def get_fcst_hours_list_var_grid(model, var, grid):
    if model == 'icon-eu-eps':
        if grid == 'icosahedral':
            fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120+1,6))
        elif grid == 'latlon_0.2':
            fcst_hours_list = list(range(0,120+1,6))
    elif model == 'icon-global-eps':
        fcst_hours_list = list(range(0,48,1)) + list(range(48,72,3)) + list(range(72,120,6)) +list(range(120,180+1,12))
    elif model == 'icon-global-eps_eu-extension':
        fcst_hours_list = list(range(132,180+1,12))
    elif model == 'icon-eu-det':
        if var == 'tot_prec':
            fcst_hours_list = list(range(0,78,1)) + list(range(78,120+1,3))
        else:
            fcst_hours_list = list(range(0,120+1,3))
            #fcst_hours_list = list(range(0,78+1,1))
    elif model == 'icon-global-det':
        if var == 'tot_prec':
            fcst_hours_list = list(range(0,78,1)) + list(range(78,180+1,3))
        else:
            fcst_hours_list = list(range(0,180+1,6))
            #fcst_hours_list = list(range(0,78,1)) + list(range(78,180+1,3))
            #fcst_hours_list = list(range(0,78+1,1))
    elif model == 'pamore_icon-global-eps':
        fcst_hours_list = list(range(0,75,1)) + list(range(75,180+1,3))

    return fcst_hours_list

########################################################################
########################################################################
########################################################################

def get_all_available_vars(models, date):
    if models == 'both-eps':
        if date['hour'] == 0 or date['hour'] == 12:
            #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','wind_mean_10m','vmax_10m','mslp','clct',\
            #'direct_rad','diffuse_rad','tqv','gph_500hPa','t_850hPa','wind_850hPa',\
            #'shear_0-6km','lapse_rate_850hPa-500hPa']
            var_list = ['t_2m','prec_rate','snow_rate','prec_sum','wind_10m','mslp','clct',
                        'direct_rad','diffuse_rad','tqv','cape_ml','t_850hPa','shear_0-6km']
            #var_list = ['snow_rate']
        else:
            #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','wind_mean_10m','vmax_10m','mslp','clct',\
            #'direct_rad','diffuse_rad']
            var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad', 'diffuse_rad']
    elif models == 'icon-global-eps':
        var_list = ['t_2m','prec_rate','prec_sum','wind_mean_10m','clct']


    return var_list

########################################################################
########################################################################
########################################################################

def read_grid_coordinates(model, grid):
    path = dict(base = '/')
    path['grid'] = 'data/model_data/{}/grid/'.format(model)

    if model == 'icon-eu-eps':
        if grid == 'icosahedral':
            filename = 'icon_grid_0028_R02B07_N02.nc'
        elif grid == 'latlon_0.2':
            filename = 'icon-eu-eps_latlon_0.2_grid_coordinates.nc'
    elif model == 'icon-global-eps':
        filename = 'icon_grid_0024_R02B06_G.nc'
    elif model == 'icon-eu-det':
        filename_clat = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLAT.grib2'
        filename_clon = 'icon-eu_europe_regular-lat-lon_time-invariant_2019040800_RLON.grib2'
    elif model == 'icon-global-det':
        if grid == 'icosahedral':
            filename = 'icon_grid_0026_R03B07_G.nc'
        elif grid == 'latlon_0.25':
            filename = 'icon-global-det_latlon_0.25_grid_coordinates.nc'
        elif grid == 'latlon_0.1':
            filename = 'icon-global-det_latlon_0.1_grid_coordinates.nc'

    if grid == 'icosahedral':
        with xr.open_dataset(path['base'] + path['grid'] + filename) as ds:
            clat = ds['clat'].values * 180 / np.pi
            clon = ds['clon'].values * 180 / np.pi
            vlat = ds['clat_vertices'].values * 180 / np.pi
            vlon = ds['clon_vertices'].values * 180 / np.pi
        return clat, clon, vlat, vlon

    elif grid == 'latlon_0.0625':
        with open(path['base'] + path['grid'] + filename_clat,'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clat = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        with open(path['base'] + path['grid'] + filename_clon,'rb') as file:
            grib_id = eccodes.codes_grib_new_from_file(file)
            clon = eccodes.codes_get_array(grib_id, 'values')
            eccodes.codes_release(grib_id)
        return clat.reshape((657, 1097)), clon.reshape((657, 1097))

    elif grid == 'latlon_0.2':
        with xr.open_dataset(path['base'] + path['grid'] + filename) as ds:
            clat = ds['lat'].values
            clon = ds['lon'].values
        return clat, clon

    elif grid == 'latlon_0.25':
        with xr.open_dataset(path['base'] + path['grid'] + filename) as ds:
            clat = ds['lat'].values
            clon = ds['lon'].values
        clon = np.where(clon > 180, clon - 360, clon)
        clon_new = np.empty_like(clon)
        clon_new[719:] = clon[:721]
        clon_new[:719] = clon[721:]
        return clat, clon_new

    elif grid == 'latlon_0.1':
        with xr.open_dataset(path['base'] + path['grid'] + filename) as ds:
            clat = ds['lat'].values
            clon = ds['lon'].values
        clon = np.where(clon > 180, clon - 360, clon)
        clon_new = np.empty_like(clon)
        clon_new[1799:] = clon[:1801]
        clon_new[:1799] = clon[1801:]
        return clat, clon_new

########################################################################
########################################################################
########################################################################
