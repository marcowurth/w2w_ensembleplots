#######################################################################
###    Script for Calling Plotting Scripts and Merging the Plots    ###
#######################################################################

import sys
current_path = sys.path[0]
ex_op_str = current_path[current_path.index('progs')+6: current_path.index('w2w_ensembleplots')-1]
sys.path.append('/progs/{}'.format(ex_op_str))
#from w2w_ensembleplots.core.deterministic_maps.py import plot_mslp_totprecip
from w2w_ensembleplots.core.deterministic_contourplot import det_contourplot
from w2w_ensembleplots.core.download_forecast import calc_latest_run_time

def main():

    #model = 'eu-eps'     # icon-eu-eps and icon-global-eps
    #model= 'eu-det'     # icon-eu-det and icon-global-det
    #model = 'global-eps'     # icon-global-eps
    model = 'icon-global-det'     # icon-global-det
    #model = 'icon-eu-det'

    run=calc_latest_run_time(model)
    #run = dict(year = 2020, month = 4, day = 21, hour = 12)

    domain = dict(method = 'centerpoint', radius = 1400, deltalat =   0, deltalon =   0,
                  lat = 48.0, lon =  9.0, name = 'europe')

    variable1=dict(name='prec_rate', unit='mm/h', grid='icosahedral')
    variable2=dict(name='mslp', unit='hPa', grid='latlon_0.25')

    #plot_det_map(domains, variable1, variable2, model)
    det_contourplot(domain, variable1, variable2, model, run)

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
