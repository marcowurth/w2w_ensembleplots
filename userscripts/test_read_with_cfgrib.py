
import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.read_data import read_forecast_data


def main():

    date = dict(year = 2020, month = 2, day = 13, hour = 0)

    #model = 'icon-eu-eps'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m',\
    #            'tqv','gph_500hPa','gph_300hPa','t_850hPa','wind_850hPa','wind_300hPa',\
    #            'shear_0-6km','lapse_rate_850hPa-500hPa']
    #var_list = ['t_2m','prec_sum','wind_10m','mslp','clct','vmax_10m',\
    #            'tqv','gph_500hPa','gph_300hPa','t_850hPa','wind_850hPa','wind_300hPa',\
    #            'shear_0-6km','lapse_rate_850hPa-500hPa']
    #var_list = []

    #model = 'icon-eu-det'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','mslp','clct','direct_rad','diffuse_rad','vmax_10m']
    #var_list = ['t_2m','prec_sum','wind_10m','mslp','clct','vmax_10m']

    #model = 'icon-global-eps'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','clct']
    #var_list = ['t_2m','prec_sum','wind_10m','clct']

    #model = 'icon-global-det'
    #var_list = ['t_2m','prec_rate','prec_sum','wind_10m','clct']
    #var_list = ['t_2m','prec_sum','wind_10m','clct']

    #point = dict(lat = 49.014, lon =  8.404)
    #point = dict(name = 'Mainz')

    #fcst_hour = 1

    for var in var_list:
        print(var)
        #data = read_forecast_data(model, date, var, point=point)
        #data = read_forecast_data(model, date, var, fcst_hour=fcst_hour)
        print(data)

    return

########################################################################
########################################################################
########################################################################

if __name__ == '__main__':
    import time
    t1 = time.time()
    main()
    t2 = time.time()
    print('total script time:  {:.0f}ms'.format( 1000 * (t2-t1) ))
