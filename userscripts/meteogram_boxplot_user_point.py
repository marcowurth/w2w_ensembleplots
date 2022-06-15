###############################################################################
###  script for plotting boxplot meteograms of point data of icon-eu-eps    ###
###############################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.meteogram_boxplot import boxplot_forecast_raw


def main():

  ###########################################################
    models = 'both-eps'     # plot icon-eu-eps only if global not available
    date = dict(year = 2022, month = 6, day = 13, hour = 0)
    #date = 'latest'

    #var = 'all_available'
    #var = 't_2m'
    #var = 'prec_rate'
    #var = 'prec_sum'
    #var = 'mslp'
    #var = 'wind_10m'
    #var = 't_850hPa'
    var = 'cape_ml'

    #pointnames_raw =   ['Karlsruhe','Mainz','Munich','Berlin','Hamburg','Offenbach',\
    #                    'Amsterdam','Athens','Bologna','Brussels','Copenhagen','Dublin',\
    #                    'Madrid','Leeds','Lisbon','London','Paris','Rome',\
    #                    'Toulouse','Valencia','Vienna','Warsaw','Zurich']
    pointnames_raw = ['Karlsruhe']

    point_type = 'operational_city'
    verbose = True
  ###########################################################

    for pointname in pointnames_raw:
        if verbose:
            print('--- next meteogram (raw) point is {} ---'.format(pointname))

        save_point_data = False
        y_axis_limits = 'raw'
        boxplot_forecast_raw(models, date, var, dict(name = pointname),
                             point_type, save_point_data, y_axis_limits, verbose)


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
