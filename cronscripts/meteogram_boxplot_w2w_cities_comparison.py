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
    date = 'comparison'
    var = 'all_available'
    pointnames =   ['Karlsruhe','Mainz','Munich',\
                    'Amsterdam','Athens','Berlin','Bologna','Brussels','Copenhagen','Dublin','Hamburg',\
                    'Madrid','Leeds','Lisbon','London','Paris','Rome','Toulouse','Valencia','Vienna','Warsaw','Zurich']
    plot_type = 'w2w_city'
    verbose = True

  ###########################################################

    for pointname in pointnames:
        boxplot_forecast(models, date, var, dict(name = pointname), plot_type, verbose)


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
