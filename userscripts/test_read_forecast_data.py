
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_forecast_data


def main():

    date = dict(year = 2020, month = 10, day = 16, hour = 0)

    model = 'icon-eu-eps'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_mean_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m',\
    #            'tqv','gph_500hPa','gph_300hPa','t_850hPa','wind_850hPa','wind_300hPa',\
    #            'shear_0-6km','lapse_rate_850hPa-500hPa']
    var_list = ['orography']

    #model = 'icon-eu-det'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_mean_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m']
    #var_list = ['synth_bt_ir10.8']
    #var_list = ['vmax_10m']

    #model = 'icon-global-eps'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_mean_10m','clct']
    #var_list = ['prec_24h']

    #model = 'icon-global-det'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_mean_10m','clct','mslp','t_850hPa',\
    #            'gph_500hPa','gph_300hPa','wind_300hPa','theta_e_850hPa']
    #var_list = ['shear_0-6km']
    #var_list = ['mslp','t_850hPa','gph_500hPa','gph_300hPa','wind_300hPa']

    #grid = 'icosahedral'
    grid = 'latlon_0.2'
    #grid = 'latlon_0.1'
    #grid = 'latlon_0.0625'  # dwd provides icon-eu-det fields only on this grid

    #point = dict(lat = 49.014, lon =  8.404)
    #point = dict(name = 'Mainz')

    fcst_hour = 0   # in hours

    #for fcst_hour in range(0, 180+1, 12):
    for var in var_list:
        #print(var)
        #data = read_forecast_data(model, grid, date, var, point=point)
        data = read_forecast_data(model, grid, date, var, fcst_hour=fcst_hour)
        print(data)
        #print(max(data.ravel()))

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    delta_t = t2-t1
    if delta_t < 60:
        print('total script time:  {:.1f}s'.format(delta_t))
    elif 60 <= delta_t <= 3600:
        print('total script time:  {:.0f}min{:.0f}s'.format(delta_t//60, delta_t-delta_t//60*60))
    else:
        print('total script time:  {:.0f}h{:.1f}min'.format(delta_t//3600, (delta_t-delta_t//3600*3600)/60))
