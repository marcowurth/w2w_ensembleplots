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
    models = 'both-eps'     # plot icon-eu-eps only if global not available
    #models = 'icon-global-eps'

    #date = dict(year = 2020, month = 2, day = 16, hour = 12)
    date = 'latest'
    #date = 'comparison'

    #var = 'all_available'
    var = 't_2m'
    #var = 'prec_rate'
    #var = 'prec_sum'
    #var = 'wind_10m'
    #var = 'wind_mean_10m'
    #var = 'vmax_10m'

    point = dict(lat = 49.014, lon =  8.404, name='Karlsruhe')
    #point = dict(lat = 48.860, lon =  2.350, name = 'Paris')
    #point = dict(lat =-34.800, lon =-58.400, name = 'Buenos Aires')
    #point = dict(lat =-31.409, lon =-64.186, name = 'Córdoba Capital')

    plot_type = 'w2w_city'
    #plot_type = 'user_point'

    verbose = True

  ###########################################################

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
    print('total script time:  {:.1f}s'.format(t2-t1))
