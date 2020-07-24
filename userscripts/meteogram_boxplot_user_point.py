###############################################################################
###  script for plotting boxplot meteograms of point data of icon-eu-eps    ###
###############################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.meteogram_boxplot import boxplot_forecast


def main():

  ###########################################################
    #date = dict(year = 2020, month = 3, day = 3, hour = 0)
    date = 'latest'

    var = 'all_available'
    #var = 't_2m'
    #var = 'prec_rate'
    #var = 'prec_sum'
    #var = 'mslp'
    #var = 'wind_10m'
    #var = 'wind_850hPa'

    #point = dict(lat = 52.519, lon = 13.407, name = 'Berlin')
    #point = dict(lat = 49.014, lon =  8.404, name='Karlsruhe')
    #point = dict(lat = 37.984, lon = 23.690, name = 'Athens')
    #point = dict(lat =-33.337, lon =-60.213, name = 'San Nicolás')
    point = dict(lat =-34.800, lon =-58.400, name = 'Buenos Aires')
    #point = dict(lat =-31.409, lon =-64.186, name = 'Córdoba Capital')
    #point = dict(lat =-27.486, lon =-58.814, name = 'Corrientes Capital')

    plot_type = 'user_point'

    verbose = True

  ###########################################################

    if point['lon'] > 180.0:
        point['lon'] -= 360.0
    if point['lat'] > 29.5 and point['lat'] < 70.5 and point['lon'] > -23.5 and point['lon'] < 62.5:
        models = 'both-eps'
    #else:
    models = 'icon-global-eps'


    boxplot_forecast(models, date, var, point, plot_type, verbose)



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
