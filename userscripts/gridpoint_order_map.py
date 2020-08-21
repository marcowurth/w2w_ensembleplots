#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
from w2w_ensembleplots.core.gridpoint_order import grid_order_contourplot
from w2w_ensembleplots.core.domain_definitions import get_domain

def main():

    model = 'icon-global-det'

    #cut_domain = dict(name = 'uncut')
    cut_domain = get_domain('europe')
    cut_domain = get_domain('northern_pacific')
    cut_domain = get_domain('atlantic_basin')

    grid_order_contourplot(model, cut_domain)

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
